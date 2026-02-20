# NLP Module & Training Process

> Documentation technique du module NLP — extraction d'entites de voyage

---

## 1. Vue d'ensemble

Le module NLP extrait les villes d'origine et de destination a partir de phrases en francais. Deux approches sont implementees :

| Approche | Precision exacte | Avantage | Inconvenient |
|----------|-----------------|----------|--------------|
| **Baseline** (regles) | 60.1% | Interpretable, zero entrainement | Fragile aux fautes, noms composes |
| **CamemBERT** (NER) | 96.76% | Robuste, generalise | Necessite GPU pour entrainement, ~440 MB |

---

## 2. Approche Baseline (`src/nlp/baseline.py`)

### Architecture

```
Phrase -> preprocess_for_matching() -> is_valid_order() -> extract()
                                                              |
                                                    +---------+---------+
                                                    |         |         |
                                          keywords  direct  heuristic
                                          (prio 1) (prio 2) (prio 3)
```

### Extraction par mots-cles (priorite 1)

Mots-cles d'origine :
```python
ORIGIN_KEYWORDS = ["de", "depuis", "en partance de", "au depart de",
                   "en partant de", "a partir de", "depart"]
```

Mots-cles de destination :
```python
DESTINATION_KEYWORDS = ["a", "vers", "pour", "jusqua", "en direction de",
                        "direction", "arrivee"]
```

**Fonctionnement** : pour chaque token, si c'est un mot-cle d'origine, on cherche la prochaine localisation du gazetteer dans le texte restant. Idem pour les mots-cles de destination.

### Format direct (priorite 2)

Pattern : "billet X Y" ou "ticket X Y" -> les 2 premieres localisations trouvees sont respectivement l'origine et la destination.

### Heuristique (priorite 3)

Si les strategies precedentes echouent :
- 1 localisation trouvee : verifier le contexte (precede de "a"/"vers" -> destination, de "de"/"depuis" -> origine)
- 2+ localisations : premiere = origine, derniere = destination

### Detection d'ordres invalides

Phrases rejetees si elles contiennent : "quel temps", "quelle heure est", "comment allez", "bonjour", "merci", "azerty" OU si aucune localisation du gazetteer n'est detectee.

### Gazetteer (`src/nlp/gazetteer.py`)

Base de **66 villes** avec :
- Noms canoniques et normalises
- Aliases (ex: "st-etienne" -> "saint-etienne")
- **Fuzzy matching** par distance de Levenshtein (`max_distance=2`)

Le fuzzy matching est desactive par defaut dans la baseline. L'activer fait passer la categorie "misspelling" de 9.3% a ~50%.

---

## 3. Approche CamemBERT (`src/nlp/transformer.py`)

### Modele de base

**CamemBERT-base** (camembert-base) :
- Architecture : RoBERTa
- Pre-entrainement : corpus OSCAR (138 Go de texte francais)
- Parametres : 110M
- Tokenizer : SentencePiece (subword)
- Vocabulaire : 32 005 tokens

### Tache : Token Classification (NER)

Le modele est fine-tune pour la classification de tokens avec un schema BIO a 5 labels :

| Label | ID | Description |
|-------|-----|-------------|
| `O` | 0 | En dehors de toute entite |
| `B-ORIGIN` | 1 | Debut d'une ville d'origine |
| `I-ORIGIN` | 2 | Suite d'une ville d'origine (noms composes) |
| `B-DEST` | 3 | Debut d'une ville de destination |
| `I-DEST` | 4 | Suite d'une ville de destination |

### Tete de classification

```
CamemBERT (110M params)
    |
    v
Hidden states (768 dims par token)
    |
    v
Linear(768, 5)  -> logits par token
    |
    v
Softmax -> probabilites par label
    |
    v
Argmax -> label predit
```

### Alignement subwords

CamemBERT utilise SentencePiece qui decoupe les mots en sous-mots. L'alignement est critique :

```
Mot original :     "Aix-en-Provence"
Subwords :         ["Aix", "-en", "-", "Prov", "ence"]
Labels originaux : [B-DEST]
Labels alignes :   [B-DEST, -100, -100, -100, -100]
```

**Strategie** : le premier subword d'un mot recoit le label original. Les subwords suivants du meme mot recoivent `-100` (ignore par la loss CrossEntropy).

Implementation dans `tokenize_and_align_labels()` :
```python
for word_idx in word_ids:
    if word_idx is None:        # Token special [CLS]/[SEP]
        label_ids.append(-100)
    elif word_idx != previous_word_idx:  # Premier subword
        label_ids.append(label[word_idx])
    else:                       # Subword de continuation
        label_ids.append(-100)
```

### Inference (`predict()`)

```
1. Tokenisation : text.split() -> tokens -> tokenizer(is_split_into_words=True)
2. Forward pass : model(**inputs) -> logits
3. Argmax : torch.argmax(logits, dim=2) -> predicted labels
4. Realignement : word_ids() pour mapper subwords -> mots originaux
5. Post-processing : extract_entities(tokens, labels) -> origin, destination
```

---

## 4. Processus d'entrainement

### 4.1 Preparation des donnees

**Etape 1 : Generation du dataset** (`scripts/dataset_generation/generate_dataset_10k.py`)
- 10 000 phrases francaises generees avec 15 categories
- Split : 7 000 train / 1 500 val / 1 500 test (seed=42)
- Fichiers : `data/processed/{train,val,test}.csv`

**Etape 2 : Conversion NER** (`scripts/camembert/convert_dataset_to_ner.py`)
- Convertit chaque phrase en format BIO word-level
- Produit : `data/processed/{train,val,test}_ner.json`

