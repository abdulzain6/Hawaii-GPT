from database_manager import BlogPostManager, SqliteDatabase
from langchain import PromptTemplate, LLMChain
import json

class BlogSearch():

    name = "blog_information_search"
    description = """"useful for when you want to search for a blog by either blog title, its author or the blog content.
The input of this tool should be a comma separated list of the criteria to search by and the search term.
For example, `title,Raising inflation` would be the input if you wanted to search for a blog with title Raising inflation.
`author,Joe kent` would be the input if you want posts by Joe kent.
The tool accepts the one following strings as the search criteria make sure they are correct and the most relavent one.
1. title
2. author
3. date_published
4. about
5. post

The dates are accepted in the following format August 18, 2022.
"""

    def __init__(self, blog_post_manager: BlogPostManager):
        self.blog_post_manager = blog_post_manager
                
    def get_data(self, query: str) -> list:
        try:
            criteria, search = query.split(",")
            if info := self.blog_post_manager.get_post_by_column(
                criteria, search
            ):
                return [i.to_dict() for i in info]
            else:
                return ["No data found"]
        except Exception as e:
            return ["No data found"]

    def _run(self, query: str) -> str:
        """Use the tool."""
        return self.get_data(query)
    
    def determine_args(self, query: str, llm) -> dict[str, str]:
        tools_list = [self]
        
        if not tools_list:
            return {}

        template = """Specify which tools and arguments can be used to answer the question. The available tools are:

    ===============
    Tools : {tools}
    ===============

    ===============
    Answer Format:{{"tool_name_one" : ["tool_usage_one_args", "tool_usage_two_args", ...], "tool_name_two" : ["tool_usage_one_args", ...]}} 
    You can call the tool many times. tool_usage_one_args means args for first time usage tool_usage_two_args for second and so on
    ===============

    ===============
    Question: {input}
    ===============

    ===============
    Rules:
    1. Format response for compatibility with json.loads.
    2. Return {{}} if no applicable tool available to answer question.
    3, Ensure args match tool requirements; exclude tool if incompatible.
    ===============

    The Answer in proper format with all the rules followed (Important):
    """


        llm_chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(template), verbose=True)
        try:
            return json.loads(
                llm_chain.predict(
                    tools="\n".join(
                        [f"{tool.name}: {tool.description}" for tool in tools_list]
                    ),
                    input=query,
                    verbose=True
                )
            )
        except Exception as e:
            print(e)
            return {}
 
 
    def execute_tool(self, question: str, llm, limit_per_call: int) -> dict[str, str]:
        tools = self.determine_args(question, llm)
        if not tools:
            return {"posts" : []}
        data = []
        for v in tools.values():
            for val in v:
                data.extend(self.get_data(val)[:limit_per_call])
        return {
            "posts" : data
        }
            
if __name__ == "__main__":
    
    search = BlogSearch(BlogPostManager(SqliteDatabase("blog_posts.db")))
   # print(data)
