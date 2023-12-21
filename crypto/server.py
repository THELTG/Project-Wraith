from Cryptodome.Cipher import AES 
from Cryptodome.PublicKey import RSA 
from Cryptodome.Util.Padding import pad, unpad
from secrets import token_bytes
from OpenSSL import crypto
import ssl
from pwn import *

def regenerate():
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA,4096)
    cert = crypto.X509()
    cert.get_subject().C = 'SG'
    cert.get_subject().CN = 'Singapore'
    cert.set_issuer(cert.get_subject())
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_pubkey(k)
    cert.sign(k,'sha512')
    # rsa_private = RSA.generate(2048,token_bytes,65537)
    # rsa_public = rsa_private.public_key()
    rsa_cert = crypto.dump_certificate(crypto.FILETYPE_PEM,cert)
    rsa_private = crypto.dump_privatekey(crypto.FILETYPE_PEM,k)
    rsa_public = crypto.dump_publickey(crypto.FILETYPE_PEM,k)
    print("[+] Generating new key pair...")
    open("./credentials/certificate.pem",'wb').write(rsa_cert) 
    open("./credentials/public.pem",'wb').write(rsa_public)  #rsa_private.export_key('PEM')
    open("./credentials/private.pem",'wb').write(rsa_private) #rsa_private.public_key().export_key('PEM'))
    return rsa_cert, rsa_private, rsa_public

def encrypt(pt, key):
    cipher = AES.new(key,AES.MODE_GCM)
    ct, tag = cipher.encrypt_and_digest(pad(pt,cipher.block_size))
    nonce = cipher.nonce
    return tag+ct,nonce

def decrypt(ct,key,nonce):
    tag,ct = ct[:16],ct[16:]
    cipher = AES.new(key,AES.MODE_GCM,nonce=nonce)
    try:
        pt = unpad(cipher.decrypt_and_verify(ct,tag),cipher.block_size)
        return pt
    except ValueError:
        print("[-] Something sus happened with that encryption.")
        return False

def encryption_service(r:remote):
    try:
        r.send(b"Encryption Service v1\n\nPlease enter the command to encrypt\n>>")
        buffer = r.recv(1024,5)
        key = token_bytes(32)
        ct,nonce = encrypt(buffer,key)
        r.send(f"Please enjoy\n\nKEY = {key.hex()}\nNonce = {nonce.hex()}\nCT = {ct.hex()}".encode())
        r.close()
    except:
        print('[-] lost connection')
    r.close()

def decryption_service(r:remote):
    try:
        r.send(b"Decryption Service v1\n\nPlease enter the ciphertext: ")
        ct = r.recv(1024,30).decode()
        r.send(b"Please enter the key: ")
        key = r.recv(1024,30).decode()
        r.send(b"Please enter the nonce: ")
        nonce = r.recv(1024,30).decode()
        plaintext = decrypt(bytes.fromhex(ct),bytes.fromhex(key),bytes.fromhex(nonce))
        r.send(plaintext)
        r.close()
    except:
        print('[-] lost connection')

def tls_service(r:remote):
    print(f'RHOST: {r.rhost}, RPORT: {r.rport}')
    print(f'LHOST: {r.lhost}, LPORT: {r.lport}')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER,)
    # context.wrap_socket(r.sock,'./credentials/private.pem','./credentials/certificate.pem')
    r.send(b'hello!')
    r.close()

class SSL_Wrap(server):
    def __init__(self,host,port,handler):
        super().__init__(port,host,'ipv4','tcp',handler)
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        try:
            context.load_cert_chain(certfile='./credentials/certificate.pem',keyfile='./credentials/private.pem')
        except ssl.SSLError as e:
            print(e)
        self.context = context

    def new_client(self,fd,addr):
        fd = self.context.wrap_socket(fd,server_side=True)
        super().new_client(fd,addr)

if __name__ == '__main__':
    try:
        public = open("./credentials/public.pem",'rb').read()
        private = open("./credentials/private.pem",'rb').read()
        rsa_cert = open("./credentials/certificate.pem",'rb').read()
        rsa_private = RSA.import_key(private)
        rsa_public = RSA.import_key(public).public_key()
        print('[+] Importing keys')
        if rsa_private.public_key() != rsa_public:
            print('[-] Keys corrupted or tampered, regenerating...')
            rsa_cert, rsa_private, rsa_public = regenerate()
    except FileNotFoundError:
        rsa_cert,rsa_private, rsa_public = regenerate()

    tlsservice = SSL_Wrap('0.0.0.0',1234,tls_service)
    # start the socket server for basic communication
    # server(1234,'0.0.0.0','ipv4','tcp',tls_service)
    # server(9999,'0.0.0.0','ipv4','tcp',encryption_service)
    # server(8888,'0.0.0.0','ipv4','tcp',decryption_service)

input("enter anything here to stop the service: ")
        



    



