# utilisateurs/router.py
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .model import UserLogin, Token, ChangePassword, UserRegister, ForgotPasswordRequest, ResetPasswordRequest
from .service import UserService

router = APIRouter(prefix="/auth", tags=["Authentification"])
security = HTTPBearer()
user_service = UserService()

@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    """Authentifie un utilisateur et retourne un token JWT"""
    result = user_service.authenticate_user(user_login)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result

@router.post("/register")
async def register(user_data: UserRegister):
    """Inscription d'un nouvel utilisateur"""
    result = user_service.register_user(user_data)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    return {
        "message": "Inscription réussie ! Vous pouvez maintenant vous connecter.",
        "user": result
    }

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    """Envoie un lien de réinitialisation du mot de passe par email"""
    # Créer le token de réinitialisation
    token = user_service.create_password_reset_token(request.email)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun compte trouvé avec cet email"
        )
    
    # Créer le lien de réinitialisation
    reset_link = f"http://localhost:5173/?reset=true&token={token}"
    
    # Envoyer l'email en arrière-plan
    background_tasks.add_task(user_service.send_reset_password_email, request.email, reset_link)
    
    return {
        "message": "Un lien de réinitialisation a été envoyé à votre adresse email",
        "success": True
    }

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Réinitialise le mot de passe avec un token valide"""
    success = user_service.reset_password(request.token, request.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token invalide ou expiré"
        )
    
    return {"message": "Mot de passe réinitialisé avec succès"}

@router.get("/verify")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifie la validité du token JWT"""
    token = credentials.credentials
    payload = user_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_service.get_user_by_id(payload['user_id'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
        )
    
    return {
        "valid": True,
        "user": user
    }

@router.get("/profile")
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Récupère le profil de l'utilisateur connecté"""
    token = credentials.credentials
    payload = user_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
        )
    
    user = user_service.get_user_by_id(payload['user_id'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )
    
    return user

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Change le mot de passe de l'utilisateur"""
    token = credentials.credentials
    payload = user_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
        )
    
    success = user_service.change_password(
        payload['user_id'],
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel incorrect",
        )
    
    return {"message": "Mot de passe changé avec succès"}