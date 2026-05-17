from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from etudiants import service

router = APIRouter(prefix="/etudiants", tags=["Etudiants"])


class Etudiant(BaseModel):
    numero_matricule: str
    date_inscription: str | None = None
    nom: str
    prenom: str
    genre: str | None = None
    date_naissance: str | None = None
    lieu_naissance: str | None = None
    nom_pere: str | None = None
    nom_mere: str | None = None
    nom_tuteur: str | None = None
    adresse: str | None = None
    telephone: str | None = None
    filiere_choisie: str | None = None
    niveau: str | None = None
    id_filiere: int | None = None
    id_niveau: int | None = None
    id_annee: int | None = None
    projet_professionnel: str | None = None


@router.get("/")
def get_etudiants(id_annee: int | None = None):
    return service.get_etudiants(id_annee)


@router.get("/{numero_matricule}")
def get_etudiant(numero_matricule: str):
    result = service.get_etudiant(numero_matricule)
    if not result or "error" in result:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    return result


@router.post("/")
def add_etudiant(etudiant: Etudiant):
    return service.add_etudiant(etudiant.dict())


@router.delete("/{numero_matricule}")
def delete_etudiant(numero_matricule: str):
    return service.delete_etudiant(numero_matricule)


@router.put("/{numero_matricule}")
def update_etudiant(numero_matricule: str, etudiant: Etudiant):
    return service.update_etudiant(numero_matricule, etudiant.dict())