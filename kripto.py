from cryptography.fernet import Fernet
import base64 #library base64 
import hashlib #menggunakan MD5 dengan library hashlib

'''
penggunaan library base64 untuk konversi bytes yg mempunyai binary / text ke ASCII
base64.urlsafe_b64encode(s)
'''

def enkripsiData(data: bytes, key: str) -> bytes:
    
    key = base64.urlsafe_b64encode(hashlib.md5(key.encode()).hexdigest().encode())
   
    '''
    catatan kaki
    
    penggunaan base64.urlsafe_b64encode untuk melakukan encoding ke dalam bentuk binary
    hashlib.md5 --> berfungsi untuk mengubah inputan ke dalam bentuk 128-bit
    
    '''
    
    f = Fernet(key)
    
    '''
    fernet adalah adalah algoritma kriptografi yang digunakan untuk memastikan bahwa data tidak dapat dibuka tanpa key
    dalam algoritma modern bernama simetric encription
    '''
    enkripsiData = f.encrypt(data)
    return enkripsiData

def deskripsiData(data: bytes, key: str) -> bytes:
    try:
        key = base64.urlsafe_b64encode(hashlib.md5(key.encode()).hexdigest().encode())

        f = Fernet(key)
        deskripsiData = f.decrypt(data)
        return deskripsiData
    except:
        print("salah password")
        exit()