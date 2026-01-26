import pandas as pd
import pytest
from typing import List, Dict, Any
from dataframe_processing import replace_and_flatten_activities

@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Fixture for a standard activities DataFrame."""
    data = {
        'id': [1, 2, 3, 4],
        'activities': [
            ['run', 'swim', 'cycle'],
            ['walk', 'run', 'read'],
            ['cycle', 'eat'],
            ['sleep', 'read'] # No replacements
        ]
    }
    return pd.DataFrame(data)

@pytest.fixture
def replacement_map() -> Dict[str, List[str]]:
    """Fixture for the replacement dictionary."""
    return {
        'run': ['marathon', 'stretch'],
        'cycle': ['triathlon', 'prep'],
        'read': ['book', 'magazine']
    }

def test_full_replacement(replacement_map: Dict[str, List[str]]):
    """Test case where multiple items are replaced."""
    input_list = ['run', 'swim', 'cycle']
    expected_output = ['marathon', 'stretch', 'swim', 'triathlon', 'prep']
    assert replace_and_flatten_activities(input_list, replacement_map) == expected_output

def test_partial_replacement(replacement_map: Dict[str, List[str]]):
    """Test case where only one item is replaced and others are kept."""
    input_list = ['walk', 'run', 'read']
    expected_output = ['walk', 'marathon', 'stretch', 'book', 'magazine']
    assert replace_and_flatten_activities(input_list, replacement_map) == expected_output

def test_no_replacement(replacement_map: Dict[str, List[str]]):
    """Test case where no items in the list are keys in the map."""
    input_list = ['sleep', 'eat']
    expected_output = ['sleep', 'eat']
    assert replace_and_flatten_activities(input_list, replacement_map) == expected_output

def test_empty_list(replacement_map: Dict[str, List[str]]):
    """Test case for an empty input list."""
    input_list: List[str] = []
    expected_output: List[str] = []
    assert replace_and_flatten_activities(input_list, replacement_map) == expected_output

def test_replacement_map_application(sample_dataframe: pd.DataFrame, replacement_map: Dict[str, List[str]]):
    """
    Integration test: Check the function's application on the entire pandas Series.
    """
    df = sample_dataframe.copy()
    
    # Apply the function to the 'activities' column
    df['modified_activities'] = df['activities'].apply(
        lambda x: replace_and_flatten_activities(x, replacement_map)
    )
    
    # Define the expected results for all rows
    expected_activities = [
        ['marathon', 'stretch', 'swim', 'triathlon', 'prep'], # run, swim, cycle
        ['walk', 'marathon', 'stretch', 'book', 'magazine'],   # walk, run, read
        ['triathlon', 'prep', 'eat'],                          # cycle, eat
        ['sleep', 'book', 'magazine']                                      # sleep, read (no replacement for 'sleep')
    ]
    
    # Assert tht the resulting column matches the expected list
    pd.testing.assert_series_equal(
        df['modified_activities'],
        pd.Series(expected_activities, name='modified_activities'),
        check_names=True
    )
