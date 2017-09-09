# - generate cards considering that some Spanish forms may be the same for different tenses and even
#   different verbs. Need to generate one-sided cards.
from collections import defaultdict
from itertools import product

from utils import *


# TOP 200 verbs by frequency, from http://world.arsu.org/pages-es/200-common-verbs/
TOP200_VERBS = [
'ser', 'haber', 'estar', 'tener', 'hacer',
'poder', 'decir', 'ir', 'ver', 'dar',
'saber', 'querer', 'llegar', 'pasar', 'deber',
'poner', 'parecer', 'quedar', 'creer', 'hablar',
'llevar', 'dejar', 'seguir', 'encontrar', 'llamar,',
'venir', 'pensar', 'salir', 'volver', 'tomar',
'conocer', 'vivir', 'sentir', 'tratar', 'mirar',
'contar', 'empezar', 'esperar', 'buscar', 'existir',
'entrar', 'trabajar', 'escribir', 'perder', 'producir',
'ocurrir', 'entender', 'pedir', 'recibir', 'recordar',
'terminar', 'permitir', 'aparecer', 'conseguir', 'comenzar',
'servir', 'sacar', 'necesitar', 'mantener', 'resultar',
'leer', 'caer', 'cambiar', 'presentar', 'crear',
'abrir', 'considerar', 'oír', 'acabar', 'convertir',
'ganar', 'formar', 'traer', 'partir', 'morir',
'aceptar', 'realizar', 'suponer', 'comprender', 'lograr',
'explicar', 'preguntar', 'tocar', 'reconocer', 'estudiar',
'alcanzar', 'nacer', 'dirigir', 'correr', 'utilizar',
'pagar', 'ayudar', 'gustar', 'jugar', 'escuchar',
'cumplir', 'ofrecer', 'descubrir', 'levantar', 'intentar',
'usar', 'decidir', 'repetir', 'olvidar', 'valer',
'comer', 'mostrar', 'ocupar', 'mover', 'continuar',
'suceder', 'fijar', 'referir', 'acercar', 'dedicar',
'aprender', 'comprar', 'subir', 'evitar', 'interesar',
'cerrar', 'echar', 'responder', 'sufrir', 'importar',
'obtener', 'observar', 'indicar', 'imaginar', 'soler',
'detener', 'desarrollar', 'señalar', 'elegir', 'preparar',
'proponer', 'demostrar', 'significar', 'reunir', 'faltar',
'acompañar', 'desear', 'enseñar', 'construir', 'vender',
'representar', 'desaparecer', 'mandar', 'andar', 'preferir',
'asegurar', 'crecer', 'surgir', 'matar', 'entregar',
'colocar', 'establecer', 'guardar', 'iniciar', 'bajar',
'notar', 'meter', 'actuar', 'pretender', 'acordar',
'cortar', 'corresponder', 'romper', 'adquirir', 'lanzar',
'aprovechar', 'apoyar', 'negar', 'avanzar', 'resolver',
'costar', 'exigir', 'aumentar', 'recoger', 'abandonar',
'imponer', 'obligar', 'aplicar', 'pertenecer', 'disponer',
'expresar', 'provocar', 'defender', 'quitar', 'conservar',
'depender', 'marcar', 'compartir', 'consistir', 'constituir',
'cubrir', 'funcionar', 'caber', 'atender', 'insistir',
]



def generate_cards(infinitives=None, tenses=None):
    json_data = load_verbs()

    cards = []

    if infinitives is None:
        infinitives = json_data

    if tenses is None:
        form_tags = TEMPLATE
    else:
        form_tags = [
            "; ".join([tense, person, plurality])
            for tense, person, plurality in product(
                tenses,
                ["1a persona", "2a persona", "3a persona"],
                ["singular", "plural"])]


    for infinitive in infinitives:

        entry = json_data[infinitive]

        has_irregular_forms = len(entry['irregular_forms']) > 0

        for form_tag in form_tags:

            template_entry = TEMPLATE[form_tag]

            if tenses is not None and form_tag.split(';')[0] not in tenses:
                continue

            english_template, spanish_templates = template_entry
            if form_tag in entry['irregular_forms']:
                irregular = True
                spanish = entry['irregular_forms'][form_tag]
            else:
                irregular = False
                if 'Participio' in entry['irregular_forms']:
                    pparticiple = entry['irregular_forms']['Participio']
                else:
                    pparticiple = regular_form(infinitive, 'Participio')

                spanish = regular_form(infinitive, form_tag, pparticiple)

            english_replacements = {
                "<e_present>": entry["e_present"],
                "<e_present3p>": entry["e_present3p"],
                "<e_past>": entry["e_past"],
                "<e_gerund>": entry["e_gerund"],
                "<e_pparticiple>": entry["e_pparticiple"]
            }
            english = english_template[entry["english_template_type"]]
            for code, rep in english_replacements.items():
                english = english.replace(code, rep)

            cards.append(dict(
                tags=[tag.strip().replace(" ", "-") for tag in form_tag.split(";")]
                    + (["irregular"] if irregular else [])
                    + (["has-irregular-forms"] if has_irregular_forms else []),
                english=english,
                spanish=spanish,
                english_disambiguation=entry['english_disambiguation'],
                ))

    return cards


def check_duplicate_cards(cards):
    english = defaultdict(lambda: [])
    for card in cards:
        english[(card['english_disambiguation'], card['english'])].append(card)

    print("* Cards with the same English side:")
    for en, cards in english.items():
        if len(cards) > 1:
            print(en)
            for card in cards:
                print(" ", card['spanish'])


def generate_unique_cards(cards):
    spanish_index = {}
    unique_cards = []

    disambiguation_note = lambda card: (
        ("(" + card['english_disambiguation'] + ") ")
        if card['english_disambiguation'] != ""
        else "")

    for card in cards:
        # English to Spanish
        unique_cards.append(dict(
            Front=disambiguation_note(card) + card['english'],
            Back=card['spanish'],
            Tags=" ".join(sorted(card['tags'] + ['eng-spa']))
            ))

        if card['spanish'] not in spanish_index:
            spanish_index[card['spanish']] = len(unique_cards)
            unique_cards.append([card])
        else:
            unique_cards[spanish_index[card['spanish']]].append(card)

    # Join cards with the repeating Spanish sides
    for spanish, idx in spanish_index.items():
        dup_cards = unique_cards[idx]
        back = "; ".join(
            disambiguation_note(card) + card['english']
            for card in dup_cards)
        tags = set(['spa-eng'])
        for card in dup_cards:
            tags = tags.union(card['tags'])
        tags = " ".join(sorted(tags))
        unique_cards[idx] = dict(
            Front=spanish,
            Back=back,
            Tags=tags
            )

    return unique_cards


def generate_my_cards():

    infinitives = TOP200_VERBS[:4]
    tenses = [
        'Presente Indicativo',
        'Pretérito Indicativo',
        ]

    cards = generate_cards(infinitives=infinitives, tenses=tenses)
    check_duplicate_cards(cards)
    unique_cards = generate_unique_cards(cards)
    for card in unique_cards:
        print(card)
    return unique_cards


if __name__ == '__main__':
    generate_my_cards()

