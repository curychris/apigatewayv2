# Gunakan image Python 3.13 sebagai base
FROM python:3.13-slim

# Atur working directory di dalam container
WORKDIR /app

# Salin file requirements.txt terlebih dahulu (untuk caching layer)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh isi proyek ke dalam working directory container
COPY . .

# Buka port yang digunakan Flask (default 5000)
EXPOSE 5000

# Jalankan aplikasi Flask
CMD ["python", "app.py"]
