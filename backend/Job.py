import os
import random
import time
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Încărcăm variabilele de mediu pentru a lua conexiunea la baza de date
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Conexiune proprie la DB (separată de backend-ul web)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Definiția tabelei pentru ca acest script izolat să o recunoască
class JobRun(Base):
    __tablename__ = "job_runs"
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String)
    message = Column(String)

def run_job():
    db = SessionLocal()
    
    # PASUL A: Salvăm momentul de START
    now = datetime.utcnow()
    job_record = JobRun(started_at=now, status="running", message="Job started...")
    db.add(job_record)
    db.commit()
    db.refresh(job_record) # Luăm ID-ul din baza de date

    print(f"[*] Job #{job_record.id} a pornit la {now}")

    try:
        # PASUL B: Facem acțiunea (simulăm ceva ce durează 2 secunde + generăm un număr)
        time.sleep(2)
        random_number = random.randint(1, 100)
        
        rezultat = f"Acțiune completă cu succes. Număr norocos: {random_number}"
        print(f"[+] {rezultat}")

        # Actualizăm înregistrarea cu succesul
        job_record.status = "success"
        job_record.message = rezultat

    except Exception as e:
        # PASUL C: Dacă ceva crapă, prindem eroarea în loc să oprim scriptul brusc
        eroare = f"Eroare întâmpinată: {str(e)}"
        print(f"[-] {eroare}")
        job_record.status = "failed"
        job_record.message = eroare

    finally:
        # PASUL D: Se execută la final, fie că a mers, fie că a dat eroare
        job_record.finished_at = datetime.utcnow()
        db.commit()
        db.close()
        print(f"[*] Job #{job_record.id} s-a terminat și a închis conexiunea la DB.\n")

# Aici este punctul de intrare (de unde pornește scriptul când îl rulezi)
if __name__ == "__main__":
    run_job()