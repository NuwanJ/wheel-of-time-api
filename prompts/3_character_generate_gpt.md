Based on the "Wheel of Time" series by Robert Jordan, here is a list of main characters, antagonists, and notable groups. I want to parepare a detailed database of these characters and groups for a fan website.

Rand al'Thor
Perrin Aybara
Mat Cauthon
Egwene al'Vere
Nynaeve al'Meara
Elayne Trakand
Moiraine Damodred
Lan Mandragoran
Aviendha
Min Farshaw

Thom Merrilin
Loial
Birgitte Silverbow
Elyas Machera
Bayle Domon
Androl Genhald
Juilin Sandar
Valan Luca
Noal Charin

Ishamael
Demandred
Sammael
Asmodean
Rahvin
Be'lal
Aginor
Balthamel

Lanfear
Moghedien
Graendal
Mesaana
Semirhage

Moridin
Aran'gar
Osan'gar
Cyndane
Hessalam
M'hael

The Dark One
Shaidar Haran
Padan Fain
Slayer
Gholam
The Black Ajah
Shadowspawn

Siuan Sanche
Elaida do Avriny a'Roihan
Cadsuane Melaidhrin
Verin Mathwin
Sheriam Bayanar
Leane Sharif
Alviarin Friedhen
Pevara Tazanovni
Silviana Brehon

Faile Bashere
Gawyn Trakand
Galad Damodred
Tuon Athaem Kore Paendrag
Morgase Trakand
Berelain sur Paendrag Paeron
Logain Ablar
Dobraine Taborwin
Tylin Quintara Mitsobar

Amys
Rhuarc
Sorilea
Gaul
Bair
Sevanna
Melaine
Bain
Chiad
Therava

Rodel Ituralde
Pedron Niall
Gareth Bryne
Davram Bashere
Masema Dagar
Agelmar Jagad
Furyk Karede
Lunal Galgan

First, Please categorize them into Groups as follows:

- Protagonists
- Companions
- The Shadow
- Aes Sedai
- Nobles and Rulers
- Forsaken
- Aiel
- Military

Then based on the books and Fandom Wiki (<https://wot.fandom.com/wiki/Category:People>) collect the following details for each character, and save as a JSON array of objects under below format.

```json
{
  "id": "<integer>",
  "first_name": "<given name>",
  "last_name": "<family name>",
  "full_name": "<full name>",
  "nationality": "<nationality or origin>",
  "date_of_birth": "<date in series format>",
  "race": "<race or species>",
  "physical_appearance": {
    "gender": "<gender>",
    "height": "<height in cm>",
    "hair_color": "<hair color>",
    "eye_color": "<eye color>"
  },
  "titles": ["<list of titles>"],
  "other_names": ["<list of other names or nicknames>"],
  "rank": "<rank or position>",
  "belonged_groups": ["<list of groups>"],
  "first_appearance": {
    "book": "<book title>",
    "chapter": "<chapter title>"
  },
  "last_appearance": {
    "book": "<book title>",
    "chapter": "<chapter title>"
  },
  "description": "<brief character description>",
  "profile_picture": "<image URL>",
  "wiki_page_link": "<wiki URL>"
}
```

Output format:

- Single downloadable JSON file containing the categorized characters with their details as specified above.
