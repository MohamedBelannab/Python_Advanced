# config.py
import os
from cryptography.fernet import Fernet

class Config:
    # Configuration de la base de données
    DATABASE_PATH = "passwords.db"
    
    # Génération et stockage de la clé de chiffrement
    @staticmethod
    def get_encryption_key():
        key_file = "encryption_key.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    # Configuration du logging
    LOGGING_CONFIG_PATH = "logging_config.yaml"