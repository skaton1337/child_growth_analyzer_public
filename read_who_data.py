import pandas as pd
import os

# Define the file path
file_path = r"C:\Users\Skaton\Desktop\Enkeltsunami\who_data\hfa-boys-perc-who2007-exp.csv"

# Debug: Print current working directory
print(f"Current working directory: {os.getcwd()}")
print(f"Checking if file exists at: {file_path}")

# Verify if file exists
if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
    who_data_dir = os.path.dirname(file_path)
    if os.path.exists(who_data_dir):
        print(f"\nContents of {who_data_dir}:")
        for file in os.listdir(who_data_dir):
            print(f"  - {file}")
    else:
        print(f"\nDirectory not found: {who_data_dir}")
    exit()

try:
    # Read raw CSV file contents with semicolon delimiter
    df = pd.read_csv(
        file_path,
        header=None,  # Don't try to detect headers
        delimiter=';',  # Use semicolon as delimiter
        skip_blank_lines=True,
        decimal=',',  # Handle European decimal format if present
    )
    
    # Only proceed if we have the correct number of columns
    if len(df.columns) == 16:
        # Add column names for all WHO percentiles
        column_names = ['Age_months', 'P01', 'P1', 'P3', 'P5', 'P10', 'P15', 'P25', 'P50', 
                        'P75', 'P85', 'P90', 'P95', 'P97', 'P99', 'P999']
        df.columns = column_names

        # Convert data to numeric type for calculations
        for col in df.columns:
            # Replace any commas with periods for decimal points
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Display the formatted data
        pd.set_option('display.float_format', '{:.1f}'.format)
        print("\nHeight-for-age percentiles (boys):")
        print("===================================")
        print("Age (years) | Height (cm) for different percentiles")
        print("-" * 70)
        
        # Format each row
        for index, row in df.iterrows():
            try:
                months = row['Age_months']
                if pd.isna(months):  # Skip rows with NaN values
                    continue
                    
                years = months / 12
                
                # Format age string based on the age range
                if years <= 5:
                    # Show half years for ages 0-5
                    if months % 6 == 0:  # Only show every 6 months
                        age_str = f"{years:5.1f}"
                        percentiles = ' | '.join(f"{val:5.1f}" if not pd.isna(val) else '  N/A ' for val in row[1:])
                        print(f"{age_str:11s} | {percentiles}")
                else:
                    # Show full years for ages 5-19
                    if months % 12 == 0:  # Only show every 12 months
                        age_str = f"{int(years):2d}"
                        percentiles = ' | '.join(f"{val:5.1f}" if not pd.isna(val) else '  N/A ' for val in row[1:])
                        print(f"{age_str:11s} | {percentiles}")
                        
            except Exception as row_error:
                print(f"Skipping row {index} due to error: {row_error}")

except Exception as e:
    print(f"An error occurred: {str(e)}") 