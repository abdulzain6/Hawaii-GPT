from peewee import *
from fuzzywuzzy import fuzz
import json

class BlogPostManager:
    def __init__(self, database_handle: SqliteDatabase):
        class BlogPost(Model):
            author = CharField()
            title = CharField()
            date_published = CharField()
            about = CharField()
            post = TextField()
            
            class Meta:
                database = database_handle
                table_name = 'blog_posts'
                
            def to_json(self):
                return json.dumps(
                    {
                        "author": self.author, 
                        "title" : self.title,
                        "date_published":  self.date_published,
                        "about" : self.about,
                        "post" : self.post
                    }
                )

            def to_dict(self):
                return  {
                        "author": self.author, 
                        "title" : self.title,
                        "date_published":  self.date_published,
                        "about" : self.about,
                        "post" : self.post
                    }

        database_handle.connect()
        database_handle.create_tables([BlogPost])
        self.model = BlogPost
        
    def add_post(self, author, title, date_published, about, post):
        self.model.create(author=author, title=title, date_published=date_published, about=about, post=post)
        
    def get_post_by_column(self, column_name, search_term, threshold=70):
        column_names = self.model._meta.fields.keys()
        best_column = None
        for column in column_names:
            ratio = fuzz.token_set_ratio(column, column_name)
            if best_column is None or ratio > best_column[1]:
                best_column = (column, ratio)
            if ratio == 100:
                break
        best_column = best_column[0]

        def search_function(post, search_term):
            return fuzz.token_set_ratio(str(getattr(post, best_column)), search_term)

        all_posts = self.get_all_posts()
        return [post for post in all_posts if search_function(post, search_term) >= threshold]


    
    def update_post(self, title, new_post):
        post = self.get_post_by_title(title)
        post.post = new_post
        post.save()
        
    def delete_post(self, title):
        post = self.get_post_by_title(title)
        post.delete_instance()
        
    def get_all_posts(self):
        return list(self.model.select().execute())

if __name__ == "__main__":
    db = SqliteDatabase('blog_posts.db')
    manager = BlogPostManager(database_handle=db)
   # print(manager.get_all_posts())
    print(manager.get_post_by_column("Author", "joe")[0].author)