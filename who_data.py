"""
WHO Growth Standards data for height-for-age percentiles
Data source: World Health Organization (WHO) Child Growth Standards
"""

import pandas as pd
from scipy.interpolate import interp1d
import numpy as np
import os
import sys

# Get the base directory - works both in development and when packaged
if getattr(sys, 'frozen', False):
    # Running as compiled executable (PyInstaller)
    base_dir = sys._MEIPASS
else:
    # Running as script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct relative paths to WHO data files
boys_file = os.path.join(base_dir, 'who_data', 'hfa-boys-perc-who2007-exp.csv')
girls_file = os.path.join(base_dir, 'who_data', 'hfa-girls-perc-who2007-exp.csv')

# Read boys data
boys_df = pd.read_csv(
    boys_file, 
    header=0,        # Skip the first row (header)
    delimiter=';', 
    decimal=',',
    skiprows=1       # Skip the header row
)
boys_df.columns = ['Age_months', 'P01', 'P1', 'P3', 'P5', 'P10', 'P15', 'P25', 'P50', 
                   'P75', 'P85', 'P90', 'P95', 'P97', 'P99', 'P999']

# Read girls data
girls_df = pd.read_csv(
    girls_file, 
    header=0,        # Skip the first row (header)
    delimiter=';', 
    decimal=',',
    skiprows=1       # Skip the header row
)
girls_df.columns = ['Age_months', 'P01', 'P1', 'P3', 'P5', 'P10', 'P15', 'P25', 'P50', 
                    'P75', 'P85', 'P90', 'P95', 'P97', 'P99', 'P999']

# Convert data to dictionaries
WHO_BOYS_PERCENTILES = {}
WHO_GIRLS_PERCENTILES = {}

# Process boys data
for _, row in boys_df.iterrows():
    try:
        months = float(str(row['Age_months']).replace(',', '.'))
        years = months / 12
        
        # Only include data points at specified intervals
        if years <= 5:
            if months % 6 == 0:  # Every 6 months for ages 0-5
                age = round(years, 1)
                WHO_BOYS_PERCENTILES[age] = {
                    'P01': float(str(row['P01']).replace(',', '.')),
                    'P1': float(str(row['P1']).replace(',', '.')),
                    'P3': float(str(row['P3']).replace(',', '.')),
                    'P5': float(str(row['P5']).replace(',', '.')),
                    'P10': float(str(row['P10']).replace(',', '.')),
                    'P15': float(str(row['P15']).replace(',', '.')),
                    'P25': float(str(row['P25']).replace(',', '.')),
                    'P50': float(str(row['P50']).replace(',', '.')),
                    'P75': float(str(row['P75']).replace(',', '.')),
                    'P85': float(str(row['P85']).replace(',', '.')),
                    'P90': float(str(row['P90']).replace(',', '.')),
                    'P95': float(str(row['P95']).replace(',', '.')),
                    'P97': float(str(row['P97']).replace(',', '.')),
                    'P99': float(str(row['P99']).replace(',', '.')),
                    'P999': float(str(row['P999']).replace(',', '.'))
                }
        else:
            if months % 12 == 0:  # Every 12 months for ages 5+
                age = int(years)
                WHO_BOYS_PERCENTILES[age] = {
                    'P01': float(str(row['P01']).replace(',', '.')),
                    'P1': float(str(row['P1']).replace(',', '.')),
                    'P3': float(str(row['P3']).replace(',', '.')),
                    'P5': float(str(row['P5']).replace(',', '.')),
                    'P10': float(str(row['P10']).replace(',', '.')),
                    'P15': float(str(row['P15']).replace(',', '.')),
                    'P25': float(str(row['P25']).replace(',', '.')),
                    'P50': float(str(row['P50']).replace(',', '.')),
                    'P75': float(str(row['P75']).replace(',', '.')),
                    'P85': float(str(row['P85']).replace(',', '.')),
                    'P90': float(str(row['P90']).replace(',', '.')),
                    'P95': float(str(row['P95']).replace(',', '.')),
                    'P97': float(str(row['P97']).replace(',', '.')),
                    'P99': float(str(row['P99']).replace(',', '.')),
                    'P999': float(str(row['P999']).replace(',', '.'))
                }
    except ValueError as e:
        continue  # Skip any rows that can't be converted to numbers

