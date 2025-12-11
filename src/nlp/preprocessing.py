"""
Text Preprocessing Module for Travel Order Resolver

This module provides text normalization and preprocessing functions
for French travel order sentences before NLP processing.
"""

import re
import unicodedata
from typing import List, Tuple


def normalize_text(text: str, lowercase: bool = True,
                  remove_extra_spaces: bool = True) -> str:
    """
    Normalize input text by handling whitespace and optionally converting to lowercase.

    Args:
        text: Input text to normalize
        lowercase: Whether to convert text to lowercase (default: True)
        remove_extra_spaces: Whether to remove extra whitespace (default: True)

    Returns:
        Normalized text string

    Examples:
        >>> normalize_text("  Je  veux  aller à Paris  ")
        'je veux aller à paris'
        >>> normalize_text("TOULOUSE PARIS", lowercase=False)
        'TOULOUSE PARIS'
    """
    if not text or not isinstance(text, str):
        return ""

    # Handle UTF-8 encoding
    text = text.encode('utf-8', errors='ignore').decode('utf-8')

    # Remove extra whitespace
    if remove_extra_spaces:
        text = ' '.join(text.split())

    # Convert to lowercase
    if lowercase:
        text = text.lower()

    return text.strip()


def remove_accents(text: str, keep_cedilla: bool = True) -> str:
    """
    Remove accents from French text while optionally preserving cedilla (ç).

    Args:
        text: Input text with accents
        keep_cedilla: Whether to keep ç character (default: True)

    Returns:
        Text without accents

    Examples:
        >>> remove_accents("à Paris depuis Sète")
        'a Paris depuis Sete'
        >>> remove_accents("français", keep_cedilla=False)
        'francais'
    """
    if not text or not isinstance(text, str):
        return ""

    # Handle cedilla separately if we want to keep it
    if keep_cedilla:
        text_with_placeholder = text.replace('ç', '###CEDILLA###').replace('Ç', '###CEDILLA_UPPER###')
        # Normalize to NFD (decomposed form)
        nfd = unicodedata.normalize('NFD', text_with_placeholder)
        # Remove combining characters (accents)
        without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
        # Restore cedilla
        result = without_accents.replace('###CEDILLA###', 'ç').replace('###CEDILLA_UPPER###', 'Ç')
        return result
    else:
        # Normalize to NFD (decomposed form)
        nfd = unicodedata.normalize('NFD', text)
        # Remove combining characters (accents)
        return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def normalize_hyphens(text: str) -> str:
    """
    Normalize different types of hyphens and dashes to standard hyphen.

    Args:
        text: Input text with various hyphen types

    Returns:
        Text with normalized hyphens

    Examples:
        >>> normalize_hyphens("Port–Boulet")
        'Port-Boulet'
        >>> normalize_hyphens("Aix—en—Provence")
        'Aix-en-Provence'
    """
    if not text or not isinstance(text, str):
        return ""

    # Replace various dash types with standard hyphen
    # En dash (–), em dash (—), minus sign (−), etc.
    text = text.replace('–', '-')  # En dash
    text = text.replace('—', '-')  # Em dash
    text = text.replace('−', '-')  # Minus sign
    text = text.replace('‐', '-')  # Hyphen (non-breaking)
    text = text.replace('‑', '-')  # Non-breaking hyphen

    return text


def normalize_apostrophes(text: str) -> str:
    """
    Normalize different types of apostrophes to standard apostrophe.

    Args:
        text: Input text with various apostrophe types

    Returns:
        Text with normalized apostrophes

    Examples:
        >>> normalize_apostrophes("l'hôtel")
        "l'hôtel"
        >>> normalize_apostrophes("aujourd'hui")
        "aujourd'hui"
    """
    if not text or not isinstance(text, str):
        return ""

    # Replace various apostrophe types with standard apostrophe
    text = text.replace(''', "'")  # Right single quotation mark
    text = text.replace('`', "'")  # Grave accent
    text = text.replace('´', "'")  # Acute accent
    text = text.replace(''', "'")  # Left single quotation mark

    return text


def remove_non_alphanumeric(text: str, keep_spaces: bool = True,
                           keep_hyphens: bool = True,
                           keep_apostrophes: bool = True) -> str:
    """
    Remove non-alphanumeric characters from text with options.

    Args:
        text: Input text
        keep_spaces: Whether to keep spaces (default: True)
        keep_hyphens: Whether to keep hyphens (default: True)
        keep_apostrophes: Whether to keep apostrophes (default: True)

    Returns:
        Text with non-alphanumeric characters removed

    Examples:
        >>> remove_non_alphanumeric("Paris (capital)")
        'Paris capital'
        >>> remove_non_alphanumeric("Port-Boulet?", keep_hyphens=False)
        'PortBoulet'
    """
    if not text or not isinstance(text, str):
        return ""

    # Build pattern of characters to keep
    pattern = r'[^a-zA-ZÀ-ÿ0-9'

    if keep_spaces:
        pattern += r'\s'
    if keep_hyphens:
        pattern += r'\-'
    if keep_apostrophes:
        pattern += r"'"

    pattern += r']'

    # Remove characters not matching the pattern
    text = re.sub(pattern, ' ', text)

    # Clean up multiple spaces
    text = ' '.join(text.split())

    return text.strip()


