import pandas as pd

def remove_duplicates(input_file, output_file):
    # Read the CSV file into a pandas DataFrame without assuming headers
    df = pd.read_csv(input_file, header=None, names=["email"])

    # Remove duplicate rows
    df_cleaned = df.drop_duplicates()

    # Save the cleaned DataFrame to a new CSV file
    df_cleaned.to_csv(output_file, index=False, header=False)

    print(f"Duplicates have been removed. Cleaned data saved to {output_file}.")

# Example usage
input_file = 'input.csv'  # Replace with your input CSV file
output_file = 'cleaned_output.csv'  # Replace with your desired output CSV file

remove_duplicates(input_file, output_file)
