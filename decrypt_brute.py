import base64
import binascii
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def decrypt_ais_brute(file_path, password):
    with open(file_path, "r") as f:
        content = f.read().strip()
    
    salt_hex = content[:32]
    iv_hex = content[32:64]
    salt = binascii.unhexlify(salt_hex)
    iv = binascii.unhexlify(iv_hex)
    
    b64_payload = content[64:]
    ciphertext = base64.b64decode(b64_payload)
    
    def try_decrypt_full(key, iv, ciphertext):
        try:
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            return data.decode('utf-8')
        except:
            return None

    # Brute force common parameters
    hash_algs = [hashes.SHA1(), hashes.SHA256()]
    iteration_counts = [1000, 2000, 10000, 100, 1]
    
    for h in hash_algs:
        for count in iteration_counts:
            print(f"Trying PBKDF2 with {h.name}, iterations={count}...")
            kdf = PBKDF2HMAC(
                algorithm=h,
                length=32,
                salt=salt,
                iterations=count,
                backend=default_backend()
            )
            try:
                key = kdf.derive(password.encode())
                result = try_decrypt_full(key, iv, ciphertext)
                if result:
                    return result
            except:
                continue
                
    return None

if __name__ == "__main__":
    file_path = "path/to/your/encrypted_ais.json"
    password = "<YOUR_PAN_DOB>"
    
    decrypted = decrypt_ais_brute(file_path, password)
    if decrypted:
        print("SUCCESS!")
        with open("decrypted_ais_final.json", "w") as f:
            f.write(decrypted)
    else:
        print("FAILED. Trying Uppercase Variation...")
        decrypted = decrypt_ais_brute(file_path, password.upper())
        if decrypted:
            print("SUCCESS with Uppercase!")
            with open("decrypted_ais_final.json", "w") as f:
                f.write(decrypted)
        else:
            print("FAILED everything.")
