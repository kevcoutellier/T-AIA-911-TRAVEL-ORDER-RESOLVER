# Sentence Structure Templates for Travel Order Dataset

## Overview
This document provides comprehensive sentence templates for generating the training dataset (~10,000 sentences). The dataset should contain 70% valid travel orders and 30% invalid/trash text.

## Valid Travel Order Structures

### 1. Direct Format (Simple)
**Pattern:** `Je voudrais un billet [ORIGIN] [DESTINATION]`

Examples:
- Je voudrais un billet Toulouse Paris
- Je souhaite un billet Lyon Marseille
- J'aimerais un billet Bordeaux Lille
- Je veux un billet Nice Strasbourg

**Variations:**
- Missing capitals: `je voudrais un billet toulouse paris`
- No accents: `je voudrais un billet paris lyon`
- Informal: `Je veux un ticket Paris Lyon`

---

### 2. With Prepositions (Standard)
**Pattern:** `Je [VERB] [PREP_DEST] [DESTINATION] [PREP_ORIGIN] [ORIGIN]`

**Verbs:** voudrais, souhaite, aimerais, désire, veux, dois
**Prep Origin:** de, depuis, en partant de, en partance de, au départ de
**Prep Dest:** à, vers, pour, jusqu'à, en direction de

Examples:
- Je souhaite me rendre à Paris depuis Toulouse
- Je voudrais aller de Lyon à Marseille
- Je dois partir de Bordeaux vers Nice
- J'aimerais voyager depuis Lille pour Paris
- Je veux me déplacer de Tours vers Nantes

**Variations:**
- No accents: `je souhaite me rendre a paris depuis toulouse`
- Missing hyphens: `port boulet` instead of `Port-Boulet`
- Mixed order: origin before destination or vice versa

---

### 3. Question Format
**Pattern:** `[QUESTION] [DESTINATION] [PREP_ORIGIN] [ORIGIN]?`

**Question starters:**
- À quelle heure y a-t-il des trains vers/pour/à
- Comment me rendre à/vers
- Quel est l'horaire des trains pour/vers
- Y a-t-il un train pour/vers/à
- Existe-t-il un train pour

Examples:
- À quelle heure y a-t-il des trains vers Paris en partance de Toulouse?
- Comment me rendre à Port Boulet depuis Tours?
- Quel est l'horaire des trains pour Lyon au départ de Paris?
- Y a-t-il un train pour Marseille depuis Nice?
- Existe-t-il un train direct de Bordeaux à La Rochelle?

**Variations:**
- No question mark
- Inverted grammar
- Missing accents: `a quelle heure`

---

### 4. Inverted Order (Destination First)
**Pattern:** `[DESTINATION] depuis/de [ORIGIN]`

Examples:
- Paris depuis Toulouse
- Lyon en partant de Marseille
- Comment aller à Bordeaux de Nice
- Je veux aller à Tours depuis Paris
- Horaires pour Lyon au départ de Grenoble

---

### 5. Complex Sentences with Names
**Pattern:** Sentences containing city names that are also people names

**Challenging cities:** Paris, Albert, Florence, Lourdes, Amiens

Examples:
- Avec mes amis Florence et Paris, je voudrais aller de Paris à Florence
- Je veux aller à Tours voir mon ami Albert en partant de Bordeaux
- Mon amie Lourdes voyage de Toulouse à Lourdes demain
- Albert et moi souhaitons partir de Albert vers Paris
- Florence m'accompagne de Lyon vers Florence en Italie

**Key Challenge:** NLP must distinguish person names from city names using context

---

### 6. With Time References
**Pattern:** `[TRAVEL_ORDER] [TIME_REF]`

**Time references:**
- demain, aujourd'hui, ce soir
- lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche
- lundi prochain, ce week-end
- dans l'après-midi, en matinée
- à 10h, vers 15h

Examples:
- Je voudrais un billet Paris Lyon pour demain
- Je souhaite partir de Toulouse vers Bordeaux lundi prochain
- Y a-t-il un train de Nice à Marseille ce soir?
- Je dois être à Paris depuis Lyon demain matin
- Train pour Lille au départ de Paris à 14h30

---

### 7. Multi-word Station Names
**Pattern:** Using stations with hyphens, apostrophes, or multiple words

**Cities to include:**
- Port-Boulet, La Rochelle, Le Havre, Le Mans
- Aix-en-Provence, Bourg-Saint-Maurice
- L'Isle-sur-la-Sorgue
- Saint-Étienne, Saint-Nazaire

Examples:
- Je veux aller à Port-Boulet depuis Tours
- Comment me rendre à Aix-en-Provence de Marseille
- Train pour La Rochelle en partance de Bordeaux
- Je souhaite partir du Havre vers Paris
- Billet de Bourg-Saint-Maurice à Lyon

**Variations:**
- Missing hyphens: `port boulet`, `aix en provence`
- Missing apostrophes: `l isle sur la sorgue`
- Wrong spacing: `port-  boulet`

---

### 8. Informal/Colloquial
**Pattern:** Using informal French

Examples:
- Je vais à Paris de Lyon
- Faut que j'aille à Marseille depuis Nice
- J'ai besoin d'un train pour Toulouse
- Ça part à quelle heure de Bordeaux pour Paris?
- Un ticket Paris Lille s'il vous plaît

---

### 9. Polite/Formal
**Pattern:** Using formal French structures

