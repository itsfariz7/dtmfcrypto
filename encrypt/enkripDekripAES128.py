from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

# Fungsi untuk enkripsi AES-128
def encrypt_AES(plaintext, key):
    cipher = AES.new(key, AES.MODE_ECB)  # Menggunakan mode ECB
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))  # Padding data
    return base64.b64encode(ciphertext).decode()  # Hasil dalam Base64 agar mudah dibaca

# Fungsi untuk dekripsi AES-128
def decrypt_AES(ciphertext, key):
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = unpad(cipher.decrypt(base64.b64decode(ciphertext)), AES.block_size)
    return decrypted.decode()

# Input data dan kunci (harus 16 byte untuk AES-128)
plaintext = "BANDUNG"
key = b'Apel123456789012'  # 16-byte key (128-bit)

# Enkripsi
ciphertext = encrypt_AES(plaintext, key)
print("Ciphertext:", ciphertext)

# Dekripsi
decrypted_text = decrypt_AES(ciphertext, key)
print("Decrypted Text:", decrypted_text)
