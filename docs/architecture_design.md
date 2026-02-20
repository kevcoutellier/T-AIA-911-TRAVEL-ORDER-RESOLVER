# Architecture & System Design

> Documentation technique du projet Travel Order Resolver — T-AIA-911

---

## 1. Vue d'ensemble

Le Travel Order Resolver est un systeme de traitement du langage naturel (NLP) qui extrait les villes de depart et de destination a partir de phrases en francais, puis calcule l'itineraire optimal sur le reseau ferroviaire SNCF.

### Pipeline principal

```
Phrase francaise
    |
    v
[Preprocessing]          Normalisation : accents, casse, tirets, caracteres speciaux
    |
    v
[Extraction NLP]         Baseline (regles) OU CamemBERT (NER fine-tune)
    |
    v
[Postprocessing]         Reconstruction noms composes, validation gazetteer
    |
    v
[Mapping UIC]            city_station_mapping.csv : nom de ville -> code UIC 8 chiffres
    |
    v
[Pathfinding]            Dijkstra sur graphe NetworkX (poids = duree en minutes)
    |
    v
Itineraire avec etapes intermediaires et duree totale
```

### Diagramme de composants

```
+------------------+     +------------------+     +------------------+
|    Entry Points  |     |    NLP Module     |     |   Pathfinding    |
|                  |     |   (src/nlp/)      |     | (src/pathfinding)|
|  main.py  (CLI)  |---->| preprocessing.py  |     | graph_loader.py  |
|  app.py   (UI)   |     | gazetteer.py      |     | algorithms.py    |
|                  |     | baseline.py       |     |                  |
+--------+---------+     | transformer.py    |     +--------+---------+
         |               | postprocessing.py  |              |
         v               +--------+----------+              |
+------------------+              |                          |
|    Pipeline      |              v                          |
| (src/utils/      |     +------------------+               |
|  pipeline.py)    |<----| Extraction Result |               |
|  io_handler.py   |     | origin, dest     +-------------->|
|  stt.py          |     +------------------+     Mapping   |
+------------------+                              UIC       |
         |                                                  |
         v                                                  v
+------------------+     +------------------+     +------------------+
|    Evaluation    |     |     Output       |     |    Route         |
| (src/evaluation/ |     |  CSV / JSON      |     |  Path + Time     |
|  metrics.py)     |     +------------------+     +------------------+
+------------------+
```

---

## 2. Stack technique

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| **Langage** | Python 3.9+ | Ecosysteme NLP mature, HuggingFace natif |
| **NLP Baseline** | Regles + Gazetteer | Interpretable, pas de donnees d'entrainement necessaires |
| **NLP Avance** | CamemBERT (HuggingFace) | Meilleur modele francais, pre-entraine sur 138 Go de texte |
| **Tokenization** | SentencePiece (via CamemBERT) | Gere les mots hors vocabulaire par subwords |
| **Graphe** | NetworkX | Pur Python, pas de serveur externe, Dijkstra optimise integre |
| **Donnees SNCF** | GTFS officiel | Connexions reelles avec durees extraites de stop_times.txt |
| **Evaluation** | seqeval + scikit-learn | Metriques standard NER (Precision/Recall/F1) |
| **UI** | Streamlit | Prototypage rapide, widgets natifs, deployment simple |
| **Tests** | pytest | Fixtures, parametrize, couverture integree |

### Pourquoi CamemBERT plutot que d'autres modeles ?

| Modele | Langue | Taille | Avantage | Inconvenient |
|--------|--------|--------|----------|--------------|
| **CamemBERT** | FR natif | 110M params | Pre-entraine sur OSCAR (138 Go FR) | -- |
| mBERT | Multilingue | 110M params | Large couverture | Moins bon en FR pur |
| FlauBERT | FR natif | 138M params | Bon en FR | Moins de communaute |
| spaCy fr_core_news | FR | Petit | Rapide | Pas de fine-tuning NER custom |

CamemBERT a ete choisi car il est le modele de reference pour le francais avec la meilleure performance documentee sur les benchmarks NER francais.

### Pourquoi NetworkX plutot que Neo4j ?

- **Pas de serveur externe** : le graphe tient en memoire (~5 MB pickle)
- **Dijkstra integre** : `nx.shortest_path()` utilise une priority queue optimisee
- **Serialisation** : pickle pour cache instantane (~0.1s vs ~3s rebuild)
- **Simplicite** : zero configuration, pas de base de donnees a maintenir
- Neo4j aurait ete pertinent pour un reseau plus grand (>100k noeuds) ou des requetes complexes

---

## 3. Modules detailles

### 3.1 Preprocessing (`src/nlp/preprocessing.py`)

Fonction principale : `preprocess_for_matching(text) -> str`

Ordre d'application :
1. Normalisation des tirets (em/en dash -> tiret simple)
2. Suppression des accents (unicode NFD)
3. Mise en minuscules
4. Suppression des caracteres non-alphanumeriques (sauf espaces, tirets, apostrophes)

### 3.2 Gazetteer (`src/nlp/gazetteer.py`)

