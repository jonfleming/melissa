import spacy
import re

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
        self.handler = {}

        for sentence_type in self.sentence_types:
            if re.search(sentence_type['regex'], sentence, re.IGNORECASE):
                self.sentence_type = sentence_type['sentence_type']
                self.handler = sentence_type['handler']
                break



    def get_indefinite_article(self, starts_with):
        if starts_with in ['a', 'e', 'i', 'o', 'u']:
            return 'an '

        return 'a '

    def has_determiner(self, noun_chunk):
        token = self.doc[noun_chunk.start]
        return token.pos_ == 'DET'
            

    def strip_determiner(self, noun_chunk):
        word_list = noun_chunk.text.split()
        determiner = word_list.pop(0)
        noun = ' '.join(word_list)

        if len(noun) > 0:
            return noun, determiner
        else:
            return determiner, None


    def question_handler(self):
        noun = list(self.doc.noun_chunks)[1]
        indefinite_article = None
        determiner = None

        if self.has_determiner(noun):
            noun, determiner = self.strip_determiner(noun)
            indefinite_article = self.get_indefinite_article(noun[0])

        query = f"MATCH (s:Lemma {{name: '{noun}', pos:'n'}})-[r]->(n:Synset)" \
            f" RETURN n AS node LIMIT {self.limit}" \
            f" UNION ALL MATCH (s:Subject {{id: '{noun}', pos:'n'}})" \
            f" RETURN s AS node LIMIT {self.limit}"

        return noun, query, indefinite_article, determiner

    def statement_handler(self):
        subject = self.doc.noun_chunks[0]
        indefinate_artle = None
        determiner = None

        if self.has_determiner(subject):
            subject, determiner = self.strip_determiner(subject)

        subject = subject.replace(' ', '_')
        predicate = self.doc.noun_chunks[1]
        article = self.get_indefinite_article(predicate[0])
        definition = f'{article}{predicate}'

        if determiner:
            existing_synsets = f"MATCH (s:Synset) WHERE s.id STARTS WITH '{subject}.' RETURN COLLECT(right(s.id, 2));"
            synset_records = self.database.run_query(existing_synsets)
            ids = synset_records[0]._fields[0].sort()
            next_id = '01'

            if len(ids) > 0:
                next_id = str(int(ids[-1:]) + 1).rjust(2, '0')

            existing_lemma = f"MATCH (n:Lemma {{id: '{subject}.n'}} ) RETURN n"
            records = self.database.run_query(existing_lemma)

            if len(records) > 0:
                lemma = records[0]._fields[0]

                queries = [
                    f"CREATE (s:Synset {{" \
                        f"id: '{subject}.n.{next_id}', " \
                        f"name: '{subject}', " \
                        f"pos: 'n', " \
                        f"definition: '{definition}', " \
                        f"added:'true'" \
                    f"}}) RETURN s;", 
                    f"MATCH (n:Lemma {{name: '{subject}', pos:'n'}}) " \
                    f"MATCH (s: Synset {{ id: '{subject}.n.{next_id}' }}) " \
                    f"MERGE(n) - [r: IsA {{ dataset: 'custom', weight: 1.0, added: 'true' }}] -> (s) RETURN s;"
                ]

                self.database.run_list(queries)
        else:
            query = f"CREATE (s:Subject {{id: '{subject}', pos: 'n', definition: '{definition}'}}) RETURN s;"
            self.database.run_query(query)

        return subject, indefinate_artle, determiner