# Année_scolaire/model.py
from pydantic import BaseModel
from typing import Optional

class AnneeScolaire(BaseModel):
    libelle: str
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    actif: Optional[bool] = False  # Changé de True à False par défaut