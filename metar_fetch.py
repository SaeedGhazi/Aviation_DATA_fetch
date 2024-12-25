import requests
import re
import pandas as pd

def parse_metar(raw_metar):
    """Parse a raw METAR string into a structured dictionary."""
    metar_data = {
        "ICAO": "",
        "DateTime": "",
        "WIND_DIR": "",
        "WIND_SPEED": "",
        "WIND_GUST": "",
        "WIND_VAR": "",
        "VIS": "",
        "CLOUD1": "",
        "CLOUD2": "",
        "CLOUD3": "",
        "CLOUD4": "",
        "TEMP": "",
        "DEW": "",
        "HUMIDITY": "",
        "PRESSURE_HPA": "",
        "PRESSURE_INCH": "",
        "WX_PHENOMENA": "",
        "INTENSITY": "",
        "REMARKS": "",
        "RAW_METAR": raw_metar
    }

    # Extract ICAO code
    match = re.search(r"^METAR\s([A-Z]{4})", raw_metar)
    if match:
        metar_data["ICAO"] = match.group(1)

    # Extract DateTime
    match = re.search(r"\s(\d{6})Z", raw_metar)
    if match:
        metar_data["DateTime"] = match.group(1)  # Modify this to convert to UTC if needed

    # Extract Wind
    match = re.search(r"(\d{3})(\d{2})(G\d{2})?KT", raw_metar)
    if match:
        metar_data["WIND_DIR"] = int(match.group(1))
        metar_data["WIND_SPEED"] = int(match.group(2))
        metar_data["WIND_GUST"] = match.group(3)[1:] if match.group(3) else ""

    # Extract Variable Wind
    match = re.search(r"(\d{3}V\d{3})", raw_metar)
    if match:
        metar_data["WIND_VAR"] = match.group(1)

    # Extract Visibility
    match = re.search(r"(\d{1,4})SM", raw_metar)
    if match:
        metar_data["VIS"] = int(match.group(1)) * 1609  # Convert SM to meters

    # Extract Cloud Layers
    cloud_layers = re.findall(r"(FEW|SCT|BKN|OVC)(\d{3})", raw_metar)
    for i, (coverage, height) in enumerate(cloud_layers[:4]):
        metar_data[f"CLOUD{i + 1}"] = f"{coverage}{height}"

    # Extract Temperature and Dew Point
    match = re.search(r"(M?\d{2})/(M?\d{2})", raw_metar)
    if match:
        metar_data["TEMP"] = int(match.group(1).replace("M", "-") if match.group(1) else "")
        metar_data["DEW"] = int(match.group(2).replace("M", "-") if match.group(2) else "")

    # Calculate Humidity
    if metar_data["TEMP"] and metar_data["DEW"]:
        temp_c = metar_data["TEMP"]
        dew_c = metar_data["DEW"]
        humidity = 100 * (6.112 * 2.71828**((17.67 * dew_c) / (dew_c + 243.5))) / (6.112 * 2.71828**((17.67 * temp_c) / (temp_c + 243.5)))
        metar_data["HUMIDITY"] = round(humidity, 1)

    # Extract Pressure
    match = re.search(r"A(\d{4})", raw_metar)
    if match:
        pressure_inHg = int(match.group(1)) / 100
        metar_data["PRESSURE_HPA"] = round(pressure_inHg * 33.8639, 1)  # Convert inHg to hPa
        metar_data["PRESSURE_INCH"] = pressure_inHg

    # Extract Weather Phenomena and Intensity
    wx_match = re.findall(r"(\+|-)?(RA|SN|FG|BR|TS|HZ|DZ)", raw_metar)
    if wx_match:
        metar_data["WX_PHENOMENA"] = ", ".join([wx[1] for wx in wx_match])
        metar_data["INTENSITY"] = wx_match[0][0] if wx_match[0][0] else ""

    # Extract Remarks
    match = re.search(r"RMK\s(.+)$", raw_metar)
    if match:
        metar_data["REMARKS"] = match.group(1)

    return metar_data


def save_metar_to_csv(metar_data, file_path):
    """Save parsed METAR data to a CSV file."""
    df = pd.DataFrame(metar_data)
    df.to_csv(file_path, index=False)


def fetch_and_process_metar(icao, output_file):
    """Fetch METAR data for a given ICAO code, parse it, and save it to a CSV file."""
    #url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao}.TXT"
    url = f"https://aviationweather.gov/data/metar/?id={icao}&hours=0&include_taf=yes"
    try:
        response = requests.get(url)
        response.raise_for_status()
        raw_metar = response.text.strip().splitlines()[-1]  # Take the latest METAR
        parsed_metar = [parse_metar(raw_metar)]
        save_metar_to_csv(parsed_metar, output_file)
        print(f"METAR data saved to {output_file}")
    except Exception as e:
        print(f"Error fetching or processing METAR: {e}")


if __name__ == "__main__":
    icao_code = "OIII"  # Replace with the desired ICAO code
    output_csv = "METAR_data.csv"
    fetch_and_process_metar(icao_code, output_csv)
