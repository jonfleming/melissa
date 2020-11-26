from chatterbot.conversation import Statement
from modules.en_article import Article
import spacy
import re

class sentence_classifyer:
    def __init__(self, sentence, database, limit = 7):
        self.nlp = spacy.load('en_core_web_md')
        self.doc = self.nlp(sentence)

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
            { 'regex': 'is a', 'sentence_type': 'isA', 'handler': self.statement_handler },
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

    def get_indefinite_article(self, noun):
        result = Article.getInstance().query(noun)
        return result['article'] + ' '

    def has_determiner(self, noun_chunk):
        token = self.doc[noun_chunk.start]
        return (token.pos_ == 'DET')

    def get_determiner(self, noun_chunk):
        determiner = ''
        tag = None
        if self.has_determiner(noun_chunk):
            determiner = self.doc[noun_chunk.start].text + ' '
            tag = 'definite' if determiner == 'the' else 'indefinite'
        
        return determiner, tag              

    def strip_determiner(self, noun_chunk):
        determiner, tag = self.get_determiner(noun_chunk)
        noun = noun_chunk.text

        if determiner:
            start = noun_chunk.start + 1
            end = noun_chunk.end
            noun = self.doc[start:end].text
            
        return noun
        
    def get_existing_definitions(self, lemma):
        query = f"MATCH (s:Lemma {{name: '{lemma}', pos:'n'}})-[r]->(n:Synset)" \
            f" RETURN n.id AS id, n.definition AS definition, r.added AS added, TYPE(r) AS type LIMIT {self.limit}" \
            f" UNION ALL MATCH (s:Subject {{id: '{lemma}', pos:'n'}})" \
            f" RETURN s.id AS id, s.definition AS definition, TRUE AS added, head(labels(s)) AS type LIMIT {self.limit}"
        return self.database.run_query(query)

    def create_new_synset_and_relationship(self, id, subject, definition):
        queries = [f"CREATE (s:Synset {{id: '{subject}.n.{id}', name: '{subject}', pos: 'n', definition: '{definition}', added:'true'}}) RETURN s;",
            f"MATCH (n:Lemma {{name: '{subject}', pos:'n'}}) " \
            f"MATCH (s: Synset {{ id: '{subject}.n.{id}' }}) " \
            f"MERGE(n) - [r: IsA {{ dataset: 'custom', weight: 1.0, added: TRUE }}] -> (s) RETURN s;"]               
        self.database.run_list(queries)

    def create_new_definition(self, subject, definition):
        queries = [f"`CREATE (s:Subject {{id: '{subject}', pos: 'n', definition: '{definition}'}}) RETURN s;"]
        self.database.run_list(queries)

    def find_similar(self, definition, records):
        pass # Use spacy to check similarity (vector?).  May need to build statement
        doc1 = self.nlp(definition)

        for record in records:
            doc2 = self.nlp(record['definition'])
            similarity = doc1.similarity(doc2)
            if similarity > 0.85:
                return record

        return None

    def create_isA_sentence(self, determiner, subject, definition):
        indefinite_article = self.get_indefinite_article(subject)
        has_determiner = re.match('^(a |an |the )', definition, re.I)
        result = f'{determiner}{subject} is '

        if has_determiner:
            result += definition
        else:
            result += self.get_indefinite_article(definition) + definition

        return result
        
    def get_id(self, record):
        return record['id'][-2:]

    def question_handler(self):
        noun_chunk = list(self.doc.noun_chunks)[1]
        indefinite_article = None
        determiner, tag = self.get_determiner(noun_chunk)

        subject = self.strip_determiner(noun_chunk) if determiner else noun_chunk.text
        records = self.get_existing_definitions(subject)
        reply = None

        if (len(records) > 0):
            # Get first record with added=True or the record with lowest 2 digit id
            record = next((record for record in iter(records) if record['added']), min(records, key=self.get_id))
            reply = self.create_isA_sentence(determiner, subject, record['definition'])
    
        return Statement(reply)

    def statement_handler(self):
        noun_chunk = list(self.doc.noun_chunks)[0]
        definition = list(self.doc.noun_chunks)[1].text
        determiner = None

        determiner, tag = self.get_determiner(noun_chunk)
        subject = self.strip_determiner(noun_chunk) if determiner else noun_chunk.text        
        subject = subject.replace(' ', '_')

        records = self.get_existing_definitions(subject)
        response = None
        
        existing = self.find_similar(definition, records)
        
        if existing:
            statement = self.create_isA_sentence(determiner, subject, existing['definition'])
            response = 'I knew that ' + statement
        else:
            if len(records) > 0:
                last_record = max(records, self.get_id)
                id = int(last_record[-2:])
                nextId = str(id + 1).zfill(2)

                self.create_new_synset_and_relationship(nextId, subject, definition)
            else:
                self.create_new_definition(subject, definition)

            response = 'I have added that fact to my database.'
        return Statement(response)