# database.py
import sqlite3
import logging
from config import Config

logger = logging.getLogger(__name__)

def get_db_connection():
    """Établir une connexion à la base de données SQLite."""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la connexion à la base de données: {e}")
        raise

def initialize_database():
    """Créer les tables nécessaires si elles n'existent pas."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table des mots de passe stockés
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            site_name TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        logger.info("Base de données initialisée avec succès")
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise
    finally:
        conn.close()

def add_user(username, password_hash, email):
    """Ajouter un nouvel utilisateur à la base de données."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, password_hash, email)
        )
        
        conn.commit()
        user_id = cursor.lastrowid
        logger.info(f"Nouvel utilisateur créé avec ID: {user_id}")
        return user_id
    except sqlite3.IntegrityError:
        logger.error(f"L'utilisateur {username} ou l'email {email} existe déjà")
        raise ValueError(f"L'utilisateur {username} ou l'email {email} existe déjà")
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de l'ajout de l'utilisateur: {e}")
        raise
    finally:
        conn.close()

def get_user_by_username(username):
    """Récupérer les informations d'un utilisateur par son nom d'utilisateur."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        return dict(user) if user else None
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
        raise
    finally:
        conn.close()

def add_password(user_id, site_name, username, encrypted_password, notes=None):
    """Ajouter un nouveau mot de passe pour un utilisateur."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO passwords (user_id, site_name, username, encrypted_password, notes) VALUES (?, ?, ?, ?, ?)",
            (user_id, site_name, username, encrypted_password, notes)
        )
        
        conn.commit()
        password_id = cursor.lastrowid
        logger.info(f"Nouveau mot de passe ajouté avec ID: {password_id}")
        return password_id
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de l'ajout du mot de passe: {e}")
        raise
    finally:
        conn.close()

def get_passwords_by_user_id(user_id):
    """Récupérer tous les mots de passe d'un utilisateur."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM passwords WHERE user_id = ?", (user_id,))
        passwords = cursor.fetchall()
        
        return [dict(pw) for pw in passwords]
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération des mots de passe: {e}")
        raise
    finally:
        conn.close()

def get_password_by_id(password_id, user_id):
    """Récupérer un mot de passe spécifique d'un utilisateur."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM passwords WHERE id = ? AND user_id = ?", (password_id, user_id))
        password = cursor.fetchone()
        
        return dict(password) if password else None
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération du mot de passe: {e}")
        raise
    finally:
        conn.close()