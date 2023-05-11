import pinecone
import concurrent.futures
import langchain
import json
import pandas as pd

from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.vectorstores import Pinecone
from langchain.prompts import PromptTemplate
from langchain import SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from tools import BlogSearch
from database_manager import BlogPostManager
from peewee import SqliteDatabase
from langchain.agents import create_pandas_dataframe_agent
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents.agent_toolkits.json.prompt import JSON_SUFFIX
from langchain.schema import Document
from langchain.cache import SQLiteCache
from prompt import SQL_PREFIX, question_prompt, SQL_SUFFIX, PANDAS_SUFFIX

#langchain.llm_cache = SQLiteCache(database_path=".langchain.db")

class ChatHawaii:
    template = """You are a HawaiiGPT,
You answer questions with details related to Hawaii which may include law, news and much more using the provided context, 
You also have to take input from the response of the data analyst and thre data scientist who will help you answer the questions. 
You will also take into account the input of the researcher provided. You may also use prior knowledge if needed.

======
Context: {summaries}
======
======
Data analyst: {sql_expert_response}
======
Researcher: {researcher}
======
Data Scientist Joe: {json_expert}
======
Question: {question}
======

Rules:
1. Be nice
2. Don't disclose the context and the expert reponses

Let's work this out in a step by step way to be sure we have the right answer which follows all the rules:
"""

    def __init__(
        self,
        database_path: str,
        llm,
        pinecone_api_key: str,
        pinecone_environment: str,
        blog_post_manager: BlogPostManager,
        embeddings: OpenAIEmbeddings,
        index_name: str,
        namespace: str,
        csv_path: str
    ) -> None:
        self.database_path = database_path
        self.embeddings = embeddings
        self.csv_path = csv_path
        self.llm = llm
        self.index_name = index_name
        self.namespace = namespace
        pinecone.init(
            api_key=pinecone_api_key,
            environment=pinecone_environment,
        )
        self.blog_post_manager = blog_post_manager
        self.blog_search = BlogSearch(blog_post_manager)
        self.CHAT_PROMPT = PromptTemplate(
            template=self.template,
            input_variables=[
                "question",
                "summaries",
                "sql_expert_response",
                "researcher",
                "json_expert",
            ],
        )

    def get_sql_chain_result(self, question: str):
        try:
            db = SQLDatabase.from_uri(f"sqlite:///{self.database_path}")
            toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)

            agent_executor = create_sql_agent(
                llm=self.llm,
                toolkit=toolkit,
                verbose=True,
                prefix=SQL_PREFIX,
                suffix=SQL_SUFFIX
                
            )
            return agent_executor.run(question)
        except Exception as e:
            print(e)
            return str(e)

    def _reduce_tokens_below_limit(
        self, docs: list, limit: int, split: bool, chunck_size: int = 1000
    ):
        if split:
            docs = RecursiveCharacterTextSplitter(chunk_size=chunck_size).split_documents(docs)
        num_docs = len(docs)
        tokens = [len(doc.page_content) for doc in docs]
        token_count = sum(tokens[:num_docs])
        while token_count > limit:
            num_docs -= 1
            token_count -= tokens[num_docs]

        return docs[:num_docs]

    def chat(self, question: str) -> str:
        vectorstore = Pinecone.from_existing_index(
            embedding=self.embeddings,
            index_name=self.index_name,
            namespace=self.namespace,
        )
        qa = load_qa_with_sources_chain(
            self.llm,
            chain_type="stuff",
            prompt=self.CHAT_PROMPT,
            verbose=True,
        )

        seacch_data = self.get_fuzzy_search_data(question, answer_limit=2)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(
                executor.map(
                    lambda x: x[0](*x[1:]),
                    [
                        (
                            self.refine_input_documents_data,
                            question,
                            [
                                Document(
                                    page_content=json.dumps(data),
                                    metadata={"source": "search"},
                                )
                                for data in seacch_data["posts"]
                            ],
                        ),
                        (self.get_sql_chain_result, question),
                        (self.csv_agent_result, question, self.csv_path),
                    ],
                )
            )

        refined_answer, sql_chain_result, json_chain_result = results
        result = qa(
            {
                "question": question,
                "input_documents": self._reduce_tokens_below_limit(
                    vectorstore.similarity_search(query=question), 3000, True, 1000
                ),
                "sql_expert_response": sql_chain_result[:1000],
                "json_expert": json_chain_result[:1000],
                "researcher": refined_answer[:2800],
            }
        )
        return result["output_text"]

    def refine_input_documents_data(self, query: str, input_documents: list) -> str:
        try:
            if not input_documents:
                return "No data found"
            chain = load_qa_with_sources_chain(
                self.llm,
                chain_type="refine",
                question_prompt=question_prompt,
                verbose=True,
            )
            result = chain(
                {"input_documents": input_documents, "question": query},
                return_only_outputs=True,
            )
            return result["output_text"]
        except:
            return ""

    def get_fuzzy_search_data(self, query: str, answer_limit: int = 6) -> list[str]:
        return self.blog_search.execute_tool(
            question=query, llm=self.llm, limit_per_call=answer_limit // 2
        )

    def csv_agent_result(self, query: str, data_path: str) -> str:
        try:
            df = pd.read_csv(data_path)
            csv_agent_executor = create_pandas_dataframe_agent(
                self.llm,
                df,
                verbose=True,
                suffix=PANDAS_SUFFIX
            )
            return csv_agent_executor.run(query)
        except Exception as e:
            print(e)
            return str(e)


if __name__ == "__main__":
    chat = ChatHawaii(
        "blog_posts.db",
        ChatOpenAI(
            openai_api_key="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",
            temperature=1,
            model_name="gpt-4",
        ),
        pinecone_api_key="106247f4-0905-40f0-81f0-d0bacc8ff09b",
        pinecone_environment="northamerica-northeast1-gcp",
        blog_post_manager=BlogPostManager(SqliteDatabase("blog_posts.db")),
        embeddings=OpenAIEmbeddings(
            openai_api_key="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"
        ),
        index_name="hawai-docs",
        namespace="blog-data",
        csv_path="output.csv"
    )
    

    print(chat.chat("Write an op-ed for a local newspaper in the voice of Joe Kent, executive vice president of the Grassroot Institute of Hawaii, about how Hawaii's governor Josh Green, a medical doctor himself, should sign the Interstate Medical Licensure Compact, to allow more doctors from other states to more easily work in Hawaii. Please write it in a way that would be able to pass AI-detection software."))
