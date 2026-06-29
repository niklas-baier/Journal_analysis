import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
import pandas as pd

def save_fig(file_name):
    # Define paths relative to the script location
    OUTPUT_DIR = Path("../outputs/figures")
    LOG_DIR = Path("../outputs/logs")

    # Create folders if they don't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    plt.savefig(OUTPUT_DIR / file_name)



def visualize_rating_progression(df_sorted):
    plt.figure(figsize=(10, 6))
    plt.plot(df_sorted['date'], df_sorted['rating'], marker='o')
    plt.xlabel('Date')
    plt.ylabel('Rating')
    plt.title('Rating Over Time')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    save_fig("rating_over_time")
    plt.show()

def plot_boxplot_of_weekdays(df):
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # Create the boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='weekday', y='rating', order=weekday_order, palette='pastel', showmeans=True)
    plt.xlabel('Weekday')
    plt.ylabel('Rating')
    plt.title('Distribution of Ratings by Weekday')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    save_fig("boxplot_of_weekdays")
    plt.show()


def calculate_time_of_sleep(wakeup_time, sleeping_start):
    """Calculates duration handling midnight wrap-around"""
    if pd.isna(wakeup_time) or pd.isna(sleeping_start):
        return np.nan
    return (wakeup_time - sleeping_start) % 24


def time_to_float(time_str):
    """Converts 'HH.MM' string to a float (e.g., '23.30' -> 23.5)"""
    time_str =  time_str.replace('"','')
    try:
        if pd.isna(time_str) or not isinstance(time_str, str):
            return np.nan
        
       
        if '.' in time_str:
            hours, minutes = map(int, time_str.split('.'))
        else:
            # Handle cases like "1" or "23"
            hours = int(time_str)
            minutes = 0
            
        return hours + minutes/60
    except (ValueError, AttributeError):
        return np.nan
    
def plot_sleep_duration(df):
        # 2. Data Cleaning
    # Drop rows where essential time data is missing

    df_clean = df.dropna(subset=['Aufstehzeitpunkt', 'Schlafensgehzeitpunkt']).copy()

    df_clean = df.dropna(subset=['Aufstehzeitpunkt', 'Schlafensgehzeitpunkt']).copy()
    print(df_clean.shape)

    # 3. Processing
    # Create temporary float columns for calculation
    df_clean['wakeup_f'] = df_clean['Aufstehzeitpunkt'].apply(time_to_float)
    df_clean['bedtime_f'] = df_clean['Schlafensgehzeitpunkt'].apply(time_to_float)

    # Calculate sleep duration
    df_clean['time_of_sleep'] = df_clean.apply(
        lambda row: calculate_time_of_sleep(row['wakeup_f'], row['bedtime_f']), 
        axis=1
    )
    print(df_clean[['Aufstehzeitpunkt', 'Schlafensgehzeitpunkt', 'wakeup_f', 'bedtime_f', 'time_of_sleep']])

    # Final filter: remove rows where time_to_float failed (e.g. bad formatting)

    df_clean = df_clean.dropna(subset=['time_of_sleep'])


    # 4. Plotting
    plt.figure(figsize=(10, 5))

    # X-axis is just a range from 1 to the number of valid rows
    days = np.arange(1, len(df_clean) + 1)

    plt.scatter(days, df_clean['time_of_sleep'], color='blue', edgecolors='black')
    plt.plot(days, df_clean['time_of_sleep'], color='blue', alpha=0.3, linestyle='--')
    plt.scatter(days, df_clean['rating'], color='red', edgecolors='black')
    plt.plot(days, df_clean['rating'], color='red', alpha=0.3, linestyle='--')

    plt.title('Sleep Duration(blue) Over Time and rating (red)')
    plt.xlabel('Day (Sequence of valid entries)')
    plt.ylabel('Hours of Sleep')
    plt.xticks(days) # Ensure every day has a tick mark
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    save_fig("sleep_duration")
    plt.show()

    # 5. Remove unnecessary helper columns
    df_final = df_clean.drop(columns=['wakeup_f', 'bedtime_f'])
    return df_final
