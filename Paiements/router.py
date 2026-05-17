from fastapi import APIRouter, HTTPException
from typing import Optional
from Paiements import service
from Paiements.model import PaiementFrais, UpdatePaiement

router = APIRouter(prefix="/paiements", tags=["Paiements"])


@router.get("/")
def get_paiements(id_annee: Optional[int] = None):
    result = service.get_table_paiements(id_annee)
    return result


@router.post("/")
def add_paiement(paiement: PaiementFrais):
    """Ajoute ou met à jour un paiement"""
    print(f"📝 Réception paiement: {paiement.dict()}")
    result = service.insert_paiement(paiement.dict())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.put("/{matricule}/{type_frais}")
def update_paiement(
    matricule: str, 
    type_frais: str, 
    mois: Optional[str] = None,
    data: UpdatePaiement = None
):
    """Met à jour un paiement existant"""
    if not data:
        raise HTTPException(status_code=400, detail="Données de mise à jour requises")
    
    result = service.update_paiement(matricule, type_frais, mois, data.dict())
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/generer/{matricule}/{id_niveau}")
def generer(matricule: str, id_niveau: int):
    print(f"🔄 Génération des paiements pour {matricule}, niveau ID: {id_niveau}")
    result = service.generer_paiements(matricule, id_niveau)
    return result