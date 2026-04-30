import base64
import binascii
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def decrypt_ais(file_path, password, iterations):
    try:
        with open(file_path, "r") as f:
            content = f.read().strip()
        
        # 1. Extract Salt and IV from the 64-char hex prefix
        salt_hex = content[:32]
        iv_hex = content[32:64]
        salt = binascii.unhexlify(salt_hex)
        iv = binascii.unhexlify(iv_hex)
        
        # 2. Extract and Decode Payload (Base64)
        b64_payload = content[64:]
        ciphertext = base64.b64decode(b64_payload)
        
        # 3. Derive Key using PBKDF2-HMAC-SHA1
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA1(),
            length=32,  # 256-bit key for AES-256
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        key = kdf.derive(password.encode('utf-8'))
        
        # 4. Decrypt using AES-256-CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 5. Remove PKCS7 Padding
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        return decrypted_data.decode('utf-8')
    except Exception as e:
        return None

if __name__ == "__main__":
    target_file = "path/to/your/encrypted_ais.json"
    password = "<YOUR_PAN_DOB>"
    
    # Try the most likely iteration counts
    iteration_options = [20000, 10000, 65536, 1000, 100000, 5000, 40000]
    passwords = [password.lower(), password.upper()]
    
    found = False
    for p in passwords:
        for iters in iteration_options:
            print(f"Attempting with pwd={p}, iters={iters}...")
            result = decrypt_ais(target_file, p, iterations=iters)
            if result:
                print(f"SUCCESS with {iters} iterations!")
                with open("decrypted_ais_success.json", "w") as f:
                    f.write(result)
                print("Decrypted file saved as decrypted_ais_success.json")
                found = True
                break
        if found: break
    
    if not found:
        print("Decryption failed. Final attempt with different Salt/IV assumption...")
