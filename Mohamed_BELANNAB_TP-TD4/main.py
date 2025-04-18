# main.py
import logging
from typing import Optional, Dict, List, Any
import getpass
import sys

from models import UserRegistration, UserLogin, PasswordEntry
from database import (
    initialize_database, add_user, get_user_by_username,
    add_password, get_passwords_by_user_id, get_password_by_id
)
from security import hash_password, verify_password, encrypt_password, decrypt_password
from decorators import log_function_call, requires_auth
from logging_config import setup_logging, create_default_logging_config

# Initialiser la journalisation
create_default_logging_config()
setup_logging()
logger = logging.getLogger(__name__)

class PasswordManager:
    def __init__(self):
        self.current_user = None
        # Initialiser la base de données
        try:
            initialize_database()
            logger.info("Application de gestion de mots de passe initialisée")
        except Exception as e:
            logger.critical(f"Échec de l'initialisation de l'application: {e}")
            sys.exit(1)
    
    @log_function_call
    def register_user(self, username: str, email: str, password: str) -> bool:
        """Enregistrer un nouvel utilisateur."""
        try:
            # Valider les données utilisateur avec Pydantic
            user_data = UserRegistration(username=username, email=email, password=password)
            
            # Hacher le mot de passe
            hashed_password = hash_password(user_data.password)
            
            # Ajouter l'utilisateur à la base de données
            user_id = add_user(user_data.username, hashed_password, user_data.email)
            
            logger.info(f"Utilisateur {username} enregistré avec succès")
            return True
        except ValueError as e:
            logger.error(f"Erreur de validation: {e}")
            print(f"Erreur: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'utilisateur: {e}")
            print(f"Erreur: Une erreur inattendue s'est produite")
            return False
    
    @log_function_call
    def login_user(self, username: str, password: str) -> bool:
        """Connecter un utilisateur existant."""
        try:
            # Valider les données de connexion
            login_data = UserLogin(username=username, password=password)
            
            # Récupérer l'utilisateur depuis la base de données
            user = get_user_by_username(login_data.username)
            if not user:
                logger.warning(f"Tentative de connexion avec un nom d'utilisateur inexistant: {username}")
                print("Erreur: Nom d'utilisateur ou mot de passe incorrect")
                return False
            
            # Vérifier le mot de passe
            if not verify_password(login_data.password, user['password_hash']):
                logger.warning(f"Tentative de connexion avec un mot de passe incorrect pour {username}")
                print("Erreur: Nom d'utilisateur ou mot de passe incorrect")
                return False
            
            # Stocker l'utilisateur connecté
            self.current_user = user
            logger.info(f"Utilisateur {username} connecté avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            print(f"Erreur: Une erreur inattendue s'est produite")
            return False
    
    @requires_auth
    @log_function_call
    def store_password(self, site_name: str, username: str, password: str, notes: Optional[str] = None) -> bool:
        """Stocker un nouveau mot de passe pour l'utilisateur connecté."""
        try:
            # Valider les données du mot de passe
            password_data = PasswordEntry(site_name=site_name, username=username, password=password, notes=notes)
            
            # Chiffrer le mot de passe
            encrypted_password = encrypt_password(password_data.password)
            
            # Ajouter le mot de passe à la base de données
            add_password(
                self.current_user['id'],
                password_data.site_name,
                password_data.username,
                encrypted_password,
                password_data.notes
            )
            
            logger.info(f"Mot de passe pour {site_name} stocké avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du stockage du mot de passe: {e}")
            print(f"Erreur: Une erreur inattendue s'est produite")
            return False
    
    @requires_auth
    @log_function_call
    def retrieve_passwords(self) -> List[Dict[str, Any]]:
        """Récupérer tous les mots de passe de l'utilisateur connecté."""
        try:
            passwords = get_passwords_by_user_id(self.current_user['id'])
            logger.info(f"Récupération de {len(passwords)} mots de passe pour {self.current_user['username']}")
            return passwords
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des mots de passe: {e}")
            print(f"Erreur: Une erreur inattendue s'est produite")
            return []
    
    @requires_auth
    @log_function_call
    def retrieve_password(self, password_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer et déchiffrer un mot de passe spécifique."""
        try:
            # Récupérer le mot de passe chiffré
            password_entry = get_password_by_id(password_id, self.current_user['id'])
            if not password_entry:
                logger.warning(f"Tentative d'accès à un mot de passe inexistant: ID {password_id}")
                print("Erreur: Mot de passe non trouvé")
                return None
            
            # Déchiffrer le mot de passe
            decrypted_password = decrypt_password(password_entry['encrypted_password'])
            
            # Remplacer le mot de passe chiffré par le mot de passe déchiffré
            password_entry['password'] = decrypted_password
            del password_entry['encrypted_password']
            
            logger.info(f"Mot de passe récupéré avec succès: ID {password_id}")
            return password_entry
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du mot de passe: {e}")
            print(f"Erreur: Une erreur inattendue s'est produite")
            return None
    
    def logout(self) -> None:
        """Déconnecter l'utilisateur actuel."""
        if self.current_user:
            logger.info(f"Déconnexion de l'utilisateur {self.current_user['username']}")
            self.current_user = None
        else:
            logger.warning("Tentative de déconnexion sans utilisateur connecté")

def main():
    """Fonction principale pour l'interface en ligne de commande."""
    password_manager = PasswordManager()
    
    while True:
        if password_manager.current_user is None:
            print("\n--- Gestionnaire de Mots de Passe ---")
            print("1. Connexion")
            print("2. Inscription")
            print("3. Quitter")
            choice = input("Choix: ")
            
            if choice == "1":
                username = input("Nom d'utilisateur: ")
                password = getpass.getpass("Mot de passe: ")
                if password_manager.login_user(username, password):
                    print(f"Bienvenue, {username}!")
            
            elif choice == "2":
                username = input("Nom d'utilisateur: ")
                email = input("Email: ")
                password = getpass.getpass("Mot de passe: ")
                confirm_password = getpass.getpass("Confirmer le mot de passe: ")
                
                if password != confirm_password:
                    print("Les mots de passe ne correspondent pas.")
                    continue
                
                if password_manager.register_user(username, email, password):
                    print("Inscription réussie! Vous pouvez maintenant vous connecter.")
            
            elif choice == "3":
                print("Au revoir!")
                break
            
            else:
                print("Choix invalide, veuillez réessayer.")
        
        else:
            print(f"\n--- Bienvenue, {password_manager.current_user['username']} ---")
            print("1. Stocker un nouveau mot de passe")
            print("2. Afficher tous les mots de passe")
            print("3. Récupérer un mot de passe spécifique")
            print("4. Déconnexion")
            choice = input("Choix: ")
            
            if choice == "1":
                site_name = input("Nom du site: ")
                username = input("Nom d'utilisateur: ")
                password = getpass.getpass("Mot de passe: ")
                notes = input("Notes (optionnel): ")
                
                if password_manager.store_password(site_name, username, password, notes):
                    print("Mot de passe stocké avec succès!")
            
            elif choice == "2":
                passwords = password_manager.retrieve_passwords()
                if passwords:
                    print("\n--- Vos mots de passe ---")
                    for pw in passwords:
                        print(f"ID: {pw['id']} | Site: {pw['site_name']} | Utilisateur: {pw['username']}")
                else:
                    print("Aucun mot de passe trouvé.")
            
            elif choice == "3":
                try:
                    password_id = int(input("ID du mot de passe: "))
                    password_entry = password_manager.retrieve_password(password_id)
                    
                    if password_entry:
                        print("\n--- Détails du mot de passe ---")
                        print(f"Site: {password_entry['site_name']}")
                        print(f"Utilisateur: {password_entry['username']}")
                        print(f"Mot de passe: {password_entry['password']}")
                        if password_entry['notes']:
                            print(f"Notes: {password_entry['notes']}")
                except ValueError:
                    print("Veuillez entrer un ID valide.")
            
            elif choice == "4":
                password_manager.logout()
                print("Vous êtes déconnecté.")
            
            else:
                print("Choix invalide, veuillez réessayer.")

if __name__ == "__main__":
    main()