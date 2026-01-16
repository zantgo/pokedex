# Makefile para Pokedex Analytics Infrastructure

# Variables
DC = docker compose
SERVICE = web
MANAGE = python manage.py

# Detectar sistema operativo para comandos específicos (Opcional)
OS := $(shell uname)

.PHONY: help start build up migrate test clean stop shell fix-perms

# --- COMANDO PRINCIPAL ---
help: ## Muestra esta ayuda
	@echo "📋 Comandos disponibles para Pokedex Infrastructure:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

start: init-env build migrate up ## Levanta todo el entorno desde cero (Build + Migrate + Up)

# --- PASOS INDIVIDUALES ---
init-env: ## Crea el archivo .env si no existe
	@if [ ! -f .env ]; then \
		echo "⚙️  Creando archivo .env desde ejemplo..."; \
		cp .env.example .env; \
	else \
		echo "✅  Archivo .env ya existe."; \
	fi

build: ## Construye los contenedores
	@echo "🏗️  Construyendo imagen Docker..."
	$(DC) build

migrate: ## Ejecuta las migraciones de base de datos
	@echo "🗄️  Aplicando migraciones..."
	$(DC) run --rm $(SERVICE) $(MANAGE) migrate

up: ## Levanta el servidor
	@echo "🔥  Iniciando servidor en http://localhost:8000"
	$(DC) up

stop: ## Detiene los contenedores
	@echo "🛑  Deteniendo servicios..."
	$(DC) stop

down: ## Detiene y elimina contenedores y redes
	@echo "🗑️  Limpiando recursos Docker..."
	$(DC) down

# --- TESTING Y UTILIDADES ---
test: ## Ejecuta toda la suite de pruebas
	@echo "🧪  Corriendo tests..."
	$(DC) run --rm $(SERVICE) $(MANAGE) test analysis

shell: ## Accede a la terminal del contenedor
	$(DC) exec $(SERVICE) bash

fix-perms: ## (Linux) Arregla permisos de root en archivos generados
	@echo "🐧  Corrigiendo permisos de usuario..."
	sudo chown -R $$USER:$$USER .

clean: down ## Limpia archivos temporales de Python y contenedores
	find . -name "*.pyc" -exec rm -f {} +
	find . -name "__pycache__" -exec rm -rf {} +