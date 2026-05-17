from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class PresenceBase(BaseModel):
    numero_matricule: str
    type: str  # "absence" ou "retard"
    motif: Optional[str] = None
    date_presence: date
    heure: Optional[time] = None


class PresenceCreate(PresenceBase):
    pass


class PresenceOut(BaseModel):
    id: int
    numero_matricule: str
    nom: str
    prenom: str
    niveau: str
    filiere: str
    type: str
    motif: Optional[str]
    date_presence: date
    heure: Optional[time]

    class Config:
        from_attributes = True  