import base64
import binascii
import json
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def decrypt_ais_exhaustive(file_path, base_password):
    with open(file_path, "r") as f:
        content = f.read().strip()
    
    # Prefix variations
    # 1. 1-32 Salt, 33-64 IV
    # 2. 1-32 IV, 33-64 Salt
    # 3. 64 chars is just Hash, Salt/IV inside payload
    
    salt_iv_variations = [
        (content[:32], content[32:64], content[64:]), # Standard split
        (content[32:64], content[:32], content[64:]), # Swapped split
    ]
    
    passwords = [base_password.lower(), base_password.upper(), base_password]
    hash_algs = [hashes.SHA1(), hashes.SHA256(), hashes.SHA512()]
    iterations = [1, 1000, 2000, 10000, 20000, 65536, 100000]
    
    for s_hex, i_hex, p_b64 in salt_iv_variations:
        try:
            salt = binascii.unhexlify(s_hex)
            iv = binascii.unhexlify(i_hex)
            ciphertext = base64.b64decode(p_b64)
        except:
            continue
            
        for pwd in passwords:
            for h in hash_algs:
                for count in iterations:
                    try:
                        kdf = PBKDF2HMAC(
                            algorithm=h,
                            length=32,
                            salt=salt,
                            iterations=count,
                            backend=default_backend()
                        )
                        key = kdf.derive(pwd.encode('utf-8'))
                        
                        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                        decryptor = cipher.decryptor()
                        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
                        
                        unpadder = padding.PKCS7(128).unpadder()
                        data = unpadder.update(padded_data) + unpadder.finalize()
                        return data.decode('utf-8'), pwd, h.name, count
                    except:
                        continue

    # Try Case 3: 64 chars is Hash, IV is first 16 bytes of payload
    try:
        binary_payload = base64.b64decode(content[64:])
        iv = binary_payload[:16]
        ciphertext = binary_payload[16:]
        # What is Salt? Maybe hardcoded?
        hardcoded_salts = [b"IncomeTaxIndia", b"taxpayer", b"ITportal", b"AIS", b"TIS"]
        for salt in hardcoded_salts:
            for pwd in passwords:
                for h in hash_algs:
                    for count in iterations:
                        try:
                            kdf = PBKDF2HMAC(
                                algorithm=h,
                                length=32,
                                salt=salt,
                                iterations=count,
                                backend=default_backend()
                            )
                            key = kdf.derive(pwd.encode('utf-8'))
                            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                            decryptor = cipher.decryptor()
                            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
                            unpadder = padding.PKCS7(128).unpadder()
                            data = unpadder.update(padded_data) + unpadder.finalize()
                            return data.decode('utf-8'), f"HardSalt:{salt.decode()}", h.name, count
                        except:
                            continue
    except:
        pass

    return None

if __name__ == "__main__":
    file_path = "path/to/your/encrypted_ais.json"
    pwd = "<YOUR_PAN_DOB>"
    
    result = decrypt_ais_exhaustive(file_path, pwd)
    if result:
        data, p, h, c = result
        print(f"SUCCESS! Pwd: {p}, Hash: {h}, Iters: {c}")
        with open("decrypted_ais_brute_force.json", "w") as f:
            f.write(data)
    else:
        print("EXHAUSTIVE SEARCH FAILED.")
