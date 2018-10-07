from lxml import html
import requests
import json
import pickle

from utils import *


def get_spanishdict_all(infinitive):
    #Look into using the api .. http://translate1.spanishdict.com/api/v1/verb?q=ir&source=es 
    #I dont know if its legal thought .. check thier terms .. i think its not even your way.. but i dont think they care
    page = requests.get('http://www.spanishdict.com/conjugate/' + infinitive)
    return page.content


def get_spanishdict():
    with open('verbs.json') as f:
        verbs = json.load(f)

    data = {}
    for infinitive in sorted(verbs):
        print(infinitive)
        try:
            content = get_spanishdict_all(infinitive)
        except Exception as e:
            print(e)
            content = 'error'
        data[infinitive] = content

    with open('spanishdict_raw.pickle', 'wb') as f:
        pickle.dump(data, f)


def get_forms(sd_entry):
    tree = html.fromstring(sd_entry)
    card = tree.xpath('//div[@class="card"]')[0]

    shift = 1 if "View English conjugation" in card[2].text_content() else 0

    forms = {}

    forms['Gerundio'] = card[2 + shift][0][2].text_content()
    forms['Participio'] = card[3 + shift][0][2].text_content()

    indicative_panel = card[5 + shift]
    subjunctive_panel = card[7 + shift]
    imperative_panel = card[9 + shift]

    row_tags = [
        '1a persona; singular',
        '2a persona; singular',
        '3a persona; singular',
        '1a persona; plural',
        '2a persona; plural',
        '3a persona; plural',
        ]

    indicative_columns = [
        'Presente Indicativo',
        'Pretérito Indicativo',
        'Imperfecto Indicativo',
        'Condicional Indicativo',
        'Futuro Indicativo']

    subjunctive_columns = [
        'Presente Subjuntivo',
        'Imperfecto Subjuntivo',
        'Imperfecto 2 Subjuntivo',
        'Futuro Subjuntivo']

    imperative_columns = [
        'Presente Imperativo Afirmativo',
        'Presente Imperativo Negativo']

    indicative_rows = indicative_panel[0][1:7]
    subjunctive_rows = subjunctive_panel[0][1:7]
    imperative_rows = imperative_panel[0][1:7]

    for tense_i, tense_tag in enumerate(indicative_columns):
        for row_i, row_tag in enumerate(row_tags):
            sd_form = indicative_rows[row_i][1+tense_i][0][0].text_content()
            forms[tense_tag + '; '+ row_tag] = sd_form

    for tense_i, tense_tag in enumerate(subjunctive_columns):
        for row_i, row_tag in enumerate(row_tags):
            sd_form = subjunctive_rows[row_i][1+tense_i][0][0].text_content()
            forms[tense_tag + '; '+ row_tag] = sd_form

    for tense_i, tense_tag in enumerate(imperative_columns):
        for row_i, row_tag in enumerate(row_tags[1:]):
            sd_form = imperative_rows[row_i+1][1+tense_i][0][0].text_content()
            forms[tense_tag + '; '+ row_tag] = sd_form

    for form_tag, form in forms.items():
        form = form.split(',')[0]
        forms[form_tag] = form

    return forms


def get_sd_forms():
    with open('spanishdict_raw.pickle', 'rb') as f:
        sd_data_raw = pickle.load(f)

    sd_data_parsed = {}
    for infinitive, sd_raw in sd_data_raw.items():
        try:
            forms = get_forms(sd_raw)
            sd_data_parsed[infinitive] = forms
        except:
            print("Parsing failed:", infinitive)

    with open('spanishdict_parsed.json', 'w') as f:
        json.dump(sd_data_parsed, f, indent=4, ensure_ascii=False)


def build_1p_imperative_corrections():

    verbs = load_verbs()

    with open('spanishdict_parsed.json') as f:
        sd_data = json.load(f)

    corrs = {}
    for infinitive in list(verbs):

        if infinitive not in sd_data:
            print("Missing:", infinitive)
            continue

        aff_tag = "Presente Imperativo Afirmativo; 1a persona; plural"
        neg_tag = "Presente Imperativo Negativo; 1a persona; plural"
        aff = sd_data[infinitive][aff_tag]
        neg = sd_data[infinitive][neg_tag]
        aff_is_regular = (aff == regular_form(infinitive, aff_tag))
        neg_is_regular = (neg == regular_form(infinitive, neg_tag))

        corr_entry = {}

        if not aff_is_regular:
            corr_entry[aff_tag] = aff
        if not neg_is_regular:
            corr_entry[neg_tag] = neg
        if len(corr_entry) > 0:
            corrs[infinitive] = {'irregular_forms': corr_entry}

    with open('corrections_1p_imperative.json', 'w') as f:
        json.dump(corrs, f, indent=4, ensure_ascii=False)


def check_with_sd():
    verbs = load_verbs()
    with open('spanishdict_parsed.json') as f:
        sd_data = json.load(f)

    for infinitive, entry in verbs.items():
        if infinitive not in sd_data:
            continue
        if infinitive in ['quejarse', 'acostumbrarse', 'broncearse', 'huir', 'oponerse']:
            continue

        pparticiple = regular_form(infinitive, "Participio")
        for form_tag in TEMPLATE:

            if form_tag in entry['irregular_forms']:
                my_form = entry['irregular_forms'][form_tag]
            else:
                my_form = regular_form(infinitive, form_tag, pparticiple)

            if ',' in my_form:
                print("comma found:", infinitive, form_tag, my_form)
                continue

            if form_tag not in sd_data[infinitive]:
                continue

            sd_form = sd_data[infinitive][form_tag]
            if form_tag == 'Gerundio' and infinitive.endswith("se"):
                my_form = my_form[:-6]
                sd_form = sd_form[:-4]

            if my_form != sd_form:
                print("discrepancy found:", infinitive, form_tag, my_form, sd_form)




if __name__ == '__main__':
    #get_spanishdict()
    #get_sd_forms()
    #build_1p_imperative_corrections()
    check_with_sd()
