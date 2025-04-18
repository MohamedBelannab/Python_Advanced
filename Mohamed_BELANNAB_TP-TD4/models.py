# models.py
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class UserRegistration(BaseModel):
    """Modèle pour la validation des données d'enregistrement d'un utilisateur."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
    def password_strength(cls, v):
        """Valider la complexité du mot de passe."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une lettre majuscule')
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une lettre minuscule')
        if not re.search(r'[0-9]', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Le mot de passe doit contenir au moins un caractère spécial')
        return v

class UserLogin(BaseModel):
    """Modèle pour la validation des données de connexion d'un utilisateur."""
    username: str
    password: str

class PasswordEntry(BaseModel):
    """Modèle pour la validation des entrées de mots de passe à stocker."""
    site_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)
    notes: str = Field(None, max_length=500)