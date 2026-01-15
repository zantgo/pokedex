# Dockerfile
FROM python:3.12-slim

# Evita archivos .pyc y buffer en stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalamos dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente
COPY . /app/

# Ajustamos para que ejecute desde src donde está manage.py
WORKDIR /app/src

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]