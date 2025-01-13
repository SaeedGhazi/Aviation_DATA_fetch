# Aviation_DATA_fetch
Aviation Data Mining
pip install -r requirements.txt
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

  
## merge_notam_lists.py
- merges the two csv and append to notam_data.csv (if exists , if not creates it).
- then removes the duplicates but keeps the one that its 'Farsi' column is not empty.







﻿- The “ourairport.com.py” fetches the notam of airports listed in "IRAN_AIRPORTS_4_letter_Names.csv" and stores them in "notam_data.csv”
﻿- The “ourairport.com.py” fetches the notam of airports listed in "IRAN_AIRPORTS_4_letter_Names.csv" and stores them in "notam_data.csv” hourly (by crontab)



- The "telegram-bot.INLINE.2.py" runs a telegram bot. by which :
    /metar [xxxx] returns the metar of xxxx airport from AVWX.rest site by API TOKEN.
    /notam [xxxx] returns the notam of xxxx airport stored in "notam_data.csv".



-----------------
- A code/service should be written to update "notam_data.csv" priodically and some airports with high refresh period.
@ -17,3 +16,62 @@ The telegram-bot.INLINE.2.py is the true bot.
- A code for calendar
- Finally a telegram Group/Channel that the bot send all above mentioned to it.
- (The files imtotextbot.py and telegram_bot.py should be reconsidered.)




_______________________________
# Make the bot a service
برای آنکه برنامه بات را دائمی کنیم که حتی با ریست شدن رزپبری بازهم اجرا شود باید یک سرویس بسازیم.

sudo nano /etc/systemd/system/telegram-bot.service

با محتویات زیر :
ــــــــــــــــ
[Unit]
Description=Telegram Bot Service
After=network.target tor.service
Wants=tor.service

[Service]
Type=idle
WorkingDirectory=/home/ssq/bot
ExecStart=/bin/bash -c 'source /home/ssq/bot/bin/activate && cd /home/ssq/bot/Aviation_DATA_fetch-main/ && proxychains python3 telegram-bot.py'
Restart=always
User=ssq
Environment="TELEGRAM_TOKEN={}"
Environment="AVWX_TOKEN={}"

[Install]
WantedBy=multi-user.target




## Wait for Tor to be ready
ExecStartPre=/bin/bash -c 'until [ "$(systemctl is-active tor)" = "active" ]; do sleep 5; done'

[Install]
WantedBy=multi-user.target
ــــــــــــــــــ
sudo systemctl enable telegram-bot.service
sudo systemctl start telegram-bot.service
ــــــــــــــــــ
sudo systemctl status telegram-bot.service
journalctl -u telegram-bot.service -f
اگر نیاز شد باید systemd ریستارت شود :

sudo systemctl daemon-reload
sudo systemctl restart telegram-bot.service
ــــــــــــــــــ
برای آنکه برنامه ourairport.py مفاد نوتامها را استخراج کند یک crontab می‌سازیم :

crontab -e

0 * * * * /bin/bash -c 'source /home/ssq/bot/bin/activate && python3 /home/ssq/bot/ourairport.com.py' >> /home/ssq/bot/notam_update.log 2>&1
ــــــــــــــــــ
برای بررسی cron :

crontab -l
ــــــــــــــــــ
cat /path/to/notam_update.log
ــــــــــــــــــ


برنامه ourairport.com.py پس از آنکه نوتام ها را استخراج کرد برنامه gemini_notam_for_farsi.py را فراخوانی می کند تا شرح فارسی نوتام را استخراج کند و در ستون انتهایی یعنی Farsi قرار دهد (در صورت خالی بودن آن سلول)
باید یک فایل command شود که prompt از آن استخراج شود. دلیل زیر درخور توجه است :
-Ensure the text you send to the API doesn't contain sensitive aviation-related terms that could be misinterpreted (e.g., "danger," "restricted," "closed," etc.).
-The content of the Text, Schedule, Lower Limit, Upper Limit, From, or To fields might contain words or phrases that the Gemini API considers potentially dangerous.






  
