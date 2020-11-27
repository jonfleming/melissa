from chatterbot.conversation import Statement
from modules.en_article import Article
from datetime import datetime, time
import spacy
import re
import logging

nlp = spacy.load('en_core_web_md')
logger = logging.getLogger(__name__)
class sentence_classifyer:
    def __init__(self, sentence, database, limit = 10):
        self.startTime = datetime.now()
        logger.info(f"Initializing classifyer")
        
        self.doc = nlp(sentence)
        logger.info(f"Doc created. Elapsed {self.elapsed()}")

        self.sentence_types = [
            { 'regex': '^how is', 'sentence_type': 'howIs', 'handler': self.question_handler },
            { 'regex': '^what is', 'sentence_type': 'whatIs', 'handler': self.question_handler },
            { 'regex': '^when ', 'sentence_type': 'whyIs', 'handler': self.question_handler },
            { 'regex': '^where is', 'sentence_type': 'whereIs', 'handler': self.question_handler },
            { 'regex': '^who is', 'sentence_type': 'whoIs', 'handler': self.question_handler },
            { 'regex': '^why is', 'sentence_type': 'whyIs', 'handler': self.question_handler },
            { 'regex': '^is ', 'sentence_type': 'whyIs', 'handler': self.question_handler },
            { 'regex': '^does ', 'sentence_type': 'whyIs', 'handler': self.question_handler },
            { 'regex': '^do ', 'sentence_type': 'whyIs', 'handler': self.question_handler },
            { 'regex': ' is a ', 'sentence_type': 'isA', 'handler': self.isA_statement_handler },
            { 'regex': ' is an ', 'sentence_type': 'isA', 'handler': self.isA_statement_handler },
            { 'regex': ' is .*\.$', 'sentence_type': 'isA', 'handler': self.is_statement_handler },
            { 'regex': 'tell me', 'sentence_type': 'command', 'handler': self.statement_handler },
            { 'regex': 'give me', 'sentence_type': 'command', 'handler': self.statement_handler },
        ]

        self.sentence = sentence
        self.database = database
        self.limit = limit
        self.sentence_type = 'unknown'
        self.handler = None

        for sentence_type in self.sentence_types:
            if re.search(sentence_type['regex'], sentence, re.IGNORECASE):
                self.sentence_type = sentence_type['sentence_type']
                self.handler = sentence_type['handler']
                break

        logger.info(f"Done with initialization. Elapsed {self.elapsed()}")

    def elapsed(self):
        return datetime.now() - self.startTime

    def get_indefinite_article(self, noun):
        result = Article.getInstance().query(noun)
        return result['article'] + ' '

    def strip_determiner(self, noun_phrase):
        has_determiner = re.match('(a |an |the )', noun_phrase, re.I)
        determiner = None
        noun = noun_phrase

        if has_determiner:
            words = noun_phrase.split(' ', 1)
            determiner = words[0]
            noun = words[1]
            # if noun_phrase only has 1 word:
            #   first, _, rest = noun_phrase.partition(' ')
            #   noun = rest or first

        return determiner, noun
        
    def get_existing_definitions(self, lemma):
        query = f"MATCH (s:Lemma {{name: '{lemma}', pos:'n'}})-[r]->(n:Synset)" \
            f" RETURN n.id AS id, n.definition AS definition, r.added AS added, TYPE(r) AS type LIMIT {self.limit}" \
            f" UNION ALL MATCH (s:Subject {{id: '{lemma}', pos:'n'}})" \
            f" RETURN s.id AS id, s.definition AS definition, TRUE AS added, head(labels(s)) AS type LIMIT {self.limit}"
        return self.database.run_query(query)

    def create_new_synset_and_relationship(self, id, subject, definition):
        queries = [f"CREATE (s:Synset {{id: '{subject}.n.{id}', name: '{subject}', pos: 'n', definition: '{definition}', added:TRUE}}) RETURN s;",
            f"MATCH (n:Lemma {{name: '{subject}', pos:'n'}}) " \
            f"MATCH (s: Synset {{ id: '{subject}.n.{id}' }}) " \
            f"MERGE(n) - [r: IsA {{ dataset: 'custom', weight: 1.0, added: TRUE }}] -> (s) RETURN s;"]               
        self.database.run_list(queries)

    def create_new_definition(self, subject, definition):
        queries = [f"CREATE (s:Subject {{id: '{subject}', pos: 'n', definition: '{definition}'}}) RETURN s;"]
        self.database.run_list(queries)

    def find_similar(self, definition, records):
        pass # Use spacy to check similarity (vector?).  May need to build statement
        doc1 = nlp(definition)

        for record in records:
            doc2 = nlp(record['definition'])
            similarity = doc1.similarity(doc2)
            if similarity > 0.85:
                return record

        return None
        
    def get_id(self, record):
        return record['id'][-2:] if record['id'].startswith(self.word) else self.default_id

    def question_handler(self):
        logger.info(f"Question handler. Elapsed {self.elapsed()}")
        noun_phrase = list(self.doc.noun_chunks)[1].text
        determiner, direct_subject = self.strip_determiner(noun_phrase)

        logger.info(f"Get existing definitions. Elapsed {self.elapsed()}")
        records = self.get_existing_definitions(direct_subject)
        reply = None

        if (len(records) > 0):
            # Get first record with added=True or the record with lowest 2 digit id and matching word
            self.word = direct_subject
            self.default_id = '99'
            record = next((record for record in iter(records) if record['added']), min(records, key=self.get_id))
            reply = f"{determiner}{direct_subject} is {record['definition']}"
    
        logger.info(f"Done with question handler. Elapsed {self.elapsed()}")

        return Statement(reply)

    def statement_handler(self, determiner, subject, object_clause):
        logger.info(f"Statement handler. Elapsed {self.elapsed()}")
        records = self.get_existing_definitions(subject)
        logger.info(f"Done with Get existing definitions. Elapsed {self.elapsed()}")
        existing = self.find_similar(object_clause, records)
        logger.info(f"Done with find similar. Elapsed {self.elapsed()}")
        response = None

        if existing:
            sentence = f"{determiner}{subject.replace('_', ' ')} is {existing['definition']}"
            response = 'I knew that ' + sentence
        else:
            if len(records) > 0:
                self.word = subject
                self.default_id = '00'
                last_record = max(records, key=self.get_id)
                id = int(last_record['id'][-2:])
                nextId = str(id + 1).zfill(2)

                logger.info(f"Create new synset. Elapsed {self.elapsed()}")
                self.create_new_synset_and_relationship(nextId, subject, object_clause)
            else:
                logger.info(f"Create new definition. Elapsed {self.elapsed()}")
                self.create_new_definition(subject, object_clause)

            response = 'I have added that fact to my database.'

        logger.info(f"Done with Statement handler. Elapsed {self.elapsed()}")
        return Statement(response)

    def isA_statement_handler(self):
        logger.info(f"IsA statement handler. Elapsed {self.elapsed()}")
        direct_subject = list(self.doc.noun_chunks)[0].text
        definition = list(self.doc.noun_chunks)[1].text

        determiner, subject = self.strip_determiner(direct_subject)
        subject = subject.replace(' ', '_')

        return self.statement_handler(determiner, subject, definition)
        
    def is_statement_handler(self):
        logger.info(f"Is statement handler. Elapsed {self.elapsed()}")
        root = [token for token in self.doc if token.dep_ == 'ROOT' and token.pos_ == 'AUX']
        start = root[0].i
        direct_subject = self.doc[:start].text
        object_clause = self.doc[start+1:].text

        determiner, subject = self.strip_determiner(direct_subject)
        subject = subject.replace(' ', '_')

        return self.statement_handler(determiner, subject, object_clause)