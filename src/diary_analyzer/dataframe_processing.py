import pandas as pd
import re
from collections import defaultdict
from typing import List, Dict
def convert_to_list(df, column_name):
    # Step 1: Clean strings (remove spaces) and leave floats/NaN as-is
    df[column_name] = df[column_name].apply(
        lambda x: x.replace(' ', '') if isinstance(x, str) else x
    )
    # Step 2: Split strings by comma, convert non-strings to empty lists
    df[column_name] = df[column_name].apply(
        lambda x: x.split(',') if isinstance(x, str) else []
    )
    # Step 3: Sort lists (if they exist), otherwise keep as-is
    df[column_name] = df[column_name].apply(
        lambda x: sorted(x) if isinstance(x, list) else x
    )
    return df


def normalize_list(input_list):
    input_list = [x.lower() for x in input_list]
    return input_list
def get_total_list(df, column_name):
    total_list = list(set().union(*df[column_name]))
    total_list = normalize_list(total_list)
    total_list = sorted(list(set(total_list)))
    return total_list

def get_all_values_of_column(df, column_name):
    column_list_name = column_name + '3'
    
    # We copy the data to the '3' column so we don't destroy the original data
    df[column_list_name] = df[column_name]
    df = convert_to_list(df, column_list_name)

    # 2. Flatten all lists into one single Series (converted to lowercase)
    # .explode() is perfect here as it handles the list structure directly
    all_values_series = df[column_list_name].explode().str.lower()
    
    # 3. Drop NaNs and empty strings
    all_values_series = all_values_series.dropna()
    all_values_series = all_values_series[all_values_series != ""]

    # 4. Count occurrences
    counts = all_values_series.value_counts()

    # 5. Convert to a list of tuples (value, count) sorted alphabetically
    all_values_with_counts = sorted(list(counts.items()))

    return df, all_values_with_counts
   

def normalize_ratings(df):
    df['rating'] = df['rating'].apply(lambda x: x.split("/")[0])
    df['rating'] = df['rating'].apply(lambda x: x.replace('"', ''))
    df['rating'] = df['rating'].apply(lambda x: x.replace(',', '.'))
    df['rating'] = df['rating'].apply(lambda x: float(x) if str(x).replace('.', '', 1).isdigit() else 5.01)
    return df
import re
def remove_pasted_images(df):
    df['content'] = df['content'].apply(lambda text: re.sub(r'\!\[\[.*?\]\]', '', text))
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

def remove_empty(df, column_name):
    df = df[df[column_name]!=""]
    return df
       


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
    count_df = remove_empty(count_df, 'Item')
    
    
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
def drop_unnecessary_rows(df):
    df = remove_pasted_images(df) # remove images from the text
    #df[df['content'].str.contains(r'\!\[\[')].shape
    df = df[df['content'].str.strip() != '']
    non_empty_df = df.query('content != ""') # filter out all the values that are empty 

   
    return non_empty_df


def preprocess_dataframe(df):
    df = normalize_ratings(df)
    df = drop_unnecessary_columns(df)
    non_empty_df = drop_unnecessary_rows(df)
   
    #sorting by ascending date
    non_empty_df['date'] = non_empty_df['filename'].apply(extract_date)
    df_sorted = non_empty_df.sort_values(by='date')
    return df_sorted
    
