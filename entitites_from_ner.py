from keybert import KeyBERT
import spacy
import json

def entitites_from_ner(text):
    kw_model = KeyBERT()
    nlp = spacy.load("de_core_news_sm")

    # Extrahiere Schlüsselbegriffe mit KeyBERT
    key_phrases = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='german', top_n=15)

    # Analysiere und kategorisiere mit spaCy
    doc = nlp(text)
    categorized_entities = {"personen": [], "organisationen": [], "daten": [], "technische_begriffe": [], "produkte": []}

    # Kategorisiere extrahierte Entitäten
    for phrase, score in key_phrases:
        for ent in doc.ents:
            if phrase in ent.text:
                if ent.label_ == "PER":  # Personen
                    categorized_entities["personen"].append(phrase)
                elif ent.label_ == "ORG":  # Organisationen
                    categorized_entities["organisationen"].append(phrase)
                elif ent.label_ == "DATE":  # Daten
                    categorized_entities["daten"].append(phrase)
                elif ent.label_ == "PRODUCT":  # Produkte
                    categorized_entities["produkte"].append(phrase)

   # Zusätzliche Regeln für technische Begriffe
    technical_keywords = ["künstliche Intelligenz", "erneuerbare Energien", "Technologien"]
    for phrase, score in key_phrases:
        if any(term.lower() in phrase.lower() for term in technical_keywords):
            categorized_entities["technical_terms"].append(phrase)

    # Duplikate entfernen
    for key in categorized_entities:
        categorized_entities[key] = list(set(categorized_entities[key]))
        
    all_tags = []
    for key, entities in categorized_entities.items():
        all_tags.extend(entities)

    # Ausgabe im gewünschten JSON-Format
    print(json.dumps(categorized_entities, indent=2, ensure_ascii=False))
    return json.dumps(categorized_entities, indent=2, ensure_ascii=False), all_tags