call conda create --name chatterbot python=3.7 --yes
call conda activate chatterbot
pip install chatterbot==1.0.2
pip install chatterbot-corpus
pip install spacy
pip install django
pip install numpy==1.19.2
pip install neo4j==4.1.1
python -m spacy download en
python -m spacy download en_core_web_md
python -m spacy download en_core_web_lg