import psycopg2
from tabulate import tabulate

import environ
env = environ.Env()
environ.Env.read_env()

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    user='postgres',
    password=env('DBPASS'),
    database=env('DATABASE')
)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the tasks table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS CovidVacc
             (FirstName TEXT NOT NULL,
             MiddleName TEXT NOT NULL,
             LastName TEXT NOT NULL,
             PhoneNumber TEXT,
             Email TEXT,
             DateOf1stVaccination DATE,
             DateOf2ndVaccination DATE)''')

# Insert sample tasks into the tasks table
cursor.execute("INSERT INTO CovidVacc (FirstName, MiddleName, LastName, PhoneNumber, Email, DateOf1stVaccination, DateOf2ndVaccination) VALUES (%s, %s, %s, %s, %s, %s, %s)",
               ('Chris', 'H', 'Pham', '604-256-4729', 'ee104sjsu@gmail.com', '2022-08-28', '2022-09-18'))
cursor.execute("INSERT INTO CovidVacc (FirstName, MiddleName, LastName, PhoneNumber, Email, DateOf1stVaccination, DateOf2ndVaccination) VALUES (%s, %s, %s, %s, %s, %s, %s)",
               ('Monkey', 'D', 'Luffy', '254-276-4542', 'ee105sjsu@gmail.com', '2022-08-29', '2022-09-19'))
cursor.execute("INSERT INTO CovidVacc (FirstName, MiddleName, LastName, PhoneNumber, Email, DateOf1stVaccination, DateOf2ndVaccination) VALUES (%s, %s, %s, %s, %s, %s, %s)",
               ('Samurai', 'H', 'Champloo', '564-842-4279', 'ee106sjsu@gmail.com', '2022-07-28', '2022-08-18'))
cursor.execute("INSERT INTO CovidVacc (FirstName, MiddleName, LastName, PhoneNumber, Email, DateOf1stVaccination, DateOf2ndVaccination) VALUES (%s, %s, %s, %s, %s, %s, %s)",
               ('Adam', 'K', 'Lui', '604-246-4929', 'ee107sjsu@gmail.com', '2022-08-20', '2022-09-10'))
cursor.execute("INSERT INTO CovidVacc (FirstName, MiddleName, LastName, PhoneNumber, Email, DateOf1stVaccination, DateOf2ndVaccination) VALUES (%s, %s, %s, %s, %s, %s, %s)",
               ('Mei', 'P', 'Lynn', '408-256-4729', 'ee108sjsu@gmail.com', '2022-08-23', '2022-09-13'))
cursor.execute("INSERT INTO CovidVacc (FirstName, MiddleName, LastName, PhoneNumber, Email, DateOf1stVaccination, DateOf2ndVaccination) VALUES (%s, %s, %s, %s, %s, %s, %s)",
               ('Maxim', 'M', 'Bo', '604-298-4729', 'ee109sjsu@gmail.com', '2022-08-24', '2022-09-14'))

# Define the SQL query to remove duplicate rows
sql = """
WITH CTE AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY FirstName, MiddleName, LastName, PhoneNumber, Email, DateOf1stVaccination, DateOf2ndVaccination ORDER BY (SELECT NULL)) AS rn
    FROM CovidVacc
)
DELETE FROM CovidVacc
WHERE (FirstName, MiddleName, LastName, PhoneNumber, Email, DateOf1stVaccination, DateOf2ndVaccination) IN (
    SELECT FirstName, MiddleName, LastName, PhoneNumber, Email, DateOf1stVaccination, DateOf2ndVaccination
    FROM CTE
    WHERE rn > 2
)
"""

# Execute the SQL query
cursor.execute(sql)

# Execute a SELECT query to fetch all rows from the CovidVacc table
cursor.execute("SELECT * FROM CovidVacc")

# Fetch all rows from the result set
rows = cursor.fetchall()

# Print the table using tabulate for pretty formatting
if rows:
    print(tabulate(rows, headers=[desc[0] for desc in cursor.description]))
else:
    print("No rows found in the CovidVacc table")
    
# Commit the changes and close the connection
conn.commit()
conn.close()