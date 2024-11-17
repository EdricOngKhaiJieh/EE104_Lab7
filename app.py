# remember to pip install langchain
from langchain.sql_database import SQLDatabase
# remember to pip install langchain_experimental
from langchain_experimental.sql import SQLDatabaseChain
# remember to pip install -U langchain-community
from langchain_community.llms import OpenAI


import environ
env = environ.Env()
environ.Env.read_env()

API_KEY = env('OPENAI_API_KEY')

# Setup database

db = SQLDatabase.from_uri(
    f"postgresql+psycopg2://{env('DBUSER')}:{env('DBPASS')}@{env('DBHOST')}:5432/{env('DATABASE')}",
)

# setup llm
llm = OpenAI(temperature=0, openai_api_key=API_KEY)

# Create db chain
QUERY = """
Given an input question, first create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer.
Use the following format:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

If the SQLResult contains multiple rows, combine all the results into a single, comma-separated string in the answer.

{question}
"""




# Setup the database chain
llm = OpenAI(model_name="gpt-3.5-turbo-instruct", openai_api_key=API_KEY) 
db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)



def get_prompt():
    print("Type 'exit' to quit")

    while True:
        prompt = input("Enter a prompt: ")

        if prompt.lower() == 'exit':
            print('Exiting...')
            break
        else:
            try:
                question = QUERY.format(question=prompt)
                print(db_chain.run(question))
            except Exception as e:
                print(e)

get_prompt()