import csv
import json
import re
import collections

from utils import *


def verb_3p(verb):
    "Make the 3rd person form out of the 1st person form"
    if verb[-1] == 's' or verb[-2:] == "sh" or verb[-2] == "ch":
        return verb + "es"
    elif verb[-1] == 'y' and verb[-2] not in "aouei":
        return verb[:-1] + "ies"
    else:
        return verb + "s"


def load_csv():

    verb_extractor = re.compile("(I|it)( will)? ([\\w\\- ]*)")

    verbs = collections.OrderedDict()
    fname = 'jehle_verb_database.csv'
    with open(fname) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        # skip heading
        next(reader)

        for row in reader:

            (infinitive,
            english_translation,
            mood,
            mood_english,
            tense,
            tense_english,
            verb_english,
            form_1s,
            form_2s,
            form_3s,
            form_1p,
            form_2p,
            form_3p,
            gerund,
            gerund_english,
            pastparticiple,
            pastparticiple_english) = row

            if 'Imperativo' in mood:
                # The order in the CSV is mixed up
                form_1s, form_2s, form_2p, form_1p, form_3s, form_3p = (
                    form_1s, form_2s, form_3s, form_1p, form_2p, form_3p)

            if infinitive == 'mudar(se)':
                infinitive = 'mudar'

            if infinitive == 'vomit':
                infinitive = 'vomitar'

            if infinitive not in verbs:
                verbs[infinitive] = {
                    'e_translation': english_translation,
                    'e_pparticiple': pastparticiple_english,
                    'e_gerund': gerund_english,
                    'forms': {
                        "Participio": [
                            pastparticiple_english,
                            pastparticiple
                        ],
                        "Gerundio": [
                            gerund_english,
                            gerund
                        ]
                    }
                }

                if english_translation == "to be":
                    verbs[infinitive]['english_template_type'] = "to_be"
                    verbs[infinitive]['e_present'] = 'be'
                    verbs[infinitive]['e_present3p'] = 'is'
                    verbs[infinitive]['e_past'] = 'was'
                elif english_translation.startswith("to be"):
                    verbs[infinitive]['english_template_type'] = "to_be_smth"
                    if verbs[infinitive]['e_pparticiple'].startswith('been '):
                        verbs[infinitive]['e_pparticiple'] = verbs[infinitive]['e_pparticiple'][5:]
                    verbs[infinitive]['e_present'] = 'be ' + verbs[infinitive]['e_pparticiple']
                    verbs[infinitive]['e_present3p'] = 'is ' + verbs[infinitive]['e_pparticiple']
                    verbs[infinitive]['e_past'] = 'was ' + verbs[infinitive]['e_pparticiple']
                else:
                    verbs[infinitive]['english_template_type'] = "regular"

            persons = [
                "1a persona; singular",
                "2a persona; singular",
                "3a persona; singular",
                "1a persona; plural",
                "2a persona; plural",
                "3a persona; plural",
                ]

            for i, form in enumerate([form_1s, form_2s, form_3s, form_1p, form_2p, form_3p]):
                if form == "":
                    continue
                form_key = tense + ' ' + mood + '; ' + persons[i]
                verbs[infinitive]['forms'][form_key] = [
                    verb_english,
                    form
                ]

            if verbs[infinitive]['english_template_type'] == 'regular':
                if tense == 'Futuro' and mood == 'Indicativo':
                    verbs[infinitive]['e_present'] = verb_extractor.search(verb_english).group(3)

                    verb_expr = verbs[infinitive]['e_present']
                    verb_parts = verb_expr.split(' ')

                    verbs[infinitive]['e_present3p'] = " ".join([verb_3p(verb_parts[0])] + verb_parts[1:])
                if tense == 'Pretérito' and mood == 'Indicativo':
                    verbs[infinitive]['e_past'] = verb_extractor.search(verb_english).group(3)

    return verbs


def irregular_forms(infinitive, csv_entry):
    pparticiple = csv_entry['forms']['Participio'][1]
    forms = collections.OrderedDict()

    # These are always regular, in the sense that they are always some form of haber + participio
    skip_tenses = [
        'Presente perfecto Indicativo',
        'Futuro perfecto Indicativo',
        'Pluscuamperfecto Indicativo',
        'Pretérito anterior Indicativo',
        'Condicional perfecto Indicativo',
        'Presente perfecto Subjuntivo',
        'Futuro perfecto Subjuntivo',
        'Pluscuamperfecto Subjuntivo',
        ]

    for form_key, form_entry in csv_entry['forms'].items():
        if any(tense in form_key for tense in skip_tenses):
            continue

        spanish = form_entry[1]
        ref = regular_form(infinitive, form_key, pparticiple)
        if spanish != ref:
            forms[form_key] = spanish

    return forms


def build_json(csv_data):

    json_entries = collections.OrderedDict()

    for infinitive, csv_entry in csv_data.items():

        iforms = irregular_forms(infinitive, csv_entry)

        json_entry = {
            "e_present": csv_entry['e_present'],
            "e_present3p": csv_entry['e_present3p'],
            "e_past": csv_entry['e_past'],
            "e_pparticiple": csv_entry['e_pparticiple'],
            "e_gerund": csv_entry['e_gerund'],
            "english_disambiguation": "",
            "irregular_forms": iforms,
            "english_template_type": csv_entry["english_template_type"],
        }

        json_entries[infinitive] = json_entry

    with open("verbs_jehle.json", 'w') as f:
        json.dump(json_entries, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    csv_data = load_csv()
    build_json(csv_data)
    save_corrected_verbs()
