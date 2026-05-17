# utilisateurs/service.py - Version complète avec email intégré
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import bcrypt
import jwt
import os
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from .model import User, UserResponse, UserLogin, UserRegister

# Configuration JWT
SECRET_KEY = "votre_secret_key_tres_securisee_a_changer"  # À mettre dans variables d'environnement
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 heures
RESET_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes

# Configuration Email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "albertinochristophe030@gmail.com"
EMAIL_PASSWORD = "nrfcgniaohtenvfy"
FROM_NAME = "CFP DonBosco"
FRONTEND_URL = "http://localhost:5173"

class DatabaseConnection:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'database': 'gestions_scolaires',
            'user': 'root',
            'password': '',
            'port': 3306
        }
    
    def get_connection(self):
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"Erreur de connexion: {e}")
            return None

class EmailService:
    """Service d'envoi d'emails intégré"""
    
    @staticmethod
    def send_password_reset_email(to_email: str, reset_link: str) -> bool:
        """Envoie un email de réinitialisation de mot de passe"""
        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{FROM_NAME} <{EMAIL_ADDRESS}>"
            msg['To'] = to_email
            msg['Subject'] = "Réinitialisation de votre mot de passe - CFP Don Bosco"
            
            # Version texte
            text_content = f"""
            Bonjour,
            
            Vous avez demandé à réinitialiser votre mot de passe pour votre compte CFP Don Bosco.
            
            Cliquez sur le lien ci-dessous pour réinitialiser votre mot de passe :
            {reset_link}
            
            Ce lien est valable pendant 30 minutes.
            
            Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
            
            Cordialement,
            L'équipe CFP Don Bosco
            """
            
            # Version HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px; }}
                    .header {{ text-align: center; padding: 20px 0; background: linear-gradient(135deg, #1a3a6e, #2563eb); border-radius: 10px 10px 0 0; color: white; }}
                    .content {{ padding: 30px; background: white; border-radius: 10px; margin-top: 20px; }}
                    .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #1a3a6e, #2563eb); color: white; text-decoration: none; border-radius: 25px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>CFP Don Bosco</h2>
                        <p>Centre de Formation Professionnelle</p>
                    </div>
                    <div class="content">
                        <h3>Réinitialisation de votre mot de passe</h3>
                        <p>Bonjour,</p>
                        <p>Vous avez demandé à réinitialiser votre mot de passe pour votre compte CFP Don Bosco.</p>
                        <p style="text-align: center;">
                            <a href="{reset_link}" class="button">Réinitialiser mon mot de passe</a>
                        </p>
                        <p>Ou copiez ce lien dans votre navigateur :</p>
                        <p style="background: #f0f0f0; padding: 10px; border-radius: 5px; word-break: break-all;">
                            {reset_link}
                        </p>
                        <p><strong>Ce lien est valable pendant 30 minutes.</strong></p>
                        <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
                        <p>Cordialement,<br>L'équipe CFP Don Bosco</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 CFP Don Bosco - Tous droits réservés</p>
                        <p>Ceci est un email automatique, merci de ne pas y répondre.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Attacher les versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Envoyer l'email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
            
            print(f"Email envoyé à {to_email}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")
            return False

class UserService:
    def __init__(self):
        self.db = DatabaseConnection()
        self.email_service = EmailService()
        # Créer la table password_resets si elle n'existe pas
        self._create_password_resets_table()
    
    def _create_password_resets_table(self):
        """Crée la table pour les tokens de réinitialisation si elle n'existe pas"""
        connection = self.db.get_connection()
        if not connection:
            return
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_resets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(150) NOT NULL,
                    token VARCHAR(255) NOT NULL,
                    expires_at DATETIME NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_token (token),
                    INDEX idx_email (email)
                )
            """)
            connection.commit()
        except Error as e:
            print(f"Erreur création table password_resets: {e}")
        finally:
            cursor.close()
            connection.close()
    
    def hash_password(self, password: str) -> str:
        """Hache un mot de passe avec bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, user: Dict[str, Any]) -> str:
        """Crée un token JWT"""
        payload = {
            'user_id': user['id'],
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def generate_reset_token(self) -> str:
        """Génère un token aléatoire pour la réinitialisation"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    
    def register_user(self, user_data: UserRegister) -> Optional[Dict[str, Any]]:
        """Inscrit un nouvel utilisateur"""
        connection = self.db.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Vérifier si l'email existe déjà
            cursor.execute("SELECT id FROM utilisateurs WHERE email = %s", (user_data.email,))
            if cursor.fetchone():
                return None
            
            # Hacher le mot de passe
            hashed_password = self.hash_password(user_data.password)
            
            # Insérer le nouvel utilisateur
            query = """
                INSERT INTO utilisateurs (nom, prenom, email, password, role, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                user_data.nom,
                user_data.prenom,
                user_data.email,
                hashed_password,
                user_data.role,
                1,  # is_active = True
                datetime.now()
            ))
            connection.commit()
            
            # Récupérer l'utilisateur créé
            user_id = cursor.lastrowid
            cursor.execute("""
                SELECT id, nom, prenom, email, role, is_active, last_login, created_at 
                FROM utilisateurs WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()
            
            return user
            
        except Error as e:
            print(f"Erreur inscription: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def create_password_reset_token(self, email: str) -> Optional[str]:
        """Crée un token de réinitialisation pour un email"""
        connection = self.db.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            
            # Vérifier si l'email existe
            cursor.execute("SELECT id FROM utilisateurs WHERE email = %s", (email,))
            if not cursor.fetchone():
                return None
            
            # Générer le token
            token = self.generate_reset_token()
            expires_at = datetime.now() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
            
            # Supprimer les anciens tokens non utilisés
            cursor.execute("DELETE FROM password_resets WHERE email = %s AND used = FALSE", (email,))
            
            # Insérer le nouveau token
            cursor.execute("""
                INSERT INTO password_resets (email, token, expires_at)
                VALUES (%s, %s, %s)
            """, (email, token, expires_at))
            connection.commit()
            
            return token
            
        except Error as e:
            print(f"Erreur création token: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def send_reset_password_email(self, email: str, reset_link: str) -> bool:
        """Envoie l'email de réinitialisation"""
        return self.email_service.send_password_reset_email(email, reset_link)
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Réinitialise le mot de passe avec un token valide"""
        connection = self.db.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Vérifier le token
            cursor.execute("""
                SELECT * FROM password_resets 
                WHERE token = %s AND used = FALSE AND expires_at > %s
            """, (token, datetime.now()))
            
            reset_request = cursor.fetchone()
            if not reset_request:
                return False
            
            # Hacher le nouveau mot de passe
            hashed_password = self.hash_password(new_password)
            
            # Mettre à jour le mot de passe
            cursor.execute("""
                UPDATE utilisateurs SET password = %s, updated_at = %s
                WHERE email = %s
            """, (hashed_password, datetime.now(), reset_request['email']))
            
            # Marquer le token comme utilisé
            cursor.execute("UPDATE password_resets SET used = TRUE WHERE id = %s", (reset_request['id'],))
            
            connection.commit()
            return True
            
        except Error as e:
            print(f"Erreur réinitialisation: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[Dict[str, Any]]:
        """Authentifie un utilisateur"""
        connection = self.db.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM utilisateurs WHERE email = %s AND is_active = 1"
            cursor.execute(query, (login_data.email,))
            user = cursor.fetchone()
            
            if user and self.verify_password(login_data.password, user['password']):
                # Mettre à jour last_login
                update_query = "UPDATE utilisateurs SET last_login = %s WHERE id = %s"
                cursor.execute(update_query, (datetime.now(), user['id']))
                connection.commit()
                
                # Créer le token
                token = self.create_access_token(user)
                
                return {
                    'access_token': token,
                    'token_type': 'bearer',
                    'user': {
                        'id': user['id'],
                        'nom': user['nom'],
                        'prenom': user['prenom'],
                        'email': user['email'],
                        'role': user['role'],
                        'is_active': user['is_active'],
                        'last_login': user['last_login']
                    }
                }
            return None
        except Error as e:
            print(f"Erreur: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son ID"""
        connection = self.db.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id, nom, prenom, email, role, is_active, last_login FROM utilisateurs WHERE id = %s"
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            return user
        except Error as e:
            print(f"Erreur: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change le mot de passe d'un utilisateur"""
        connection = self.db.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor(dictionary=True)
            # Vérifier l'ancien mot de passe
            query = "SELECT password FROM utilisateurs WHERE id = %s"
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            
            if user and self.verify_password(current_password, user['password']):
                # Mettre à jour avec le nouveau mot de passe
                new_hashed_password = self.hash_password(new_password)
                update_query = "UPDATE utilisateurs SET password = %s, updated_at = %s WHERE id = %s"
                cursor.execute(update_query, (new_hashed_password, datetime.now(), user_id))
                connection.commit()
                return True
            return False
        except Error as e:
            print(f"Erreur: {e}")
            return False
        finally:
            cursor.close()
            connection.close()