def get_likely_substitutions(all_people):
    # check for permutations assumption if the permutation is the same then the person is probably the same

    # check for occurrences the assumption being that usually the name that occcurs more often is the correct spelling. 
    names = [ name for name,_ in all_people]
    #makeing a dict for faster lookup
    all_people_dict = { name:value_count for name,value_count in all_people}
    print(names)
    alphabetical_permutations = [''.join(sorted(name.lower())) for name in names]
    # probably when there is a typo in the permutation it is more likely to be the same person 
    zip_permutations = list(zip(names, alphabetical_permutations))
    # sort after the permutation
    zip_permutations = sorted(zip_permutations, key=lambda x: (x[1], x[0])) # sort by permutation then name
    names_subsitutions = {} # with first name being the name that gets substituted
    for i in range(len(zip_permutations)-1):
        name1, perm1 = zip_permutations[i]
        for j in range(i+1, len(zip_permutations)):
            name2, perm2 = zip_permutations[j]
            # if the permutations are the same then the names are likely the same person
            if perm1 == perm2:
                print(f"Possible same person: {name1} and {name2} (permutation: {perm1})") # technically multiple collisions are possible but unlikely
                if all_people_dict[name1] > all_people_dict[name2]:
                    names_subsitutions[name2] = name1
                else:
                    names_subsitutions[name1] = name2

                
            else:
                break
            
    print(names_subsitutions.items())
    return names_subsitutions

def correct_permutations(df, column_name):
    df, all_values = get_all_values_of_column(df, column_name)
    print(f'all values are {all_values}')
    names_subsitutions = get_likely_substitutions(all_values)
    df = convert_to_list(df, column_name=column_name)
    df[column_name] = df[column_name].apply(lambda person_list: [names_subsitutions.get(name, name) for name in person_list] if isinstance(person_list, list) else person_list)
    return df
def identify_compound_replacements(all_activities: List[str]) -> Dict[str, List[str]]:
    """
    Identifies compound words in the alphabetically sorted activity list 
    using a prefix-matching strategy within starting-character groups.
    
    Args:
        all_activities: A list of all unique, cleaned, and lowercased activity strings, 
                        assumed to be alphabetically sorted.
                        
    Returns:
        A dictionary mapping compound words to a list containing its two components.
        Example: {'programmingtest': ['programming', 'test']}
    """
    if not all_activities:
        return {}

    # 1. Group activities by their starting character
    groups = defaultdict(list)
    for activity in all_activities:
        if activity: # Ensure we don't process empty strings
            groups[activity[0]].append(activity)

    replacements = {}
    
    # Convert all activities to a set for O(1) membership check (crucial for remainder check)
    activity_set: Set[str] = set(all_activities)

    # 2. Iterate through each group to perform prefix checking
    for char, group in groups.items():
        # The group is already sorted alphabetically because the original list was sorted.
        
        # Iterate through the group, treating each element as a potential prefix
        for i in range(len(group)):
            prefix = group[i]
            
            # Iterate through the remaining elements in the group (potential compounds)
            for j in range(i + 1, len(group)):
                compound = group[j]
                
                # If a split was already found for the compound, skip it 
                # (e.g., if 'soccer' already split 'soccerpractice', we don't want 'soc' to re-split it)
                if compound in replacements:
                    continue
                
                # 3. Check for Prefix Match
                if compound.startswith(prefix):
                    # Calculate the remainder (potential second word)
                    remainder = compound[len(prefix):]
                    
                    # 4. Final Validity Check
                    # The remainder must be a non-empty string AND a known, valid activity 
                    # from the master list (activity_set).
                    if remainder and remainder in activity_set:
                        # Found a valid compound!
                        replacements[compound] = [prefix, remainder]
                        
                        # Note: We do NOT break the inner loop (j) here, because 
                        # a longer prefix later in the group (j) might also apply 
                        # and could be a more accurate split, but in this specific 
                        # algorithm, we add the first valid split found.
                        
    return replacements

def solve_missing_separation(df, column_name, all_values):
    replacements_map = identify_compound_replacements(all_values)
    replacements_map_sorted  = {k: sorted(v) for k,v in replacements_map.items()} # sorting for faster comparison


    # print("\n--- Compound Replacements Map ---")
    print(replacements_map_sorted)

    # 5. Apply the function to the DataFrame column
    # We create a new column 'modified_activities' to store the result
    modified_name = f'modified{column_name}'
    df[modified_name] = df[column_name].apply(
        lambda x: replace_and_flatten_activities(x, replacements_map)
    )
    return df



