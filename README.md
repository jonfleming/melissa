"# Melissa"
Speech Recognition using Django and Neo4j

Using chatterbot with Django

Outline 11/1/20

    Get user input (microphone or typed)
    Classify the sentence (question or statement)
    
    For "What Is" Questions
        Parse the sentence and query wordnet/conceptnet for an answer
        To Do: handle other question types

    For Statements
        Parse the sentence and add the fact to wordnet/conceptnet if it doesn't already exist

    For all other sentences
        Return chatterbot response

