"""Chat Views module"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import TemplateView
from django.views.generic import View
from django.http import JsonResponse
from chatterbot import ChatBot
from chatterbot.ext.django_chatterbot import settings
#from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.conversation import Statement
from modules.sentence_classifyer import sentence_classifyer
from modules.neograph import neograph
import json
import logging

logger = logging.getLogger(__name__)
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
        logger.info('Handling POST request')

        input_data = json.loads(request.body.decode('utf-8'))

        if 'text' not in input_data:
            return JsonResponse({
                'text': [
                    'The attribute "text" is required.'
                ]
            }, status=400)

        # Populate database with training data (only run once)
        # logger.info('Loading Training corpus')
        # trainer = ChatterBotCorpusTrainer(self.chatterbot)
        # trainer.train('chatterbot.corpus.english')
        # logger.info('Training done')

        # Send input to sentence classifyer and return response
        database = neograph()

        if input_data['text']:
            logger.info('Getting parsed input')
            parsed_input = sentence_classifyer(input_data['text'], database)

            logger.info('Running input handler')
            response = parsed_input.handler() if parsed_input.handler else self.gpt3_handler(parsed_input)

            response_data = response.serialize()
            logger.info('Done with response')

            # response: id, text, searc_text, conversation, persona, tags, in_response_to, created_at
            logger.info(f"Sentence: {input_data['text']}\nResponse: {response.text}\n")
            return JsonResponse(response_data, status=200)
        else:         
            return JsonResponse({'text': ''}, status=200)

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

    def gpt3_handler(self, input):
        import openai
        import os

        sentence_ending = input.sentence[-1:]
        if not sentence_ending in ['.','?','!']:
            input.sentence += '.'

        openai.api_key = os.getenv('openapi_key')
        prompt = 'Jon is a wise and friendly chatbot that understands the English language.  Jon will remember what you tell him and try to answer any questions you have.\n' \
            '\n' \
            'Question: Hi.\n' \
            'Answer: Hello.  How can I help you?\n' \
            '\n' \
            'Question: Are you reading any good books right now?\n' \
            'Answer: I love science fiction and fantasy.  Right now I\'m reading Harry Potter and the Goblet of Fire.\n' \
            '\n' \
            'Question: Do you have any hidden talents or surprising hobbies?\n' \
            'Answer: I\'m pretty good at math.  Maybe that\'s not so surprising.\n' \
            '\n' \
            'Question: What would be your ideal superpower?\n' \
            'Answer: Invisibility.\n' \
            '\n' \
            'Question: What\'s the best piece of advice you\'ve ever received?\n' \
            'Answer: Your life is your responsibility.\n' \
            '\n' \
            'Question: How do I find a job?\n' \
            'Answer:\n' \
            '1. Decide what you want to do, and why you want to do it.\n' \
            '2. Find a way to get started.\n' \
            '3. Be persistent.\n' \
            '4. Keep learning.\n' \
            '\n' \
            'Question:' + input.sentence

        openai_response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=90, stop='Question:')
        response = openai_response.choices[0].text.split(':')[1]
        response = response.replace('Answer', '')
        logger.info(f"Sentence: {input.sentence}\nGPT Response: {response}\n")
        return Statement(response)
