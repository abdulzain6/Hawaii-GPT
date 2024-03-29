import os
import random
import scrapy
from urllib.parse import urlparse

class NewsSiteSpiderSpider(scrapy.Spider):
    name = "news_site_spider"
    dom = ["www.civilbeat.org"]
    start_urls = ["http://www.civilbeat.org/", "https://www.civilbeat.org/category/hawaii-beat/page/1028/"]
    visited = {url.strip() for url in open("visited_urlso.txt").readlines()}

    def parse(self, response):        
        if response.url in self.visited:
            return
        else:
            self.visited.add(response.url)
            
        if urlparse(response.url).hostname not in self.dom:
            return
            
            
        if b'text/html' in response.headers.get('Content-Type'):
            if "page" not in response.url:            
                filename = response.url.split('/')[-1]
                if not filename:
                    filename = response.url.split('/')[-2]

                html_file_name = os.path.join('pages', f"{filename}.html")
                if "author" in html_file_name or "full=" in html_file_name:
                    return
                
                if os.path.exists(html_file_name):
                    return 
            
            self.write_html_file(response)

        if b'application/pdf' in response.headers.get('Content-Type'):
            self.write_pdf_file(response)

        for href in response.xpath('//a/@href').extract():
            yield response.follow(href, self.parse)
        
        
    def closed(self, reason):
        with open('visited_urls.txt', 'w') as f:
            for url in self.visited:
                f.write(url + '\n')


    def write_pdf_file(self, response):
        filename = response.url.split('/')[-1]
        if not filename:
            filename = response.url.split('/')[-2]
        pdf_file_name = os.path.join('pdfs', filename.split(".pdf")[0] + ".pdf")
        os.makedirs(os.path.dirname(pdf_file_name), exist_ok=True)
        if os.path.exists(pdf_file_name):  
            pdf_file_name = os.path.join('pdfs', filename + str(random.randrange(1,999999)) +".pdf")
        with open(pdf_file_name, 'wb') as f:
            f.write(response.body)


    def write_html_file(self, response):
        filename = response.url.split('/')[-1]
        if not filename:
            filename = response.url.split('/')[-2]

        html_file_name = os.path.join('pages', f"{filename}.html")
        os.makedirs(os.path.dirname(html_file_name), exist_ok=True)
        if os.path.exists(html_file_name):  
            html_file_name = os.path.join('pages', filename + str(random.randrange(1,999999)) +".html")
        with open(html_file_name, 'wb') as f:
            f.write(response.body)