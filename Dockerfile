# Imagem base leve
FROM python:3.9-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para bibliotecas de ML/Econometria
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos e instala as bibliotecas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto
COPY . .

# Expondo a porta para o Flask/FastAPI
EXPOSE 8080

# Comando para rodar a aplicação (Ajuste 'app:app' para o seu entrypoint real)
# Para Flask: CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
# Para FastAPI:
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]