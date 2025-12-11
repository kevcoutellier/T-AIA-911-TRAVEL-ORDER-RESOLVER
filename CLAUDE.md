# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an EPITECH NLP project to build a **Travel Order Resolver** that processes French text commands to generate train itineraries using SNCF (French rail) schedules. The system extracts departure and destination cities/stations from natural language and finds optimal train routes.

**Core Focus**: Natural Language Processing (70% of effort) with secondary pathfinding component.

## Critical Requirements

### Input/Output Format
- **Input**: Text file or stdin with format `sentenceID,sentence` (one per line)
- **Output** (NLP component):
  - Valid: `sentenceID,Departure,Destination`
  - Invalid: `sentenceID,INVALID` (or more specific error code)
- **Output** (Pathfinding): `sentenceID,Departure,Step1,Step2,...,Destination`
- **Encoding**: All files MUST use UTF-8

### Module Isolation
The NLP module MUST be isolated and independently testable. This is a hard requirement for evaluation.

## Key NLP Challenges

### Complex Entity Recognition
The project requires handling challenging French language patterns:

1. **Cities with common word names**: Port-Boulet (port = harbor, boulet = cannonball)
2. **Cities that are also people names**: Paris, Albert, Florence, Lourdes
3. **Missing formatting**: No capitals, accents, or hyphens (e.g., "port boulet" instead of "Port-Boulet")
4. **Misspellings**: Model must be robust to typos
5. **Ambiguous syntax**: Origin/destination order varies; prepositions ("de", "depuis", "à", "vers") aren't always reliable

### Example Sentences
```
Je voudrais un billet Toulouse Paris
Je souhaite me rendre à Paris depuis Toulouse
Comment me rendre à Port Boulet depuis Tours?
Avec mes amis florence et paris, je voudrais aller de paris a florence
je veux aller a tours voir mon ami albert en partant de bordeaux
```

## Architecture

### 3-Component Pipeline

```
[Voice Recognition (BONUS)] → [NLP Module (CORE)] → [Pathfinding Module]
     Optional                   Must Extract           Graph Algorithms
                                Origin/Destination
```

### Technology Stack

**NLP Approaches (in order of implementation):**
1. **Baseline**: spaCy + rule-based patterns (target: 60-70% accuracy)
2. **Advanced**: CamemBERT fine-tuning with NER (target: 85%+ accuracy)
3. **Alternative**: BiLSTM-CRF if resources are limited

**Recommended Libraries:**
- NLP: `spacy`, `transformers` (HuggingFace), `camembert-base`
- Pathfinding: `networkx`, `neo4j` (graph database)
- Data: `pandas`, `numpy`
- Evaluation: `scikit-learn`

**Pre-trained Models:**
- CamemBERT (French BERT variant) - needs fine-tuning for this task
- FlauBERT (alternative)
- spaCy French models (`fr_core_news_lg`)

## Development Workflow

### Phase 1: Dataset Creation (PRIORITY)
- Need ~10,000 sentences based on ~300 different grammatical structures
- Collaborate with other groups for diversity
- Include 70% valid orders, 30% invalid/trash text
- Split: 70% train, 15% validation, 15% test

### Phase 2: Baseline Implementation
- Implement simple spaCy + rule-based system
- Establish baseline metrics
- This secures minimum viable product

### Phase 3: Advanced Model
- Fine-tune CamemBERT for Named Entity Recognition
- Tag tokens as: B-ORIGIN, I-ORIGIN, B-DEST, I-DEST, O
- Hyperparameters: learning rate 2e-5 to 5e-5, batch size 16-32, 3-5 epochs

### Phase 4: Evaluation & Iteration
- Track metrics: Accuracy, Precision, Recall, F1
- Test robustness: missing capitals, misspellings, ambiguous names
- Document all experiments and metric evolution

## Data Sources

**SNCF Open Data**: https://data.sncf.com/
- Station lists with city mappings
- Train schedules/timetables
- Station connections for graph building

Import CSV data into Neo4j or NetworkX for pathfinding.

