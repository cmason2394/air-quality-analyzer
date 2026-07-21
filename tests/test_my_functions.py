
import pytest
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

class TestChangeTimeUnit:
    """Tests for the change_time_unit function."""
    def test_change_time_unit_less_than_60_returns_seconds(self):
        assert mf.change_time_unit(50) == (50, 's')
    def test_change_time_unit_60_seconds_returns_1_min(self):
        assert mf.change_time_unit(60) == (1.0, 'min')
    def test_change_time_unit_90_seconds_returns_1_and_half_min(self):
        assert mf.change_time_unit(90) == (1.5, 'min')
    def test_change_time_unit_3600_seconds_returns_1_hrs(self):
        assert mf.change_time_unit(3600) == (1.0, 'hrs')
    def test_change_time_unit_5400_seconds_returns_1_and_half_hrs(self):
        assert mf.change_time_unit(5400) == (1.5, 'hrs')
    def test_change_time_86400_seconds_returns_1_day(self):
        assert mf.change_time_unit(86400) == (1.0, 'days')
    def test_change_time_unit_129600_seconds_returns_1_and_half_days(self):
        assert mf.change_time_unit(129600) == (1.5, 'days')
    def test_change_time_unit_0_returns_0_seconds(self):
        assert mf.change_time_unit(0) == (0, 's')
    def test_change_time_unit_1_and_half_seconds_returns_1_and_half_seconds(self):
        assert mf.change_time_unit(1.5) == (1.5, 's')
    def test_change_time_unit_60_and_half_seconds_returns_1_min(self):
        assert mf.change_time_unit(60.5) == (1.0, 'min')
    def test_change_time_unit_negative_number_raises_ValueError(self):
        with pytest.raises(ValueError):
            mf.change_time_unit(-10)
    def test_change_time_unit_big_number_returns_days(self):
        assert mf.change_time_unit(99999999) == (1157.4, 'days')

    
    