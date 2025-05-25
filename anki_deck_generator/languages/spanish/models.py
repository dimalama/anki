from anki_deck_generator.core import create_cloze_deck_generator, DeckGenerator

# Common fields for Spanish language decks
SPANISH_CLOZE_FIELDS = [
    {'name': 'Text'},
    {'name': 'Translation'},
    {'name': 'Explanation'},
]

# Spanish verb conjugation deck generators
def create_ser_estar_tener_deck() -> DeckGenerator:
    """Create a deck generator for Spanish ser/estar/tener verbs."""
    return create_cloze_deck_generator(
        model_id=1607392319,
        model_name='Spanish Ser, Estar, Tener Model',
        deck_id=2059400110,
        deck_name='Spanish Ser, Estar, Tener (Cloze)',
        fields=SPANISH_CLOZE_FIELDS,
        tags=['spanish', 'verbs', 'ser-estar-tener']
    )

def create_present_tense_regular_deck() -> DeckGenerator:
    """Create a deck generator for Spanish present tense regular verbs."""
    return create_cloze_deck_generator(
        model_id=1607392320,
        model_name='Spanish Present Tense Regular Model',
        deck_id=2059400111,
        deck_name='Spanish Present Tense Regular (Cloze)',
        fields=SPANISH_CLOZE_FIELDS,
        tags=['spanish', 'verbs', 'present-tense', 'regular']
    )

def create_present_tense_irregular_deck() -> DeckGenerator:
    """Create a deck generator for Spanish present tense irregular verbs."""
    return create_cloze_deck_generator(
        model_id=1607392321,
        model_name='Spanish Present Tense Irregular Model',
        deck_id=2059400112,
        deck_name='Spanish Present Tense Irregular (Cloze)',
        fields=SPANISH_CLOZE_FIELDS,
        tags=['spanish', 'verbs', 'present-tense', 'irregular']
    )

def create_present_tense_stem_changing_deck() -> DeckGenerator:
    """Create a deck generator for Spanish present tense stem-changing verbs."""
    return create_cloze_deck_generator(
        model_id=1607392322,
        model_name='Spanish Present Tense Stem-Changing Model',
        deck_id=2059400113,
        deck_name='Spanish Present Tense Stem-Changing (Cloze)',
        fields=SPANISH_CLOZE_FIELDS,
        tags=['spanish', 'verbs', 'present-tense', 'stem-changing']
    )

def create_preposition_deck() -> DeckGenerator:
    """Create a deck generator for Spanish prepositions."""
    return create_cloze_deck_generator(
        model_id=1607392323,
        model_name='Spanish Prepositions Model',
        deck_id=2059400114,
        deck_name='Spanish Prepositions (Cloze)',
        fields=SPANISH_CLOZE_FIELDS,
        tags=['spanish', 'grammar', 'prepositions']
    )
