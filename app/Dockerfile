FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

ENV MODEL_DIR=model
ENV DEVICE=cpu
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "summarization_app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
