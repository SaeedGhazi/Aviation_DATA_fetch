import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def merge_and_remove_duplicates(file1, file2, output_file):
    try:
        # Read the CSV files into DataFrames
        logging.info(f"Reading {file1}...")
        df1 = pd.read_csv(file1)
        logging.info(f"Reading {file2}...")
        df2 = pd.read_csv(file2)

        # Concatenate the DataFrames
        logging.info("Merging data...")
        combined_df = pd.concat([df1, df2])

        # Remove duplicates based on 'ICAO' and 'NOTAM No'
        logging.info("Removing duplicate rows...")
        deduplicated_df = combined_df.drop_duplicates(subset=['ICAO', 'NOTAM No'])

        # Save the merged and deduplicated DataFrame to a new CSV file
        logging.info(f"Saving merged data to {output_file}...")
        deduplicated_df.to_csv(output_file, index=False)

        logging.info("Merging and deduplication completed successfully!")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    # Input CSV files
    file1 = "notam_fetch_ourairports.csv"
    file2 = "notam_fetch_faa.csv"

    # Output CSV file
    output_file = "notam_data.csv"

    # Merge and remove duplicates
    merge_and_remove_duplicates(file1, file2, output_file)
