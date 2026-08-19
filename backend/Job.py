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

def run_job():
    db = SessionLocal()
    
    # Salvăm momentul de START (folosim timezone.utc ca să nu mai primim avertismente)
    now = datetime.now(timezone.utc)
    job_record = JobRun(started_at=now, status="running", message="Job started...")
    db.add(job_record)
    db.commit()
    db.refresh(job_record) 

    print(f"[*] Job #{job_record.id} a pornit la {now}")

    try:
        # Simulăm acțiunea
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
        
        # PRINT-ul este acum ÎNAINTE de a închide conexiunea
        print(f"[*] Job #{job_record.id} s-a terminat și a închis conexiunea la DB.\n")
        
        db.close() # Închidem ușa la final de tot

if __name__ == "__main__":
    run_job()