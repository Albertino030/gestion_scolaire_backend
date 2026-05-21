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


# =========================
# MATIERE
# =========================
def get_all_matieres():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM matiere")
    data = cursor.fetchall()
    conn.close()
    return data

def get_matieres_by_filiere_niveau(filiere: str, niveau: str, id_annee: int = None):
    """Récupère les matières pour une filière, un niveau et une année donnés"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id_filiere FROM filiere WHERE nom_filiere = %s", (filiere,))
    filiere_result = cursor.fetchone()
    if not filiere_result:
        conn.close()
        return []
    
    niveau_map = {
        "1ère année": 1,
        "2ème année": 2,
        "3ème année": 3,
        "1 année": 1,
        "2 années": 2,
        "3 années": 3
    }
    id_niveau = niveau_map.get(niveau, 1)
    
    cursor.execute("""
        SELECT m.id_matiere, m.nom_matiere, ps.coefficient
        FROM programme_scolaire ps
        JOIN matiere m ON ps.id_matiere = m.id_matiere
        WHERE ps.id_filiere = %s AND ps.id_niveau = %s
        ORDER BY m.nom_matiere
    """, (filiere_result['id_filiere'], id_niveau))
    
    data = cursor.fetchall()
    conn.close()
    return data

def add_matiere(nom_matiere):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO matiere (nom_matiere) VALUES (%s)", (nom_matiere,))
    conn.commit()
    conn.close()
    return {"message": "Matière ajoutée"}

def delete_matiere(id_matiere):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matiere WHERE id_matiere=%s", (id_matiere,))
    conn.commit()
    conn.close()
    return {"message": "Matière supprimée"}


# =========================
# PROGRAMME SCOLAIRE
# =========================
def get_programme():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT ps.id, f.nom_filiere, n.libelle as nom_niveau, m.nom_matiere, ps.coefficient
        FROM programme_scolaire ps
        JOIN filiere f ON ps.id_filiere = f.id_filiere
        JOIN niveau n ON ps.id_niveau = n.id_niveau
        JOIN matiere m ON ps.id_matiere = m.id_matiere
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def add_programme(id_filiere, id_niveau, id_matiere, coefficient):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO programme_scolaire (id_filiere, id_niveau, id_matiere, coefficient)
        VALUES (%s, %s, %s, %s)
    """, (id_filiere, id_niveau, id_matiere, coefficient))
    conn.commit()
    conn.close()
    return {"message": "Programme ajouté"}


# =========================
# ETUDIANTS PAR FILIERE ET NIVEAU
# =========================
def get_etudiants_by_filiere_niveau(filiere: str, niveau: str, id_annee: int = None):
    """Récupère les étudiants d'une filière, niveau et année spécifiques"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    niveau_map = {
        "1ère année": 1,
        "2ème année": 2,
        "3ème année": 3,
        "1 année": 1,
        "2 années": 2,
        "3 années": 3
    }
    id_niveau = niveau_map.get(niveau, 1)
    
    query = """
        SELECT e.numero_matricule, e.nom, e.prenom, e.id_niveau, f.nom_filiere
        FROM etudiants e
        JOIN filiere f ON e.id_filiere = f.id_filiere
        WHERE f.nom_filiere = %s AND e.id_niveau = %s AND e.statut = 'actif'
    """
    params = [filiere, id_niveau]
    
    if id_annee:
        query += " AND e.id_annee = %s"
        params.append(id_annee)
    
    query += " ORDER BY e.nom, e.prenom"
    
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data


# =========================
# NOTES AVEC FILTRES ET ANNEE
# =========================
def add_note(numero_matricule, id_matiere, id_examen, note):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id_note FROM note 
        WHERE numero_matricule = %s AND id_matiere = %s AND id_examen = %s
    """, (numero_matricule, id_matiere, id_examen))
    
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("""
            UPDATE note SET note = %s 
            WHERE numero_matricule = %s AND id_matiere = %s AND id_examen = %s
        """, (note, numero_matricule, id_matiere, id_examen))
    else:
        cursor.execute("""
            INSERT INTO note (numero_matricule, id_matiere, id_examen, note)
            VALUES (%s, %s, %s, %s)
        """, (numero_matricule, id_matiere, id_examen, note))
    
    conn.commit()
    conn.close()
    return {"message": "Note enregistrée"}

