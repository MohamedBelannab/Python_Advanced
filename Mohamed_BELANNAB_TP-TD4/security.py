# security.py
import bcrypt
import logging
from cryptography.fernet import Fernet
from config import Config

logger = logging.getLogger(__name__)

# Initialiser la clé de chiffrement Fernet
ENCRYPTION_KEY = Config.get_encryption_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

def hash_password(password):
    """Hacher un mot de passe avec bcrypt."""
    try:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Erreur lors du hachage du mot de passe: {e}")
        raise

def verify_password(plain_password, hashed_password):
    """Vérifier si un mot de passe correspond à son hash."""
    try:
        plain_password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du mot de passe: {e}")
        return False

def encrypt_password(password):
    """Chiffrer un mot de passe avec Fernet."""
    try:
        password_bytes = password.encode('utf-8')
        encrypted = cipher_suite.encrypt(password_bytes)
        return encrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Erreur lors du chiffrement du mot de passe: {e}")
        raise

def decrypt_password(encrypted_password):
    """Déchiffrer un mot de passe chiffré avec Fernet."""
    try:
        encrypted_bytes = encrypted_password.encode('utf-8')
        decrypted = cipher_suite.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Erreur lors du déchiffrement du mot de passe: {e}")
        raise