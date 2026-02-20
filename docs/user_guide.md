# Guide Utilisateur

> Installation, configuration et utilisation du Travel Order Resolver

---

## 1. Prerequis systeme

| Composant | Version minimale |
|-----------|-----------------|
| Python | 3.9+ |
| RAM | 4 Go minimum (8 Go recommande pour CamemBERT) |
| Espace disque | ~2 Go (modele CamemBERT + donnees SNCF) |
| GPU | Optionnel (CUDA pour entrainement, inference CPU OK) |
| OS | Windows 10+, Linux, macOS |

---

## 2. Installation

### 2.1 Cloner le depot

```bash
git clone <url>
cd T-AIA-911-TRAVEL-ORDER-RESOLVER
```

### 2.2 Creer l'environnement virtuel

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2.3 Installer les dependances

```bash
pip install -r requirements.txt
```

### 2.4 Telecharger le modele CamemBERT

Le modele fine-tune (~440 MB) doit etre place dans `models/camembert-ner/`.

Voir [models/README.md](../models/README.md) pour le lien de telechargement.

Structure attendue :
```
models/camembert-ner/
    config.json
    model.safetensors
    tokenizer.json
    tokenizer_config.json
    special_tokens_map.json
    sentencepiece.bpe.model
```

---

## 3. Utilisation CLI

### 3.1 Mode interactif

```bash
# Avec la baseline (regles)
python main.py --interactive

# Avec CamemBERT (recommande)
python main.py --interactive --model camembert
# ou raccourci :
python main.py -I --model camembert
```

Tapez une phrase en francais, le systeme extrait l'origine et la destination, puis affiche l'itineraire SNCF si les villes sont trouvees.

### 3.2 Traitement d'un fichier CSV

**Format d'entree** (`input.csv`) :
```csv
sentenceID,sentence
1,Je veux aller de Paris a Lyon
2,j'veu ale de roquefort-les-pins @ niiice
3,Bonjour comment allez-vous
```

**Commandes** :
```bash
# Mode NLP only (extraction origine/destination)
python main.py -i data/demo/input_demo.csv -o out.csv

# Mode pipeline complet (avec itineraire SNCF)
python main.py -i data/demo/input_demo.csv -o out.csv -m full-pipeline

# Avec CamemBERT
python main.py -i data/demo/input_demo.csv -o out.csv --model camembert

# Pipeline complet + CamemBERT
python main.py -i data/demo/input_demo.csv -o out.csv -m full-pipeline --model camembert
```

**Sortie mode `nlp-only`** :
```csv
sentenceID,Departure,Destination
1,Paris,Lyon
2,roquefort-les-pins,nice
3,INVALID,INVALID
```

**Sortie mode `full-pipeline`** :
```csv
sentenceID,Departure,Step1,...,Destination
1,Paris,Lyon
2,roquefort-les-pins,Cannes,...,Nice
```

### 3.3 Evaluation

```bash
# Evaluer la baseline sur le split validation
python main.py --evaluate --split val

# Evaluer CamemBERT sur le split test
python main.py --evaluate --split test --model camembert

# Specifier un dossier de donnees
python main.py --evaluate --split val --data-dir data/processed
```

### 3.4 Preparation des donnees (CamemBERT)

```bash
# Convertir les donnees NER word-level en format tokenise pour le Trainer
python main.py --prepare-data
```

### 3.5 Entree vocale (experimentale)

```bash
# Enregistrer depuis le microphone (5 secondes par defaut)
python main.py --voice

# Avec duree personnalisee et modele Whisper
python main.py --voice --voice-duration 8 --whisper-model small
```

Necessite : `pip install openai-whisper sounddevice soundfile`

---

## 4. Interface graphique Streamlit

### Lancement

```bash
streamlit run app.py
```

Ouvre **http://localhost:8501** dans le navigateur.

### Onglets

| Onglet | Description |
|--------|-------------|
| **Projet** | Architecture du systeme, resultats cles, exemples de phrases |
| **Donnees** | Exploration du dataset par categorie et difficulte |
| **Extraction NLP** | Tester une phrase avec Baseline et CamemBERT cote a cote |
| **Itineraire** | Route optimale avec carte interactive du reseau SNCF |
| **Evaluation** | Metriques completes + graphiques (resultats pre-calcules ou evaluation live) |
| **Pipeline CSV** | Upload d'un CSV, traitement, telechargement des resultats |

### Fonctionnalites

