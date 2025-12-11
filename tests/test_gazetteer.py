"""
Unit tests for gazetteer module
"""

import unittest
import sys
import tempfile
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from nlp.gazetteer import (
    Gazetteer,
    load_gazetteer,
    MAJOR_FRENCH_CITIES,
    MULTI_WORD_STATIONS
)


class TestGazetteerBasics(unittest.TestCase):
    """Test basic gazetteer functionality"""

    def setUp(self):
        """Create a fresh gazetteer for each test"""
        self.gaz = Gazetteer()

    def test_initialization(self):
        """Test gazetteer initializes with default cities"""
        self.assertGreater(len(self.gaz), 0)
        self.assertIn("Paris", self.gaz.cities)
        self.assertIn("Lyon", self.gaz.cities)

    def test_add_city(self):
        """Test adding a city"""
        initial_count = len(self.gaz)
        self.gaz.add_city("TestCity")
        self.assertEqual(len(self.gaz), initial_count + 1)
        self.assertIn("TestCity", self.gaz.cities)

    def test_add_station(self):
        """Test adding a station"""
        self.gaz.add_station("Paris Gare du Nord")
        self.assertIn("Paris Gare du Nord", self.gaz.stations)

    def test_get_stats(self):
        """Test getting gazetteer statistics"""
        stats = self.gaz.get_stats()
        self.assertIn('cities', stats)
        self.assertIn('stations', stats)
        self.assertIn('total_locations', stats)
        self.assertGreater(stats['cities'], 0)


class TestLocationValidation(unittest.TestCase):
    """Test location validation functionality"""

    def setUp(self):
        """Create a fresh gazetteer for each test"""
        self.gaz = Gazetteer()

    def test_is_valid_location_exact(self):
        """Test exact location validation"""
        self.assertTrue(self.gaz.is_valid_location("Paris"))
        self.assertTrue(self.gaz.is_valid_location("Lyon"))
        self.assertFalse(self.gaz.is_valid_location("Gotham"))

    def test_is_valid_location_case_insensitive(self):
        """Test case-insensitive validation"""
        self.assertTrue(self.gaz.is_valid_location("paris"))
        self.assertTrue(self.gaz.is_valid_location("PARIS"))
        self.assertTrue(self.gaz.is_valid_location("PaRiS"))

    def test_is_valid_location_with_accents(self):
        """Test validation with accent variations"""
        # Add city with accents
        self.gaz.add_city("Sète")
        self.assertTrue(self.gaz.is_valid_location("Sète"))
        self.assertTrue(self.gaz.is_valid_location("Sete"))  # Without accents

    def test_contains_operator(self):
        """Test __contains__ operator"""
        self.assertIn("Paris", self.gaz)
        self.assertNotIn("Gotham", self.gaz)

    def test_get_canonical_name(self):
        """Test getting canonical name"""
        self.assertEqual(self.gaz.get_canonical_name("paris"), "Paris")
        self.assertEqual(self.gaz.get_canonical_name("LYON"), "Lyon")
        self.assertIsNone(self.gaz.get_canonical_name("Gotham"))

    def test_multi_word_stations(self):
        """Test multi-word station names"""
        self.assertTrue(self.gaz.is_valid_location("Port-Boulet"))
        self.assertTrue(self.gaz.is_valid_location("La Rochelle"))
        # Test case insensitive with hyphens
        self.assertTrue(self.gaz.is_valid_location("port-boulet"))


class TestFindMatches(unittest.TestCase):
    """Test finding location names in text"""

    def setUp(self):
        """Create a fresh gazetteer for each test"""
        self.gaz = Gazetteer()

    def test_find_single_location(self):
        """Test finding a single location"""
        text = "Je veux aller à Paris"
        matches = self.gaz.find_matches(text)
        self.assertIn("Paris", matches)
        self.assertEqual(len(matches), 1)

    def test_find_multiple_locations(self):
        """Test finding multiple locations"""
        text = "Je veux aller de Paris à Lyon"
        matches = self.gaz.find_matches(text)
        self.assertIn("Paris", matches)
        self.assertIn("Lyon", matches)
        self.assertEqual(len(matches), 2)

    def test_find_with_case_variations(self):
        """Test finding with case variations"""
        text = "Je veux aller de PARIS à lyon"
        matches = self.gaz.find_matches(text)
        self.assertIn("Paris", matches)
        self.assertIn("Lyon", matches)

    def test_find_multi_word_station(self):
        """Test finding multi-word station names"""
        text = "Comment aller à Port-Boulet"
        matches = self.gaz.find_matches(text)
        self.assertIn("Port-Boulet", matches)

    def test_find_no_matches(self):
        """Test with text containing no locations"""
        text = "Quelle heure est-il?"
        matches = self.gaz.find_matches(text)
        self.assertEqual(len(matches), 0)

    def test_find_duplicate_prevention(self):
        """Test that same location isn't added twice"""
        text = "De Paris à Lyon puis retour à Paris"
        matches = self.gaz.find_matches(text)
        # Paris should only appear once in matches
        self.assertEqual(matches.count("Paris"), 1)