Examples:
- Je voudrais solliciter un billet de train de Toulouse à Paris
- Pourriez-vous m'indiquer les horaires pour me rendre à Lyon depuis Marseille?
- Je souhaiterais réserver une place dans le train en direction de Bordeaux
- Auriez-vous l'amabilité de me renseigner sur les trains pour Paris?
- Je me permets de vous demander les horaires de Lille vers Strasbourg

---

### 10. With Intermediate Stops (BONUS)
**Pattern:** `[ORIGIN] à [DESTINATION] en passant par [INTERMEDIATE]`

Examples:
- Je veux aller de Toulouse à Paris en passant par Limoges
- Train de Marseille vers Lyon avec arrêt à Valence
- Bordeaux Paris via Tours
- Partir de Nice pour Paris en passant par Lyon

---

## Invalid Travel Orders (30% of dataset)

### 1. Missing Information
Examples:
- Je veux aller à Paris (no origin)
- Train depuis Lyon (no destination)
- Y a-t-il des trains demain? (no origin or destination)

### 2. Nonsense/Garbage Text
Examples:
- azerty qwerty uiop
- 123456789 test test
- Lorem ipsum dolor sit amet
- aaa bbb ccc ddd eee fff

### 3. Unrelated Questions
Examples:
- Quel temps fait-il à Paris?
- J'aime manger des croissants
- Comment allez-vous aujourd'hui?
- Quelle est la capitale de la France?
- Paris est une belle ville

### 4. Ambiguous Without Context
Examples:
- Je pars demain (no cities)
- Mon ami voyage ce soir (no cities)
- Le train est en retard (no cities)
- Réservation annulée (no cities)

### 5. Non-existent Stations
Examples:
- Je veux aller de Atlantis à Gotham
- Train pour Narnia depuis Poudlard
- Billet Westeros Mordor
- Partir de Wakanda vers Asgard

---

## City/Station Lists

### Major French Cities (Must Include)
Paris, Lyon, Marseille, Toulouse, Bordeaux, Nice, Nantes, Strasbourg, Montpellier, Lille, Rennes, Reims, Le Havre, Saint-Étienne, Toulon, Grenoble, Dijon, Angers, Nîmes, Villeurbanne, Clermont-Ferrand, Limoges, Tours, Amiens, Metz, Besançon, Perpignan, Orléans, Brest, Mulhouse, Caen, Boulogne-Billancourt, Rouen, Nancy

### Cities with Ambiguous Names
- **Albert**: Person name / City in Somme
- **Paris**: Person name / Capital city
- **Florence**: Person name / City in Italy (sometimes travel context)
- **Lourdes**: Person name / City in Hautes-Pyrénées
- **Amiens**: Can be confusing with "amis" (friends)

### Multi-word Stations
Port-Boulet, La Rochelle, Le Havre, Le Mans, Aix-en-Provence, Bourg-Saint-Maurice, Bourg-en-Bresse, La Souterraine, Le Creusot, Saint-Pierre-des-Corps, Champagne-Ardenne, Vitry-le-François

---

## Variations to Apply Systematically

### 1. Capitalization
- All lowercase: `je veux aller de paris a lyon`
- No city capitals: `je veux aller de paris à Lyon`
- ALL CAPS: `JE VEUX ALLER DE PARIS A LYON`
- Random: `jE VeUx AlLeR dE pArIs A lYoN`

### 2. Accents
- No accents: `a` instead of `à`, `e` instead of `é/è/ê`
- Extra accents: `pàris`, `lyôn`
- Wrong accents: `â` instead of `à`

### 3. Spacing
- Extra spaces: `Je  veux  aller`
- No spaces: `Jeveuxaller`
- Wrong hyphen spacing: `Port - Boulet`, `Port -Boulet`

### 4. Typos/Misspellings
Common misspellings to include:
- `Parris`, `Parus` (Paris)
- `Lyyon`, `Lylon` (Lyon)
- `Marsseille`, `Marceille` (Marseille)
- `Tolouse`, `Toulouze` (Toulouse)
- `Bordeax`, `Bordo` (Bordeaux)

---

## Generation Strategy

### Distribution
- 70% valid orders (7,000 sentences)
  - 20% direct format (1,400)
  - 25% with prepositions (1,750)
  - 15% question format (1,050)
  - 10% inverted order (700)
  - 10% complex with names (700)
  - 10% with time references (700)
  - 5% multi-word stations (350)
  - 5% informal/formal mix (350)

- 30% invalid orders (3,000 sentences)
  - 40% missing information (1,200)
  - 30% nonsense/garbage (900)
  - 20% unrelated questions (600)
  - 10% ambiguous (300)

### Variation Application
For each template sentence, generate variations with:
- 50% with some variation (missing capitals, accents, etc.)
- 20% with multiple variations
- 10% with misspellings
- 20% perfect formatting

---

## Dataset Split
- **Training:** 70% (7,000 sentences)
- **Validation:** 15% (1,500 sentences)
- **Test:** 15% (1,500 sentences)

Total: 10,000 sentences

---

## CSV Format
```csv
sentenceID,sentence
1,Je voudrais un billet Toulouse Paris
2,je veux aller a lyon depuis paris
3,INVALID
```

For invalid sentences, the origin and destination are "INVALID".

---

## Next Steps
1. Generate sentences using these templates
2. Apply variations systematically
3. Collaborate with other groups to diversify dataset
4. Review for quality and balance
5. Split into train/val/test sets
