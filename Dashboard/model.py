# Dashboard/model.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Modèle pour les statistiques étudiants
class EtudiantsStats(BaseModel):
    total_etudiants: int
    total_filles: int
    total_garcons: int
    etudiants_actifs: int
    etudiants_exclus: int
    etudiants_sortants: int
    pourcentage_filles: float
    pourcentage_garcons: float

# Modèle pour les statistiques paiements
class PaiementsStats(BaseModel):
    total_paiements: int
    paiements_payes: int
    paiements_impayes: int
    paiements_partiels: int
    total_encaissement: float
    total_attendu: float
    taux_recouvrement: float
    etudiants_avec_paiements: int

# Modèle pour les statistiques présence
class PresenceStats(BaseModel):
    total_absences: int
    total_retards: int
    total_presences_enregistrees: int
    absences_30j: int
    retards_30j: int
    taux_assiduite: float

# Modèle pour les statistiques examens
class ExamensStats(BaseModel):
    total_examens: int
    total_notes: int
    moyenne_generale: float
    note_minimale: float
    note_maximale: float
    taux_reussite: float

# Modèle pour les statistiques suivi formation
class SuiviStats(BaseModel):
    total_suivis: int
    anciens_eleves_suivis: int
    cdi: int
    cdd: int
    stages: int
    essais: int
    auto_emploi: int
    sous_emploi: int
    non_renseigne: int
    salaire_moyen: float
    taux_insertion: float

# Modèle pour la répartition par niveau
class RepartitionNiveau(BaseModel):
    niveau: str
    nombre_etudiants: int
    pourcentage: float

# Modèle pour la répartition par filière
class RepartitionFiliere(BaseModel):
    filiere: str
    nombre_etudiants: int
    pourcentage: float

# Modèle pour l'évolution mensuelle
class EvolutionMensuelle(BaseModel):
    annee: int
    mois: int
    mois_nom: str
    inscriptions: int

# Modèle principal du Dashboard
class DashboardStats(BaseModel):
    etudiants: EtudiantsStats
    paiements: PaiementsStats
    presence: PresenceStats
    examens: ExamensStats
    suivi: SuiviStats
    repartition_niveaux: List[RepartitionNiveau]
    repartition_filieres: List[RepartitionFiliere]
    evolution_mensuelle: List[EvolutionMensuelle]
    annee_courante: Optional[Dict[str, Any]]