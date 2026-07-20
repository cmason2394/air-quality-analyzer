from assets import my_functions as mf

class TestContainsNumber:
    """Tests for the contains_number function."""
    def test_contains_number_with_digit_returns_true(self):
        assert mf.contains_number('abc123') == True

    def test_contains_number_without_digit_returns_false(self):
        assert mf.contains_number('abcdef') == False

    def test_contains_number_empty_string_returns_false(self):
        assert mf.contains_number('') == False

    def test_contains_number_single_character_returns_true(self):
        assert mf.contains_number('1') == True

class TestContainsLetter:
    """Tests for the contains_letter function."""
    def test_contains_letter_with_letter_returns_true(self):
        assert mf.contains_letter('abc123') == True

    def test_contains_letter_without_letter_returns_false(self):
        assert mf.contains_letter('123456') == False

    def test_contains_letter_empty_string_returns_false(self):
        assert mf.contains_letter('') == False

    def test_contains_letter_single_character_returns_true(self):
        assert mf.contains_letter('a') == True