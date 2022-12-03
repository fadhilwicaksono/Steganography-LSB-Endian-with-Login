import bcrypt
from Steganografi import konversiFileBytes,ubah2BitTerakhir,packDatabits,unpackDatabits,enkripsiFileKeGambar,deskripsiDataDariGambar,menu_utama

def welcome():
    print("Selamat Datang Silahkan Pilih Menu")
    menu_utama()
    #pembatas
    


def gainAccess(Username=None, Password=None):
    Username = input("Masukan Username:")
    Password = input("Masukan Password:")
    
    if not len(Username or Password) < 1:
        if True:
            db = open("database.txt", "r")
            d = []
            f = []
            for i in db:
                a,b = i.split(",")
                b = b.strip()
                c = a,b
                d.append(a)
                f.append(b)
                data = dict(zip(d, f))
            try:
                if Username in data:
                    hashed = data[Username].strip('b')
                    hashed = hashed.replace("'", "")
                    hashed = hashed.encode('utf-8')
                    
                    try:
                        if bcrypt.checkpw(Password.encode(), hashed):
                        
                            print("Login Berhasil!")
                            print("Hi", Username)
                            welcome()
                        else:
                            print("Password Salah")
                        
                    except:
                        print("Salah passwords atau username")
                else:
                    print("Username tidak ada")
            except:
                print("Password atau username tidak ada")
        else:
            print("Error")
            
    else:
        print("Sialhkan coba lagi")
        gainAccess()
        
        # b = b.strip()
# accessDb()

def register(Username=None, Password1=None, Password2=None):
    Username = input("Masukan username:")
    Password1 = input("Buat password:")
    Password2 = input("Konfirmasi Password:")
    db = open("database.txt", "r")
    d = []
    for i in db:
        a,b = i.split(",")
        b = b.strip()
        c = a,b
        d.append(a)
    if not len(Password1)<=8:
        db = open("database.txt", "r")
        if not Username ==None:
            if len(Username) <1:
                print("Masukan username")
                register()
            elif Username in d:
                print("Username telah digunakan")
                register()		
            else:
                if Password1 == Password2:
                    Password1 = Password1.encode('utf-8')
                    Password1 = bcrypt.hashpw(Password1, bcrypt.gensalt())
                                       
                    db = open("database.txt", "a")
                    db.write(Username+", "+str(Password1)+"\n")
                    print("User sukses dibuat!")
                    print("Silahkan Login:")

                    
                    # print(texts)
                else:
                    print("Passwords salah")
                    register()
    else:
        print("Password terlalu pendek")



def home(option=None):
    print("Selamat Datang!")
    option = input("Login | Daftar:")
    if option == "Login":
        gainAccess()        
    elif option == "Daftar":
        register()
    else:
        print("Ketikan dengan benar")

home()