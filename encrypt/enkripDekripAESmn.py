from Crypto.Cipher import AES
from Crypto import Random
import base64

def enkripsi(pesan):
    print("Plainteks: \n", pesan)
    print("Ketikkan kunci (16 karakter):")
    kunci = input()  # Input kunci harus sepanjang 16 karakter (128-bit)
    iv = Random.new().read(AES.block_size)  # Membuat IV acak sepanjang 16 byte
    cipher = AES.new(kunci, AES.MODE_CBC, iv)  # Membuat objek AES dengan mode CBC
    
    cipherteks = base64.b64encode(iv + cipher.encrypt(pesan))  # Enkripsi pesan
    print("\n")
    print("Cipherteks: \n", cipherteks)  # Menampilkan hasil enkripsi

def dekripsi(pesan):
    print("Cipherteks: \n", pesan)
    print("Ketikkan kunci (16 karakter):")
    kunci = input()
    iv = pesan[:16]  # IV diambil dari bagian awal pesan terenkripsi
    cipher = AES.new(kunci, AES.MODE_CBC, iv)  # Membuat objek AES dengan mode CBC
    
    plainteks = cipher.decrypt(base64.b64decode(pesan))  # Dekripsi pesan
    print("\n")
    print("Pesan setelah didekripsi adalah: \n", plainteks[16:])

def ProgramEnkripsiDekripsiAES():
    print("-- Enkripsi dan dekripsi pesan dengan AES --")
    print("1: Enkripsi pesan")
    print("2: Dekripsi pesan")

    pilih = input()
    if pilih == '1':
        print("Ketikkan pesan yang akan dienkripsi:")
        pesan = input()
        n = len(pesan)
        if n % 16 != 0:
            pesan = pesan + ' ' * (16 - n % 16)  # Padding manual dengan spasi
        print("Enkripsi pesan...")
        enkripsi(pesan)

    elif pilih == '2':
        print("Ketikkan pesan yang akan didekripsi:")
        pesan = input()
        print("Dekripsi pesan...")
        dekripsi(pesan)
    else:
        print("Pilihan salah")
