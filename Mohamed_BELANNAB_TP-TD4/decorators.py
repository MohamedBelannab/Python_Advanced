# decorators.py
import logging
import time
from typing import Callable, Any

logger = logging.getLogger(__name__)

def log_function_call(func: Callable) -> Callable:
    """
    Décorateur pour journaliser les appels de fonction.
    Enregistre les informations sur l'entrée et la sortie de la fonction,
    ainsi que le temps d'exécution.
    """

    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.info(f"Appel de la fonction {func_name}")
        
        try:
            # Masquer les informations sensibles dans les logs
            safe_args = ["*****" if isinstance(arg, str) and len(arg) > 10 else arg for arg in args]
            safe_kwargs = {k: "*****" if isinstance(v, str) and len(v) > 10 else v for k, v in kwargs.items()}
            
            logger.debug(f"Arguments: {safe_args}, Kwargs: {safe_kwargs}")
            
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"Fonction {func_name} exécutée en {execution_time:.4f} secondes")
            return result
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de {func_name}: {str(e)}")
            raise
    
    return wrapper

def requires_auth(func: Callable) -> Callable:
    """
    Décorateur pour vérifier l'authentification de l'utilisateur.
    Vérifie si l'utilisateur est connecté avant d'autoriser l'accès à la fonction.
    """
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'current_user') or self.current_user is None:
            logger.warning("Tentative d'accès non autorisé à une fonction protégée")
            raise PermissionError("Authentification requise pour accéder à cette fonctionnalité")
        
        logger.info(f"Accès autorisé pour l'utilisateur {self.current_user['username']} à la fonction {func.__name__}")
        return func(self, *args, **kwargs)
    
    return wrapper