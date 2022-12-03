from PIL import Image
'''
Library Pillow /PIL digunakan untuk memanipulasi berbagai jenis file, termasuk gambar
'''

from getopt import getopt #untj melakukan parsing perintah seperti argumen 
from sys import argv #untuk memanipulasi environtment python
 
import kripto

'''
mengubah 2bits dari tiap pixel
file dapat diubah 3 unit/ pixel --> RGB : Red Green Blue (max 4 bit)

'''

def konversiFileBytes(data: bytes) -> bytes:
    """
    mengubah datasize daklam bentuk 8 bit
    """
    return (len(data)).to_bytes(8, byteorder='big') #msb 

def ubah2BitTerakhir(oriBits: int, baruBits: int) -> int:
    """
    mengubah 2 bits terakhir dengan bit baru (baruBits)
    """
    
    return (oriBits >> 2) << 2 | baruBits


def packDatabits(data: bytes, padding: int = 1) -> list:
    """
    memasukan kumpulan data bits ke dalam list
    """
    listDatabits = list()
    for bits in data:
        listDatabits.append((bits >> 6) & 0b11)
        listDatabits.append((bits >> 4) & 0b11)
        listDatabits.append((bits >> 2) & 0b11)
        listDatabits.append((bits >> 0) & 0b11)

    while len(listDatabits) % padding != 0:
        listDatabits.append(0)

    return listDatabits


def unpackDatabits(data: list) -> bytes:
    """
    mengunpack kumpulan 2bits menjadi data semula
    """
    unpackDatabits = list()
    for i in range(0, len(data) - 4 + 1, 4):
        bits = (data[i] << 6) + (data[i + 1] << 4) + (data[i + 2] << 2) + (data[i + 3] << 0)
        unpackDatabits.append(bits)

    return bytes(unpackDatabits)


#Magic data digunakan untuk mengenali jenis file 
magicBytes = {
    "encryptedLSB": 0x1337c0de,
    "unencryptedLSB": 0xdeadc0de,
    "encrypted": 0xbabec0de,
    "unencrypted": 0x5afec0de
}


def enkripsiFileKeGambar(inputGambarPath: str, filePesanPath: str, outputHasilPath: str, password: str, modeEnkripsi: str) -> None:
 
    fp = open(filePesanPath, "rb")

    data = fp.read()
    print("[*] {} file size : {} bytes".format(filePesanPath, len(data)))

    if modeEnkripsi == "lsb":
        image = Image.open(inputGambarPath).convert('RGB')
        pixels = image.load()

        if password:
            data = kripto.enkripsiData(data, password)
            print("[*] size data enkripsi: {} bytes".format(len(data)))
            data = (magicBytes["encryptedLSB"]).to_bytes(4, byteorder='big') + konversiFileBytes(data) + data
            print("[*] Magic bytes : {}".format(hex(magicBytes["encryptedLSB"])))
        else:
            data = (magicBytes["unencryptedLSB"]).to_bytes(4, byteorder='big') + konversiFileBytes(data) + data
            print("[*] Magic bytes used: {}".format(hex(magicBytes["unencryptedLSB"])))

        data = packDatabits(data, padding=3)
        data.reverse()


        #koordinat pixel gambar (0,0) // (255,255)
        imageX, imageY = 0, 0
        while data:
            # Pixel index x y
            pixel_val = pixels[imageX, imageY]
            
            # Menyembunyikan data di 3 channel dari setiap pixel
            pixel_val = (ubah2BitTerakhir(pixel_val[0], data.pop()),
                         ubah2BitTerakhir(pixel_val[1], data.pop()),
                         ubah2BitTerakhir(pixel_val[2], data.pop()))

            # Menyimpan perubahan 
            pixels[imageX, imageY] = pixel_val

            if imageX == image.size[0] - 1:          
                # Increment Y Axis dan reset X Axis
                imageX = 0
                imageY += 1
            else:
                # Increment X Axis
                imageX += 1

        if not outputHasilPath:
            outputHasilPath = ".".join(inputGambarPath.split(".")[:-1]) + "_dengan_file_tersembunyi_" + "." + inputGambarPath.split(".")[-1]

        print(f"[+] Menyimpan gambar ke {outputHasilPath}")
        image.save(outputHasilPath)
        
    elif modeEnkripsi == "endian":
        if password:
            data = kripto.enkripsiData(data, password)
            print("Size dari enkripsi data: {} bytes".format(len(data)))
            data = data + konversiFileBytes(data) + (magicBytes["encrypted"]).to_bytes(4, byteorder='big')
            print("Magic bytes yang dipakai: {}".format(hex(magicBytes["encrypted"])))
        else:
            data = data + konversiFileBytes(data) + (magicBytes["unencrypted"]).to_bytes(4, byteorder='big')
            print("Magic bytes yang dipakai: {}".format(hex(magicBytes["unencrypted"])))

        inputGambar = open(inputGambarPath, "rb").read()
        inputGambar += data

        outputGambar = open(outputHasilPath, "wb")
        outputGambar.write(inputGambar)
        outputGambar.close()

