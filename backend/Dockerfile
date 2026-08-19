# 1. Imaginea de bază
FROM python:3.11-slim

# 2. Director de lucru
WORKDIR /app

# 3. Copiem fișierul requirements (îl luăm din backend când dăm build)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiem scriptul job-ului
COPY Job.py .

# 5. Comanda directă de execuție
CMD ["python", "Job.py"]