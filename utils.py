import json


with open('template.json') as f:
    TEMPLATE = json.load(f)


def split_inifinitive(infinitive):
    if infinitive.endswith('se'):
        reflexive = True
        infinitive = infinitive[:-2]
    else:
        reflexive = False

    stem = infinitive[:-2]
    ending = infinitive[-2:]

    if ending == "ír":
        ending = "ir"

    return infinitive, stem, ending, reflexive


def stress_final_vowel(stem):
    vowels = [i for (i, e) in enumerate(stem) if e in 'aeoiuáéóíú']
    replacements = {"a": "á", "e": "é", "o": "ó", "i": "í", "u": "ú"}

    if len(vowels) > 0:
        if (len(vowels) > 1 and vowels[-2] + 1 == vowels[-1]
                and stem[vowels[-2]:vowels[-2]+2] in ['ei', 'ia']):
            last_idx = vowels[-2]
        else:
            last_idx = vowels[-1]
        last_vowel = stem[last_idx]
    else:
        last_vowel = None

    if last_vowel in replacements:
        mod_stem = stem[:last_idx] + replacements[last_vowel] + stem[last_idx+1:]
    else:
        mod_stem = stem

    return mod_stem


def regular_form(infinitive, form_key, pparticiple=None):
    nonreflexive_inf, stem, ending, reflexive = split_inifinitive(infinitive)

    res = TEMPLATE[form_key][1][ending + ("se" if reflexive else "")]

    replacements = {
        '<s_stem>': stem,
        '<s_stem_stressed>': stress_final_vowel(stem),
        '<s_pparticiple>': (pparticiple if pparticiple is not None else "<s_pparticiple>")
    }

    for code, rep in replacements.items():
        res = res.replace(code, rep)

    return res


def load_verbs():

    with open('verbs.json') as f:
        verbs = json.load(f)

    return verbs
