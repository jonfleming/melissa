from django.test import TestCase
from unittest.mock import Mock
from modules.sentence_classifyer import sentence_classifyer
from unittest.mock import patch
from chatterbot.conversation import Statement
#from chatterbot.ext.django_chatterbot.models import Statement, Tag
class SentenceTestCase(TestCase):
    def setUp(self):
        input_data = {'text': 'What is a car?'}
        database = Mock()
        database.run_query.return_value = ['test response']
        self.parsed_input = sentence_classifyer(input_data['text'], database)

    @patch('modules.neograph')
    def statementSetUp(self, mock_neograph):
        input_data = {'text': 'A car is a vehicle?'}
        database = Mock()
        database.run_query.return_value = [Mock(_fields=[['test response']])]
        #database.run_query.return_value.__getitem__._fields = ['test response']
        self.parsed_input = sentence_classifyer(input_data['text'], database)

    def test_get_indefinite_article(self):
        result = self.parsed_input.get_indefinite_article('car')
        self.assertEqual(result, 'a ')

    def test_sentence_type_set(self):
        self.assertEqual(self.parsed_input.sentence_type, 'whatIs')

    def test_sentence_handler_set(self):
        self.assertIsNotNone(self.parsed_input.handler)

    def test_get_determiner_returns_a(self):
        noun = list(self.parsed_input.doc.noun_chunks)[1]
        determiner, tag = self.parsed_input.get_determiner(noun)
        self.assertEqual(determiner, 'a')
        self.assertEqual(tag, 'indefinite')

    def test_has_determiner_returns_true(self):
        noun = list(self.parsed_input.doc.noun_chunks)[1]
        determiner = self.parsed_input.has_determiner(noun)
        self.assertTrue(determiner)

    def test_strip_determiner_returns_word(self):
        noun_chunk = list(self.parsed_input.doc.noun_chunks)[1]
        noun = self.parsed_input.strip_determiner(noun_chunk)
        self.assertEqual(noun, 'car')

    def test_question_handler_runs_query(self):
        response = self.parsed_input.handler()
        self.parsed_input.database.run_query.assert_called_once()
        self.assertEqual(self.parsed_input.database.run_query.return_value, ['test response'])
        self.assertEqual(response.text, Statement('a car is a test response').text)

    def test_statement_hander_runs_query(self):
        self.statementSetUp()

        response = self.parsed_input.handler()
        self.parsed_input.database.run_query.assert_called()
        self.assertEqual(self.parsed_input.database.run_query.return_value[0]._fields[0], ['test response'])
        self.assertEqual(response.text, Statement("I thought car is a ['test response'].  Is car also a vehicle?").text)
