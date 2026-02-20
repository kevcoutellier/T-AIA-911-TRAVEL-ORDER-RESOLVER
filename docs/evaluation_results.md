# Evaluation Results & Analysis

> Resultats d'evaluation complets — Baseline vs CamemBERT

---

## 1. Metriques utilisees

### Metriques d'extraction

| Metrique | Definition |
|----------|-----------|
| **Exact Match** | % de phrases ou origine ET destination sont correctes |
| **Origin Accuracy** | % d'origines correctement extraites |
| **Destination Accuracy** | % de destinations correctement extraites |

### Metriques de detection d'ordres valides

| Metrique | Definition |
|----------|-----------|
| **Precision** | Parmi les phrases predites comme valides, % reellement valides |
| **Recall** | Parmi les phrases reellement valides, % detectees comme valides |
| **F1 Score** | Moyenne harmonique de Precision et Recall |

### Pourquoi ces metriques ?

- **Exact Match** est la metrique principale car le systeme doit extraire correctement les DEUX villes pour etre utile
- **Precision/Recall** mesurent la capacite a distinguer les ordres de voyage des phrases non pertinentes
- **Robustesse par categorie** identifie les faiblesses specifiques du modele

---

## 2. Resultats globaux

### Comparaison Baseline vs CamemBERT

| Metrique | Baseline | CamemBERT | Amelioration |
|----------|----------|-----------|--------------|
| **Exact Match** | 60.1% | **96.76%** | +36.7 pts |
| Origin Accuracy | 74.9% | **98.1%** | +23.2 pts |
| Destination Accuracy | 71.8% | **97.5%** | +25.7 pts |

### Metriques de detection (Baseline, 10k phrases)

| Metrique | Valeur |
|----------|--------|
| Precision | 89.94% |
| Recall | 81.23% |
| F1 Score | 85.36% |
| True Positives | 5 686 |
| True Negatives | 2 364 |
| False Positives | 636 |
| False Negatives | 1 314 |

---

## 3. Resultats par difficulte

### Baseline

| Difficulte | Total | Correct | Accuracy |
|------------|-------|---------|----------|
| Easy | 2 309 | 1 835 | **79.5%** |
| Medium | 2 300 | 1 442 | **62.7%** |
| Hard | 2 391 | 879 | **36.8%** |

### CamemBERT

| Difficulte | Total | Correct | Accuracy |
|------------|-------|---------|----------|
| Easy | 358 | 358 | **100.0%** |
| Medium | 343 | 330 | **96.2%** |
| Hard | 349 | 328 | **94.0%** |

**Observation** : CamemBERT atteint 100% sur les phrases faciles et maintient >94% sur les phrases difficiles, la ou la baseline chute a 36.8%.

---

## 4. Resultats par categorie

### Comparaison detaillee

| Categorie | Baseline | CamemBERT | Delta |
|-----------|----------|-----------|-------|
| standard | 77.4% | **100.0%** | +22.6 |
| no_markers | 84.6% | **100.0%** | +15.4 |
| no_capitals | 75.5% | **100.0%** | +24.5 |
| additional_info | 86.1% | **100.0%** | +13.9 |
| complex_question | 43.2% | **100.0%** | +56.8 |
| inverted_order | 53.7% | **100.0%** | +46.3 |
| name_ambiguity | 81.5% | **97.9%** | +16.4 |
| **misspelling** | **9.3%** | **89.1%** | **+79.8** |
| compound_name | 38.6% | **83.5%** | +44.9 |
| garbage/no_intent | 100.0% | 100.0% | 0.0 |

### Points cles

1. **Misspelling** : amelioration la plus spectaculaire (+79.8 pts). La baseline echoue car le fuzzy matching est insuffisant pour les fautes lourdes ("pariz", "Bordo", "annnecy"). CamemBERT generalise grace aux representations contextuelles.

2. **Complex question & Inverted order** : +56.8 et +46.3 pts. La baseline ne gere pas les structures non standard ("A quelle heure peut-on aller a Lyon en partant de Paris?"). CamemBERT comprend le contexte grammatical.

3. **Compound names** : 83.5% (vs 38.6%). Les noms composes comme "Aix-en-Provence", "La Roche-sur-Yon" sont mieux geres grace au schema BIO (B-DEST + I-DEST pour chaque partie).