# Process girls data
for _, row in girls_df.iterrows():
    try:
        months = float(str(row['Age_months']).replace(',', '.'))
        years = months / 12
        
        # Only include data points at specified intervals
        if years <= 5:
            if months % 6 == 0:  # Every 6 months for ages 0-5
                age = round(years, 1)
                WHO_GIRLS_PERCENTILES[age] = {
                    'P01': float(str(row['P01']).replace(',', '.')),
                    'P1': float(str(row['P1']).replace(',', '.')),
                    'P3': float(str(row['P3']).replace(',', '.')),
                    'P5': float(str(row['P5']).replace(',', '.')),
                    'P10': float(str(row['P10']).replace(',', '.')),
                    'P15': float(str(row['P15']).replace(',', '.')),
                    'P25': float(str(row['P25']).replace(',', '.')),
                    'P50': float(str(row['P50']).replace(',', '.')),
                    'P75': float(str(row['P75']).replace(',', '.')),
                    'P85': float(str(row['P85']).replace(',', '.')),
                    'P90': float(str(row['P90']).replace(',', '.')),
                    'P95': float(str(row['P95']).replace(',', '.')),
                    'P97': float(str(row['P97']).replace(',', '.')),
                    'P99': float(str(row['P99']).replace(',', '.')),
                    'P999': float(str(row['P999']).replace(',', '.'))
                }
        else:
            if months % 12 == 0:  # Every 12 months for ages 5+
                age = int(years)
                WHO_GIRLS_PERCENTILES[age] = {
                    'P01': float(str(row['P01']).replace(',', '.')),
                    'P1': float(str(row['P1']).replace(',', '.')),
                    'P3': float(str(row['P3']).replace(',', '.')),
                    'P5': float(str(row['P5']).replace(',', '.')),
                    'P10': float(str(row['P10']).replace(',', '.')),
                    'P15': float(str(row['P15']).replace(',', '.')),
                    'P25': float(str(row['P25']).replace(',', '.')),
                    'P50': float(str(row['P50']).replace(',', '.')),
                    'P75': float(str(row['P75']).replace(',', '.')),
                    'P85': float(str(row['P85']).replace(',', '.')),
                    'P90': float(str(row['P90']).replace(',', '.')),
                    'P95': float(str(row['P95']).replace(',', '.')),
                    'P97': float(str(row['P97']).replace(',', '.')),
                    'P99': float(str(row['P99']).replace(',', '.')),
                    'P999': float(str(row['P999']).replace(',', '.'))
                }
    except ValueError as e:
        continue  # Skip any rows that can't be converted to numbers

def create_percentile_interpolators():
    """Create interpolation functions for each percentile for both boys and girls."""
    percentiles = ['P01', 'P1', 'P3', 'P5', 'P10', 'P15', 'P25', 'P50',
                  'P75', 'P85', 'P90', 'P95', 'P97', 'P99', 'P999']
    
    boys_interpolators = {}
    girls_interpolators = {}
    
    # Create interpolators for boys
    ages_boys = sorted(WHO_BOYS_PERCENTILES.keys())
    for p in percentiles:
        heights = [WHO_BOYS_PERCENTILES[age][p] for age in ages_boys]
        boys_interpolators[p] = interp1d(ages_boys, heights, kind='cubic')
    
    # Create interpolators for girls
    ages_girls = sorted(WHO_GIRLS_PERCENTILES.keys())
    for p in percentiles:
        heights = [WHO_GIRLS_PERCENTILES[age][p] for age in ages_girls]
        girls_interpolators[p] = interp1d(ages_girls, heights, kind='cubic')
    
    return boys_interpolators, girls_interpolators

def calculate_exact_percentile(age, height, interpolators, gender='both'):
    """Calculate the exact percentile for a given height and age."""
    percentiles = [0.1, 1, 3, 5, 10, 15, 25, 50, 75, 85, 90, 95, 97, 99, 99.9]
    percentile_keys = ['P01', 'P1', 'P3', 'P5', 'P10', 'P15', 'P25', 'P50',
                      'P75', 'P85', 'P90', 'P95', 'P97', 'P99', 'P999']
    
    boys_interp, girls_interp = interpolators
    
    if gender == 'both':
        # Calculate for both genders
        heights_at_percentiles_boys = [boys_interp[p](age) for p in percentile_keys]
        heights_at_percentiles_girls = [girls_interp[p](age) for p in percentile_keys]
        
        # Calculate percentile for each gender
        boys_percentile = np.interp(height, heights_at_percentiles_boys, percentiles)
        girls_percentile = np.interp(height, heights_at_percentiles_girls, percentiles)
        
        return {
            'boys': round(boys_percentile, 1),
            'girls': round(girls_percentile, 1),
            'average': round((boys_percentile + girls_percentile) / 2, 1)
        }
    else:
        # Use the appropriate interpolators based on gender
        is_male = gender in ['male', 'boys']  # Accept both 'male' and 'boys'
        interp = interpolators[0] if is_male else interpolators[1]
        heights_at_percentiles = [interp[p](age) for p in percentile_keys]
        result = np.interp(height, heights_at_percentiles, percentiles)
        
        if is_male:
            return {'boys': round(result, 1), 'girls': None, 'average': round(result, 1)}
        else:
            return {'boys': None, 'girls': round(result, 1), 'average': round(result, 1)}

# Clean up - remove the dataframes as they're no longer needed
del boys_df
del girls_df

if __name__ == "__main__":
    # Print some sample data to verify
    print("\nSample boys data at age 2.5 years:")
    print(WHO_BOYS_PERCENTILES[2.5])
    
    print("\nSample girls data at age 10 years:")
    print(WHO_GIRLS_PERCENTILES[10])
    
    # Test interpolation
    boys_interp, girls_interp = create_percentile_interpolators()
    test_age = 3.5
    test_height = 100
    percentile = calculate_exact_percentile(test_age, test_height, (boys_interp, girls_interp), 'male')
    print(f"\nTest: A {test_height}cm tall boy at {test_age} years is at the {percentile:.1f}th percentile") 