# Hawaii-GPT

Hawaii-GPT is a Streamlit application that allows users chat with the contents of green institutes website.

## Features

- **AI Interaction**: Utilizes both LangChain and local AI models for processing and generating responses.
- **Docker Support**: Includes a Dockerfile for easy and consistent deployment.

## Prerequisites

- Docker installed on your machine
- Basic knowledge of Docker and Streamlit if you wish to modify the app

## Installation and Running with Docker

1. **Clone the repository:**

```bash
git clone https://github.com/abdulzain6/Hawaii-GPT.git
cd Hawaii-GPT
```

2. **Build the Docker container:**

```bash
docker build -t hawaii-gpt .
```

3. **Run the application:**

```bash
docker run --net=host  hawaii-gpt 
```


## Usage

- **Interacting with AI**: You can type in queries or prompts, and the AI will respond based on the contents of your uploaded documents.

## Contributing

Your contributions are welcome! Please fork this repository, make your changes, and submit a pull request.
