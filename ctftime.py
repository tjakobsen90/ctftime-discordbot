#!/usr/bin/python3
# https://github.com/tjakobsen90/ctftime-discordbot

from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime

import feedparser
import requests
import time

ctftime_url = "https://ctftime.org/event/list/upcoming/rss/"
ctftime_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
}
discord_url = "https://discord.com/api/webhooks/{{REDACTED}}"
discord_username = "ctftime-bot"
discord_webhook = DiscordWebhook(discord_url, username=discord_username)


def main():
    # Retrieve the RSS feed of CTFtime
    r = requests.get(ctftime_url, headers=ctftime_headers)

    # Parse the RSS entries into a workable list
    ctfs = feedparser.parse(r.content)

    for ctf in ctfs.entries:
        # Drop if it is a certain type CTF
        if "Attack-Defense" in ctf.format_text:
            continue

        # If the CTF is already posted, skip it
        # I use a local file to be persistant after reboots and to not have a list in memory
        # The script runs every week, I don't want to keep the script running idle for a week
        ctf_id = ctf.ctftime_url.replace("/event/", "")
        ctf_ids = open("./ctf_ids.txt", "r+")
        if ctf_id in ctf_ids.read():
            ctf_ids.close()
            continue

        # Parse time into a workable string
        start_date = str(datetime.strptime(ctf.start_date, "%Y%m%dT%H%M%S"))[:-3]
        end_date = str(datetime.strptime(ctf.finish_date, "%Y%m%dT%H%M%S"))[:-3]

        # Create the message that will be sent
        message = DiscordEmbed(title=ctf.title, description=ctf.link, color="03b2f8")
        message.set_timestamp()
        message.add_embed_field(name="Start date", value=start_date)
        message.add_embed_field(name="End date", value=end_date)
        message.add_embed_field(name="Difficulty", value=ctf.weight)
        message.add_embed_field(name="Link", value=ctf.url)
        message.add_embed_field(name="Type", value=ctf.format_text)

        # Add the message to the webhook, sent the message and clear the embeds
        discord_webhook.add_embed(message)
        discord_webhook.execute(remove_embeds=True)

        # Add the ctf_id to the seen ctf_ids
        ctf_ids.write(ctf_id + "\n")
        ctf_ids.close()

        # Sleep for 5 seconds to not trigger the rate-limiter of Discord
        time.sleep(5)


if __name__ == "__main__":
    main()
