import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="gestions_scolaires"
)

cursor = db.cursor(dictionary=True)


def get_presences(id_annee=None):
    print(f"🔍 get_presences called with id_annee={id_annee}")  # Debug
    
    query = """
        SELECT 
            p.id,
            p.numero_matricule,
            e.nom,
            e.prenom,
            n.libelle AS niveau,
            f.nom_filiere AS filiere,
            p.type,
            p.motif,
            DATE_FORMAT(p.date_presence, '%Y-%m-%d') AS date_presence,
            p.heure,
            p.created_at
        FROM presence p
        JOIN etudiants e 
            ON p.numero_matricule = e.numero_matricule
        LEFT JOIN niveau n 
            ON e.id_niveau = n.id_niveau
        LEFT JOIN filiere f 
            ON e.id_filiere = f.id_filiere
    """

    params = []

    # 🔥 FILTRE ANNÉE SCOLAIRE
    if id_annee:
        query += " WHERE e.id_annee = %s "
        params.append(id_annee)

    query += " ORDER BY p.id DESC"
    
    print(f"📝 Query: {query}")
    print(f"📝 Params: {params}")

    cursor.execute(query, params)
    results = cursor.fetchall()
    
    print(f"✅ Found {len(results)} records")
    for r in results:
        print(f"   - {r}")
    
    return results


def add_presence(data):
    try:
        cursor.execute("""
            INSERT INTO presence (
                numero_matricule,
                type,
                motif,
                date_presence,
                heure
            )
            VALUES (%s, %s, %s, CURDATE(), CURTIME())
        """, (
            data["numero_matricule"],
            data["type"],
            data.get("motif", "")
        ))

        db.commit()
        return {"message": "OK", "id": cursor.lastrowid}
    except Exception as e:
        print(f"❌ Error in add_presence: {e}")
        return {"error": str(e)}


def delete_presence(id):
    try:
        cursor.execute("DELETE FROM presence WHERE id=%s", (id,))
        db.commit()
        return {"message": "deleted"}
    except Exception as e:
        print(f"❌ Error in delete_presence: {e}")
        return {"error": str(e)}


def update_presence(id, data):
    try:
        cursor.execute("""
            UPDATE presence 
            SET motif = %s, type = %s
            WHERE id = %s
        """, (
            data.get("motif", ""),
            data.get("type", "absence"),
            id
        ))
        db.commit()
        return {"message": "updated"}
    except Exception as e:
        print(f"❌ Error in update_presence: {e}")
        return {"error": str(e)}