class TestFuzzyMatching(unittest.TestCase):
    """Test fuzzy matching functionality"""

    def setUp(self):
        """Create a fresh gazetteer for each test"""
        self.gaz = Gazetteer()

    def test_fuzzy_match_exact(self):
        """Test fuzzy match with exact name"""
        matches = self.gaz.fuzzy_match("Paris", max_distance=2)
        self.assertTrue(len(matches) > 0)
        # First match should be exact
        self.assertEqual(matches[0][0], "Paris")
        self.assertEqual(matches[0][1], 0)

    def test_fuzzy_match_misspelling(self):
        """Test fuzzy match with misspelling"""
        matches = self.gaz.fuzzy_match("Parris", max_distance=3)
        self.assertTrue(len(matches) > 0)
        # Should find Paris
        names = [m[0] for m in matches]
        self.assertIn("Paris", names)

    def test_fuzzy_match_no_results(self):
        """Test fuzzy match with completely different word"""
        matches = self.gaz.fuzzy_match("Gotham", max_distance=2)
        # Should have no good matches within distance 2
        self.assertEqual(len(matches), 0)

    def test_fuzzy_match_sorted_by_distance(self):
        """Test that fuzzy matches are sorted by distance"""
        matches = self.gaz.fuzzy_match("Lyon", max_distance=5)
        if len(matches) > 1:
            # Distances should be in ascending order
            for i in range(len(matches) - 1):
                self.assertLessEqual(matches[i][1], matches[i+1][1])


class TestFileOperations(unittest.TestCase):
    """Test loading and saving gazetteer data"""

    def setUp(self):
        """Create a fresh gazetteer for each test"""
        self.gaz = Gazetteer()

    def test_save_and_load_json(self):
        """Test saving to and loading from JSON"""
        # Add a custom city
        self.gaz.add_city("TestCity")

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            self.gaz.save_to_json(temp_path)

            # Load into new gazetteer
            new_gaz = Gazetteer()
            # Clear default cities for clean test
            new_gaz.cities.clear()
            new_gaz.stations.clear()
            new_gaz.normalized_to_original.clear()

            new_gaz.load_from_json(temp_path)

            # Check that custom city was loaded
            self.assertIn("TestCity", new_gaz.cities)
        finally:
            # Clean up
            Path(temp_path).unlink()

    def test_load_from_nonexistent_file(self):
        """Test loading from nonexistent file raises error"""
        with self.assertRaises(FileNotFoundError):
            self.gaz.load_from_json("nonexistent_file.json")


class TestAliases(unittest.TestCase):
    """Test alias functionality"""

    def setUp(self):
        """Create a fresh gazetteer for each test"""
        self.gaz = Gazetteer()

    def test_add_alias(self):
        """Test adding an alias"""
        self.gaz.add_alias("Paris", "Paree")
        self.assertIn("paris", self.gaz.aliases)

    def test_default_aliases_loaded(self):
        """Test that default aliases are loaded"""
        self.assertTrue(len(self.gaz.aliases) > 0)
        self.assertIn("paris", self.gaz.aliases)


class TestLoadGazetteer(unittest.TestCase):
    """Test load_gazetteer helper function"""

    def test_load_gazetteer_default(self):
        """Test loading gazetteer with defaults"""
        gaz = load_gazetteer()
        self.assertIsInstance(gaz, Gazetteer)
        self.assertGreater(len(gaz), 0)

    def test_load_gazetteer_with_file(self):
        """Test loading gazetteer with additional file"""
        # Create temp file with additional data
        temp_data = {
            "cities": ["CustomCity1", "CustomCity2"],
            "stations": ["Custom Station"],
            "aliases": {}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(temp_data, f)
            temp_path = f.name

        try:
            gaz = load_gazetteer(temp_path)
            self.assertIn("CustomCity1", gaz.cities)
            self.assertIn("CustomCity2", gaz.cities)
        finally:
            Path(temp_path).unlink()


class TestConstants(unittest.TestCase):
    """Test that constants are properly defined"""

    def test_major_cities_exist(self):
        """Test that major cities list exists and is populated"""
        self.assertTrue(len(MAJOR_FRENCH_CITIES) > 0)
        self.assertIn("Paris", MAJOR_FRENCH_CITIES)
        self.assertIn("Lyon", MAJOR_FRENCH_CITIES)

    def test_multi_word_stations_exist(self):
        """Test that multi-word stations list exists"""
        self.assertTrue(len(MULTI_WORD_STATIONS) > 0)
        self.assertIn("Port-Boulet", MULTI_WORD_STATIONS)
        self.assertIn("La Rochelle", MULTI_WORD_STATIONS)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        """Create a fresh gazetteer for each test"""
        self.gaz = Gazetteer()

    def test_empty_text(self):
        """Test finding matches in empty text"""
        matches = self.gaz.find_matches("")
        self.assertEqual(len(matches), 0)

    def test_short_words_filtered(self):
        """Test that very short words are filtered"""
        matches = self.gaz.find_matches("a b c", min_length=3)
        self.assertEqual(len(matches), 0)

    def test_repr(self):
        """Test string representation"""
        repr_str = repr(self.gaz)
        self.assertIn("Gazetteer", repr_str)
        self.assertIn("cities=", repr_str)

    def test_len(self):
        """Test __len__ operator"""
        length = len(self.gaz)
        self.assertGreater(length, 0)
        self.assertIsInstance(length, int)


if __name__ == '__main__':
    unittest.main(verbosity=2)
