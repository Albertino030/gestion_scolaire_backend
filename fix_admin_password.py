import bcrypt
import mysql.connector

# Connexion à la base de données
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="gestions_scolaires"
)

cursor = conn.cursor()

# Générer un nouveau hash pour "admin123"
password = "admin123"
salt = bcrypt.gensalt(rounds=12)
new_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

# Mettre à jour le mot de passe de l'admin
cursor.execute(
    "UPDATE utilisateurs SET password = %s WHERE email = %s",
    (new_hash.decode('utf-8'), "admin@example.com")
)

conn.commit()
print("✅ Mot de passe admin mis à jour avec succès!")
print(f"📧 Email: admin@example.com")
print(f"🔑 Mot de passe: admin123")
print(f"🔐 Nouveau hash: {new_hash.decode('utf-8')}")

cursor.close()
conn.close()