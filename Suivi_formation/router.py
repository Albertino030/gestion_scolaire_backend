# Suivi_formation/router.py
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from Suivi_formation import service
from Suivi_formation.model import SuiviFormation, SuiviFormationUpdate

router = APIRouter(prefix="/suivi", tags=["Suivi Formation"])


@router.get("/annees-sortie")
def get_annees_sortie() -> List[Dict[str, Any]]:
    return service.get_annees_sortie()


@router.get("/annee-active")
def get_annee_active() -> Optional[Dict[str, Any]]:
    return service.get_annee_active()


@router.get("/etudiants-sortants")
def get_etudiants_sortants(id_annee_sortie: Optional[int] = None) -> List[Dict[str, Any]]:
    return service.get_etudiants_sortants(id_annee_sortie)


@router.get("/tableau")
def get_tableau_suivi(id_annee_sortie: Optional[int] = None) -> List[Dict[str, Any]]:
    return service.get_tableau_suivi(id_annee_sortie)


@router.get("/")
def get_all_suivis(
    id_annee_sortie: Optional[int] = None,
    annee_suivi: Optional[int] = None,
    type_suivi: Optional[str] = None
) -> List[Dict[str, Any]]:
    return service.get_all_suivis(id_annee_sortie, annee_suivi, type_suivi)


@router.get("/{matricule}/{id_annee_sortie}/{annee_suivi}")
def get_suivi_etudiant(matricule: str, id_annee_sortie: int, annee_suivi: int) -> Dict[str, Any]:
    result = service.get_suivi_etudiant(matricule, id_annee_sortie, annee_suivi)
    if not result:
        raise HTTPException(status_code=404, detail="Suivi non trouve")
    return result


@router.post("/")
def ajouter_suivi(suivi: SuiviFormation) -> Dict[str, Any]:
    result = service.ajouter_ou_modifier_suivi(suivi.dict())
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.put("/{matricule}/{id_annee_sortie}/{annee_suivi}")
def modifier_suivi(
    matricule: str,
    id_annee_sortie: int,
    annee_suivi: int,
    data: SuiviFormationUpdate
) -> Dict[str, Any]:
    existing = service.get_suivi_etudiant(matricule, id_annee_sortie, annee_suivi)
    if not existing:
        raise HTTPException(status_code=404, detail="Suivi non trouve")
    
    update_data = {
        "numero_matricule": matricule,
        "id_annee_sortie": id_annee_sortie,
        "annee_suivi": annee_suivi,
        "type_suivi": data.type_suivi or existing["type_suivi"],
        "employeur": data.employeur if data.employeur is not None else existing.get("employeur"),
        "poste_occupe": data.poste_occupe if data.poste_occupe is not None else existing.get("poste_occupe"),
        "salaire": data.salaire if data.salaire is not None else existing.get("salaire"),
        "contact_employeur": data.contact_employeur if data.contact_employeur is not None else existing.get("contact_employeur"),
        "commentaire": data.commentaire if data.commentaire is not None else existing.get("commentaire"),
    }
    
    result = service.ajouter_ou_modifier_suivi(update_data)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.delete("/{suivi_id}")
def supprimer_suivi(suivi_id: int) -> Dict[str, Any]:
    result = service.supprimer_suivi(suivi_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@router.get("/statistiques/resume")
def get_statistiques(id_annee_sortie: Optional[int] = None) -> Dict[str, Any]:
    return service.get_statistiques_suivi(id_annee_sortie)