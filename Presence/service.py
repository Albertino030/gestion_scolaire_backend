# presence/service.py
import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'gestions_scolaires'),
        port=int(os.environ.get('DB_PORT', 3306))
    )


def get_presences(id_annee=None):
    print(f"🔍 get_presences called with id_annee={id_annee}")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
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

        if id_annee:
            query += " WHERE e.id_annee = %s "
            params.append(id_annee)

        query += " ORDER BY p.id DESC"
        
        print(f"📝 Query: {query}")
        print(f"📝 Params: {params}")

        cursor.execute(query, params)
        results = cursor.fetchall()
        
        print(f"✅ Found {len(results)} records")
        return results
    finally:
        cursor.close()
        conn.close()


def add_presence(data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
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

        conn.commit()
        return {"message": "OK", "id": cursor.lastrowid}
    except Exception as e:
        print(f"❌ Error in add_presence: {e}")
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()


def delete_presence(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("DELETE FROM presence WHERE id=%s", (id,))
        conn.commit()
        return {"message": "deleted"}
    except Exception as e:
        print(f"❌ Error in delete_presence: {e}")
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()


def update_presence(id, data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
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
        conn.commit()
        return {"message": "updated"}
    except Exception as e:
        print(f"❌ Error in update_presence: {e}")
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()