FROM python:3.12-slim

WORKDIR /app

# Copia só o requirements primeiro para otimizar cache do Docker
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Agora copia o restante do código do projeto
COPY . .

# Comando padrão para rodar seu consumer
CMD ["python", "binance_price_consumer.py"]
