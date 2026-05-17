from pydantic import BaseModel
from typing import Optional


class Matiere(BaseModel):
    id_matiere: Optional[int] = None
    nom_matiere: str


class ProgrammeScolaire(BaseModel):
    id: Optional[int] = None
    id_filiere: int
    id_niveau: int
    id_matiere: int
    coefficient: int


class Examen(BaseModel):
    id_examen: Optional[int] = None
    nom_examen: str
    id_annee: int


class Note(BaseModel):
    id_note: Optional[int] = None
    numero_matricule: str
    id_matiere: int
    id_examen: int
    note: float