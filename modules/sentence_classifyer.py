import spacy
import re

class sentence_classifyer:
    def __init__(self, sentence, database, limit = 5):
        nlp = spacy.load('en')
        self.doc = nlp(sentence)

        self.sentence_types = [
            { 'regex': '^how is', 'sentent_type': 'howIs', 'handler': self.questionHandler },
            { 'regex': '^what is', 'sentent_type': 'whatIs', 'handler': self.questionHandler },
            { 'regex': '^when ', 'sentent_type': 'whyIs', 'handler': self.questionHandler },
            { 'regex': '^where is', 'sentent_type': 'whereIs', 'handler': self.questionHandler },
            { 'regex': '^who is', 'sentent_type': 'whoIs', 'handler': self.questionHandler },
            { 'regex': '^why is', 'sentent_type': 'whyIs', 'handler': self.questionHandler },
            { 'regex': '^is ', 'sentent_type': 'whyIs', 'handler': self.questionHandler },
            { 'regex': '^does ', 'sentent_type': 'whyIs', 'handler': self.questionHandler },
            { 'regex': '^do ', 'sentent_type': 'whyIs', 'handler': self.questionHandler },
            { 'regex': 'is a', 'sentent_type': 'isA', 'handler': self.statementHandler },
        ]

        self.sentence = sentence
        self.database = database
        self.limit = limit
        self.handler = {}

        self.sentence_type = next(stype for stype in self.sentence_types if re.search(stype.regex, sentence, re.IGNORECASE) )
        return self.sentence_type

    def get_indefinite_article(starts_with):
        if starts_with in ['a', 'e', 'i', 'o', 'u']:
            return 'an '

        return 'a '

    def has_determiner(self, noun_chunk):
        token = self.doc[noun_chunk.start]
        return token.pos_ == 'DET'
            

    def strip_determiner(self, noun_chunk):
        word_list = noun_chunk.text.split()
        determiner = word_list.pop(0)
        noun = word_list.join()

        if len(noun) > 0:
            return noun, determiner
        else:
            return determiner, None


    def question_handler(self):
        noun = self.doc.noun_chunks[1]
        indefinite_article = None
        determiner = None

        if self.has_determiner(self, noun):
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

                queies = [
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

                self.database.run_list(queies)
        else:
            query = f"CREATE (s:Subject {{id: '{subject}', pos: 'n', definition: '{definition}'}}) RETURN s;"
            self.database.run_query(query)

        return subject, indefinate_artle, determiner