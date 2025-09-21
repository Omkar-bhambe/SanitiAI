import spacy

class SpacyNer:
    def __init__(self, model_name="en_core_web_sm"):
        self.nlp = spacy.load(model_name)

    def detect_pii(self, text):
        
        doc = self.nlp(text)
        pii_entities = []
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'GPE', 'ORG', 'DATE', 'MONEY', 'CARDINAL']:
                pii_entities.append({'text': ent.text, 'label': ent.label_})
        return pii_entities
