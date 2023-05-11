from langchain.vectorstores import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
import pinecone


loader = DirectoryLoader("../Data/Main Website Data/pdfs", loader_cls=PyPDFLoader, show_progress=True)
docs = loader.load()

docs = RecursiveCharacterTextSplitter().split_documents(docs)
pinecone.init(api_key="106247f4-0905-40f0-81f0-d0bacc8ff09b", environment="northamerica-northeast1-gcp")
Pinecone.from_documents(embedding=OpenAIEmbeddings(openai_api_key="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"),
                        index_name="hawai-docs",
                        namespace="blog-data",
                        documents=docs)