import os
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def merge_and_remove_duplicates(new_data_files, output_file):
    try:
        # Read new data from the input files
        data_frames = []
        for new_file in new_data_files:
            logging.info(f"Reading {new_file}...")
            df = pd.read_csv(new_file)
            data_frames.append(df)
        
        # Combine new data into one DataFrame
        logging.info("Combining new data...")
        new_data = pd.concat(data_frames, ignore_index=True)

        # Check if the output file exists
        if os.path.exists(output_file):
            logging.info(f"{output_file} exists. Reading existing data...")
            existing_data = pd.read_csv(output_file)
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            logging.info(f"{output_file} does not exist. Creating it...")
            combined_data = new_data

        # Remove duplicates, keeping rows where 'Farsi' is not empty
        logging.info("Removing duplicates...")
        combined_data['Farsi'] = combined_data['Farsi'].fillna('')
        combined_data.sort_values(by='Farsi', ascending=False, inplace=True)
        deduplicated_data = combined_data.drop_duplicates(subset=['ICAO', 'NOTAM No'], keep='first')

        # Save the result back to the output file
        logging.info(f"Saving deduplicated data to {output_file}...")
        deduplicated_data.to_csv(output_file, index=False)

        logging.info("Merging and deduplication completed successfully!")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    # Input CSV files
    input_files = ["notam_fetch_ourairports.csv", "notam_fetch_faa.csv"]

    # Output CSV file
    output_file = "notam_data.csv"

    # Merge and remove duplicates
    merge_and_remove_duplicates(input_files, output_file)
