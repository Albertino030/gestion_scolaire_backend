import mysql.connector
import os
from mysql.connector import Error

db = mysql.connector.connect(
    host=os.environ.get('DB_HOST', 'localhost'),
    user=os.environ.get('DB_USER', 'root'),
    password=os.environ.get('DB_PASSWORD', ''),
    database=os.environ.get('DB_NAME', 'gestions_scolaires'),
    port=int(os.environ.get('DB_PORT', 3306))
)

cursor = db.cursor(dictionary=True)


def clean_dates(data):
    """Convertir les dates vides en None pour éviter les erreurs MySQL"""
    for field in ["date_inscription", "date_naissance"]:
        if data.get(field) == "":
            data[field] = None
    return data


def map_text_to_ids(data):
    """Convertir les noms de filière et niveau en IDs"""
    # FILIERE
    if data.get("filiere_choisie"):
        cursor.execute(
            "SELECT id_filiere FROM filiere WHERE LOWER(nom_filiere) = LOWER(%s)",
            (data['filiere_choisie'],)
        )
        f = cursor.fetchone()
        data["id_filiere"] = f["id_filiere"] if f else None
        
        if not f:
            cursor.execute(
                "SELECT id_filiere FROM filiere WHERE LOWER(nom_filiere) LIKE LOWER(%s)",
                (f"%{data['filiere_choisie']}%",)
            )
            f = cursor.fetchone()
            data["id_filiere"] = f["id_filiere"] if f else None

    # NIVEAU
    if data.get("niveau"):
        cursor.execute(
            "SELECT id_niveau FROM niveau WHERE LOWER(libelle) = LOWER(%s)",
            (data['niveau'],)
        )
        n = cursor.fetchone()
        data["id_niveau"] = n["id_niveau"] if n else None
        
        if not n:
            cursor.execute(
                "SELECT id_niveau FROM niveau WHERE LOWER(libelle) LIKE LOWER(%s)",
                (f"%{data['niveau']}%",)
            )
            n = cursor.fetchone()
            data["id_niveau"] = n["id_niveau"] if n else None

    return data


def get_etudiants(id_annee=None):
    query = """
        SELECT 
            e.numero_matricule,
            e.date_inscription,
            e.nom,
            e.prenom,
            e.genre,
            e.date_naissance,
            e.lieu_naissance,
            e.nom_pere,
            e.nom_mere,
            e.nom_tuteur,
            e.adresse,
            e.telephone,
            e.projet_professionnel,
            e.id_annee,
            f.nom_filiere,
            n.libelle AS niveau,
            a.libelle AS annee_scolaire
        FROM etudiants e
        LEFT JOIN filiere f ON e.id_filiere = f.id_filiere
        LEFT JOIN niveau n ON e.id_niveau = n.id_niveau
        LEFT JOIN annee_scolaire a ON e.id_annee = a.id_annee
    """
    params = ()
    if id_annee:
        query += " WHERE e.id_annee = %s"
        params = (id_annee,)

    cursor.execute(query, params)
    return cursor.fetchall()


def get_etudiant(numero_matricule: str):
    """Récupérer un étudiant par son matricule"""
    query = """
        SELECT 
            e.numero_matricule,
            e.date_inscription,
            e.nom,
            e.prenom,
            e.genre,
            e.date_naissance,
            e.lieu_naissance,
            e.nom_pere,
            e.nom_mere,
            e.nom_tuteur,
            e.adresse,
            e.telephone,
            e.projet_professionnel,
            e.id_annee,
            e.id_filiere,
            e.id_niveau,
            f.nom_filiere,
            n.libelle AS niveau
        FROM etudiants e
        LEFT JOIN filiere f ON e.id_filiere = f.id_filiere
        LEFT JOIN niveau n ON e.id_niveau = n.id_niveau
        WHERE e.numero_matricule = %s
    """
    cursor.execute(query, (numero_matricule,))
    result = cursor.fetchone()
    
    if not result:
        return {"error": "Étudiant non trouvé"}
    
    return result


def add_etudiant(data):
    try:
        data = clean_dates(data)
        data = map_text_to_ids(data)

        if not data.get("id_annee"):
            data["id_annee"] = get_id_annee_active()

        query = """
            INSERT INTO etudiants (
                numero_matricule, date_inscription, nom, prenom, genre,
                date_naissance, lieu_naissance, nom_pere, nom_mere, nom_tuteur,
                adresse, telephone, id_filiere, id_niveau, id_annee, projet_professionnel
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(query, (
            data.get("numero_matricule"),
            data.get("date_inscription"),
            data.get("nom"),
            data.get("prenom"),
            data.get("genre"),
            data.get("date_naissance"),
            data.get("lieu_naissance"),
            data.get("nom_pere"),
            data.get("nom_mere"),
            data.get("nom_tuteur"),
            data.get("adresse"),
            data.get("telephone"),
            data.get("id_filiere"),
            data.get("id_niveau"),
            data.get("id_annee"),
            data.get("projet_professionnel")
        ))
        db.commit()
        return {"message": "Étudiant ajouté avec succès"}
    except Error as err:
        db.rollback()
        return {"error": f"Erreur MySQL: {err}"}


def delete_etudiant(numero_matricule):
    try:
        cursor.execute(
            "DELETE FROM etudiants WHERE numero_matricule = %s",
            (numero_matricule,)
        )
        db.commit()
        return {"message": "Étudiant supprimé avec succès"}
    except Error as err:
        db.rollback()
        return {"error": f"Erreur MySQL: {err}"}


def update_etudiant(numero_matricule, data):
    try:
        data = clean_dates(data)
        data = map_text_to_ids(data)
        
        if not data.get("id_annee"):
            data["id_annee"] = get_id_annee_active()
        
        cursor.execute("SELECT id_filiere, id_niveau FROM etudiants WHERE numero_matricule = %s", (numero_matricule,))
        existing = cursor.fetchone()
        
        if existing:
            if not data.get("id_filiere"):
                data["id_filiere"] = existing["id_filiere"]
            if not data.get("id_niveau"):
                data["id_niveau"] = existing["id_niveau"]
        
        query = """
            UPDATE etudiants
            SET
                date_inscription=%s, nom=%s, prenom=%s, genre=%s,
                date_naissance=%s, lieu_naissance=%s, nom_pere=%s, nom_mere=%s,
                nom_tuteur=%s, adresse=%s, telephone=%s, id_filiere=%s,
                id_niveau=%s, id_annee=%s, projet_professionnel=%s
            WHERE numero_matricule=%s
        """
        cursor.execute(query, (
            data.get("date_inscription"),
            data.get("nom"),
            data.get("prenom"),
            data.get("genre"),
            data.get("date_naissance"),
            data.get("lieu_naissance"),
            data.get("nom_pere"),
            data.get("nom_mere"),
            data.get("nom_tuteur"),
            data.get("adresse"),
            data.get("telephone"),
            data.get("id_filiere"),
            data.get("id_niveau"),
            data.get("id_annee"),
            data.get("projet_professionnel"),
            numero_matricule
        ))
        db.commit()
        return {"message": "Étudiant modifié avec succès"}
    except Error as err:
        db.rollback()
        return {"error": f"Erreur MySQL: {err}"}


def get_id_annee_active():
    cursor.execute("SELECT id_annee FROM annee_scolaire WHERE actif = 1 LIMIT 1")
    result = cursor.fetchone()
    return result["id_annee"] if result else None