- **Comparaison Baseline vs CamemBERT** : extraction cote a cote dans l'onglet NLP
- **Carte interactive** : visualisation geographique du reseau SNCF avec Plotly
- **Evaluation live** : lancer une evaluation complete depuis l'UI avec barre de progression
- **Pipeline CSV** : uploader un fichier, traiter, telecharger les resultats

---

## 5. Entrainement CamemBERT

### Pipeline complet

```bash
# 1. Generer le dataset (si pas deja fait)
python scripts/dataset_generation/generate_dataset_10k.py

# 2. Convertir en format NER (BIO)
python scripts/camembert/convert_dataset_to_ner.py

# 3. Entrainer (20 epochs, ~2h sur GPU)
python scripts/camembert/train_camembert.py

# 4. Evaluer
python scripts/camembert/evaluate_camembert.py
```

### Personnaliser les hyperparametres

```bash
python scripts/camembert/train_camembert.py \
    --epochs 10 \
    --batch-size 32 \
    --learning-rate 3e-5 \
    --warmup-ratio 0.1
```

### Suivi de l'entrainement

Les logs TensorBoard sont ecrits dans `models/camembert-ner/logs/` :

```bash
tensorboard --logdir models/camembert-ner/logs
```

---

## 6. Tests

```bash
# Tous les tests
python -m pytest tests/ -v

# Un module specifique
python -m pytest tests/test_baseline.py -v
python -m pytest tests/test_postprocessing.py -v

# Avec couverture
python -m pytest tests/ --cov=src --cov-report=html
```

---

## 7. Structure des fichiers

```
T-AIA-911-TRAVEL-ORDER-RESOLVER/
|
|-- app.py                          # Interface Streamlit
|-- main.py                         # CLI principal
|-- requirements.txt
|
|-- src/
|   |-- nlp/                        # Module NLP
|   |   |-- preprocessing.py        # Normalisation du texte
|   |   |-- gazetteer.py            # Base de villes + fuzzy matching
|   |   |-- baseline.py             # Extracteur par regles
|   |   |-- transformer.py          # CamemBERT NER
|   |   |-- postprocessing.py       # Nettoyage post-extraction
|   |   +-- data_preparation.py     # Tokenisation pour Trainer
|   |
|   |-- pathfinding/                # Module itineraire
|   |   |-- graph_loader.py         # Graphe NetworkX depuis CSV
|   |   +-- algorithms.py           # Dijkstra
|   |
|   |-- utils/
|   |   |-- pipeline.py             # Orchestration bout en bout
|   |   |-- io_handler.py           # Lecture/ecriture CSV
|   |   +-- stt.py                  # Speech-to-text (Whisper)
|   |
|   +-- evaluation/
|       +-- metrics.py              # Precision / Recall / F1
|
|-- data/
|   |-- processed/                  # Donnees traitees
|   |   |-- train.csv / val.csv / test.csv
|   |   |-- *_ner.json              # Labels BIO word-level
|   |   +-- sncf/                   # Gares, connexions, mapping
|   +-- raw/sncf/gtfs/              # Donnees GTFS brutes
|
|-- models/
|   +-- camembert-ner/              # Modele fine-tune (~440 MB)
|
|-- scripts/                        # Scripts utilitaires
|-- tests/                          # Tests unitaires
|-- results/                        # Resultats d'evaluation JSON
+-- docs/                           # Documentation
```

---

## 8. Depannage

### "ModuleNotFoundError: No module named 'src'"

Toujours lancer les scripts depuis la **racine du projet** :
```bash
cd T-AIA-911-TRAVEL-ORDER-RESOLVER
python main.py ...
```

### "Model not found" pour CamemBERT

Verifier que le dossier `models/camembert-ner/` existe et contient les fichiers du modele. Voir `models/README.md`.

### Encodage UTF-8

Tous les fichiers CSV doivent etre en UTF-8. Sur Windows, Excel sauvegarde par defaut en ANSI — utiliser "Enregistrer sous" > "CSV UTF-8".

### Performances lentes

- **Premiere utilisation** : le graphe est construit depuis CSV (~3s), puis cache en pickle pour les fois suivantes (~0.1s)
- **CamemBERT** : premiere inference lente (chargement modele ~5s), puis ~50ms par phrase
- **GPU** : pour l'entrainement, un GPU CUDA est fortement recommande (20 epochs : ~2h GPU vs ~24h CPU)
