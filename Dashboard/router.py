# Dashboard/router.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
from Dashboard import service
from Dashboard.model import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats() -> Dict[str, Any]:
    """Récupère toutes les statistiques du dashboard"""
    try:
        return service.get_dashboard_complet()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/etudiants")
def get_etudiants_stats() -> Dict[str, Any]:
    """Récupère les statistiques des étudiants"""
    return service.get_etudiants_stats()


@router.get("/paiements")
def get_paiements_stats() -> Dict[str, Any]:
    """Récupère les statistiques des paiements"""
    return service.get_paiements_stats()


@router.get("/presence")
def get_presence_stats() -> Dict[str, Any]:
    """Récupère les statistiques de présence"""
    return service.get_presence_stats()


@router.get("/examens")
def get_examens_stats() -> Dict[str, Any]:
    """Récupère les statistiques des examens"""
    return service.get_examens_stats()


@router.get("/suivi")
def get_suivi_stats() -> Dict[str, Any]:
    """Récupère les statistiques du suivi formation"""
    return service.get_suivi_stats()


@router.get("/repartition/niveaux")
def get_repartition_niveaux() -> List[Dict[str, Any]]:
    """Récupère la répartition des étudiants par niveau"""
    return service.get_repartition_niveaux()


@router.get("/repartition/filieres")
def get_repartition_filieres() -> List[Dict[str, Any]]:
    """Récupère la répartition des étudiants par filière"""
    return service.get_repartition_filieres()


@router.get("/evolution")
def get_evolution_mensuelle(limit: int = Query(12, ge=1, le=24)) -> List[Dict[str, Any]]:
    """Récupère l'évolution mensuelle des inscriptions"""
    return service.get_evolution_mensuelle(limit)


@router.get("/annee-courante")
def get_annee_courante() -> Optional[Dict[str, Any]]:
    """Récupère l'année scolaire active"""
    return service.get_annee_courante() 