def get_notes_with_filters(filiere: Optional[str] = None, niveau: Optional[str] = None, examen: Optional[str] = None, id_annee: Optional[int] = None):
    """Récupère les notes avec filtres optionnels incluant l'année"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    id_filiere = None
    id_niveau = None
    id_examen = None
    
    niveau_map = {
        "1ère année": 1,
        "2ème année": 2,
        "3ème année": 3,
        "1 année": 1,
        "2 années": 2,
        "3 années": 3
    }
    
    if filiere:
        cursor.execute("SELECT id_filiere FROM filiere WHERE nom_filiere = %s", (filiere,))
        result = cursor.fetchone()
        if result:
            id_filiere = result['id_filiere']
    
    if niveau:
        id_niveau = niveau_map.get(niveau)
    
    if examen and id_annee:
        cursor.execute("SELECT id_examen FROM examen WHERE nom_examen = %s AND id_annee = %s LIMIT 1", (examen, id_annee))
        result = cursor.fetchone()
        if result:
            id_examen = result['id_examen']
    elif examen:
        cursor.execute("SELECT id_examen FROM examen WHERE nom_examen = %s AND id_annee = 1 LIMIT 1", (examen,))
        result = cursor.fetchone()
        if result:
            id_examen = result['id_examen']
    
    query = """
        SELECT 
            e.numero_matricule,
            e.nom,
            e.prenom,
            e.id_niveau,
            f.nom_filiere as filiere,
            m.nom_matiere,
            m.id_matiere,
            n.note
        FROM etudiants e
        JOIN filiere f ON e.id_filiere = f.id_filiere
        CROSS JOIN matiere m
        LEFT JOIN note n ON n.numero_matricule = e.numero_matricule 
            AND n.id_matiere = m.id_matiere
            AND n.id_examen = %s
        WHERE 1=1
    """
    
    params = [id_examen if id_examen else 1]
    
    if id_filiere:
        query += " AND e.id_filiere = %s"
        params.append(id_filiere)
    
    if id_niveau:
        query += " AND e.id_niveau = %s"
        params.append(id_niveau)
    
    if id_annee:
        query += " AND e.id_annee = %s"
        params.append(id_annee)
    
    if id_filiere and id_niveau:
        query += """ AND m.id_matiere IN (
            SELECT id_matiere FROM programme_scolaire 
            WHERE id_filiere = %s AND id_niveau = %s
        )"""
        params.append(id_filiere)
        params.append(id_niveau)
    
    query += " ORDER BY e.nom, e.prenom, m.nom_matiere"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    notes_by_student = {}
    for row in results:
        key = row['numero_matricule']
        if key not in notes_by_student:
            notes_by_student[key] = {
                'numero_matricule': row['numero_matricule'],
                'nom': row['nom'],
                'prenom': row['prenom'],
                'id_niveau': row['id_niveau'],
                'filiere': row['filiere'],
                'notes': {}
            }
        notes_by_student[key]['notes'][row['nom_matiere']] = row['note'] if row['note'] is not None else None
    
    return list(notes_by_student.values())

def update_note(id_note, note):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE note SET note = %s WHERE id_note = %s", (note, id_note))
    conn.commit()
    conn.close()
    return {"message": "Note modifiée"}

def delete_note(id_note):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM note WHERE id_note = %s", (id_note,))
    conn.commit()
    conn.close()
    return {"message": "Note supprimée"}


# =========================
# FILIERES ET NIVEAUX
# =========================
def get_all_filieres():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_filiere, nom_filiere FROM filiere ORDER BY nom_filiere")
    data = cursor.fetchall()
    conn.close()
    return [f['nom_filiere'] for f in data]

def get_all_niveaux():
    return ["1ère année", "2ème année", "3ème année"]

def get_all_examens(id_annee: int = None):
    """Récupère la liste des examens"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    if id_annee:
        cursor.execute("SELECT id_examen, nom_examen FROM examen WHERE id_annee = %s ORDER BY id_examen", (id_annee,))
    else:
        cursor.execute("SELECT id_examen, nom_examen FROM examen ORDER BY id_examen")
    
    data = cursor.fetchall()
    conn.close()
    return data

def get_annee_active():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_annee, libelle, actif FROM annee_scolaire WHERE actif = 1 LIMIT 1")
    data = cursor.fetchone()
    conn.close()
    return data