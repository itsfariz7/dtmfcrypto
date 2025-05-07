from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto import Random
import base64

# Fungsi Enkripsi AES-128 dan Konversi ke ASCII Desimal
def encrypt_and_convert_to_ascii():
    plaintext = input("Masukkan plaintext: ")  # Input pesan dari user
    key = input("Masukkan kunci (16 karakter): ").encode()  # Input kunci (16-byte)
    
    if len(key) != 16:
        print("Error: Kunci harus 16 karakter!")
        return
    
    iv = Random.new().read(AES.block_size)  # Generate IV acak (16 byte)
    cipher = AES.new(key, AES.MODE_CBC, iv)  # Inisialisasi AES CBC
    ciphertext = iv + cipher.encrypt(pad(plaintext.encode(), AES.block_size))  # Enkripsi
    
    # Encode ciphertext ke Base64 agar mudah dikonversi ke ASCII
    ciphertext_base64 = base64.b64encode(ciphertext).decode()
    
    # Konversi setiap karakter dalam ciphertext_base64 ke ASCII desimal
    ascii_values = [ord(char) for char in ciphertext_base64]
    
    print("\nCiphertext (Base64):", ciphertext_base64)
    print("ASCII Code (Decimal):", ascii_values)

# Fungsi Konversi Ciphertext (Base64) ke ASCII Desimal secara Manual
def convert_manual_ciphertext_to_ascii():
    ciphertext_base64 = input("Masukkan ciphertext dalam Base64: ")  # Input ciphertext Base64 dari user
    
    # Konversi setiap karakter dalam ciphertext_base64 ke ASCII desimal
    ascii_values = [ord(char) for char in ciphertext_base64]
    
    print("\nASCII Code (Decimal):", ascii_values)

# Fungsi utama
def main():
    print("Pilih opsi:")
    print("1: Enkripsi teks dan konversi ke ASCII desimal")
    print("2: Konversi ciphertext yang dimasukkan secara manual ke ASCII desimal")
    
    pilihan = input("Masukkan pilihan (1/2): ")
    
    if pilihan == '1':
        encrypt_and_convert_to_ascii()
    elif pilihan == '2':
        convert_manual_ciphertext_to_ascii()
    else:
        print("Pilihan tidak valid!")

# Jalankan program
main()
