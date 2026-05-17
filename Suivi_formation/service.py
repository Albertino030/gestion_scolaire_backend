# Suivi_formation/service.py
import mysql.connector
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'gestions_scolaires'),
        port=int(os.environ.get('DB_PORT', 3306))
    )


def get_annee_active() -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_annee, libelle FROM annee_scolaire WHERE actif = 1 LIMIT 1")
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_annees_sortie() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_annee_sortie as id_annee, libelle FROM annee_sortie ORDER BY id_annee_sortie DESC")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_etudiants_sortants(id_annee_sortie: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT DISTINCT
                s.numero_matricule,
                e.nom,
                e.prenom,
                f.nom_filiere as filiere,
                s.id_annee_sortie as annee_sortie_id,
                a.libelle as annee_sortie_libelle
            FROM suivi_formation s
            JOIN etudiants e ON s.numero_matricule = e.numero_matricule
            LEFT JOIN filiere f ON e.id_filiere = f.id_filiere
            JOIN annee_sortie a ON s.id_annee_sortie = a.id_annee_sortie
        """
        if id_annee_sortie:
            query += " WHERE s.id_annee_sortie = %s"
            cursor.execute(query, (id_annee_sortie,))
        else:
            cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_suivi_etudiant(matricule: str, id_annee_sortie: int, annee_suivi: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT sf.*, a.libelle as annee_sortie_libelle
            FROM suivi_formation sf
            JOIN annee_sortie a ON sf.id_annee_sortie = a.id_annee_sortie
            WHERE sf.numero_matricule = %s AND sf.id_annee_sortie = %s AND sf.annee_suivi = %s
        """, (matricule, id_annee_sortie, annee_suivi))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_all_suivis(id_annee_sortie: Optional[int] = None, annee_suivi: Optional[int] = None, 
                   type_suivi: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                sf.id,
                sf.numero_matricule,
                e.nom,
                e.prenom,
                f.nom_filiere as filiere,
                a.libelle as annee_sortie,
                sf.annee_suivi,
                sf.type_suivi,
                sf.employeur,
                sf.poste_occupe,
                sf.salaire,
                sf.contact_employeur,
                sf.commentaire,
                sf.created_at,
                sf.updated_at,
                sf.id_annee_sortie
            FROM suivi_formation sf
            JOIN etudiants e ON sf.numero_matricule = e.numero_matricule
            LEFT JOIN filiere f ON e.id_filiere = f.id_filiere
            JOIN annee_sortie a ON sf.id_annee_sortie = a.id_annee_sortie
            WHERE 1=1
        """
        params = []
        if id_annee_sortie:
            query += " AND sf.id_annee_sortie = %s"
            params.append(id_annee_sortie)
        if annee_suivi:
            query += " AND sf.annee_suivi = %s"
            params.append(annee_suivi)
        if type_suivi:
            query += " AND sf.type_suivi = %s"
            params.append(type_suivi)
        query += " ORDER BY a.libelle DESC, sf.annee_suivi, e.nom"
        
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def ajouter_ou_modifier_suivi(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM suivi_formation WHERE numero_matricule = %s AND id_annee_sortie = %s AND annee_suivi = %s",
                      (data["numero_matricule"], data["id_annee_sortie"], data["annee_suivi"]))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE suivi_formation
                SET type_suivi = %s, employeur = %s, poste_occupe = %s, 
                    salaire = %s, contact_employeur = %s, commentaire = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (data["type_suivi"], data.get("employeur"), data.get("poste_occupe"),
                  data.get("salaire"), data.get("contact_employeur"), data.get("commentaire"),
                  existing["id"]))
        else:
            cursor.execute("""
                INSERT INTO suivi_formation
                (numero_matricule, id_annee_sortie, annee_suivi, type_suivi, 
                 employeur, poste_occupe, salaire, contact_employeur, commentaire)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (data["numero_matricule"], data["id_annee_sortie"], data["annee_suivi"],
                  data["type_suivi"], data.get("employeur"), data.get("poste_occupe"),
                  data.get("salaire"), data.get("contact_employeur"), data.get("commentaire")))
        
        conn.commit()
        return {"success": True, "message": "Suivi enregistré"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()


def supprimer_suivi(suivi_id: int) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM suivi_formation WHERE id = %s", (suivi_id,))
        conn.commit()
        return {"success": True, "message": "Suivi supprimé"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()


def get_tableau_suivi(id_annee_sortie: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT 
                s.numero_matricule,
                e.nom,
                e.prenom,
                COALESCE(f.nom_filiere, '-') as filiere,
                a.libelle as annee_sortie_libelle,
                a.id_annee_sortie as annee_sortie_id,
                s.annee_suivi,
                s.type_suivi
            FROM suivi_formation s
            JOIN etudiants e ON s.numero_matricule = e.numero_matricule
            LEFT JOIN filiere f ON e.id_filiere = f.id_filiere
            JOIN annee_sortie a ON s.id_annee_sortie = a.id_annee_sortie
        """
        if id_annee_sortie:
            query += " WHERE s.id_annee_sortie = %s"
            cursor.execute(query, (id_annee_sortie,))
        else:
            cursor.execute(query)
        
        resultats = cursor.fetchall()
        
        pivot = {}
        for row in resultats:
            key = row["numero_matricule"]
            if key not in pivot:
                pivot[key] = {
                    "numero_matricule": row["numero_matricule"],
                    "nom": row["nom"],
                    "prenom": row["prenom"],
                    "filiere": row["filiere"],
                    "annee_sortie_id": row["annee_sortie_id"],
                    "annee_sortie_libelle": row["annee_sortie_libelle"],
                    "suivi_an1": "Non renseigne",
                    "suivi_an2": "Non renseigne",
                    "suivi_an3": "Non renseigne",
                    "suivi_an4": "Non renseigne",
                    "suivi_an5": "Non renseigne"
                }
            annee = row["annee_suivi"]
            if 1 <= annee <= 5:
                pivot[key][f"suivi_an{annee}"] = row["type_suivi"] if row["type_suivi"] else "Non renseigne"
        
        return list(pivot.values())
    except Exception as e:
        print(f"Erreur get_tableau_suivi: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_statistiques_suivi(id_annee_sortie: Optional[int] = None) -> Dict[str, Any]:
    return {"total": len(get_all_suivis(id_annee_sortie))}