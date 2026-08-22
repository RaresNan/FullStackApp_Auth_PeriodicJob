## Rulare cu Docker Compose (Livrabil 2)

Acest proiect este complet containerizat și poate fi rulat folosind Docker Compose. Arhitectura include 4 servicii: Frontend (Nginx), Backend (FastAPI/Uvicorn), Job Periodic (Python script) și Baza de date (PostgreSQL).

### 1. Configurarea variabilelor de mediu
Înainte de a porni aplicația, creați un fișier `.env` la rădăcina proiectului cu următorul conținut (acesta este ignorat de Git pentru securitate):
```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=parolasecreta
POSTGRES_DB=proiect_db
DATABASE_URL=postgresql://admin:parolasecreta@db:5432/proiect_db
SECRET_KEY=cheie_super_secreta_pentru_jwt_local