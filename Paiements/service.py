import mysql.connector
from typing import Optional
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestions_scolaires"
    )


def insert_paiement_single(data):
    """Insère ou met à jour un paiement dans une transaction séparée"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Vérifier si le paiement existe déjà
        if data.get("mois"):
            check_query = """
                SELECT id FROM paiement_frais 
                WHERE numero_matricule = %s 
                AND type_frais = %s 
                AND mois = %s
            """
            cur.execute(check_query, (
                data["numero_matricule"],
                data["type_frais"],
                data["mois"]
            ))
        else:
            check_query = """
                SELECT id FROM paiement_frais 
                WHERE numero_matricule = %s 
                AND type_frais = %s 
                AND mois IS NULL
            """
            cur.execute(check_query, (
                data["numero_matricule"],
                data["type_frais"]
            ))
        
        existing = cur.fetchone()
        cur.close()
        
        cur2 = conn.cursor(dictionary=True)
        
        if existing:
            # Mettre à jour le paiement existant
            update_query = """
                UPDATE paiement_frais 
                SET montant = %s, statut = %s, date_paiement = %s
                WHERE id = %s
            """
            cur2.execute(update_query, (
                float(data["montant"]),
                data.get("statut", "impayé"),
                datetime.now(),
                existing["id"]
            ))
            message = "Paiement mis à jour"
        else:
            # Insérer un nouveau paiement
            insert_query = """
                INSERT INTO paiement_frais
                (numero_matricule, id_niveau, id_filiere, type_frais, mois, montant, statut, date_paiement)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur2.execute(insert_query, (
                data["numero_matricule"],
                int(data["id_niveau"]),
                int(data["id_filiere"]),
                data["type_frais"],
                data.get("mois"),
                float(data["montant"]),
                data.get("statut", "impayé"),
                datetime.now()
            ))
            message = "Nouveau paiement ajouté"
        
        cur2.close()
        conn.commit()
        return message
    
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur insert_paiement_single: {str(e)}")
        raise e
    finally:
        conn.close()


def insert_paiement(data):
    """Insère ou met à jour un paiement (API externe)"""
    try:
        message = insert_paiement_single(data)
        return {"message": message}
    except Exception as e:
        return {"error": str(e)}


def update_paiement(matricule: str, type_frais: str, mois: Optional[str], data: dict):
    """Met à jour un paiement spécifique"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        if mois:
            query = """
                UPDATE paiement_frais 
                SET montant = %s, statut = %s, date_paiement = %s
                WHERE numero_matricule = %s 
                AND type_frais = %s 
                AND mois = %s
            """
            cur.execute(query, (
                data["montant"],
                data["statut"],
                datetime.now(),
                matricule,
                type_frais,
                mois
            ))
        else:
            query = """
                UPDATE paiement_frais 
                SET montant = %s, statut = %s, date_paiement = %s
                WHERE numero_matricule = %s 
                AND type_frais = %s 
                AND mois IS NULL
            """
            cur.execute(query, (
                data["montant"],
                data["statut"],
                datetime.now(),
                matricule,
                type_frais
            ))
        
        conn.commit()
        affected = cur.rowcount
        cur.close()
        
        if affected == 0:
            return {"error": "Paiement non trouvé"}
        return {"message": "Paiement mis à jour"}
    
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur update_paiement: {str(e)}")
        return {"error": str(e)}
    finally:
        conn.close()


def generer_paiements(matricule, id_niveau):
    """Génère les paiements initiaux pour un étudiant"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Récupérer id_filiere depuis etudiants
        cur.execute(
            "SELECT id_filiere FROM etudiants WHERE numero_matricule = %s",
            (matricule,)
        )
        etudiant = cur.fetchone()
        cur.close()

        if not etudiant or not etudiant.get("id_filiere"):
            conn.close()
            return {"error": "Étudiant introuvable ou filière non définie"}

        id_filiere = etudiant["id_filiere"]
        
        cur2 = conn.cursor(dictionary=True)
        cur2.execute(
            "SELECT COUNT(*) as total FROM paiement_frais WHERE numero_matricule = %s",
            (matricule,)
        )
        count = cur2.fetchone()["total"]
        cur2.close()
        
        if count > 0:
            conn.close()
            return {"already": True, "message": "Paiements déjà générés"}

        conn.close()

        # Inscription
        result = insert_paiement_single({
            "numero_matricule": matricule, 
            "id_niveau": id_niveau,
            "id_filiere": id_filiere, 
            "type_frais": "inscription",
            "mois": None, 
            "montant": 50000, 
            "statut": "impayé"
        })
        print(f"✅ Inscription: {result}")

        # Équipements
        for type_frais, montant in [
            ("combinaison", 30000), 
            ("tablier", 20000), 
            ("tenue_fete", 30000)
        ]:
            result = insert_paiement_single({
                "numero_matricule": matricule, 
                "id_niveau": id_niveau,
                "id_filiere": id_filiere, 
                "type_frais": type_frais,
                "mois": None, 
                "montant": montant, 
                "statut": "impayé"
            })
            print(f"✅ {type_frais}: {result}")

        # Écolage 10 mois
        mois_list = ["septembre","octobre","novembre","decembre",
                     "janvier","fevrier","mars","avril","mai","juin"]
        for m in mois_list:
            result = insert_paiement_single({
                "numero_matricule": matricule, 
                "id_niveau": id_niveau,
                "id_filiere": id_filiere, 
                "type_frais": "ecolage",
                "mois": m, 
                "montant": 20000, 
                "statut": "impayé"
            })
            print(f"✅ {m}: {result}")
        
        return {"message": "Paiements générés avec succès"}
    
    except Exception as e:
        print(f"❌ Erreur generer_paiements: {str(e)}")
        return {"error": str(e)}