## Graph/Pathfinding Algorithms

Not the core focus, but must understand complexity:
- **Dijkstra's algorithm**: For shortest path (sufficient)
- **A***: With heuristics (optional enhancement)
- Graph database schema:
  - Nodes: Station (id, name, city, lat, lon)
  - Edges: CONNECTS_TO (duration, distance, line_name)

## Project Structure

```
travel-order-resolver/
├── data/
│   ├── raw/              # SNCF CSV files
│   ├── train.csv         # Training sentences
│   ├── val.csv
│   └── test.csv
├── src/
│   ├── nlp/              # NLP module (MUST BE ISOLATED)
│   │   ├── baseline.py
│   │   ├── transformer.py
│   │   ├── preprocessing.py
│   │   └── postprocessing.py
│   ├── pathfinding/
│   │   ├── graph_builder.py
│   │   ├── algorithms.py
│   │   └── neo4j_client.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   └── visualize.py
│   └── utils/
├── models/               # Saved model weights
├── notebooks/            # Jupyter notebooks for experiments
├── docs/
│   └── technical_report.pdf  # MAJOR DELIVERABLE
├── tests/
├── requirements.txt
└── main.py              # CLI entry point
```

## Running the Project

### Installation
```bash
pip install -r requirements.txt
python -m spacy download fr_core_news_lg
```

### NLP Module (Isolated)
```bash
# Read from file
python src/nlp/main.py --input data/test.csv --output results.csv

# Read from stdin
cat sentences.txt | python src/nlp/main.py
```

### Full Pipeline
```bash
python main.py --input sentences.csv --output routes.csv
```

### Training
```bash
# Baseline
python scripts/train_baseline.py --train data/train.csv --val data/val.csv

# Transformer
python scripts/train_transformer.py --model camembert-base --epochs 5
```

### Evaluation
```bash
python src/evaluation/metrics.py --predictions results.csv --ground-truth data/test.csv
```

## Testing

Run tests with:
```bash
pytest tests/
python -m pytest tests/test_nlp.py -v
```

## Documentation Requirements

Must deliver PDF technical report including:
1. **Architecture**: Full system diagram, data flow, component descriptions
2. **Training Process**: Dataset description, hyperparameters, fine-tuning process
3. **Detailed Example**: Step-by-step walkthrough of one sentence through the pipeline
4. **Experiments**: Different approaches tried, results comparison
5. **Metrics**: Baseline vs advanced model, robustness tests, error analysis
6. **Pathfinding**: Algorithm choice, complexity analysis

## Important Notes

- **NO WEB APPLICATION**: CLI is sufficient, web UI not required
- **Metrics are mandatory**: Must evaluate and document model performance
- **Collaboration encouraged**: Share datasets with other groups for diversity
- **Baseline first**: Secure working solution before attempting complex models
- **Document from day 1**: Track all experiments and decisions
- **Focus on NLP**: Pathfinding is secondary (but must understand algorithms)

## Bonus Features (Optional)

- Speech-to-text integration (Google Speech API, Mozilla DeepSpeech)
- Intermediate stops: "aller de Toulouse à Paris en passant par Limoges"
- Multiple optimization criteria (fastest, fewest connections)
- Cloud deployment monitoring (CPU/RAM usage)
- Handle destinations not in timetable
- Multi-language support

## Success Criteria

**Minimum Viable Product:**
- NLP extracts origin/destination with >70% accuracy
- Handles basic French sentences
- Proper UTF-8 input/output format
- Isolated NLP module
- Basic pathfinding works

**Target:**
- NLP accuracy >85% on test set
- Robust to misspellings and formatting issues
- Fine-tuned transformer model
- Comprehensive documentation with metrics

## Key Constraints

1. Must handle French language (primary requirement)
2. Must distinguish between valid/invalid travel orders
3. Must handle ambiguous city names in context
4. Must process text without capitals/accents/hyphens
5. NLP component must be testable independently
6. All I/O must use UTF-8 encoding
