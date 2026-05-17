from pydantic import BaseModel
from typing import Optional, Literal


class PaiementFrais(BaseModel):
    numero_matricule: str
    id_niveau: int
    id_filiere: int

    type_frais: Literal[
        "inscription", "combinaison", "tablier", "tenue_fete", "ecolage"
    ]

    mois: Optional[Literal[
        "septembre","octobre","novembre","decembre",
        "janvier","fevrier","mars","avril","mai","juin"
    ]] = None

    montant: float
    statut: Optional[Literal["payé", "impayé", "partiel"]] = "impayé"


class UpdatePaiement(BaseModel):
    """Pour mettre à jour un paiement existant"""
    montant: float
    statut: Literal["payé", "impayé", "partiel"]