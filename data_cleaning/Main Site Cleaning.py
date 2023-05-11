import csv
import os
import pandas as pd
import sqlite3
import pickle
import pinecone

from lxml.html import fromstring
from datetime import datetime
from langchain.document_loaders import CSVLoader
from langchain.vectorstores import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings

def extract_year(date_str):
    date_obj = datetime.strptime(date_str, "%B %d, %Y")
    return date_obj.year

def extract_html_files(older_than_year: int):
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Author', 'Title', 'Date Published', 'About', 'Post'])

        # Loop through the files in the directory
        files = os.listdir("Data/Main Website Data/pages")
        for file in files:
            path = os.path.join('Data/Main Website Data/pages', file)
            with open(path) as fp:
                try:
                    content = fp.read()
                    page = fromstring(content)
                    author = page.xpath('//li[@itemprop = "author"]')[0].text_content().replace("By", "").strip()
                    title = page.xpath('//h1[contains(@class, "heading-title")]')[0].text_content().strip()
                    datepublished = page.xpath('//li[@itemprop = "datePublished"]')[0].text_content().strip()
                    about = page.xpath('//li[@itemprop = "about"]')[0].text_content().strip()
                    post = page.xpath('//div[@data-widget_type = "theme-post-content.default"]')[0].text_content().strip()
                except Exception:
                    continue

                year = extract_year(datepublished)

                if year >= older_than_year:
                    writer.writerow([author, title, datepublished, about, post])
                    print(author, datepublished)
            
def df_to_sql():
    # Create a sample DataFrame
    df = pd.read_csv("../Data/Main Website Data/csv/output.csv")
    df.columns = ["author", "title", "date_published", "about", "post"]
    conn = sqlite3.connect('blog_posts.db')

    df.to_sql('blog_posts', conn, if_exists='replace', index=True, index_label="id")

    conn.close()


if __name__ == "__main__":
    loader = CSVLoader(file_path="/home/zain/hawaiiGPT/Data/Main Website Data/csv/output.csv")
    docs = loader.load()
    spliter = RecursiveCharacterTextSplitter(chunk_size=4000)
    docs = spliter.split_documents(docs)
    with open("MainSite.pkl", "wb") as fp:
        pickle.dump(docs, fp)
    
    pinecone.init(api_key="106247f4-0905-40f0-81f0-d0bacc8ff09b", environment="northamerica-northeast1-gcp")
    Pinecone.from_documents(embedding=OpenAIEmbeddings(openai_api_key="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"),
                            index_name="hawai-docs",
                            namespace="blog-data",
                            documents=docs)