4. **Detection d'invalides** : 100% pour les deux approches. Les phrases "garbage" et "no_intent" sont bien rejetees.

---

## 5. Analyse des erreurs CamemBERT

### Distribution des 34 erreurs (sur 1 050 phrases test)

| Type d'erreur | Nombre | % des erreurs |
|---------------|--------|---------------|
| Misspelling severe | 19 | 55.9% |
| Compound name non reconnu | 13 | 38.2% |
| Name ambiguity | 2 | 5.9% |

### Patterns d'erreur recurrents

**1. Misspellings extremes (55.9% des erreurs)**

Le modele echoue quand la faute deforme trop le mot :
- "annnecy" (triple n), "Bordo" (Bordeaux), "Nisse" (Nice), "Lyl" (Lille)
- "pariz" -> le modele predit "aller" comme origine (confusion totale)

Ces cas sont a la limite de la lisibilite humaine.

**2. Noms composes sans tirets (38.2% des erreurs)**

Quand les tirets sont remplaces par des espaces, le modele perd les frontieres :
- "Aix en Provence" -> ne reconnait pas comme une seule entite
- "La Roche sur Yon" -> manque completement
- "Salon de Provence" -> confusion avec "de" (mot-cle d'origine)
- "Chalons en Champagne" -> absorbe tout le texte apres

**3. Ambiguite de noms (5.9% des erreurs)**

Phrases construites pour pieger :
- "Lourdes, Paris et moi devons aller de Metz a Paris" -> le modele confond les deux "Paris"

### Erreurs illustratives

```
Phrase:    "Billet Metz Aix en Provence"
Attendu:   Origine=Metz, Destination=Aix-en-Provence
Predit:    Origine="", Destination="Metz Aix en Provence"
Cause:     Sans tirets, "Aix en Provence" n'est pas reconnu comme entite unique

Phrase:    "Je veu partir de Annec ver toulouse"
Attendu:   Origine=Annecy, Destination=Toulouse
Predit:    Origine="", Destination="toulouse"
Cause:     "Annec" trop eloigne de "Annecy" + "ver" perturbe le contexte

Phrase:    "je ve aller de pariz a le man"
Attendu:   Origine=Paris, Destination=Le Mans
Predit:    Origine="aller", Destination="le man"
Cause:     "pariz" non reconnu, le modele s'accroche a un autre token
```

---

## 6. Lecons apprises et ameliorations possibles

### Ameliorations implementees

1. **Fuzzy matching** : activer le matching Levenshtein dans la baseline (9% -> ~50% sur misspelling)
2. **Schema BIO** : le passage de labels simples a B-ORIGIN/I-ORIGIN permet de gerer les noms composes
3. **20 epochs** (vs 4 par defaut) : convergence plus complete, surtout sur les cas difficiles

### Ameliorations futures possibles

1. **Data augmentation** : generer plus d'exemples avec noms composes sans tirets
2. **Post-processing enrichi** : appliquer le fuzzy matching gazetteer APRES l'extraction CamemBERT pour corriger "strasboure" -> "Strasbourg"
3. **Ensemble** : combiner les predictions baseline + CamemBERT (la baseline est meilleure sur certaines structures simples)
4. **Modele plus grand** : CamemBERT-large (335M params) pourrait aider sur les cas extremes

---

## 7. Reproductibilite

### Lancer l'evaluation

```bash
# Baseline sur validation
python main.py --evaluate --split val

# CamemBERT sur test
python main.py --evaluate --split test --model camembert

# Evaluation complete (10k phrases)
python scripts/baseline_evaluation/evaluate_baseline_10k.py
python scripts/camembert/evaluate_camembert.py
```

### Fichiers de resultats

| Fichier | Contenu |
|---------|---------|
| `results/evaluation_baseline_10k.json` | Metriques baseline sur 10k phrases |
| `results/camembert_evaluation.json` | Metriques CamemBERT sur test (1050 phrases) |
| `results/baseline_validation_metrics.json` | Metriques baseline sur validation |
| `results/baseline_validation_errors.json` | Erreurs detaillees baseline |
