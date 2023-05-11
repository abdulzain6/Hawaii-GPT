import streamlit as st
from chat import ChatHawaii, ChatOpenAI, BlogPostManager, OpenAIEmbeddings, SqliteDatabase

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

st.title("AI Chat")
prompt = st.text_input("You: ", "")
if prompt:
    response = chat.chat(prompt)
    st.text_area("AI: " ,value= response, max_chars=None, height=700)
