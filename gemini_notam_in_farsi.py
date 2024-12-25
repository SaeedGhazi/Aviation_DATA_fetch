import pandas as pd
import google.generativeai as genai
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Your Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def load_dictionary(dict_file):
    """Load the English-to-Farsi dictionary from a CSV file."""
    dictionary = {}
    if os.path.exists(dict_file):
        df = pd.read_csv(dict_file)
        if 'English' in df.columns and 'Farsi' in df.columns:
            dictionary = pd.Series(df['Farsi'].values, index=df['English']).to_dict()
    return dictionary

def get_farsi_translation(text, dictionary):
    """Connect to Gemini API and get the Farsi translation."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = (
            f"""
            Please provide a short concisely and clearly description, using aviation terminology and phrases, for the following NOTAM (Notice to Airmen) in Farsi(Persian), keep the english aviation terminology :
            '{text}'.
            there is no need for date/time expression/conversion, no need for saying Creation date/time and the source (OIIIYNYX) .
            Use the following English-to-Farsi(or English abbreviation) dictionary for specific terms:
            {dictionary}
            """
        )

        logging.info("Sending request to Gemini API...")
        response = model.generate_content(prompt)
        logging.info("Received response from Gemini API.")
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error with Gemini API: {e}")
        return ""

def update_farsi_column(csv_file, dict_file):
    """Update the 'Farsi' column for rows where it is empty or nan."""
    try:
        # Load the CSV file
        df = pd.read_csv(csv_file)
        
        # Ensure 'Farsi' column exists
        if 'Farsi' not in df.columns:
            df['Farsi'] = ""

        # Load the dictionary
        dictionary = load_dictionary(dict_file)

        # Identify rows where 'Farsi' is empty or nan
        rows_to_update = df[df['Farsi'].isna() | df['Farsi'].eq("")]
        
        # Log the total number of rows to be processed
        logging.info(f"Total rows to process: {len(rows_to_update)}")
        
        # Iterate through the rows and update 'Farsi' column
        for index, row in rows_to_update.iterrows():
            logging.info(f"Processing row index: {index}")
            text = row['Text']
            #schedule = row['Schedule'] if pd.notna(row['Schedule']) else ''
            #lower_limit = row['Lower Limit'] if pd.notna(row['Lower Limit']) else ''
            #upper_limit = row['Upper Limit'] if pd.notna(row['Upper Limit']) else ''
            #from_date = row['From'] if pd.notna(row['From']) else ''
            #to_date = row['To'] if pd.notna(row['To']) else ''

            # Combine the relevant fields into a single text block
            combined_text = f"{text}"

            #combined_text = f"{text}\nSchedule: {schedule}\nLower Limit: {lower_limit}\nUpper Limit: {upper_limit}\nFrom: {from_date}\nTo: {to_date}"

            # Get the Farsi translation from Gemini API
            translation = get_farsi_translation(combined_text, dictionary)

            if translation:
                df.at[index, 'Farsi'] = translation
                logging.info(f"Updated row index: {index}")
                # Save the file after each successful update
                df.to_csv(csv_file, index=False)
                time.sleep(1)  # Add delay to avoid rate limits

        logging.info("Farsi column updated successfully!")

    except Exception as e:
        logging.error(f"Error updating Farsi column: {e}")

def main(csv_file, dict_file):
    update_farsi_column(csv_file, dict_file)

if __name__ == "__main__":
    csv_file = "notam_data.csv"
    dict_file = "dict.for.gemini.csv"
    main(csv_file, dict_file)
