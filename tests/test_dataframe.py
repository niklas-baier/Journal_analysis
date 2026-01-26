import pandas as pd
import pytest
from typing import List, Dict, Any
from diary_analyzer.dataframe_processing import replace_and_flatten_activities, normalize_ratings
import numpy as np
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
    return {
        'run': ['marathon', 'stretch'],
        'cycle': ['triathlon', 'prep'],
        'read': ['book', 'magazine']
    }
"""
# ____________________________ test_full_replacement _____________________________
def test_full_replacement(replacement_map: Dict[str, List[str]]):
    input_list = ['run', 'swim', 'cycle']
    # Sorted order: marathon, prep, stretch, swim, triathlon
    expected_output = ['marathon', 'prep', 'stretch', 'swim', 'triathlon']
    print(sorted(expected_output)
    assert replace_and_flatten_activities(input_list, replacement_map) == sorted(expected_output)

# ___________________________ test_partial_replacement ___________________________
def test_partial_replacement(replacement_map: Dict[str, List[str]]):
    input_list = ['walk', 'run', 'read']
    # Sorted order: book, magazine, marathon, stretch, walk
    expected_output = ['book', 'magazine', 'marathon', 'stretch', 'walk']
    assert replace_and_flatten_activities(input_list, replacement_map) == sorted(expected_output)

# _____________________________ test_no_replacement ______________________________
def test_no_replacement(replacement_map: Dict[str, List[str]]):
    input_list = ['sleep', 'eat']
    # Sorted order: eat, sleep
    expected_output = ['eat', 'sleep']
    assert replace_and_flatten_activities(input_list, replacement_map) == sorted(expected_output)
def test_empty_list(replacement_map: Dict[str, List[str]]):
    input_list: List[str] = []
    expected_output: List[str] = []
    assert replace_and_flatten_activities(input_list, replacement_map) == sorted(expected_output)
"""
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
        ['marathon', 'prep', 'stretch', 'swim', 'triathlon'], # 'prep' moves up
        ['book', 'magazine', 'marathon', 'stretch', 'walk'],  # 'book' moves up
        ['eat', 'prep', 'triathlon'],                         # 'eat' moves up
        ['book', 'magazine', 'sleep']                         # 'book' moves up
    ]
    # Assert tht the resulting column matches the expected list
    pd.testing.assert_series_equal(
        df['modified_activities'],
        pd.Series(expected_activities, name='modified_activities'),
        check_names=True
    )
'''
def test_normalize_ratings_edge_cases():
    """
    Tests the normalize_ratings function against various edge cases including:
    - Minimum and maximum valid values (0 and 10).
    - Values just outside the valid range (e.g., -0.1, 10.1).
    - Different numeric formats (integers, floats, fraction strings 'X/10').
    - Invalid data types and formats (strings, None, NaN).
    - An empty DataFrame.
    """
    
    # 1. Setup the DataFrame with Edge Case Data
    data = {
        'rating': [
            # --- Valid Edge Cases (0 and 10) ---
            '0/10',     # Min fraction
            0,          # Min integer
            0.0,        # Min float
            '10/10',    # Max fraction
            10,         # Max integer
            10.0,       # Max float
            
            # --- Boundary Violations (Should be NaN) ---
            '-0.1',     # Below 0
            10.1,       # Above 10
            '11/10',    # Fraction above 10
            '-1/10',    # Fraction below 0

            # --- Mixed Valid Formats ---
            '5/10',     # Mid-range fraction
            1,          # Small integer
            9.9,        # Near-max float
            
            # --- Invalid/Missing Data (Should be NaN) ---
            'N/A',      # Non-numeric string
            None,       # Python None
            np.nan,     # NumPy NaN
            'ten',      # Non-numeric word
            '5/9',      # Incorrect fraction denominator
            '',         # Empty string
            '10/0',     # Division by zero attempt (should be handled as invalid format)
            '0.5',      # Float as a string
            1.1,        # Your example float
            2           # Your example integer
        ]
    }
    df = pd.DataFrame(data)

    # 2. Define Expected Results (normalized to float 0.0-10.0 or NaN)
    # The order MUST match the 'rating' column in the DataFrame
    expected_results = [
        0.0, 0.0, 0.0,  # Min
        10.0, 10.0, 10.0, # Max
        np.nan, np.nan, np.nan, np.nan, # Boundary Violations
        5.0, 1.0, 9.9, # Mixed Valid
        np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, # Invalid/Missing
        0.5, 1.1, 2.0 # Your examples
    ]

    # 3. Call the function
    result_df = normalize_ratings(df.copy()) # Use a copy to ensure purity

    # 4. Assertions
    
    # Check 1: The output column 'normalized_rating' exists
    assert 'normalized_rating' in result_df.columns, "Output DataFrame must contain 'normalized_rating' column."
    
    # Check 2: The length of the result matches the expected length
    assert len(result_df) == len(expected_results), "Result DataFrame size does not match expected size."
    
    # Check 3: Data types are correct (should be float for normalized values)
    assert pd.api.types.is_float_dtype(result_df['normalized_rating']), "The normalized column should be of float type."

    # Check 4: Compare the results, paying attention to NaNs
    # This is the most crucial step. `np.testing.assert_series_equal` is best for this.
    expected_series = pd.Series(expected_results, name='normalized_rating')
    
    # The `check_exact=False` and `rtol` allow for floating point comparisons.
    # We use `check_names=False` because the Series name might differ slightly 
    # based on the underlying pandas version or operation, although it should be 
    # 'normalized_rating'.
    pd.testing.assert_series_equal(
        result_df['normalized_rating'],
        expected_series,
        check_names=True,
        check_exact=False,
        rtol=1e-5
    )

    # --- Additional Edge Case: Empty DataFrame ---
    empty_df = pd.DataFrame({'rating': []})
    result_empty_df = normalize_ratings(empty_df.copy())
    
    # Check 5: Empty DataFrame check
    assert result_empty_df.empty, "An empty DataFrame should result in an empty DataFrame."
    assert 'normalized_rating' in result_empty_df.columns, "Even an empty DataFrame should have the new column name."
    
    print("\n✅ All edge cases passed successfully!")'''
