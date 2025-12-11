"""
NLP Module for Travel Order Resolver

This module contains all NLP-related functionality including:
- Text preprocessing and normalization
- Entity recognition and extraction
- Gazetteer matching
- Baseline rule-based approach
- Advanced transformer-based models
"""

from .preprocessing import (
    normalize_text,
    remove_accents,
    normalize_hyphens,
    normalize_apostrophes,
    remove_non_alphanumeric,
    tokenize_french,
    preprocess_for_matching,
    split_multi_word_name,
    fuzzy_normalize,
    extract_quoted_text,
    clean_sentence_id
)

__all__ = [
    'normalize_text',
    'remove_accents',
    'normalize_hyphens',
    'normalize_apostrophes',
    'remove_non_alphanumeric',
    'tokenize_french',
    'preprocess_for_matching',
    'split_multi_word_name',
    'fuzzy_normalize',
    'extract_quoted_text',
    'clean_sentence_id'
]

__version__ = '0.1.0'
