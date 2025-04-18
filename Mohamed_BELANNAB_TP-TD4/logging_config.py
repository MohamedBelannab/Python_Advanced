# logging_config.py
import os
import yaml
import logging
import logging.config

def setup_logging(config_path="logging_config.yaml", default_level=logging.INFO):
    """
    Configure la journalisation à partir d'un fichier YAML.
    """
    if os.path.exists(config_path):
        with open(config_path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(f"Erreur lors du chargement de la configuration de journalisation: {e}")
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        print(f"Fichier de configuration {config_path} non trouvé. Utilisation de la configuration par défaut.")

# Créer le fichier de configuration de journalisation par défaut s'il n'existe pas
def create_default_logging_config():
    """
    Crée un fichier de configuration YAML par défaut pour la journalisation.
    """
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': 'password_manager.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': 'error.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    }
    
    with open('logging_config.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)