def tokenize_french(text: str, keep_punctuation: bool = False) -> List[str]:
    """
    Simple French tokenization splitting on whitespace and punctuation.

    Args:
        text: Input text to tokenize
        keep_punctuation: Whether to keep punctuation as separate tokens

    Returns:
        List of tokens

    Examples:
        >>> tokenize_french("Je veux aller à Paris")
        ['Je', 'veux', 'aller', 'à', 'Paris']
        >>> tokenize_french("Port-Boulet")
        ['Port', 'Boulet']
    """
    if not text or not isinstance(text, str):
        return []

    if keep_punctuation:
        # Split on whitespace and keep punctuation as separate tokens
        tokens = re.findall(r"\w+(?:[-']\w+)*|[^\w\s]", text)
    else:
        # Split on whitespace and punctuation (including hyphens)
        # This is useful for matching multi-word city names
        tokens = re.findall(r'\w+', text)

    return [token for token in tokens if token]


def preprocess_for_matching(text: str) -> str:
    """
    Complete preprocessing pipeline for entity matching against gazetteer.
    This function applies all normalization steps in sequence.

    Args:
        text: Raw input text

    Returns:
        Fully preprocessed text ready for entity matching

    Examples:
        >>> preprocess_for_matching("  À quelle heure pour Port–Boulet?  ")
        'a quelle heure pour port-boulet'
        >>> preprocess_for_matching("JE VEUX ALLER À PARIS")
        'je veux aller a paris'
    """
    if not text or not isinstance(text, str):
        return ""

    # Step 1: Normalize hyphens and apostrophes
    text = normalize_hyphens(text)
    text = normalize_apostrophes(text)

    # Step 2: Remove accents
    text = remove_accents(text)

    # Step 3: Normalize text (lowercase, whitespace)
    text = normalize_text(text, lowercase=True, remove_extra_spaces=True)

    # Step 4: Remove non-alphanumeric except spaces, hyphens, apostrophes
    text = remove_non_alphanumeric(text, keep_spaces=True,
                                   keep_hyphens=True, keep_apostrophes=True)

    return text


def split_multi_word_name(name: str) -> List[str]:
    """
    Split multi-word station/city names handling hyphens and spaces.

    Args:
        name: Station or city name

    Returns:
        List of name components

    Examples:
        >>> split_multi_word_name("Port-Boulet")
        ['Port', 'Boulet']
        >>> split_multi_word_name("La Rochelle")
        ['La', 'Rochelle']
        >>> split_multi_word_name("Aix-en-Provence")
        ['Aix', 'en', 'Provence']
    """
    if not name or not isinstance(name, str):
        return []

    # Split on both hyphens and spaces
    components = re.split(r'[-\s]+', name)

    return [comp for comp in components if comp]


def fuzzy_normalize(text: str) -> str:
    """
    Aggressive normalization for fuzzy matching (removes all special chars).
    Useful for handling misspellings and variations.

    Args:
        text: Input text

    Returns:
        Aggressively normalized text

    Examples:
        >>> fuzzy_normalize("Port-Boulet")
        'portboulet'
        >>> fuzzy_normalize("Aix-en-Provence")
        'aixenprovence'
    """
    if not text or not isinstance(text, str):
        return ""

    # Remove accents
    text = remove_accents(text, keep_cedilla=False)

    # Convert to lowercase
    text = text.lower()

    # Remove all non-alphanumeric characters (including spaces and hyphens)
    text = re.sub(r'[^a-z0-9]', '', text)

    return text


def extract_quoted_text(text: str) -> List[str]:
    """
    Extract text within quotes (for handling complex sentences with names).

    Args:
        text: Input text potentially containing quoted sections

    Returns:
        List of quoted text fragments

    Examples:
        >>> extract_quoted_text('Je veux aller à "Port-Boulet" depuis Tours')
        ['Port-Boulet']
        >>> extract_quoted_text("Mon ami 'Albert' vient de Albert")
        ['Albert']
    """
    if not text or not isinstance(text, str):
        return []

    # Find text in double quotes
    double_quoted = re.findall(r'"([^"]*)"', text)

    # Find text in single quotes
    single_quoted = re.findall(r"'([^']*)'", text)

    return double_quoted + single_quoted


def clean_sentence_id(sentence_id: str) -> str:
    """
    Clean and validate sentence ID from input.

    Args:
        sentence_id: Raw sentence ID from input

    Returns:
        Cleaned sentence ID

    Examples:
        >>> clean_sentence_id("  123  ")
        '123'
        >>> clean_sentence_id("abc_456")
        'abc_456'
    """
    if not sentence_id or not isinstance(sentence_id, str):
        return ""

    return sentence_id.strip()


if __name__ == "__main__":
    # Example usage
    test_sentences = [
        "  Je veux aller à Paris  ",
        "À quelle heure pour Port–Boulet?",
        "JE VOUDRAIS UN BILLET TOULOUSE PARIS",
        "Mon amie Florence voyage de Lyon à Florence",
        "Aix—en—Provence depuis Marseille",
        "je souhaite me rendre a paris depuis toulouse"
    ]

    print("=== Text Preprocessing Examples ===\n")

    for sentence in test_sentences:
        print(f"Original: {sentence}")
        print(f"Preprocessed: {preprocess_for_matching(sentence)}")
        print(f"Tokens: {tokenize_french(preprocess_for_matching(sentence))}")
        print()
