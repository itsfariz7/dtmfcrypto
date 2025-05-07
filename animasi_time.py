import numpy as np
import simpleaudio as sa
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider
import os
import time
from scipy.io.wavfile import write
from pydub import AudioSegment
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto import Random
import base64

OUTPUT_FOLDER = "/Users/macintoshhd/Documents/SANJIF/KULIAH/TUGAS AKHIR/coba program/Output Mixing/"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

DTMF_FREQUENCIES = {
    '1': (21697, 22209), '2': (21697, 22336), '3': (21697, 22477),
    '4': (21770, 22209), '5': (21770, 22336), '6': (21770, 22477),
    '7': (21852, 22209), '8': (21852, 22336), '9': (21852, 22477),
    '0': (21941, 21336), '*': (21941, 21209), '#': (22941, 22477)
}
DEFAULT_FREQUENCY = (1000, 1500)

def aes128():
    plaintext = input("Masukkan pesan: ")
    key = input("Masukkan kunci (16 karakter): ").encode()
    if len(key) != 16:
        print("Error: Kunci harus 16 karakter!")
        return None
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = iv + cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    ciphertext_base64 = base64.b64encode(ciphertext).decode()
    ascii_values = ''.join(str(ord(char)) for char in ciphertext_base64)
    print("\nCiphertext:", ciphertext_base64)
    print("Index ASCII (Decimal):", ascii_values)
    return ascii_values

def generate_dtmf_signal(ascii_values, duration=0.2, sample_rate=44100):
    signal = np.array([])
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    for digit in ascii_values:
        f1, f2 = DTMF_FREQUENCIES.get(digit, DEFAULT_FREQUENCY)
        tone = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)
        signal = np.append(signal, tone)
    signal *= 0.5
    return signal

def save_audio(signal, filename="dtmf_signal.wav", sample_rate=44100):
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    write(filepath, sample_rate, np.int16(signal * 32767))
    print(f"\nSinyal DTMF disimpan sebagai: {filepath}")
    return filepath

def mix_audio(dtmf_signal, carrier_path, output_name="mixed_audio.wav", sample_rate=44100):
    if not os.path.exists(carrier_path):
        print("[ERROR] File carrier tidak ditemukan.")
        return None

    carrier_audio = AudioSegment.from_file(carrier_path).set_channels(1)
    carrier_audio = carrier_audio.set_frame_rate(sample_rate)
    carrier_samples = np.array(carrier_audio.get_array_of_samples()).astype(np.float32)
    carrier_samples /= np.max(np.abs(carrier_samples))

    min_len = min(len(dtmf_signal), len(carrier_samples))
    dtmf_signal = dtmf_signal[:min_len]
    carrier_samples = carrier_samples[:min_len]

    alpha = 0.05
    mixed_signal = carrier_samples + alpha * dtmf_signal
    mixed_signal /= np.max(np.abs(mixed_signal))

    output_path = os.path.join(OUTPUT_FOLDER, output_name)
    write(output_path, sample_rate, np.int16(mixed_signal * 32767))
    print(f"\n✅ File hasil mixing disimpan di: {output_path}")
    return output_path, carrier_samples, mixed_signal

def animate_all_signals(dtmf_signal, carrier_signal, mixed_signal, sample_rate=44100):
    fig, axes = plt.subplots(4, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 1, 1, 0.2]})
    fig.subplots_adjust(hspace=0.5)

    window_size = 1000
    duration = len(mixed_signal) / sample_rate

    x = np.arange(window_size)
    titles = ['Sinyal DTMF', 'Sinyal Audio Carrier', 'Sinyal Hasil Mixing']
    signals = [dtmf_signal, carrier_signal, mixed_signal]
    colors = ['blue', 'red', 'green']

    lines = []
    for ax, title, color in zip(axes[:3], titles, colors):
        ax.set_title(title)
        ax.set_xlim(0, window_size)
        ax.set_ylim(-1, 1)
        line, = ax.plot(x, np.zeros_like(x), color=color)
        lines.append(line)

    ax_slider = axes[3]
    ax_slider.set_title("Waktu (detik)")
    slider = Slider(ax_slider, "", 0, duration, valinit=0, valstep=0.01)

    audio_data = (mixed_signal * 32767).astype(np.int16)
    play_obj = sa.play_buffer(audio_data.tobytes(), 1, 2, sample_rate)
    start_time = time.time()

    def update(frame):
        elapsed = time.time() - start_time
        index = int(elapsed * sample_rate)

        if not play_obj.is_playing() or index + window_size > len(mixed_signal):
            for line in lines:
                line.set_ydata(np.zeros_like(x))
            return lines

        for i, signal in enumerate(signals):
            lines[i].set_ydata(signal[index:index + window_size])
        slider.set_val(min(elapsed, duration))
        return lines

    ani = animation.FuncAnimation(fig, update, blit=False, interval=30)
    plt.show()
    play_obj.wait_done()

def main():
    ascii_values = aes128()
    if ascii_values is None:
        return

    dtmf_signal = generate_dtmf_signal(ascii_values)
    save_audio(dtmf_signal, "dtmf_signal.wav")

    carrier_path = input("Masukkan nama file MP3 carrier: ").strip()
    result = mix_audio(dtmf_signal, carrier_path)
    if result is None:
        return

    mixed_path, carrier_signal, mixed_signal = result
    min_len = min(len(dtmf_signal), len(carrier_signal), len(mixed_signal))
    animate_all_signals(dtmf_signal[:min_len], carrier_signal[:min_len], mixed_signal[:min_len])

main()
