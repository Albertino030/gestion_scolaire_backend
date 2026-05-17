# Année_scolaire/service.py
import mysql.connector
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# =========================
# CONNEXION DB - À chaque appel
# =========================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestions_scolaires"
    )

# =========================
# AJOUT
# =========================
def add_annee(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            INSERT INTO annee_scolaire (libelle, date_debut, date_fin, actif)
            VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            data.get("libelle"),
            data.get("date_debut"),
            data.get("date_fin"),
            data.get("actif", False)
        ))
        
        conn.commit()
        return {"message": "Année ajoutée avec succès", "id_annee": cursor.lastrowid}
    except Exception as e:
        logger.error(f"Erreur dans add_annee: {str(e)}")
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# =========================
# LISTE
# =========================
def get_annees() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM annee_scolaire ORDER BY id_annee DESC")
        result = cursor.fetchall()
        return result
    except Exception as e:
        logger.error(f"Erreur dans get_annees: {str(e)}")
        raise e
    finally:
        cursor.close()
        conn.close()

# =========================
# GET ACTIVE
# =========================
def get_annee_active() -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM annee_scolaire WHERE actif = 1 LIMIT 1")
        result = cursor.fetchone()
        return result
    except Exception as e:
        logger.error(f"Erreur dans get_annee_active: {str(e)}")
        raise e
    finally:
        cursor.close()
        conn.close()

# =========================
# ACTIVER UNE ANNÉE
# =========================
def activer_annee(id_annee: int) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Vérifier si l'année existe
        cursor.execute("SELECT * FROM annee_scolaire WHERE id_annee = %s", (id_annee,))
        annee = cursor.fetchone()
        
        if not annee:
            raise Exception(f"L'année avec l'ID {id_annee} n'existe pas")
        
        # Désactiver toutes les années
        cursor.execute("UPDATE annee_scolaire SET actif = 0")
        
        # Activer l'année sélectionnée
        cursor.execute(
            "UPDATE annee_scolaire SET actif = 1 WHERE id_annee = %s",
            (id_annee,)
        )
        
        conn.commit()
        return {"message": f"Année {annee['libelle']} activée avec succès", "id_annee": id_annee}
    except Exception as e:
        logger.error(f"Erreur dans activer_annee: {str(e)}")
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# =========================
# DELETE
# =========================
def delete_annee(id_annee: int) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Vérifier si l'année est active
        cursor.execute("SELECT actif FROM annee_scolaire WHERE id_annee = %s", (id_annee,))
        annee = cursor.fetchone()
        
        if not annee:
            raise Exception("Année non trouvée")
        
        if annee['actif'] == 1:
            raise Exception("Impossible de supprimer l'année active")
        
        cursor.execute(
            "DELETE FROM annee_scolaire WHERE id_annee = %s",
            (id_annee,)
        )
        conn.commit()
        return {"message": "Année supprimée avec succès"}
    except Exception as e:
        logger.error(f"Erreur dans delete_annee: {str(e)}")
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# =========================
# UPDATE
# =========================
def update_annee(id_annee: int, data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Vérifier si l'année existe
        cursor.execute("SELECT * FROM annee_scolaire WHERE id_annee = %s", (id_annee,))
        annee = cursor.fetchone()
        
        if not annee:
            raise Exception("Année non trouvée")
        
        query = """
            UPDATE annee_scolaire
            SET libelle=%s, date_debut=%s, date_fin=%s
            WHERE id_annee=%s
        """
        
        cursor.execute(query, (
            data.get("libelle"),
            data.get("date_debut"),
            data.get("date_fin"),
            id_annee
        ))
        
        conn.commit()
        return {"message": "Année modifiée avec succès"}
    except Exception as e:
        logger.error(f"Erreur dans update_annee: {str(e)}")
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()