def get_table_paiements(id_annee=None):
    """Récupère tous les étudiants avec leurs statuts de paiement"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    try:
        # Requête pour récupérer les étudiants avec leurs paiements
        query = """
            SELECT 
                e.numero_matricule,
                e.nom,
                e.id_niveau,
                COALESCE(n.libelle, 'Non défini') AS niveau,
                COALESCE(f.nom_filiere, 'Non défini') AS nom_filiere,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'inscription' 
                          LIMIT 1), 'impayé') AS inscription,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'combinaison' 
                          LIMIT 1), 'impayé') AS combinaison,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'tablier' 
                          LIMIT 1), 'impayé') AS tablier,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'tenue_fete' 
                          LIMIT 1), 'impayé') AS tenue_fete,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'ecolage' AND mois = 'septembre' 
                          LIMIT 1), 'impayé') AS septembre,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'ecolage' AND mois = 'octobre' 
                          LIMIT 1), 'impayé') AS octobre,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'ecolage' AND mois = 'novembre' 
                          LIMIT 1), 'impayé') AS novembre,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'ecolage' AND mois = 'decembre' 
                          LIMIT 1), 'impayé') AS decembre,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'ecolage' AND mois = 'janvier' 
                          LIMIT 1), 'impayé') AS janvier,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'ecolage' AND mois = 'fevrier' 
                          LIMIT 1), 'impayé') AS fevrier,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'ecolage' AND mois = 'mars' 
                          LIMIT 1), 'impayé') AS mars,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'ecolage' AND mois = 'avril' 
                          LIMIT 1), 'impayé') AS avril,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'ecolage' AND mois = 'mai' 
                          LIMIT 1), 'impayé') AS mai,
                
                COALESCE((SELECT statut FROM paiement_frais 
                          WHERE numero_matricule = e.numero_matricule 
                          AND type_frais = 'ecolage' AND mois = 'juin' 
                          LIMIT 1), 'impayé') AS juin
                
            FROM etudiants e
            LEFT JOIN niveau n ON e.id_niveau = n.id_niveau
            LEFT JOIN filiere f ON e.id_filiere = f.id_filiere
        """
        
        # Ajouter le filtre d'année si fourni
        if id_annee:
            query += " WHERE e.id_annee = %s"
            cur.execute(query, (id_annee,))
        else:
            cur.execute(query)
        
        result = cur.fetchall()
        print(f"✅ {len(result)} étudiants récupérés")
        return result
    
    except Exception as e:
        print(f"❌ Erreur dans get_table_paiements: {str(e)}")
        return []
    finally:
        cur.close()
        conn.close()