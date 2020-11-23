from neo4j import GraphDatabase
import os
import sys

uri = 'bolt://localhost:7687' #os.getenv('neouri')
user = os.getenv('neousername')
password = os.getenv('neopassword')
WORDNET = 'wordnetconceptnet'

class neograph:
    def __init__(self, uri=uri, user=user, password=password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def get_session(self, database):
        self.session = self.driver.session(database=database)
        return self.session
    
    def runner(self, tx, query, property):
        records = []
        result = tx.run(query)
        for record in result:
            records.append(record[0]._properties[property])

        return records

    def run_query(self, query, property):
        print(query)
        try:
            records = self.get_session(WORDNET).read_transaction(self.runner, query, property)
            return records
        except:
            print('Error', sys.exc_info())

    def run_list(self, queries):
        for query in queries:
            print(query)
            result = self.get_session(WORDNET).write_transaction(self.runner, query)
            
    def close(self):
        self.driver.close()

