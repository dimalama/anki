import genanki
import pandas as pd

# Load CSV
df = pd.read_csv('csv/spanish_ser_estar_tener_cloze.csv')

# Create model
model = genanki.Model(
  1607392319,
  'Spanish Ser, Estar, Tener Model',
  fields=[
    {'name': 'Text'},
    {'name': 'Translation'},
    {'name': 'Explanation'},
  ],
  templates=[
    {
      'name': 'Cloze Card',
      'qfmt': '{{cloze:Text}}',
      'afmt': '{{cloze:Text}}<hr><b>Translation:</b> {{Translation}}<br><b>Explanation:</b> {{Explanation}}',
    },
  ],
  css="""
    .card { font-family: arial; font-size: 20px; }
    .cloze { font-weight: bold; color: blue; }
  """,
  model_type=genanki.Model.CLOZE,
)

# Create deck
deck = genanki.Deck(2059400110, 'Spanish Ser, Estar, Tener (Cloze)')

# Add notes
for _, row in df.iterrows():
    note = genanki.Note(
        model=model,
        fields=[row['Text'], row['Translation'], row['Explanation']],
        tags=['spanish-ser-estar-tener']
    )
    deck.add_note(note)

# Export package
genanki.Package(deck).write_to_file('spanish_ser_estar_tener_cloze.apkg')
print("✅ Deck exported as spanish_ser_estar_tener_cloze.apkg")
