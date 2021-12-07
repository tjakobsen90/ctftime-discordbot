A simple bot that queries ctftime's upcoming events and posts them in Discord.

I use cron to run the script:
$ crontab -l
00 19 * * 1 /usr/bin/python3 /opt/ctftime/ctftime.py
