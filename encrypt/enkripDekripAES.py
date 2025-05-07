from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto import Random
import base64

# Fungsi Enkripsi AES-128 dengan CBC
def enkripsi(pesan):
    print("Plainteks: \n", pesan)
    print("Ketikkan kunci (16 karakter):")
    kunci = input().encode()  # Konversi kunci ke byte
    iv = Random.new().read(AES.block_size)  # Generate IV acak (16 byte)
    cipher = AES.new(kunci, AES.MODE_CBC, iv)  # Inisialisasi AES CBC
    cipherteks = base64.b64encode(iv + cipher.encrypt(pad(pesan.encode(), AES.block_size)))  # Enkripsi & Base64 encoding
    
    print("\nCipherteks (Base64): \n", cipherteks.decode())  # Tampilkan hasil
    return cipherteks.decode()

# Fungsi Dekripsi AES-128 dengan CBC
def dekripsi(cipherteks):
    print("Cipherteks: \n", cipherteks)
    print("Ketikkan kunci (16 karakter):")
    kunci = input().encode()  # Konversi kunci ke byte
    decoded_cipher = base64.b64decode(cipherteks)  # Base64 decoding
    iv = decoded_cipher[:AES.block_size]  # Ambil IV dari 16 byte pertama
    cipher = AES.new(kunci, AES.MODE_CBC, iv)  # Inisialisasi AES CBC
    plainteks = unpad(cipher.decrypt(decoded_cipher[AES.block_size:]), AES.block_size)  # Dekripsi & Unpad
    
    print("\nPesan setelah didekripsi: \n", plainteks.decode())  # Tampilkan hasil
    return plainteks.decode()

# Fungsi utama
def ProgramEnkripsiDekripsiAES():
    print("-- Enkripsi dan Dekripsi Pesan dengan AES --")
    print("1: Enkripsi Pesan")
    print("2: Dekripsi Pesan")

    pilih = input()
    if pilih == '1':
        print("Ketikkan pesan yang akan dienkripsi:")
        pesan = input()
        print("Enkripsi pesan...")
        enkripsi(pesan)

    elif pilih == '2':
        print("Ketikkan pesan yang akan didekripsi:")
        cipherteks = input()
        print("Dekripsi pesan...")
        dekripsi(cipherteks)

    else:
        print("Pilihan salah")

# Jalankan program
ProgramEnkripsiDekripsiAES()
