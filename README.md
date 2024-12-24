# Aviation_DATA_fetch
Aviation Data Mining

## FAA Notams (https://www.notams.faa.gov/dinsQueryWeb/queryRetrievalMapAction.do?reportType=Raw&retrieveLocId={icao}&actionType=notamRetrievalbyICAOs)
extract NOTAMs from the website and store parsed of them in the csv file
### notam_fetch_faa.py {ICAO}
  **e.g : python3 notam_fetch_faa.py 'OIII'**
### notam_fetch_faa.py {filename.csv}
  **e.g : python3 notam_fetch_faa.py IRAN_AIRPORTS.csv**

  output : a csv file with the following header :
    ICAO,NOTAM No,Q Code,From,To,Schedule,Text,Lower,Limit,Upper,Limit,Created Time,Farsi

## OurAirports Notams (https://ourairports.com/airports/{icao}/notams.html)
extract NOTAMs from the website and store parsed of them in the csv file
### notam_fetch_ourairports.py {ICAO}
  **e.g : python3 notam_fetch_ourairports.py 'OIII'**
### notam_fetch_ourairports.py {filename.csv}
  **e.g : python3 notam_fetch_ourairports.py IRAN_AIRPORTS.csv**

  output : a csv file with the following header :
    ICAO,NOTAM No,Q Code,From,To,Schedule,Text,Lower,Limit,Upper,Limit,Created Time,Farsi

## shamsi_date
- returns the shamsi date + day and month text in farsi + GMT add to time
- also extracts the time form ntp servers : 'pool.ntp.org'
  
  **e.g : python shamsi_date.py <format/ntp> <date_string/GMT_difference> [GMT_difference]**
  **e.g : python shamsi_date.py "YYMMDDhhmmss" "241212123526" 3.5**
  **e.g : python shamsi_date.py ntp 3.5**
