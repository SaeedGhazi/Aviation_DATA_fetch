import jdatetime
import datetime
import sys
import ntplib
import time

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
    year = int(date_str[:2])
    if year < 50:  # Adjust for 2000s
        year += 2000
    else:  # Adjust for 1900s
        year += 1900
    month = int(date_str[2:4])
    day = int(date_str[4:6])
    hour = int(date_str[6:8])
    minute = int(date_str[8:10])
    second = int(date_str[10:12])

    # Create a datetime object
    input_datetime = datetime.datetime(year, month, day, hour, minute, second)
    
    # Adjust for GMT difference
    gmt_delta = datetime.timedelta(hours=float(gmt_difference))
    local_datetime = input_datetime + gmt_delta

    # Convert to Shamsi date
    shamsi_date = jdatetime.datetime.fromgregorian(datetime=local_datetime)
    persian_day_of_week = PERSIAN_DAYS[shamsi_date.weekday()]
    persian_month_name = PERSIAN_MONTHS[shamsi_date.month - 1]

    formatted_time = local_datetime.strftime("%H:%M:%S")
    formatted_date = f"{persian_day_of_week} {shamsi_date.day} {persian_month_name} ({shamsi_date.month}) {shamsi_date.year} ساعت {formatted_time} محلی"
    return formatted_date

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python shamsi_date.py <format/ntp> <date_string/GMT_difference> [GMT_difference]")
        sys.exit(1)

    date_format = sys.argv[1]
    gmt_difference = sys.argv[3] if date_format != "ntp" else sys.argv[2]

    try:
        if date_format == "ntp":
            # Fetch time from NTP server
            current_time = get_ntp_time()
            gmt_delta = datetime.timedelta(hours=float(gmt_difference))
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
