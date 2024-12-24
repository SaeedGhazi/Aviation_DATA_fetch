import jdatetime
import datetime
import sys
import ntplib

# Persian month names
PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر",
    "مرداد", "شهریور", "مهر", "آبان",
    "آذر", "دی", "بهمن", "اسفند"
]

# Persian day of the week names
PERSIAN_DAYS = [
    "شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه",
    "چهارشنبه", "پنج‌شنبه", "جمعه"
]

def get_ntp_time():
    """Fetch the current time from an NTP server."""
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        ntp_time = datetime.datetime.utcfromtimestamp(response.tx_time)
        return ntp_time
    except Exception as e:
        print(f"Error fetching NTP time: {e}")
        sys.exit(1)

def convert_to_shamsi(date_str, gmt_difference):
    """Convert the given date/time string to Shamsi date and adjust for GMT."""
    date_str = date_str.upper()
    suffix = ""

    # Handle "PERM"
    if date_str == "PERM":
        return "دائمی"

    # Extract suffix (e.g., EST, PERM)
    if " " in date_str:
        date_part, suffix = date_str.split(maxsplit=1)
    else:
        date_part = date_str

    # Set suffix text without affecting time calculation
    suffix_text = " - تخمینی" if suffix == "EST" else ""

    # Determine format length
    if len(date_part) == 10:  # "YYMMDDhhmm"
        year = int(date_part[:2])
        month = int(date_part[2:4])
        day = int(date_part[4:6])
        hour = int(date_part[6:8])
        minute = int(date_part[8:10])
        second = 0
    elif len(date_part) == 12:  # "YYMMDDhhmmss"
        year = int(date_part[:2])
        month = int(date_part[2:4])
        day = int(date_part[4:6])
        hour = int(date_part[6:8])
        minute = int(date_part[8:10])
        second = int(date_part[10:12])
    else:
        raise ValueError("Invalid date format")

    # Adjust year
    if year < 50:
        year += 2000
    else:
        year += 1900

    # Create datetime object
    input_datetime = datetime.datetime(year, month, day, hour, minute, second)
    
    # Apply GMT difference
    local_datetime = input_datetime + datetime.timedelta(hours=gmt_difference)

    # Convert to Shamsi date
    shamsi_date = jdatetime.datetime.fromgregorian(datetime=local_datetime)
    persian_day_of_week = PERSIAN_DAYS[shamsi_date.weekday()]
    persian_month_name = PERSIAN_MONTHS[shamsi_date.month - 1]

    formatted_time = local_datetime.strftime("%H:%M:%S")
    formatted_date = f"{persian_day_of_week} {shamsi_date.day} {persian_month_name} ({shamsi_date.month}) {shamsi_date.year} ساعت {formatted_time} محلی{suffix_text}"
    return formatted_date

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python shamsi_date.py <format/ntp> <date_string/GMT_difference> [GMT_difference]")
        sys.exit(1)

    date_format = sys.argv[1]
    gmt_difference = float(sys.argv[3]) if date_format != "ntp" else float(sys.argv[2])

    try:
        if date_format == "ntp":
            # Fetch time from NTP server
            current_time = get_ntp_time()
            gmt_delta = datetime.timedelta(hours=gmt_difference)
            local_time = current_time + gmt_delta
            shamsi_date = jdatetime.datetime.fromgregorian(datetime=local_time)
            persian_day_of_week = PERSIAN_DAYS[shamsi_date.weekday()]
            persian_month_name = PERSIAN_MONTHS[shamsi_date.month - 1]

            formatted_time = local_time.strftime("%H:%M:%S")
            formatted_date = f"{persian_day_of_week} {shamsi_date.day} {persian_month_name} ({shamsi_date.month}) {shamsi_date.year} ساعت {formatted_time} محلی"
            print(formatted_date)
        else:
            # Convert provided date
            result = convert_to_shamsi(sys.argv[2], gmt_difference)
            print(result)
    except Exception as e:
        print(f"Error: {e}")
