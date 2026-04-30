import base64
import binascii
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def decrypt_ais(file_path, password):
    with open(file_path, "r") as f:
        content = f.read().strip()
    
    # 1. Extract Prefix (Salt & IV)
    # Researcher says: 1-32 = Salt, 33-64 = IV
    salt_hex = content[:32]
    iv_hex = content[32:64]
    
    salt = binascii.unhexlify(salt_hex)
    iv = binascii.unhexlify(iv_hex)
    
    # 2. Extract and Decode Payload (Base64)
    b64_payload = content[64:]
    ciphertext = base64.b64decode(b64_payload)
    
    # 3. Derive Key using PBKDF2
    # Researcher says: HMAC-SHA1, 1000 iterations, 32-byte key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=32,
        salt=salt,
        iterations=1000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    
    # 4. Decrypt using AES-256-CBC
    try:
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 5. Remove Padding
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"Decryption Error: {e}")
        return None

if __name__ == "__main__":
    # Test with the specific file provided
    file_path = "path/to/your/encrypted_ais.json"
    password = "<YOUR_PAN_DOB>"
    
    decrypted = decrypt_ais(file_path, password)
    if decrypted:
        print("SUCCESS!")
        with open("decrypted_ais_final.json", "w") as f:
            f.write(decrypted)
        print("Decrypted content saved to decrypted_ais_final.json")
    else:
        print("Decryption FAILED. Trying variation (PAN UPPERCASE)...")
        # Try variation
        password_up = password.upper()
        decrypted = decrypt_ais(file_path, password_up)
        if decrypted:
            print("SUCCESS with Uppercase PAN!")
            with open("decrypted_ais_final.json", "w") as f:
                f.write(decrypted)
        else:
            print("FAILED again.")
