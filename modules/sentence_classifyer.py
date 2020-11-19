from chatterbot.conversation import Statement
from modules.en_article import Article
import spacy
import re
import random

class sentence_classifyer:
    def __init__(self, sentence, database, limit = 5):
        nlp = spacy.load('en')
        self.doc = nlp(sentence)

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
        determiner = None
        tag = None
        if self.has_determiner(noun_chunk):
            determiner = self.doc[noun_chunk.start].text
            tag = 'definite' if determiner == 'the' else 'indefinite'
        
        return determiner, tag              

    def strip_determiner(self, noun_chunk):
        determiner = self.get_determiner(noun_chunk)
        noun = noun_chunk.text

        if determiner:
            start = noun_chunk.start + 1
            end = noun_chunk.end
            noun = self.doc[start:end].text
            
        return noun
        
    def question_handler(self):
        noun_chunk = list(self.doc.noun_chunks)[1]
        indefinite_article = None
        determiner, tag = self.get_determiner(noun_chunk)

        subject = self.strip_determiner(noun_chunk) if determiner else noun_chunk.text
        indefinite_article = self.get_indefinite_article(subject)

        query = f"MATCH (s:Lemma {{name: '{subject}', pos:'n'}})-[r]->(n:Synset)" \
            f" RETURN n AS node LIMIT {self.limit}" \
            f" UNION ALL MATCH (s:Subject {{id: '{subject}', pos:'n'}})" \
            f" RETURN s AS node LIMIT {self.limit}"

        records = self.database.run_query(query)
        reply = None

        if (len(records) > 0):
            n = random.randint(0, len(records) - 1)
            definition = records[n]
            has_determiner = definition.startswith('a ') or definition.startswith('the ')
            prefix = f'{indefinite_article}{subject} is' if has_determiner else f'{indefinite_article}{subject} is a'
            reply = f'{prefix} {definition}'
    
        return Statement(reply)

    def statement_handler(self):
        noun_chunk = list(self.doc.noun_chunks)[0]
        determiner = None

        determiner, tag = self.get_determiner(noun_chunk)
        subject = self.strip_determiner(noun_chunk) if determiner else noun_chunk.text
        
        subject = subject.replace(' ', '_')
        definition = list(self.doc.noun_chunks)[1].text
        response = None
        
        if determiner:
            existing_lemma = f"MATCH (n:Lemma {{id: '{subject}.n'}} ) RETURN n"
            records = self.database.run_query(existing_lemma)

            if len(records) > 0:
                lemma = records[0]._fields[0]

                response = Statement(f"I thought {subject} is a {lemma}.  Is {subject} also {definition}?")
        else:
            query = f"CREATE (s:Subject {{id: '{subject}', pos: 'n', definition: '{definition}'}}) RETURN s;"
            self.database.run_query(query)
            response = Statement(f"I've added {subject} is {definition} to my database")

        return response