Base de 66 villes et gares francaises avec :
- Noms normalises (sans accents, minuscules)
- Aliases (ex: "saint-etienne" = "st-etienne")
- Fuzzy matching par distance de Levenshtein (`max_distance=2`)

Le fuzzy matching est le **plus grand gain rapide** sur la categorie "misspelling" (9% -> ~50%).

### 3.3 Baseline (`src/nlp/baseline.py`)

Classe `BaselineExtractor` avec 3 strategies en cascade :

| Priorite | Strategie | Description |
|----------|-----------|-------------|
| 1 | `extract_with_keywords()` | Mots-cles : "de/depuis" -> origine, "a/vers/pour" -> destination |
| 2 | `extract_direct_format()` | Format "billet X Y" |
| 3 | `extract_heuristic()` | 1ere localisation = origine, derniere = destination |

### 3.4 Transformer (`src/nlp/transformer.py`)

Classe `CamembertNER` :
- Token classification avec 5 labels BIO
- Fine-tuning via HuggingFace `Trainer`
- Alignement subwords : 1er subword garde le label, suivants -> `-100`
- Inference : `predict(text)` retourne `(tokens, labels, origin, destination)`

### 3.5 Pathfinding (`src/pathfinding/`)

- **graph_loader.py** : charge stations (noeuds) et connexions (aretes) depuis CSV, serialise en pickle
- **algorithms.py** : `dijkstra(graph, origin_uic, dest_uic)` via `nx.shortest_path()`, complexite O((V+E) log V)
- Noeuds = codes UIC 8 chiffres, aretes = duree en minutes

### 3.6 Pipeline (`src/utils/pipeline.py`)

Fonction `process_pipeline(input_file, output_file, mode, nlp_model)` :
1. Charge le modele NLP (baseline ou camembert)
2. Charge le mapping ville -> UIC
3. Charge le graphe (cache pickle ou rebuild CSV)
4. Pour chaque phrase : extraction -> mapping -> routing
5. Ecrit les resultats CSV

### 3.7 Evaluation (`src/evaluation/metrics.py`)

Fonction `evaluate_model()` retourne un `EvaluationResult` avec :
- Accuracy (origine, destination, exact match)
- Precision / Recall / F1 pour la detection d'ordres valides
- Matrice de confusion
- Scores de robustesse par categorie et difficulte

---

## 4. Flux de donnees

### Entree

```csv
sentenceID,sentence
1,Je veux aller de Paris a Lyon
2,j'veu ale de roquefort-les-pins @ niiice
3,Bonjour comment allez-vous
```

### Sortie mode `nlp-only`

```csv
sentenceID,Departure,Destination
1,Paris,Lyon
2,roquefort-les-pins,nice
3,INVALID,INVALID
```

### Sortie mode `full-pipeline`

```csv
sentenceID,Departure,Step1,...,Destination
1,Paris,Lyon
2,roquefort-les-pins,Cannes,...,Nice
```

---

## 5. Infrastructure de donnees

### Reseau ferroviaire

| Donnee | Source | Volume |
|--------|--------|--------|
| Gares | GTFS SNCF `stops.txt` | 2 782 stations avec coordonnees GPS |
| Connexions | GTFS SNCF `stop_times.txt` | 11 230 segments bidirectionnels |
| Durees | Calcul median sur ~359k stop_times | Poids en minutes reelles |
| Mapping | Normalisation noms de villes | ~2 700 entrees ville -> UIC |

### Cache

Le graphe NetworkX est serialise en pickle (`models/train_network.pkl`, ~5 MB) pour un chargement instantane (~0.1s vs ~3s depuis CSV).

---

## 6. Points d'entree

| Point d'entree | Fichier | Usage |
|-----------------|---------|-------|
| CLI interactif | `main.py --interactive` | Tester phrase par phrase |
| CLI batch | `main.py -i input.csv -o output.csv` | Traitement CSV |
| CLI evaluation | `main.py --evaluate --split val` | Metriques sur dataset |
| CLI voice | `main.py --voice` | Entree vocale (Whisper) |
| UI Streamlit | `app.py` | Interface graphique 6 onglets |

---

## 7. Decisions d'architecture

### Isolation des modules

Le module NLP (`src/nlp/`) est **completement independant** du module pathfinding (`src/pathfinding/`). Ils communiquent uniquement via des strings (noms de villes) dans le pipeline. Cela permet :
- Tests unitaires isoles
- Remplacement du modele NLP sans toucher au pathfinding
- Evolution independante

### Strategie de cache

- **Graphe** : pickle + `get_or_build_graph()` avec fallback automatique
- **Modele Whisper** : variable globale `_whisper_model` chargee une fois
- **Streamlit** : `@st.cache_resource` pour modeles, `@st.cache_data` pour donnees

### Gestion des erreurs

Le pipeline utilise un pattern de resultat structure : chaque `process_single_sentence()` retourne un dictionnaire avec `success`, `error_type`, `error_message`. Les erreurs sont classifiees en 3 categories : NLP, mapping, pathfinding.
