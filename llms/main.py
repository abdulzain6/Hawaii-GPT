import streamlit as st
from chat import ChatHawaii, ChatOpenAI, BlogPostManager, OpenAIEmbeddings, SqliteDatabase
from creds import OPENAI_API_KEY, PINECONE_API_KEY
st.set_theme('dark')

chat = ChatHawaii(
        "blog_posts.db",
        ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            temperature=1,
            model_name="gpt-4",
        ),
        pinecone_api_key=PINECONE_API_KEY,
        pinecone_environment="northamerica-northeast1-gcp",
        blog_post_manager=BlogPostManager(SqliteDatabase("blog_posts.db")),
        embeddings=OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY
        ),
        index_name="hawai-docs",
        namespace="blog-data",
        csv_path="output.csv"
    )

st.title("AI Chat")
if prompt := st.text_input("You: ", ""):
    response = chat.chat(prompt)
    st.text_area("AI: " ,value= response, max_chars=None, height=700)
