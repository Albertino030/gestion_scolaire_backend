# Suivi_formation/model.py
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

# Types de suivi possibles
TYPE_SUIVI = Literal["Stage", "Essai", "CDD", "CDI", "Auto-emploi", "Sous emploi", "Non renseigne"]


class SuiviFormation(BaseModel):
    """Modele pour le suivi de formation"""
    numero_matricule: str
    id_annee_sortie: int
    annee_suivi: int
    type_suivi: TYPE_SUIVI = "Non renseigne"
    employeur: Optional[str] = None
    poste_occupe: Optional[str] = None
    salaire: Optional[float] = None
    contact_employeur: Optional[str] = None
    commentaire: Optional[str] = None


class SuiviFormationUpdate(BaseModel):
    """Modele pour la mise a jour du suivi"""
    type_suivi: Optional[TYPE_SUIVI] = None
    employeur: Optional[str] = None
    poste_occupe: Optional[str] = None
    salaire: Optional[float] = None
    contact_employeur: Optional[str] = None
    commentaire: Optional[str] = None


class AnneeScolaireSortie(BaseModel):
    """Modele pour les annees de sortie"""
    id_annee: int
    libelle: str


class SuiviAvecEtudiant(BaseModel):
    """Modele avec informations etudiant"""
    id: int
    numero_matricule: str
    nom: str
    prenom: str
    filiere: str
    annee_sortie: str
    annee_suivi: int
    type_suivi: str
    employeur: Optional[str]
    poste_occupe: Optional[str]
    salaire: Optional[float]
    contact_employeur: Optional[str]
    commentaire: Optional[str]
    created_at: datetime
    updated_at: datetime