import pandas as pd
import re
from collections import defaultdict
from typing import List, Dict
def get_all_values_of_column(df, column_name):
    column_name_of_list = column_name + '3'
    df[column_name]  = df[column_name] .apply(lambda x: x.replace(' ', '') if isinstance(x, str) else x)
    df[column_name_of_list] = df[column_name].apply(lambda x: x.split(',') if isinstance(x, str) else [])

    df[column_name_of_list] = df[column_name_of_list].apply(lambda x: sorted(x) if isinstance(x, list) else x)
    df[column_name_of_list].value_counts()
    all_values = list(set().union(*df[column_name_of_list]))
    all_values = [x.lower() for x in all_values]
    all_values = sorted(list(set(all_values)))
    return df, all_values

def normalize_ratings(df):
    df['rating'] = df['rating'].apply(lambda x: x.split("/")[0])
    df['rating'] = df['rating'].apply(lambda x: x.replace('"', ''))
    df['rating'] = df['rating'].apply(lambda x: x.replace(',', '.'))
    df['rating'] = df['rating'].apply(lambda x: float(x) if str(x).replace('.', '', 1).isdigit() else 5.01)
    return df

def extract_date(filename):
    # Assuming the date is always the first part of the filename
    date_str = filename.split()[0] 
    return pd.to_datetime(date_str, format='%d-%m-%Y')

def drop_unnecessary_columns(df):
    df.drop(columns=["Start", "End", "Name", "Author",])
    return df

def check_coocurrence(df, column_name, main_activity):
    dart_days = df[df[column_name].apply(lambda x: main_activity in x if isinstance(x, list) else False)]
    print(f"Days with {main_activity}: {len(dart_days)}")
    print(f"Average rating with {main_activity}: {dart_days['rating'].mean():.2f}")
    print(f"Average rating without {main_activity}: {df[~df.index.isin(dart_days.index)]['rating'].mean():.2f}")

    # See what activities co-occur with dart
    from collections import Counter
    cooccur = Counter()
    for activities in dart_days[column_name]:
        for act in activities:
            if act != main_activity:
                cooccur[act] += 1

    print(f"\nTop activities that co-occur with {main_activity}:")
    for act, count in cooccur.most_common(10):
        print(f"  {act}: {count} times ({count/len(dart_days)*100:.1f}%)")

import re
import pandas as pd
from collections import defaultdict

# --- Configuration for Units to Strip ---
# Define common units to be stripped from the item name after quantity extraction.
# This pattern is built to be case-insensitive and handle optional spaces after the unit.
UNITS_TO_STRIP = [
    r'L\s*', r'l\s*', r'ML\s*', r'ml\s*', r'CL\s*', r'cl\s*', # Volume (Liters, milliliters, centiliters)
    r'KG\s*', r'kg\s*', r'G\s*', r'g\s*', # Weight (Kilograms, grams)
    r'STK\s*', r'stk\s*', r'X\s*', # Count (Stück/piece, x)
    r'TL\s*', r'tbl\s*', r'EL\s*', # Spoons/Measures
]
# Compile the regex pattern for efficient stripping
UNIT_PATTERN = re.compile(f'^({"|".join(UNITS_TO_STRIP)})', re.IGNORECASE)


def normalize_item(item):
    """
    Normalize a single item (e.g., '3x Oranges' -> '3.0 Oranges').
    This function's output format is now slightly redundant but kept for original structure.
    """
    # Use the stricter regex: requires at least one digit
    match = re.match(r'^(\d*\.?\d+)(x?)?\s*(.*)$', str(item).strip())
    
    if match:
        prefix, _, name = match.groups()
        # The prefix should now be safely convertible to float
        
        # Use the unit stripping logic here for a clean item name, 
        # but keep the float prefix format for the intermediate step
        name_with_units = name.strip()
        name_cleaned = UNIT_PATTERN.sub('', name_with_units).strip()
        if not name_cleaned:
             # Fallback if only a unit remains
            return f"{float(prefix)} {name_with_units}"
        
        return f"{float(prefix)} {name_cleaned}"
        
    return str(item).strip()  # No prefix (e.g., "Lemons")


def normalize_and_count(item):
    """
    Extract item name and quantity, and now additionally strips common units 
    from the beginning of the item name.
    """
    item_str = str(item).strip()
    
    # 1. Extract quantity and the rest of the string ('name')
    match = re.match(r'^(\d*\.?\d+)(x?)?\s*(.*)$', item_str)
    
    if match:
        quantity, _, name = match.groups()
        quantity = float(quantity)
        name = name.strip()

        # 2. Strip units from the start of the remaining name string
        # This handles cases like '2LWasser' -> name='LWasser' -> name_cleaned='Wasser'
        name_cleaned = UNIT_PATTERN.sub('', name).strip()
        
        # Fallback in case stripping resulted in an empty string (e.g., input was just '2L')
        if not name_cleaned:
            return (name, quantity)
            
        return (name_cleaned, quantity)
    
    # Default quantity = 1.0 if no prefix is found
    return (item_str, 1.0)


def generate_specialized_dataframe_with_counts(df, column_name):
    """
    Generates a DataFrame with unique items and their total quantities,
    now using the unit-aware normalize_and_count function.
    """
    # Ensure all list elements are strings
    df[column_name] = df[column_name].apply(lambda x: [str(i) for i in x])
    
    # Initialize a dictionary to accumulate counts
    item_counts = defaultdict(float)

    # Iterate over all entries in the target column
    for item_list in df[column_name]:
        for item in item_list:
            # Use the modified normalize_and_count
            name, quantity = normalize_and_count(item)
            item_counts[name] += quantity

    # Convert to a DataFrame for better readability
    count_df = pd.DataFrame(
        {"Item": item_counts.keys(), "Total Quantity": item_counts.values()}
    ).sort_values("Total Quantity", ascending=False)
    
    # Remove the intermediate normalized column if it was created
    if "normalized_item_list" in df.columns:
        df.drop(columns=["normalized_item_list"], inplace=True)
        
    return count_df
    
def replace_and_flatten_activities(activity_list: List[str], replacement_map: Dict[str, List[str]]) -> List[str]:
    """
    Replaces elements in a list if they are keys in the replacement_map
    (which contains list values) and flattens the resulting list.
    """
    new_activity_list: List[Any] = []
    
    for activity in activity_list:
        if activity in replacement_map:
            # If the activity is a key, append the list of replacement values
            new_activity_list.append(replacement_map[activity])
        else:
            # Otherwise, append the original activity
            new_activity_list.append(activity)

    # 4. Flatten the final list
    # The list may now contain a mix of strings and lists of strings (from the replacement)
    flattened_list: List[str] = []
    for item in new_activity_list:
        if isinstance(item, list):
            # Extend the list with the elements of the replacement list
            flattened_list.extend(item)
        else:
            # Append the original string element
            flattened_list.append(item)
    
            
    return sorted(flattened_list)