Format NER JSON :
```json
{
  "tokens": ["Je", "veux", "aller", "de", "Paris", "a", "Lyon"],
  "labels": ["O", "O", "O", "O", "B-ORIGIN", "O", "B-DEST"],
  "metadata": {
    "sentenceID": "1",
    "category": "standard",
    "difficulty": "easy"
  }
}
```

**Etape 3 : Tokenisation** (`src/nlp/data_preparation.py` ou en ligne dans le Trainer)
- Tokenise avec CamemBERT tokenizer
- Aligne les labels avec les subwords
- Produit des tenseurs `{input_ids, attention_mask, labels}`

### 4.2 Hyperparametres

| Parametre | Valeur |
|-----------|--------|
| Modele de base | `camembert-base` |
| Epochs | 20 |
| Batch size | 16 |
| Learning rate | 2e-5 |
| Warmup ratio | 0.1 |
| Weight decay | 0.01 |
| Max sequence length | 128 tokens |
| Optimizer | AdamW (default Trainer) |
| Scheduler | Linear avec warmup |
| Mixed precision (fp16) | Oui si GPU disponible |
| Metric de selection | F1 (`load_best_model_at_end=True`) |
| Checkpoints gardes | 3 meilleurs |

### 4.3 Commandes d'entrainement

```bash
# 1. Convertir le dataset en format NER (BIO)
python scripts/camembert/convert_dataset_to_ner.py

# 2. Entrainer le modele
python scripts/camembert/train_camembert.py

# 3. Evaluer
python scripts/camembert/evaluate_camembert.py

# Avec parametres personnalises
python scripts/camembert/train_camembert.py --epochs 10 --batch-size 32 --learning-rate 3e-5
```

### 4.4 Strategie de validation

- Evaluation a chaque epoch sur le split validation (1 500 phrases)
- Metriques : Precision, Recall, F1 (seqeval), Accuracy
- Selection du meilleur modele par F1
- Early stopping implicite via `load_best_model_at_end=True`

---

## 5. Statistiques du dataset

### Distribution par categorie

| Categorie | Train | Val | Test | Description |
|-----------|-------|-----|------|-------------|
| `standard` | ~910 | ~200 | ~200 | Phrases bien formees avec mots-cles |
| `no_markers` | ~520 | ~110 | ~110 | Sans mots-cles explicites |
| `no_capitals` | ~640 | ~140 | ~140 | Sans majuscules |
| `misspelling` | ~850 | ~175 | ~175 | Fautes d'orthographe |
| `inverted_order` | ~400 | ~88 | ~88 | Destination avant origine |
| `compound_name` | ~415 | ~80 | ~80 | Noms composes (Aix-en-Provence) |
| `complex_question` | ~345 | ~77 | ~77 | Structures grammaticales complexes |
| `name_ambiguity` | ~475 | ~97 | ~97 | Noms ambigus (Paris prenom) |
| `additional_info` | ~330 | ~72 | ~72 | Infos supplementaires (horaire, etc.) |
| `garbage` / `no_intent` | ~590 | ~130 | ~130 | Phrases non-voyage (invalides) |

### Distribution par difficulte

| Difficulte | Train | Val | Test |
|------------|-------|-----|------|
| Easy | ~1 600 | ~350 | ~350 |
| Medium | ~1 600 | ~340 | ~340 |
| Hard | ~1 700 | ~350 | ~350 |

---

## 6. Exemple de traitement pas a pas

### Phrase : "Je voudrais un billet de Aix-en-Provence a Nice"

**Etape 1 : Preprocessing**
```
Input:  "Je voudrais un billet de Aix-en-Provence a Nice"
Output: "je voudrais un billet de aix-en-provence a nice"
```

**Etape 2 : Tokenisation CamemBERT**
```
Mots:     ["Je", "voudrais", "un", "billet", "de", "Aix-en-Provence", "a", "Nice"]
Subwords: ["<s>", "Je", "voudrais", "un", "billet", "de", "Aix", "-en", "-", "Prov", "ence", "a", "Nice", "</s>"]
Word IDs: [None,   0,     1,        2,    3,       4,    5,     5,    5,   5,     5,    6,    7,    None]
```

**Etape 3 : Prediction**
```
Logits:  [[0.1, 0.0, 0.0, 0.0, 0.9], ...]   (5 classes par token)
Labels:  [-100,  O,   O,   O,   O,   O,  B-ORIGIN, -100, -100, -100, -100, O, B-DEST, -100]
```

**Etape 4 : Realignement vers mots**
```
Mots:   ["Je", "voudrais", "un", "billet", "de", "Aix-en-Provence", "a",  "Nice"]
Labels: ["O",  "O",        "O",  "O",     "O",  "B-ORIGIN",         "O",  "B-DEST"]
```

**Etape 5 : Post-processing**
```
Origin:      "Aix-en-Provence"
Destination: "Nice"
```

**Etape 6 : Mapping UIC**
```
"aix-en-provence" -> UIC 87751008
"nice"            -> UIC 87756056
```

**Etape 7 : Dijkstra**
```
Chemin: Aix-en-Provence -> Marseille -> Toulon -> ... -> Nice
Duree:  ~3h45
```

---

## 7. Post-processing (`src/nlp/postprocessing.py`)

Le post-processing recoit les tokens et labels bruts du modele et :

1. **Reconstruit les noms composes** : tokens consecutifs B-ORIGIN/I-ORIGIN sont concatenes
   - Ex: `["Aix", "-en", "-Provence"]` avec `[B-ORIGIN, I-ORIGIN, I-ORIGIN]` -> `"Aix-en-Provence"`

2. **Valide avec le gazetteer** : verifie que le nom extrait correspond a une ville connue

3. **Normalise** : nettoie les espaces, tirets, casse

La fonction `extract_entities(tokens, labels)` retourne `(origin, destination)`.