def deskripsiDataDariGambar(inputGambarPath: str, outputFilePath: str, password: str) -> None:

    inputGambar = open(inputGambarPath, "rb").read()
    if int.from_bytes(inputGambar[-4:], byteorder='big') in [magicBytes["encrypted"], magicBytes["unencrypted"]]:
        print("Terdapat file tersembunyi di Gambar")
        hiddenDataSize = int.from_bytes(inputGambar[-12:-4], byteorder="big")
        hiddenData = inputGambar[-hiddenDataSize - 12:-12]

        if int.from_bytes(inputGambar[-4:], byteorder='big') == magicBytes["encrypted"]:
            print("File tersembuyi dan terenskripsi")
            hiddenData = kripto.deskripsiData(hiddenData, password)

        outputFilePath = open(outputFilePath, "wb")
        outputFilePath.write(hiddenData)
        outputFilePath.close()
    else:

        image = Image.open(inputGambarPath).convert('RGB')
        pixels = image.load()

        data = list()                                 # list tempat menyimpan bit yang sudah terekstrasi
        for imageY in range(image.size[1]):
            for imageX in range(image.size[0]):
                if len(data) >= 48:
                    break

                # membaca values pixel dari [0, 0] sampai akhir
                pixel = pixels[imageX, imageY]

                # Extract pesan tersembunyi dari tiap Channel
                data.append(pixel[0] & 0b11)
                data.append(pixel[1] & 0b11)
                data.append(pixel[2] & 0b11)

        encrypted = False
        if unpackDatabits(data)[:4] == bytes.fromhex(hex(magicBytes["unencryptedLSB"])[2:]):
            print("terdapat file tersembunyi")
        elif unpackDatabits(data)[:4] == bytes.fromhex(hex(magicBytes["encryptedLSB"])[2:]):
            print("terdapat file tersembunyi dan terenskripsi")
            encrypted = True
        else:
            print("gambar tidak ada file tersembunyi")
            print("Magic bytes :    0x{}".format(unpackDatabits(data)[:4].hex()))
            print("Magic bytes supported: {}".format(", ".join([hex(x) for x in magicBytes.values()])))
            exit()

        hiddenDataSize = int.from_bytes(unpackDatabits(data)[4:16], byteorder='big') * 4

        data = list()
        for imageY in range(image.size[1]):
            for imageX in range(image.size[0]):
                if len(data) >= hiddenDataSize + 48:
                    break

                # membaca values pixel dari [0, 0] sampai terakhir
                pixel = pixels[imageX, imageY]
                
                # meng-deskripsi pesan tersembunyi dari 2 bits tiap channel
                data.append(pixel[0] & 0b11)
                data.append(pixel[1] & 0b11)
                data.append(pixel[2] & 0b11)

        data = unpackDatabits(data[48:])
        if encrypted:
            data = kripto.deskripsiData(data, password)

        print(f"Menyimpan hidden file tersembunyi ke {outputFilePath}")
        print(f"Size dari data yang telah dideskripsi : {len(data)} bytes")

        f = open(outputFilePath, 'wb')
        f.write(data)
        f.close()

def menu_utama():
    print("Menyembunyikan Pesan Di Dalam Gambar")
    print("\t1. Enkripsi File")
    print("\t2. Deskripsi File")

    ch = input("Pilih : ")
    if ch == "1":
        inputGambarPath = input("Path Gambar: ")
        pesanFilePath = input("Path Pesan: ")
        outputHasilPath = input("Path Hasil: ")
        password = input("password (bisa ditambah/tidak): ")

        print("Metode Enkripsi:")
        print("\t1. LSB")
        print("\t2. Endian")
        ch = input("Pilih: ")
        modeEnkripsi = "lsb" if ch == "lsb" else "endian"

        enkripsiFileKeGambar(inputGambarPath, pesanFilePath, outputHasilPath, password, modeEnkripsi)
    elif ch == "2":
        inputGambarPath = input("Path Gambar: ")
        pesanFilePath = input("Path Hasil: ")
        password = input("Masukan password [jika ada]: ")

        deskripsiDataDariGambar(inputGambarPath, pesanFilePath, password)
    else:
        print("Pilihan Salah")


#if __name__ == '__main__':
#    main()
