import sys
import os
sys.path.append("anki")
from anki.storage import Collection

from flashcards import generate_my_cards


def update_anki_deck(deck_name, new_cards):

    # Load Anki library

    # Define the path to the Anki SQLite collection
    PROFILE_HOME = os.path.expanduser("~/Library/Application Support/Anki2/User 1")
    cpath = os.path.join(PROFILE_HOME, "collection.anki2")
    col = Collection(cpath, log=True)

    # Load existing cards
    existing_cards = {}
    for card_id in col.findCards("deck:'" + deck_name + "'"):
        card = col.getCard(card_id)
        note = card.note()
        existing_cards[note['Front']] = dict(
            Id=card_id,
            Front=note['Front'],
            Back=note['Back'],
            Tags=" ".join(sorted(note.stringTags().strip().split(' '))))

    # Set the model
    modelBasic = col.models.byName('Basic')
    col.decks.current()['mid'] = modelBasic['id']

    # Get the deck
    deck = col.decks.byName(deck_name)

    for card in new_cards:

        if card['Front'] in existing_cards:
            existing_card = existing_cards[card['Front']]
            if existing_card['Back'] != card['Back'] or existing_card['Tags'] != card['Tags']:
                print("Replacing the card", card['Front'])
                col.remCards([existing_card['Id']])
            else:
                continue

        print("Adding a new card:", card['Front'], "-", card['Back'])

        # Instantiate the new note
        note = col.newNote()
        note.model()['did'] = deck['id']

        # Set the content
        note.fields[0] = card['Front']
        note.fields[1] = card['Back']

        # Set the tags (and add the new ones to the deck configuration
        note.tags = col.tags.canonify(col.tags.split(card['Tags']))
        m = note.model()
        m['tags'] = note.tags
        col.models.save(m)

        # Add the note
        col.addNote(note)


    # Save the changes to DB
    col.save()


if __name__ == '__main__':
    cards = generate_my_cards()
    # Note: the deck needs to be created manually
    update_anki_deck("Spanish verbs", cards)
