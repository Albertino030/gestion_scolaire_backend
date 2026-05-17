# Année_scolaire/router.py
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from .model import AnneeScolaire
from . import service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/annees", tags=["Année scolaire"])

@router.get("/")
def get_all() -> List[Dict[str, Any]]:
    try:
        return service.get_annees()
    except Exception as e:
        logger.error(f"Erreur dans get_all: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active")
def get_active() -> Optional[Dict[str, Any]]:
    try:
        return service.get_annee_active()
    except Exception as e:
        logger.error(f"Erreur dans get_active: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def add(annee: AnneeScolaire) -> Dict[str, Any]:
    try:
        return service.add_annee(annee.dict())
    except Exception as e:
        logger.error(f"Erreur dans add: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/activer/{id_annee}")
def activer(id_annee: int) -> Dict[str, Any]:
    try:
        return service.activer_annee(id_annee)
    except Exception as e:
        logger.error(f"Erreur dans activer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id_annee}")
def update(id_annee: int, annee: AnneeScolaire) -> Dict[str, Any]:
    try:
        return service.update_annee(id_annee, annee.dict())
    except Exception as e:
        logger.error(f"Erreur dans update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id_annee}")
def delete(id_annee: int) -> Dict[str, Any]:
    try:
        return service.delete_annee(id_annee)
    except Exception as e:
        logger.error(f"Erreur dans delete: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))