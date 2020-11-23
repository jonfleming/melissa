import spacy
import pytextrank

sentence = 'Please give me the large nail; it’s the only one strong enough to hold this painting.'
nlp = spacy.load('en_core_web_lg')

# add PyTextRank to the spaCy pipeline
tr = pytextrank.TextRank()
nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)

doc = nlp(sentence)

for p in doc._.phrases:
    print('{:.4f} {:5d}  {}'.format(p.rank, p.count, p.text))
    print(p.chunks)

exit(0)
#region Noun Chunks
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
#endregion