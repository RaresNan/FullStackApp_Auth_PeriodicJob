import os
import random
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# Încărcăm variabilele de mediu
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Conexiune proprie la DB
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definiția tabelei
class JobRun(Base):
    __tablename__ = "job_runs"
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String)
    message = Column(String)

# Creăm tabela automat dacă nu există în baza de date
Base.metadata.create_all(bind=engine)

def run_job():
    db = SessionLocal()
    
    now = datetime.now(timezone.utc)
    job_record = JobRun(started_at=now, status="running", message="Job started...")
    db.add(job_record)
    db.commit()
    db.refresh(job_record) 

    print(f"[*] Job #{job_record.id} a pornit la {now}")

    try:
        # Simulăm acțiunea normală cu succes
        time.sleep(2)
        random_number = random.randint(1, 100)
        
        rezultat = f"Acțiune completă cu succes. Număr norocos: {random_number}"
        print(f"[+] {rezultat}")

        job_record.status = "success"
        job_record.message = rezultat

    except Exception as e:
        eroare = f"Eroare întâmpinată: {str(e)}"
        print(f"[-] {eroare}")
        job_record.status = "failed"
        job_record.message = eroare

    finally:
        job_record.finished_at = datetime.now(timezone.utc)
        db.commit()
        
        print(f"[*] Job #{job_record.id} s-a terminat și a închis conexiunea la DB.\n")
        
        db.close() 

if __name__ == "__main__":
    print("[*] Asteptam 5 secunde pentru initializarea bazei de date...")
    time.sleep(5)
    
    while True:
        run_job()
        print("[*] Scheduler: Asteptam 60 secunde pana la urmatoarea rulare...\n")
        time.sleep(60)