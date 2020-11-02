from neo4j import GraphDatabase
import os
import sys

uri = 'bolt://localhost:7687' #os.getenv('neouri')
user = os.getenv('neousername')
password = os.getenv('neopoassword')

class neograph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def get_db(self, database):
        self.db = self.driver.session(database=database)
        return self.db
    
    def run_query(self, query):
        print(query)
        try:
            result = self.db.run(query)
            records = result.records
            return records
        except:
            print('Error', sys.exec_info())

    def run_list(self, queries):
        for query in queries:
            print(query)
            result = self.db.run(query)
            
    def close(self):
        self.driver.close()

