FROM python:3.9-slim

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
ENV PINECONE_API_KEY=${{ secrets.PINECONE_API_KEY }}


RUN pip3 install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "llms/main.py", "--server.port=8501", "--server.address=0.0.0.0"]