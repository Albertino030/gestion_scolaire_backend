from fastapi import APIRouter, Query
from typing import Optional
from examen import service

# ⚠️ Le préfixe doit être "/examen" pour correspondre au frontend
router = APIRouter(
    prefix="/examen",  # ← CHANGER de "" à "/examen"
    tags=["Examen"]
)

# =========================
# MATIERE
# =========================
@router.get("/matieres")
def list_matieres():
    return service.get_all_matieres()

@router.get("/matieres/by-filiere-niveau")
def get_matieres_by_filiere_niveau(
    filiere: str = Query(..., description="Nom de la filière"),
    niveau: str = Query(..., description="Niveau (ex: 1ère année, 2ème année, 3ème année)")
):
    return service.get_matieres_by_filiere_niveau(filiere, niveau)

@router.post("/matieres")
def create_matiere(nom_matiere: str):
    return service.add_matiere(nom_matiere)

@router.delete("/matieres/{id_matiere}")
def remove_matiere(id_matiere: int):
    return service.delete_matiere(id_matiere)

# =========================
# PROGRAMME
# =========================
@router.get("/programme")
def list_programme():
    return service.get_programme()

@router.post("/programme")
def create_programme(id_filiere: int, id_niveau: int, id_matiere: int, coefficient: int):
    return service.add_programme(id_filiere, id_niveau, id_matiere, coefficient)

# =========================
# ETUDIANTS PAR FILIERE ET NIVEAU
# =========================
@router.get("/etudiants/filter")
def get_etudiants_by_filiere_niveau(
    filiere: str = Query(..., description="Nom de la filière"),
    niveau: str = Query(..., description="Niveau")
):
    return service.get_etudiants_by_filiere_niveau(filiere, niveau)

# =========================
# NOTES (AVEC FILTRES)
# =========================
@router.post("/notes")
def create_note(numero_matricule: str, id_matiere: int, id_examen: int, note: float):
    return service.add_note(numero_matricule, id_matiere, id_examen, note)

@router.get("/notes")
def list_notes(
    filiere: Optional[str] = Query(None, description="Nom de la filière"),
    niveau: Optional[str] = Query(None, description="Niveau"),
    examen: Optional[str] = Query(None, description="Nom de l'examen")
):
    return service.get_notes_with_filters(filiere, niveau, examen)

@router.put("/notes/{id_note}")
def update_note(id_note: int, note: float):
    return service.update_note(id_note, note)

@router.delete("/notes/{id_note}")
def delete_note(id_note: int):
    return service.delete_note(id_note)

# =========================
# FILIERES ET NIVEAUX
# =========================
@router.get("/filieres")
def get_all_filieres():
    return service.get_all_filieres()

@router.get("/niveaux")
def get_all_niveaux():
    return service.get_all_niveaux()

@router.get("/examens")
def get_all_examens():
    return service.get_all_examens()