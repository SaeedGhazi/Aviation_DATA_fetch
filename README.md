# Aviation_DATA_fetch
Aviation Data Mining

# FAA Notams (https://www.notams.faa.gov/dinsQueryWeb/queryRetrievalMapAction.do?reportType=Raw&retrieveLocId={icao}&actionType=notamRetrievalbyICAOs)
- notam_fetch_faa.py {ICAO}
  e.g : python3 notam_fetch_faa.py 'OIII'
- notam_fetch_faa.py {filename.csv}
  e.g : python3 notam_fetch_faa.py IRAN_AIRPORTS.csv

  output : a csv file with the following header :
    ICAO,NOTAM No,Q Code,From,To,Schedule,Text,Lower,Limit,Upper,Limit,Created Time,Farsi

# OurAirports.com (https://ourairports.com/airports/{icao}/notams.html)
- notam_fetch_ourairports.py {ICAO}
  e.g : python3 notam_fetch_ourairports.py 'OIII'
- notam_fetch_ourairports.py {filename.csv}
  e.g : python3 notam_fetch_ourairports.py IRAN_AIRPORTS.csv

  output : a csv file with the following header :
    ICAO,NOTAM No,Q Code,From,To,Schedule,Text,Lower,Limit,Upper,Limit,Created Time,Farsi
