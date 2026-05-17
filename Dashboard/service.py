# Dashboard/service.py
import mysql.connector
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

def get_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'gestions_scolaires'),
        port=int(os.environ.get('DB_PORT', 3306))
    )


def get_etudiants_stats() -> Dict[str, Any]:
    """Récupère les statistiques des étudiants"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_etudiants,
                SUM(CASE WHEN genre = 'F' THEN 1 ELSE 0 END) as total_filles,
                SUM(CASE WHEN genre = 'M' THEN 1 ELSE 0 END) as total_garcons,
                SUM(CASE WHEN statut = 'actif' THEN 1 ELSE 0 END) as etudiants_actifs,
                SUM(CASE WHEN statut = 'exclu' THEN 1 ELSE 0 END) as etudiants_exclus,
                SUM(CASE WHEN statut = 'sortant' THEN 1 ELSE 0 END) as etudiants_sortants
            FROM etudiants
        """)
        result = cursor.fetchone()
        
        total = result['total_etudiants']
        if total > 0:
            result['pourcentage_filles'] = round((result['total_filles'] / total) * 100, 1)
            result['pourcentage_garcons'] = round((result['total_garcons'] / total) * 100, 1)
        else:
            result['pourcentage_filles'] = 0
            result['pourcentage_garcons'] = 0
            
        return result
    finally:
        cursor.close()
        conn.close()


def get_paiements_stats() -> Dict[str, Any]:
    """Récupère les statistiques des paiements"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_paiements,
                COUNT(DISTINCT numero_matricule) as etudiants_avec_paiements,
                SUM(CASE WHEN statut = 'payé' THEN 1 ELSE 0 END) as paiements_payes,
                SUM(CASE WHEN statut = 'impayé' THEN 1 ELSE 0 END) as paiements_impayes,
                SUM(CASE WHEN statut = 'partiel' THEN 1 ELSE 0 END) as paiements_partiels,
                SUM(CASE WHEN statut = 'payé' THEN montant ELSE 0 END) as total_encaissement,
                SUM(montant) as total_attendu
            FROM paiement_frais
        """)
        result = cursor.fetchone()
        
        if result['total_attendu'] and result['total_attendu'] > 0:
            result['taux_recouvrement'] = round((result['total_encaissement'] / result['total_attendu']) * 100, 1)
        else:
            result['taux_recouvrement'] = 0
            
        return result
    finally:
        cursor.close()
        conn.close()


def get_presence_stats() -> Dict[str, Any]:
    """Récupère les statistiques de présence"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        date_30j = datetime.now() - timedelta(days=30)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_presences_enregistrees,
                SUM(CASE WHEN type = 'absence' THEN 1 ELSE 0 END) as total_absences,
                SUM(CASE WHEN type = 'retard' THEN 1 ELSE 0 END) as total_retards,
                SUM(CASE WHEN type = 'absence' AND date_presence >= %s THEN 1 ELSE 0 END) as absences_30j,
                SUM(CASE WHEN type = 'retard' AND date_presence >= %s THEN 1 ELSE 0 END) as retards_30j
            FROM presence
        """, (date_30j, date_30j))
        
        result = cursor.fetchone()
        
        total = result['total_presences_enregistrees']
        if total > 0:
            result['taux_assiduite'] = round(((total - result['total_absences']) / total) * 100, 1)
        else:
            result['taux_assiduite'] = 0
            
        return result
    finally:
        cursor.close()
        conn.close()


