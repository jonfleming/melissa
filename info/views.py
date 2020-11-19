"""Chat Views module"""
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
import json

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
        response = parsed_input.handler() if parsed_input.handler else self.chat_handler(parsed_input)
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

    def chat_handler(self, input):
        statement = Statement(input.sentence)
        response = self.chatterbot.get_response(statement)
        return Statement(response.text)