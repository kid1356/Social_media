
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import serialization, hashes
import re,json



def clean_pem_key(pem_key):
    
    # Remove outer `b'` and decode any escaped characters
    cleaned_key = re.sub(r"^b'|'$", '', pem_key).encode('utf-8').decode('unicode_escape')
    return cleaned_key.encode('utf-8')

def generate_key_pair():
    # Generate RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    # Serialize keys
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


    return private_key_bytes, public_key_bytes




def encrypt_message_by_public_key(public_key_pem, message):
  
    if isinstance(message, dict):
        message = json.dumps(message).encode('utf-8') 

    if isinstance(public_key_pem, str):
        public_key_pem = clean_pem_key(public_key_pem)

    try:
        
        public_key = serialization.load_pem_public_key(public_key_pem)

        # Encrypt the message
        encrypted_message = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_message
    except Exception as e:
        raise ValueError(f"Failed to load or use the public key: {e}")


def decrypt_message_by_private_key(private_key_pem, encrypted_message):
  
    if isinstance(private_key_pem,str):
        private_key_pem = clean_pem_key(private_key_pem)
    
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)

    # Decrypt the message
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    try:
        return json.loads(decrypted_message.decode('utf-8'))
    except json.JSONDecodeError:
       
        return decrypted_message.decode('utf-8')