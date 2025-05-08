from flask import Flask, render_template, request, jsonify
import os
import base64
import numpy as np
from scipy.io.wavfile import write
from pydub import AudioSegment
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto import Random

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "static/output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

DTMF_FREQUENCIES = {
    '1': (21697, 22209), '2': (21697, 22336), '3': (21697, 22477),
    '4': (21770, 22209), '5': (21770, 22336), '6': (21770, 22477),
    '7': (21852, 22209), '8': (21852, 22336), '9': (21852, 22477),
    '0': (21941, 21336), '*': (21941, 21209), '#': (22941, 22477)
}
DEFAULT_FREQUENCY = (1000, 1500)
SAMPLE_RATE = 44100

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/encryptDecrypt')
def encrypt_decrypt():
    return render_template("encryptDecrypt.html")

@app.route('/encrypt', methods=["POST"])
def encrypt_only():
    try:
        message = request.form.get("message")
        key = request.form.get("key")

        if not message or not key:
            return jsonify({"error": "Pesan dan kunci harus diisi!"}), 400

        if len(key) != 16:
            return jsonify({"error": "Kunci harus terdiri dari 16 karakter!"}), 400

        key_bytes = key.encode()
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        ciphertext = iv + cipher.encrypt(pad(message.encode(), AES.block_size))
        ciphertext_base64 = base64.b64encode(ciphertext).decode()
        ascii_values = ''.join(str(ord(c)) for c in ciphertext_base64)

        return jsonify({
            "ciphertext": ciphertext_base64,
            "ascii": ascii_values
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process', methods=["POST"])
def process():
    try:
        message = request.form.get("message")
        key = request.form.get("key")
        file = request.files.get("file")

        if not message or not key or not file:
            return jsonify({"error": "Pesan, kunci, dan file audio harus diisi!"}), 400

        if len(key) != 16:
            return jsonify({"error": "Kunci harus 16 karakter!"}), 400

        # Enkripsi AES
        key_bytes = key.encode()
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        ciphertext = iv + cipher.encrypt(pad(message.encode(), AES.block_size))
        ciphertext_base64 = base64.b64encode(ciphertext).decode()
        ascii_values = ''.join(str(ord(c)) for c in ciphertext_base64)

        # Generate sinyal DTMF
        dtmf_signal = generate_dtmf_signal(ascii_values)
        dtmf_path = os.path.join(OUTPUT_FOLDER, "dtmf_only.wav")
        write(dtmf_path, SAMPLE_RATE, np.int16(dtmf_signal * 32767))

        # Simpan file asli
        audio_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(audio_path)

        # Load carrier
        carrier = AudioSegment.from_file(audio_path).set_channels(1)
        carrier = carrier.set_frame_rate(SAMPLE_RATE)
        carrier_samples = np.array(carrier.get_array_of_samples()).astype(np.float32)
        carrier_samples /= np.max(np.abs(carrier_samples))

        carrier_path = os.path.join(OUTPUT_FOLDER, "carrier_only.wav")
        write(carrier_path, SAMPLE_RATE, np.int16(carrier_samples * 32767))

        # Mixing
        min_len = min(len(dtmf_signal), len(carrier_samples))
        mixed = carrier_samples[:min_len] + 0.05 * dtmf_signal[:min_len]
        mixed /= np.max(np.abs(mixed))

        mixed_path = os.path.join(OUTPUT_FOLDER, "mixed_audio.wav")
        write(mixed_path, SAMPLE_RATE, np.int16(mixed * 32767))

        return jsonify({
            "ciphertext": ciphertext_base64,
            "ascii": ascii_values,
            "waveforms": {
                "dtmf": "/static/output/dtmf_only.wav",
                "carrier": "/static/output/carrier_only.wav",
                "mixed": "/static/output/mixed_audio.wav"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/decrypt', methods=["POST"])
def decrypt():
    try:
        ciphertext_base64 = request.form.get("ciphertext")
        key = request.form.get("key")

        if not ciphertext_base64 or not key:
            return jsonify({"error": "Ciphertext dan kunci harus diisi!"}), 400

        if len(key) != 16:
            return jsonify({"error": "Kunci harus 16 karakter!"}), 400

        ciphertext = base64.b64decode(ciphertext_base64)
        key_bytes = key.encode()
        iv = ciphertext[:AES.block_size]
        encrypted_data = ciphertext[AES.block_size:]

        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(encrypted_data), AES.block_size).decode()

        return jsonify({"plaintext": plaintext})
    except Exception as e:
        return jsonify({"error": f"Gagal mendekripsi: {str(e)}"}), 500

def generate_dtmf_signal(ascii_values, duration=0.2, sample_rate=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    signal = np.array([], dtype=np.float32)
    for digit in ascii_values:
        f1, f2 = DTMF_FREQUENCIES.get(digit, DEFAULT_FREQUENCY)
        tone = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)
        signal = np.append(signal, tone)
    return signal * 0.5

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
