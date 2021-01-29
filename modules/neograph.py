from neo4j import GraphDatabase
import os
import sys

uri = os.getenv('neouri')
user = os.getenv('neousername')
password = os.getenv('neopassword')
WORDNET = 'wordnetconceptnet'

class neograph:
    def __init__(self, uri=uri, user=user, password=password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def get_session(self, database):
        self.session = self.driver.session(database=database)
        return self.session
    
    def runner(self, tx, query):
        records = []
        result = tx.run(query)
        for item in result:
            record = {}
            for key in result.keys():
                record[key] = item[key] 
            records.append(record)
            
        return records

    def run_query(self, query):
        print(query)
        try:
            return  self.get_session(WORDNET).read_transaction(self.runner, query)
        except:
            print('Error', sys.exc_info())
            return []

    def run_list(self, queries):
        count = 0
        for query in queries:
            print(query)
            count += 1
            try:
                self.get_session(WORDNET).write_transaction(self.runner, query)
            except:
                print('Error', sys.exc_info())
                return ['Error', sys.exc_info()]
        
        return [f"Success.  {count} queries executed"]
        
    def close(self):
        self.driver.close()

