FROM python:3.9-slim

ARG OPENAI_API_KEY
ARG PINECONE_API_KEY

ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV PINECONE_API_KEY=$PINECONE_API_KEY

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


RUN pip3 install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "llms/main.py", "--server.port=8501", "--server.address=0.0.0.0"]