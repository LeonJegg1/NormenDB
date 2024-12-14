from keybert import KeyBERT
import spacy
import json

def entitites_from_ner(text):
    kw_model = KeyBERT()
    nlp = spacy.load("de_core_news_sm")

    # Extrahiere Schlüsselbegriffe mit KeyBERT
    key_phrases = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='german', top_n=15)
    print("Extrahierte Schlüsselbegriffe:", key_phrases)

    # Analysiere und kategorisiere mit spaCy
    doc = nlp(text)
    # print("Erkannte Entitäten:", [(ent.text, ent.label_) for ent in doc.ents])

    categorized_entities = {
        "personen": [],
        "organisationen": [],
        "daten": [],
        "technische_begriffe": [],
        "produkte": [],
        "orte": [],
        "kunstwerke": [],
        "veranstaltungen": [],
        "sprachen": [],
        "gesetze": [],
        "sonstiges": []
    }

    # Kategorisiere erkannte Entitäten
    for ent in doc.ents:
        ent_text = ent.text.lower()
        if ent.label_ == "PER":  # Personen
            categorized_entities["personen"].append(ent_text)
        elif ent.label_ == "ORG":  # Organisationen
            categorized_entities["organisationen"].append(ent_text)
        elif ent.label_ == "DATE":  # Daten
            categorized_entities["daten"].append(ent_text)
        elif ent.label_ == "PRODUCT":  # Produkte
            categorized_entities["produkte"].append(ent_text)
        elif ent.label_ == "LOC":  # Orte
            categorized_entities["orte"].append(ent_text)
        elif ent.label_ == "WORK_OF_ART":  # Kunstwerke
            categorized_entities["kunstwerke"].append(ent_text)
        elif ent.label_ == "EVENT":  # Veranstaltungen
            categorized_entities["veranstaltungen"].append(ent_text)
        elif ent.label_ == "LANGUAGE":  # Sprachen
            categorized_entities["sprachen"].append(ent_text)
        elif ent.label_ == "LAW":  # Gesetze
            categorized_entities["gesetze"].append(ent_text)
        else:  # Sonstiges
            categorized_entities["sonstiges"].append(ent_text)

    # Zusätzliche Regeln für technische Begriffe
    technical_keywords = ["künstliche Intelligenz", "erneuerbare Energien", "Technologien"]
    for phrase, score in key_phrases:
        if any(term.lower() in phrase.lower() for term in technical_keywords):
            categorized_entities["technische_begriffe"].append(phrase.lower())

    # Duplikate entfernen
    for key in categorized_entities:
        categorized_entities[key] = list(set(categorized_entities[key]))
        
    all_tags = []
    for key, entities in categorized_entities.items():
        all_tags.extend(entities)
    
    return categorized_entities, all_tags