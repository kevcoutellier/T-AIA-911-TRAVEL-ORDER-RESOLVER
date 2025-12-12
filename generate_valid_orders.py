#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate valid travel orders dataset (3,000 phrases)

Categories:
1. Standard (800): Clear markers
2. Inverted order (400): Destination before origin
3. No markers (300): "billet X Y"
4. Name ambiguities (500): Florence, Paris, Albert, Lourdes
5. Compound names (250): Port-Boulet, Aix-en-Provence
6. Spelling errors (300): misspellings
7. No capitals/accents (250): lowercase
8. Additional info (150): times, passengers
9. Complex questions (50): "fastest way", "how long"

Difficulty distribution:
- Easy (900): 30%
- Medium (1,500): 50%
- Hard (600): 20%
"""

import csv
import random

# Cities for France (top 30 + complex cases)
MAIN_CITIES = [
    "Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes",
    "Strasbourg", "Montpellier", "Bordeaux", "Lille", "Rennes",
    "Reims", "Saint-Étienne", "Le Havre", "Toulon", "Grenoble",
    "Dijon", "Angers", "Nîmes", "Villeurbanne", "Le Mans",
    "Aix-en-Provence", "Clermont-Ferrand", "Brest", "Tours",
    "Amiens", "Limoges", "Annecy", "Perpignan", "Metz"
]

COMPOUND_CITIES = [
    "Port-Boulet", "Bourg-en-Bresse", "Aix-en-Provence",
    "Saint-Étienne", "La Roche-sur-Yon", "Salon-de-Provence",
    "Aix-les-Bains", "Boulogne-sur-Mer", "Châlons-en-Champagne"
]

AMBIGUOUS_NAMES = ["Albert", "Florence", "Paris", "Lourdes", "Rémy", "Clément"]

# Common misspellings
MISSPELLINGS = {
    "Paris": ["Pari", "Paric", "Pariss"],
    "Lyon": ["Lion", "Lyo", "Lionne"],
    "Marseille": ["Marsel", "Marseile", "Marceille"],
    "Toulouse": ["Tolouse", "Toulouze", "Toulouse"],
    "Nice": ["Nise", "Nices", "Nisse"],
    "Bordeaux": ["Bordo", "Bordeau", "Bordeaus"],
    "Lille": ["Lile", "Lilles", "Lill"],
    "Nantes": ["Nante", "Nantess", "Nantez"],
    "Tours": ["Tour", "Tourz", "Toure"],
}

def misspell(city):
    """Return a misspelled version of a city name"""
    if city in MISSPELLINGS:
        return random.choice(MISSPELLINGS[city])
    # Generic misspelling: remove last letter or double a letter
    if len(city) > 4:
        if random.random() < 0.5:
            return city[:-1]
        else:
            idx = random.randint(1, len(city)-2)
            return city[:idx] + city[idx] + city[idx:]
    return city

def generate_standard(count=800):
    """Generate standard phrases with clear markers"""

    templates_easy = [
        ("Je voudrais un billet de {origin} à {dest}", "easy"),
        ("Je souhaite me rendre à {dest} depuis {origin}", "easy"),
        ("Un aller simple de {origin} à {dest}", "easy"),
        ("Un billet {origin} {dest} s'il vous plaît", "easy"),
        ("Je veux aller de {origin} à {dest}", "easy"),
        ("Comment aller de {origin} à {dest}", "easy"),
        ("Quel est le prix d'un billet de {origin} à {dest}", "easy"),
        ("Y a-t-il un train de {origin} vers {dest}", "easy"),
        ("Je cherche un train de {origin} à {dest}", "easy"),
        ("Pouvez-vous me donner les horaires de {origin} à {dest}", "easy"),
        ("Un train de {origin} pour {dest}", "easy"),
        ("Je dois me rendre de {origin} à {dest}", "easy"),
        ("Trajet de {origin} vers {dest}", "easy"),
        ("Départ {origin} arrivée {dest}", "easy"),
        ("De {origin} vers {dest} s'il vous plaît", "easy"),
    ]

    templates_medium = [
        ("Quand part le prochain train de {origin} vers {dest}", "medium"),
        ("À quelle heure y a-t-il des trains de {origin} à {dest}", "medium"),
        ("Quel est l'horaire des trains au départ de {origin} pour {dest}", "medium"),
        ("Combien coûte un billet de train de {origin} à {dest}", "medium"),
        ("Je voudrais réserver un billet de {origin} pour {dest}", "medium"),
        ("Pouvez-vous me réserver une place de {origin} à {dest}", "medium"),
        ("Y a-t-il des trains directs de {origin} à {dest}", "medium"),
        ("Quel est le temps de trajet de {origin} à {dest}", "medium"),
    ]

    phrases = []
    sentence_id = 1

    # 70% easy, 30% medium
    easy_count = int(count * 0.7)
    medium_count = count - easy_count

    for _ in range(easy_count):
        template, difficulty = random.choice(templates_easy)
        origin = random.choice(MAIN_CITIES)
        dest = random.choice([c for c in MAIN_CITIES if c != origin])

        sentence = template.format(origin=origin, dest=dest)

        phrases.append({
            'sentenceID': sentence_id,
            'sentence': sentence,
            'origin': origin,
            'destination': dest,
            'is_valid': 1,
            'difficulty': difficulty,
            'category': 'standard',
            'notes': ''
        })
        sentence_id += 1

    for _ in range(medium_count):
        template, difficulty = random.choice(templates_medium)
        origin = random.choice(MAIN_CITIES)
        dest = random.choice([c for c in MAIN_CITIES if c != origin])

        sentence = template.format(origin=origin, dest=dest)

        phrases.append({
            'sentenceID': sentence_id,
            'sentence': sentence,
            'origin': origin,
            'destination': dest,
            'is_valid': 1,
            'difficulty': difficulty,
            'category': 'standard',
            'notes': ''
        })
        sentence_id += 1

    return phrases, sentence_id

def generate_inverted_order(count=400, start_id=1):
    """Generate phrases with inverted order (destination before origin)"""

    templates = [
        ("Je veux aller à {dest} en partant de {origin}", "medium"),
        ("Comment se rendre à {dest} si on part de {origin}", "medium"),
        ("Pour aller à {dest} depuis {origin}", "medium"),
        ("À {dest} en partance de {origin}", "medium"),
        ("Vers {dest} au départ de {origin}", "medium"),
        ("Direction {dest} en partant de {origin}", "medium"),
        ("Cap sur {dest} depuis {origin}", "medium"),
        ("Je me rends à {dest} en provenance de {origin}", "medium"),
        ("Trajet vers {dest} au départ de {origin}", "medium"),
        ("Pour me rendre à {dest} je pars de {origin}", "medium"),
    ]

    phrases = []
    sentence_id = start_id

    for _ in range(count):
        template, difficulty = random.choice(templates)
        origin = random.choice(MAIN_CITIES)
        dest = random.choice([c for c in MAIN_CITIES if c != origin])

        sentence = template.format(origin=origin, dest=dest)

        phrases.append({
            'sentenceID': sentence_id,
            'sentence': sentence,
            'origin': origin,
            'destination': dest,
            'is_valid': 1,
            'difficulty': difficulty,
            'category': 'inverted_order',
            'notes': ''
        })
        sentence_id += 1

    return phrases, sentence_id

def generate_no_markers(count=300, start_id=1):
    """Generate phrases without clear markers"""

    templates = [
        ("Billet {origin} {dest}", "medium"),
        ("Trajet {origin} {dest}", "medium"),
        ("{origin} {dest} demain", "medium"),
        ("{origin} {dest} s'il vous plaît", "medium"),
        ("Un billet {origin} {dest}", "easy"),
        ("Réservation {origin} {dest}", "medium"),
        ("{origin} {dest} aujourd'hui", "medium"),
        ("{origin} {dest} ce soir", "medium"),
        ("Train {origin} {dest}", "easy"),
        ("{origin} {dest} aller simple", "medium"),
    ]

    phrases = []
    sentence_id = start_id

    for _ in range(count):
        template, difficulty = random.choice(templates)
        origin = random.choice(MAIN_CITIES)
        dest = random.choice([c for c in MAIN_CITIES if c != origin])

        sentence = template.format(origin=origin, dest=dest)

        phrases.append({
            'sentenceID': sentence_id,
            'sentence': sentence,
            'origin': origin,
            'destination': dest,
            'is_valid': 1,
            'difficulty': difficulty,
            'category': 'no_markers',
            'notes': ''
        })
        sentence_id += 1

    return phrases, sentence_id

def generate_name_ambiguities(count=500, start_id=1):
    """Generate phrases with ambiguous proper names"""

    # Required examples from spec
    required = [
        {
            'sentence': "Avec mes amis florence et paris, je voudrais aller de paris a florence",
            'origin': "Paris",
            'destination': "Florence",
            'difficulty': "hard",
            'notes': "lowercase, florence/paris=prénoms"
        },
        {
            'sentence': "Je veux aller à Tours voir mon ami Albert en partant de Bordeaux",
            'origin': "Bordeaux",
            'destination': "Tours",
            'difficulty': "medium",
            'notes': "Albert=prénom"
        },
    ]

    templates_with_distractors = [
        ("Je vais à {dest} voir mon ami {name} en partant de {origin}", "medium", "{name}=prénom"),
        ("Avec mon ami {name} je voudrais aller de {origin} à {dest}", "medium", "{name}=prénom"),
        ("Je dois rejoindre {name} à {dest} depuis {origin}", "medium", "{name}=prénom"),
        ("Mon ami {name} m'attend à {dest} je pars de {origin}", "medium", "{name}=prénom"),
        ("Retrouver {name} à {dest} en partant de {origin}", "hard", "{name}=prénom"),
        ("Avec mes amis {name1} et {name2}, je voudrais aller de {origin} à {dest}", "hard", "{name1}/{name2}=prénoms"),
        ("Je voyage avec {name1} et {name2} de {origin} vers {dest}", "hard", "{name1}/{name2}=prénoms"),
        ("{name1}, {name2} et moi voulons aller de {origin} à {dest}", "hard", "{name1}/{name2}=prénoms"),
    ]

    phrases = []
    sentence_id = start_id

    # Add required examples
    for req in required:
        phrases.append({
            'sentenceID': sentence_id,
            'sentence': req['sentence'],
            'origin': req['origin'],
            'destination': req['destination'],
            'is_valid': 1,
            'difficulty': req['difficulty'],
            'category': 'name_ambiguity',
            'notes': req['notes']
        })
        sentence_id += 1

    # Generate remaining
    remaining = count - len(required)

    for _ in range(remaining):
        template, difficulty, note_template = random.choice(templates_with_distractors)

        # Choose cities (may include ambiguous names)
        if random.random() < 0.3:
            # Use ambiguous name as city
            dest = random.choice(["Paris", "Florence"])
            origin = random.choice([c for c in MAIN_CITIES if c != dest and c not in AMBIGUOUS_NAMES])
        else:
            origin = random.choice(MAIN_CITIES)
            dest = random.choice([c for c in MAIN_CITIES if c != origin])

        # Choose distractor names
        name = random.choice(AMBIGUOUS_NAMES)
        name1 = random.choice(AMBIGUOUS_NAMES)
        name2 = random.choice([n for n in AMBIGUOUS_NAMES if n != name1])

        # Format sentence
        sentence = template.format(
            origin=origin,
            dest=dest,
            name=name,
            name1=name1,
            name2=name2
        )

        # Lowercase variation for hard difficulty
        if difficulty == "hard" and random.random() < 0.5:
            sentence = sentence.lower()
            note = note_template + ", lowercase"
        else:
            note = note_template

        phrases.append({
            'sentenceID': sentence_id,
            'sentence': sentence,
            'origin': origin,
            'destination': dest,
            'is_valid': 1,
            'difficulty': difficulty,
            'category': 'name_ambiguity',
            'notes': note.format(name=name, name1=name1, name2=name2)
        })
        sentence_id += 1

    return phrases, sentence_id

def generate_compound_names(count=250, start_id=1):
    """Generate phrases with compound city names"""

    # Required example
    required = [
        {
            'sentence': "Comment me rendre à Port Boulet depuis Tours",
            'origin': "Tours",
            'destination': "Port-Boulet",
            'difficulty': "medium",
            'notes': "compound name no hyphen"
        },
    ]

    templates = [
        ("Je veux aller de {origin} à {dest}", "medium"),
        ("Un billet de {origin} pour {dest}", "medium"),
        ("Comment aller à {dest} depuis {origin}", "medium"),
        ("Trajet {origin} {dest}", "medium"),
        ("De {origin} vers {dest}", "medium"),
        ("Je souhaite me rendre à {dest} en partant de {origin}", "medium"),
        ("Billet {origin} {dest}", "medium"),
        ("Train de {origin} à {dest}", "medium"),
    ]

    phrases = []
    sentence_id = start_id

    # Add required
    for req in required:
        phrases.append({
            'sentenceID': sentence_id,
            'sentence': req['sentence'],
            'origin': req['origin'],
            'destination': req['destination'],
            'is_valid': 1,
            'difficulty': req['difficulty'],
            'category': 'compound_name',
            'notes': req['notes']
        })
        sentence_id += 1

    # Generate remaining
    remaining = count - len(required)

    for _ in range(remaining):
        template, difficulty = random.choice(templates)

        # One city must be compound
        if random.random() < 0.5:
            origin = random.choice(COMPOUND_CITIES)
            dest = random.choice(MAIN_CITIES)
        else:
            origin = random.choice(MAIN_CITIES)
            dest = random.choice(COMPOUND_CITIES)

        sentence = template.format(origin=origin, dest=dest)

        # Sometimes remove hyphens
        sentence_display = sentence
        if random.random() < 0.3:
            sentence_display = sentence.replace("-", " ")
            note = "compound name no hyphen"
        else:
            note = "compound name"

        phrases.append({
            'sentenceID': sentence_id,
            'sentence': sentence_display,
            'origin': origin,
            'destination': dest,
            'is_valid': 1,
            'difficulty': difficulty,
            'category': 'compound_name',
            'notes': note
        })
        sentence_id += 1

    return phrases, sentence_id

def generate_misspellings(count=300, start_id=1):
    """Generate phrases with spelling errors"""

    templates = [
        ("Je veux aller de {origin} à {dest}", "hard"),
        ("Un billet {origin} {dest}", "hard"),
        ("Comment aller a {dest} depuis {origin}", "hard"),
        ("Trajet {origin} {dest}", "hard"),
        ("Je voudrais un bilet de {origin} à {dest}", "hard"),
        ("Commen aler de {origin} a {dest}", "hard"),
        ("Je souhaite me rendre a {dest} depui {origin}", "hard"),
        ("Bilet {origin} {dest}", "hard"),
    ]

    phrases = []
    sentence_id = start_id

    for _ in range(count):
        template, difficulty = random.choice(templates)

        origin = random.choice(MAIN_CITIES)
        dest = random.choice([c for c in MAIN_CITIES if c != origin])

        # Apply misspellings
        if random.random() < 0.7:
            origin_misspelled = misspell(origin)
        else:
            origin_misspelled = origin

        if random.random() < 0.7:
            dest_misspelled = misspell(dest)
        else:
            dest_misspelled = dest

        sentence = template.format(origin=origin_misspelled, dest=dest_misspelled)

        # Lowercase
        if random.random() < 0.6:
            sentence = sentence.lower()

        phrases.append({
            'sentenceID': sentence_id,
            'sentence': sentence,
            'origin': origin,
            'destination': dest,
            'is_valid': 1,
            'difficulty': difficulty,
            'category': 'misspelling',
            'notes': 'spelling errors'
        })
        sentence_id += 1

    return phrases, sentence_id

def generate_no_capitals(count=250, start_id=1):
    """Generate phrases without capitals or accents"""

    templates = [
        ("je voudrais un billet de {origin} a {dest}", "medium"),
        ("comment aller a {dest} depuis {origin}", "medium"),
        ("je veux aller de {origin} a {dest}", "medium"),
        ("un billet {origin} {dest} s'il vous plait", "medium"),
        ("je souhaite me rendre a {dest} depuis {origin}", "medium"),
        ("trajet {origin} {dest}", "medium"),
        ("billet {origin} {dest}", "medium"),
        ("je dois aller de {origin} a {dest}", "medium"),
        ("de {origin} vers {dest}", "medium"),
        ("un train de {origin} a {dest}", "medium"),
    ]

    phrases = []
    sentence_id = start_id

    for _ in range(count):
        template, difficulty = random.choice(templates)

        origin = random.choice(MAIN_CITIES)
        dest = random.choice([c for c in MAIN_CITIES if c != origin])

        sentence = template.format(origin=origin.lower(), dest=dest.lower())

        phrases.append({
            'sentenceID': sentence_id,
            'sentence': sentence,
            'origin': origin,
            'destination': dest,
            'is_valid': 1,
            'difficulty': difficulty,
            'category': 'no_capitals',
            'notes': 'lowercase, no accents'
        })
        sentence_id += 1

    return phrases, sentence_id

def generate_additional_info(count=150, start_id=1):
    """Generate phrases with additional information"""

    templates = [
        ("Je voudrais un billet de {origin} à {dest} pour demain", "medium"),
        ("Un billet {origin} {dest} pour 2 adultes", "medium"),
        ("Combien coûte un billet de {origin} à {dest}", "medium"),
        ("Quel est le prix d'un aller simple de {origin} à {dest}", "medium"),
        ("Je veux aller de {origin} à {dest} demain matin", "medium"),
        ("Un billet {origin} {dest} pour ce soir", "medium"),
        ("Deux billets de {origin} à {dest} s'il vous plaît", "medium"),
        ("Je voudrais partir de {origin} à {dest} lundi prochain", "medium"),
        ("Un aller-retour {origin} {dest} pour la semaine prochaine", "medium"),
        ("Billet {origin} {dest} pour 3 personnes", "medium"),
    ]

    phrases = []
    sentence_id = start_id

    for _ in range(count):
        template, difficulty = random.choice(templates)

        origin = random.choice(MAIN_CITIES)
        dest = random.choice([c for c in MAIN_CITIES if c != origin])

        sentence = template.format(origin=origin, dest=dest)

        phrases.append({
            'sentenceID': sentence_id,
            'sentence': sentence,
            'origin': origin,
            'destination': dest,
            'is_valid': 1,
            'difficulty': difficulty,
            'category': 'additional_info',
            'notes': 'with time/passenger info'
        })
        sentence_id += 1

    return phrases, sentence_id

def generate_complex_questions(count=50, start_id=1):
    """Generate complex questions"""

    templates = [
        ("Quel est le moyen le plus rapide pour aller de {origin} à {dest}", "hard"),
        ("Combien de temps faut-il pour aller de {origin} à {dest}", "hard"),
        ("Y a-t-il des trains directs entre {origin} et {dest}", "medium"),
        ("Quelle est la durée du trajet de {origin} à {dest}", "medium"),
        ("Combien de correspondances entre {origin} et {dest}", "hard"),
        ("Quel est le train le plus rapide de {origin} à {dest}", "hard"),
        ("À quelle heure part le premier train de {origin} pour {dest}", "medium"),
        ("À quelle heure arrive le dernier train de {origin} à {dest}", "medium"),
    ]

    phrases = []
    sentence_id = start_id

    for _ in range(count):
        template, difficulty = random.choice(templates)

        origin = random.choice(MAIN_CITIES)
        dest = random.choice([c for c in MAIN_CITIES if c != origin])

        sentence = template.format(origin=origin, dest=dest)

        phrases.append({
            'sentenceID': sentence_id,
            'sentence': sentence,
            'origin': origin,
            'destination': dest,
            'is_valid': 1,
            'difficulty': difficulty,
            'category': 'complex_question',
            'notes': ''
        })
        sentence_id += 1

    return phrases, sentence_id

def main():
    """Generate complete valid orders dataset"""

    print("Generating valid orders dataset...")

    all_phrases = []

    # Generate each category
    print("Generating standard phrases (800)...")
    standard, next_id = generate_standard(800)
    all_phrases.extend(standard)

    print("Generating inverted order phrases (400)...")
    inverted, next_id = generate_inverted_order(400, start_id=next_id)
    all_phrases.extend(inverted)

    print("Generating no markers phrases (300)...")
    no_markers, next_id = generate_no_markers(300, start_id=next_id)
    all_phrases.extend(no_markers)

    print("Generating name ambiguities phrases (500)...")
    name_ambig, next_id = generate_name_ambiguities(500, start_id=next_id)
    all_phrases.extend(name_ambig)

    print("Generating compound names phrases (250)...")
    compound, next_id = generate_compound_names(250, start_id=next_id)
    all_phrases.extend(compound)

    print("Generating misspellings phrases (300)...")
    misspell_phrases, next_id = generate_misspellings(300, start_id=next_id)
    all_phrases.extend(misspell_phrases)

    print("Generating no capitals phrases (250)...")
    no_caps, next_id = generate_no_capitals(250, start_id=next_id)
    all_phrases.extend(no_caps)

    print("Generating additional info phrases (150)...")
    additional, next_id = generate_additional_info(150, start_id=next_id)
    all_phrases.extend(additional)

    print("Generating complex questions phrases (50)...")
    complex_q, next_id = generate_complex_questions(50, start_id=next_id)
    all_phrases.extend(complex_q)

    # Reassign sequential IDs
    for i, phrase in enumerate(all_phrases, 1):
        phrase['sentenceID'] = i

    # Write to CSV
    output_file = 'data/valid_orders_initial.csv'
    print(f"\nWriting to {output_file}...")

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['sentenceID', 'sentence', 'origin', 'destination', 'is_valid', 'difficulty', 'category', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_phrases)

    print(f"[OK] Generated {len(all_phrases)} valid phrases")

    # Statistics
    categories = {}
    difficulties = {}
    for phrase in all_phrases:
        cat = phrase['category']
        categories[cat] = categories.get(cat, 0) + 1
        diff = phrase['difficulty']
        difficulties[diff] = difficulties.get(diff, 0) + 1

    print("\nDistribution by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    print("\nDistribution by difficulty:")
    for diff, count in sorted(difficulties.items()):
        print(f"  {diff}: {count}")

    return all_phrases

if __name__ == "__main__":
    main()
