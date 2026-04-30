import base64
import hashlib
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

def decrypt_ais(file_path, password):
    with open(file_path, "r") as f:
        content = f.read().strip()
    
    # Prefix is 64 hex chars
    b64_payload = content[64:]
    binary_data = base64.b64decode(b64_payload)
    
    # Try different key derivations
    # 1. SHA-256 of password
    key_sha256 = hashlib.sha256(password.encode()).digest()
    
    iv = binary_data[:16]
    ciphertext = binary_data[16:]
    
    def try_decrypt(key, iv, ciphertext):
        try:
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            return data.decode('utf-8')
        except Exception as e:
            return None

    # Try SHA-256
    print("Trying SHA-256 key...")
    result = try_decrypt(key_sha256, iv, ciphertext)
    if result:
        return result
    
    # 2. Raw password (padded/truncated to 32 bytes)
    print("Trying raw password key...")
    key_raw = password.encode().ljust(32, b'\0')[:32]
    result = try_decrypt(key_raw, iv, ciphertext)
    if result:
        return result

    # 3. PBKDF2 (Common in Java utilities)
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    
    salts = [b"IncomeTaxIndia", b"taxpayer", b"ITportal", password.lower()[:10].encode()]
    for salt in salts:
        print(f"Trying PBKDF2 with salt {salt}...")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA1(),
            length=32,
            salt=salt,
            iterations=1000,
            backend=default_backend()
        )
        try:
            key_pbkdf2 = kdf.derive(password.encode())
            result = try_decrypt(key_pbkdf2, iv, ciphertext)
            if result:
                return result
        except:
            continue

    return None

if __name__ == "__main__":
    file_path = "path/to/your/encrypted_ais.json"
    password = "<YOUR_PAN_DOB>" # e.g., ABCDE1234FDDMMYYYY
    
    decrypted = decrypt_ais(file_path, password)
    if decrypted:
        print("SUCCESS!")
        with open("decrypted_ais.json", "w") as f:
            f.write(decrypted)
        print("Saved to decrypted_ais.json")
    else:
        print("FAILED to decrypt with current methods.")
