from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot import constants
from chatterbot import ChatBot
import logging
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')

logging.basicConfig(level=logging.INFO)
from django.apps import AppConfig
from django.apps.registry import Apps, apps as global_apps
from django.conf import settings
from django.db import models

from chatterbot.ext.django_chatterbot import apps 
from chatterbot.ext.django_chatterbot import settings
from chatterbot.ext.django_chatterbot.models import Statement, Tag

def select_response(statement, statement_list, storage=None):
    selected_statement = statement_list[0]
    return selected_statement


chatbot = ChatBot(
    'Melissa',
    django_app_name = 'melissa',
    storage_adapter='chatterbot.storage.DjangoStorageAdapter',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'maximum_similarity_threshold': 0.80
        }
    ],
    response_selection_method=select_response
)

trainer = ChatterBotCorpusTrainer(chatbot)

trainer.train(
    'chatterbot.corpus.english'
)

# Now let's get a response to a greeting
response = chatbot.get_response('How are you doing today?')
print(response)
