import pandas as pd

def find_unique_emails(file1, file2, output_file):
    # Read the two CSV files into pandas DataFrames
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Ensure that both files have a column named 'email' (or rename accordingly)
    if 'email' not in df1.columns or 'email' not in df2.columns:
        raise ValueError("Both CSV files must contain an 'email' column.")

    # Normalize the email addresses to lowercase and remove leading/trailing spaces
    emails_file1 = set(df1['email'].str.strip().str.lower())
    emails_file2 = set(df2['email'].str.strip().str.lower())

    # Find emails in file1 that are not in file2
    unique_emails = emails_file1 - emails_file2

    # Create a DataFrame for the unique emails
    unique_emails_df = pd.DataFrame(list(unique_emails), columns=['email'])

    # Save the unique emails to a new CSV file
    unique_emails_df.to_csv(output_file, index=False)

    print(f"Unique email addresses have been saved to {output_file}.")

# Example usage
file1 = 'emails_file1.csv'  # Replace with your first CSV file
file2 = 'paid.csv'  # Replace with your second CSV file
output_file = 'unique_emails.csv'  # Output file for unique emails

find_unique_emails(file1, file2, output_file)
