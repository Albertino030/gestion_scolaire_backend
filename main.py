from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTERS EXISTANTS
from etudiants.router import router as etudiants_router
from Année_scolaire.router import router as annee_router

# MODULE PAIEMENTS
from Paiements.router import router as paiements_router
from Presence.router import router as presence_router

# MODULE EXAMEN
from examen.router import router as examen_router

# MODULE SUIVI FORMATION
from Suivi_formation.router import router as suivi_router
from Dashboard.router import router as dashboard_router

# 🔥 NOUVEAU MODULE AUTHENTIFICATION
from utilisateurs.router import router as auth_router

app = FastAPI(title="Gestion Scolaire API")

# =========================
# CORS CONFIG - CORRIGÉE
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://gestion-scolaire-frontend.vercel.app",
        "https://gestion-scolaire-frontend-d2contu9o.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # ← AJOUTER CETTE LIGNE
)

# =========================
# ROUTERS
# =========================

# Routes publiques (authentification)
app.include_router(auth_router)

# Routes protégées (à sécuriser avec middleware si besoin)
app.include_router(etudiants_router)
app.include_router(annee_router)
app.include_router(paiements_router)
app.include_router(presence_router)
app.include_router(examen_router)
app.include_router(suivi_router)
app.include_router(dashboard_router)

# =========================
# TEST API
# =========================
@app.get("/")
def home():
    return {
        "message": "API OK - Gestion Scolaire",
        "version": "1.0.0",
        "modules": [
            "authentification",
            "etudiants",
            "annee_scolaire",
            "paiements",
            "presence",
            "examen",
            "suivi_formation",
            "dashboard"
        ],
        "endpoints": {
            "auth": "/auth/login, /auth/verify, /auth/profile",
            "etudiants": "/etudiants",
            "annees": "/annees",
            "paiements": "/paiements",
            "presence": "/presence",
            "examen": "/examen",
            "suivi": "/suivi-formation",
            "dashboard": "/dashboard"
        }
    }

# =========================
# LANCEMENT (optionnel)
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # ← Changer 127.0.0.1 en 0.0.0.0