import spacy

sentence = 'what is the bike?'
#sentence = 'displaCy uses CSS and JavaScript to show you how computers understand language'
nlp = spacy.load('en')
doc = nlp(sentence)

# noun_chunks:
#   text: a bike
#   lemma_: a bike
#   orth_: a bike
#   label_: NP
#   start: 2
#   end: 4

# for word in doc:
#     if word.dep_ in ('xcomp', 'ccomp'):
#         subtree_span = doc[word.left_edge.i : word.right_edge.i + 1]
#         print(subtree_span.text, '|', subtree_span.root.text)
#         print(subtree_span.similarity(doc))
#         print(subtree_span.similarity(subtree_span.root))

for nc in doc.noun_chunks:
    dict = dir(nc)
    print(nc.text + ':')
    # for attr in dict:
    #     if not attr.startswith('_'):
    #         print('  ' + attr, eval('nc.' + attr))
    token = doc[nc.start] 
    print(token.text, ':', token.pos_, token.tag_)