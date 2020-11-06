"""Chat Views module"""
import json
import random
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import TemplateView
from django.views.generic import View
from django.http import JsonResponse
from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot import settings
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.conversation import Statement
from modules.sentence_classifyer import sentence_classifyer
from modules.neograph import neograph

def get_what_is(input, database):
    noun, query, indefinite_article, determiner = input.handler()
    records = database.run_query(query)
    reply = None

    if (len(records) > 0):
        n = random.randint(0, len(records) - 1)
        definition = records[n]
        has_determiner = definition.startswith('a ') or definition.startswith('the ')
        prefix = f'{indefinite_article}{noun} is' if has_determiner else f'{indefinite_article}{noun} is a'
        reply = f'{prefix} {definition}'
    
    return Statement(reply)

def save_fact(input, database):
    pass

class ChatterBotAppView(TemplateView):
    template_name = 'info/info.html'


class ChatterBotApiView(View):
    """
    Provide an API endpoint to interact with ChatterBot.
    """

    chatterbot = ChatBot(
        **settings.CHATTERBOT,
        logic_adapters = [
            {
                'import_path':'chatterbot.logic.BestMatch',
                'maimum_similarity_threshold': 0.80
            }
        ]
    )

    def post(self, request, *args, **kwargs):
        """
        Return a response to the statement in the posted data.

        * The JSON data should contain a 'text' attribute.
        """
        input_data = json.loads(request.body.decode('utf-8'))

        if 'text' not in input_data:
            return JsonResponse({
                'text': [
                    'The attribute "text" is required.'
                ]
            }, status=400)

        # Send input to sentence classifyer and return response
        database = neograph()
        parsed_input = sentence_classifyer(input_data['text'], database)
        process = {'whatIs': get_what_is, 'isA':save_fact, 'unknown':self.chat_response}
        response = process[parsed_input.sentence_type](parsed_input, database)
        response_data = response.serialize()
# response: id, text, searc_text, conversation, persona, tags, in_response_to, created_at

        # Populate database with training data (only run once)
        #trainer = ChatterBotCorpusTrainer(self.chatterbot)
        #trainer.train('chatterbot.corpus.english')

        return JsonResponse(response_data, status=200)

    def get(self, request, *args, **kwargs):
        """
        Return data corresponding to the current conversation.
        """
        return JsonResponse({
            'name': self.chatterbot.name
        })

    def chat_response(self, input, database):
        statement = Statement(input.sentence)
        return self.chatterbot.get_response(statement)