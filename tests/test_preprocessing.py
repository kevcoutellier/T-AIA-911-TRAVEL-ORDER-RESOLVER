"""
Unit tests for text preprocessing module
"""

import unittest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from nlp.preprocessing import (
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


class TestNormalizeText(unittest.TestCase):
    """Test cases for normalize_text function"""

    def test_basic_normalization(self):
        """Test basic text normalization"""
        text = "  Je veux aller à Paris  "
        result = normalize_text(text)
        self.assertEqual(result, "je veux aller à paris")

    def test_extra_spaces(self):
        """Test removal of extra spaces"""
        text = "Je  veux   aller    à     Paris"
        result = normalize_text(text)
        self.assertEqual(result, "je veux aller à paris")

    def test_no_lowercase(self):
        """Test with lowercase=False"""
        text = "TOULOUSE PARIS"
        result = normalize_text(text, lowercase=False)
        self.assertEqual(result, "TOULOUSE PARIS")

    def test_empty_string(self):
        """Test with empty string"""
        result = normalize_text("")
        self.assertEqual(result, "")

    def test_none_input(self):
        """Test with None input"""
        result = normalize_text(None)
        self.assertEqual(result, "")


class TestRemoveAccents(unittest.TestCase):
    """Test cases for remove_accents function"""

    def test_remove_accents(self):
        """Test removing French accents"""
        text = "à Paris depuis Sète"
        result = remove_accents(text)
        self.assertEqual(result, "a Paris depuis Sete")

    def test_keep_cedilla(self):
        """Test keeping cedilla by default"""
        text = "français"
        result = remove_accents(text)
        self.assertEqual(result, "français")

    def test_remove_cedilla(self):
        """Test removing cedilla when specified"""
        text = "français"
        result = remove_accents(text, keep_cedilla=False)
        self.assertEqual(result, "francais")

    def test_multiple_accents(self):
        """Test removing multiple types of accents"""
        text = "été élève à l'école"
        result = remove_accents(text, keep_cedilla=False)
        self.assertEqual(result, "ete eleve a l'ecole")


class TestNormalizeHyphens(unittest.TestCase):
    """Test cases for normalize_hyphens function"""

    def test_en_dash(self):
        """Test normalizing en dash"""
        text = "Port–Boulet"
        result = normalize_hyphens(text)
        self.assertEqual(result, "Port-Boulet")

    def test_em_dash(self):
        """Test normalizing em dash"""
        text = "Aix—en—Provence"
        result = normalize_hyphens(text)
        self.assertEqual(result, "Aix-en-Provence")

    def test_multiple_dash_types(self):
        """Test with multiple dash types"""
        text = "Port–Boulet—Tours−Paris"
        result = normalize_hyphens(text)
        self.assertEqual(result, "Port-Boulet-Tours-Paris")


class TestNormalizeApostrophes(unittest.TestCase):
    """Test cases for normalize_apostrophes function"""

    def test_right_quote(self):
        """Test normalizing right single quotation mark"""
        text = "l'hôtel"
        result = normalize_apostrophes(text)
        self.assertEqual(result, "l'hôtel")

    def test_left_quote(self):
        """Test normalizing left single quotation mark"""
        text = "'aujourd'hui"
        result = normalize_apostrophes(text)
        self.assertEqual(result, "'aujourd'hui")


class TestRemoveNonAlphanumeric(unittest.TestCase):
    """Test cases for remove_non_alphanumeric function"""

    def test_remove_parentheses(self):
        """Test removing parentheses"""
        text = "Paris (capital)"
        result = remove_non_alphanumeric(text)
        self.assertEqual(result, "Paris capital")

    def test_keep_hyphens(self):
        """Test keeping hyphens by default"""
        text = "Port-Boulet"
        result = remove_non_alphanumeric(text)
        self.assertEqual(result, "Port-Boulet")

    def test_remove_hyphens(self):
        """Test removing hyphens when specified"""
        text = "Port-Boulet?"
        result = remove_non_alphanumeric(text, keep_hyphens=False)
        self.assertEqual(result, "Port Boulet")

    def test_keep_apostrophes(self):
        """Test keeping apostrophes"""
        text = "l'hôtel"
        result = remove_non_alphanumeric(text)
        self.assertEqual(result, "l'hôtel")


class TestTokenizeFrench(unittest.TestCase):
    """Test cases for tokenize_french function"""

    def test_basic_tokenization(self):
        """Test basic tokenization"""
        text = "Je veux aller à Paris"
        result = tokenize_french(text)
        self.assertEqual(result, ['Je', 'veux', 'aller', 'à', 'Paris'])

    def test_hyphenated_name(self):
        """Test tokenization of hyphenated names"""
        text = "Port-Boulet"
        result = tokenize_french(text)
        self.assertEqual(result, ['Port', 'Boulet'])

    def test_keep_punctuation(self):
        """Test keeping punctuation as separate tokens"""
        text = "Paris?"
        result = tokenize_french(text, keep_punctuation=True)
        self.assertIn('Paris', result)
        self.assertIn('?', result)

    def test_empty_string(self):
        """Test with empty string"""
        result = tokenize_french("")
        self.assertEqual(result, [])


class TestPreprocessForMatching(unittest.TestCase):
    """Test cases for complete preprocessing pipeline"""

    def test_full_pipeline(self):
        """Test complete preprocessing pipeline"""
        text = "  À quelle heure pour Port–Boulet?  "
        result = preprocess_for_matching(text)
        self.assertEqual(result, "a quelle heure pour port-boulet")

    def test_uppercase_input(self):
        """Test with uppercase input"""
        text = "JE VEUX ALLER À PARIS"
        result = preprocess_for_matching(text)
        self.assertEqual(result, "je veux aller a paris")

    def test_no_accents_no_special_chars(self):
        """Test that accents and special chars are removed"""
        text = "Aix—en—Provence, Sète!"
        result = preprocess_for_matching(text)
        self.assertEqual(result, "aix-en-provence sete")


class TestSplitMultiWordName(unittest.TestCase):
    """Test cases for split_multi_word_name function"""

    def test_hyphenated_name(self):
        """Test splitting hyphenated name"""
        name = "Port-Boulet"
        result = split_multi_word_name(name)
        self.assertEqual(result, ['Port', 'Boulet'])

    def test_space_separated_name(self):
        """Test splitting space-separated name"""
        name = "La Rochelle"
        result = split_multi_word_name(name)
        self.assertEqual(result, ['La', 'Rochelle'])

    def test_complex_name(self):
        """Test splitting complex multi-word name"""
        name = "Aix-en-Provence"
        result = split_multi_word_name(name)
        self.assertEqual(result, ['Aix', 'en', 'Provence'])

    def test_mixed_separators(self):
        """Test with mixed hyphens and spaces"""
        name = "Saint-Pierre des Corps"
        result = split_multi_word_name(name)
        self.assertEqual(result, ['Saint', 'Pierre', 'des', 'Corps'])


class TestFuzzyNormalize(unittest.TestCase):
    """Test cases for fuzzy_normalize function"""

    def test_aggressive_normalization(self):
        """Test aggressive normalization for fuzzy matching"""
        text = "Port-Boulet"
        result = fuzzy_normalize(text)
        self.assertEqual(result, "portboulet")

    def test_with_accents_and_hyphens(self):
        """Test removing accents and hyphens"""
        text = "Aix-en-Provence"
        result = fuzzy_normalize(text)
        self.assertEqual(result, "aixenprovence")

    def test_with_spaces(self):
        """Test removing spaces"""
        text = "La Rochelle"
        result = fuzzy_normalize(text)
        self.assertEqual(result, "larochelle")


class TestExtractQuotedText(unittest.TestCase):
    """Test cases for extract_quoted_text function"""

    def test_double_quotes(self):
        """Test extracting text in double quotes"""
        text = 'Je veux aller à "Port-Boulet" depuis Tours'
        result = extract_quoted_text(text)
        self.assertEqual(result, ['Port-Boulet'])

    def test_single_quotes(self):
        """Test extracting text in single quotes"""
        text = "Mon ami 'Albert' vient de Albert"
        result = extract_quoted_text(text)
        self.assertEqual(result, ['Albert'])

    def test_multiple_quotes(self):
        """Test extracting multiple quoted sections"""
        text = 'De "Paris" à "Lyon" demain'
        result = extract_quoted_text(text)
        self.assertIn('Paris', result)
        self.assertIn('Lyon', result)

    def test_no_quotes(self):
        """Test with no quoted text"""
        text = "Je veux aller à Paris"
        result = extract_quoted_text(text)
        self.assertEqual(result, [])


class TestCleanSentenceId(unittest.TestCase):
    """Test cases for clean_sentence_id function"""

    def test_clean_whitespace(self):
        """Test removing whitespace from sentence ID"""
        sentence_id = "  123  "
        result = clean_sentence_id(sentence_id)
        self.assertEqual(result, "123")

    def test_alphanumeric_id(self):
        """Test with alphanumeric ID"""
        sentence_id = "abc_456"
        result = clean_sentence_id(sentence_id)
        self.assertEqual(result, "abc_456")

    def test_empty_string(self):
        """Test with empty string"""
        result = clean_sentence_id("")
        self.assertEqual(result, "")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_none_inputs(self):
        """Test functions with None input"""
        self.assertEqual(normalize_text(None), "")
        self.assertEqual(remove_accents(None), "")
        self.assertEqual(tokenize_french(None), [])

    def test_non_string_inputs(self):
        """Test functions with non-string input"""
        self.assertEqual(normalize_text(123), "")
        self.assertEqual(tokenize_french([]), [])

    def test_special_french_characters(self):
        """Test with special French characters"""
        text = "œuvre française"
        result = preprocess_for_matching(text)
        # Should handle œ and ç properly
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