def get_examens_stats() -> Dict[str, Any]:
    """Récupère les statistiques des examens"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM examen) as total_examens,
                COUNT(*) as total_notes,
                ROUND(AVG(note), 2) as moyenne_generale,
                MIN(note) as note_minimale,
                MAX(note) as note_maximale,
                ROUND(SUM(CASE WHEN note >= 10 THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as taux_reussite
            FROM note
        """)
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_suivi_stats() -> Dict[str, Any]:
    """Récupère les statistiques du suivi formation"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_suivis,
                COUNT(DISTINCT numero_matricule) as anciens_eleves_suivis,
                SUM(CASE WHEN type_suivi = 'CDI' THEN 1 ELSE 0 END) as cdi,
                SUM(CASE WHEN type_suivi = 'CDD' THEN 1 ELSE 0 END) as cdd,
                SUM(CASE WHEN type_suivi = 'Stage' THEN 1 ELSE 0 END) as stages,
                SUM(CASE WHEN type_suivi = 'Essai' THEN 1 ELSE 0 END) as essais,
                SUM(CASE WHEN type_suivi = 'Auto-emploi' THEN 1 ELSE 0 END) as auto_emploi,
                SUM(CASE WHEN type_suivi = 'Sous emploi' THEN 1 ELSE 0 END) as sous_emploi,
                SUM(CASE WHEN type_suivi = 'Non renseigne' OR type_suivi = '' THEN 1 ELSE 0 END) as non_renseigne,
                ROUND(AVG(CASE WHEN salaire > 0 THEN salaire END), 0) as salaire_moyen,
                ROUND(SUM(CASE WHEN type_suivi IN ('CDI', 'CDD', 'Auto-emploi') THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as taux_insertion
            FROM suivi_formation
        """)
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_repartition_niveaux() -> List[Dict[str, Any]]:
    """Récupère la répartition des étudiants par niveau"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        total = get_etudiants_stats()['total_etudiants']
        
        cursor.execute("""
            SELECT 
                n.libelle as niveau,
                COUNT(e.numero_matricule) as nombre_etudiants
            FROM etudiants e
            JOIN niveau n ON e.id_niveau = n.id_niveau
            GROUP BY n.id_niveau, n.libelle
            ORDER BY n.id_niveau
        """)
        result = cursor.fetchall()
        
        for item in result:
            if total > 0:
                item['pourcentage'] = round((item['nombre_etudiants'] / total) * 100, 1)
            else:
                item['pourcentage'] = 0
                
        return result
    finally:
        cursor.close()
        conn.close()


def get_repartition_filieres() -> List[Dict[str, Any]]:
    """Récupère la répartition des étudiants par filière"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        total = get_etudiants_stats()['total_etudiants']
        
        cursor.execute("""
            SELECT 
                f.nom_filiere as filiere,
                COUNT(e.numero_matricule) as nombre_etudiants
            FROM etudiants e
            JOIN filiere f ON e.id_filiere = f.id_filiere
            GROUP BY f.id_filiere, f.nom_filiere
            ORDER BY nombre_etudiants DESC
        """)
        result = cursor.fetchall()
        
        for item in result:
            if total > 0:
                item['pourcentage'] = round((item['nombre_etudiants'] / total) * 100, 1)
            else:
                item['pourcentage'] = 0
                
        return result
    finally:
        cursor.close()
        conn.close()


def get_evolution_mensuelle(limit: int = 12) -> List[Dict[str, Any]]:
    """Récupère l'évolution mensuelle des inscriptions"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                YEAR(date_inscription) as annee,
                MONTH(date_inscription) as mois,
                COUNT(*) as inscriptions
            FROM etudiants
            WHERE date_inscription IS NOT NULL
            GROUP BY YEAR(date_inscription), MONTH(date_inscription)
            ORDER BY annee DESC, mois DESC
            LIMIT %s
        """, (limit,))
        
        result = cursor.fetchall()
        
        mois_noms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        
        for item in result:
            item['mois_nom'] = mois_noms[item['mois'] - 1]
            
        return result
    finally:
        cursor.close()
        conn.close()


def get_annee_courante() -> Optional[Dict[str, Any]]:
    """Récupère l'année scolaire active"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id_annee, libelle FROM annee_scolaire WHERE actif = 1 LIMIT 1")
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_dashboard_complet() -> Dict[str, Any]:
    """Récupère toutes les statistiques du dashboard"""
    return {
        "etudiants": get_etudiants_stats(),
        "paiements": get_paiements_stats(),
        "presence": get_presence_stats(),
        "examens": get_examens_stats(),
        "suivi": get_suivi_stats(),
        "repartition_niveaux": get_repartition_niveaux(),
        "repartition_filieres": get_repartition_filieres(),
        "evolution_mensuelle": get_evolution_mensuelle(),
        "annee_courante": get_annee_courante()
    }