import re
import logging

import requests
import feedparser
from discord_webhook import DiscordEmbed, DiscordWebhook
from dotenv import dotenv_values
from bs4 import BeautifulSoup

config = dotenv_values(".env.sample")

DISCORD_WEBHOOK_URL = config.get("DISCORD_WEBHOOK_URL")


def main():
    with open('feeds.txt', 'r') as feeds_file:
        feeds = feeds_file.read().splitlines()

    with open('db.txt', 'r') as db_file:
        db = db_file.read().splitlines()

    for feed_url in feeds:
        response = requests.get(url=feed_url, timeout=15)

        if response.status_code == 200:
            feed_content = feedparser.parse(response.text)
        else:
            logging.error(
                f'Status code: {response.status_code} ==> URL: {feed_url}'
            )
            continue

        for item in feed_content.entries:

            feed_data = data_extractor(item)
            is_exist = None

            if feed_data is None:
                continue

            for row in db:
                if feed_data[0] == row:
                    is_exist = True

            if is_exist is None:
                discord_message_sender(feed_data[1], feed_data[2],
                                       feed_data[3], feed_data[5],
                                       feed_data[6], feed_data[7])
                db.append(feed_data[0])

        with open('db.txt', 'w') as db_file:
            for row in db:
                db_file.write(row + '\n')


def data_extractor(item):
    """Get a item from a rss feed and extract usable data"""

    logging.info(f'INFO: Data extracting from {item.link}')

    tags = '\n\n'
    for tag in item.tags:
        tags += f"#{tag['term']} "

    try:
        item_content = requests.get(item.link)
        author_image = re.search(f'img alt="{item.author}" .+? src="(.*?)" ',
                                 item_content.text).group(1)
    except Exception:
        logging.warning(
            f'an exception occurred when tried connect to: {item.link}'
        )
        author_image = None

    if item.summary:
        try:
            thumbnail_url = re.search(
                '(https://cdn-images-1.medium.com/max/.*)?" ', item.summary
            ).group(1).split('"')[0]
            soup = BeautifulSoup(item.summary, features="html.parser")
            description = soup.find(
                'p', {'class': 'medium-feed-snippet'}
            ).text + tags

        except AttributeError:
            thumbnail_url = None
            description = ''

    return [item.id, item.title, item.link, item.author, item.date,
            author_image, thumbnail_url, description]


def discord_message_sender(title, link, author_name, author_image,
                           thumbnail_url, description):
    """Send a message to the discord channel by the discord webhook URL

    Args:
        title (str): title of the post
        link (str): link of the post
        author_name (str): author of the post
        author_image (str): the image of the post
        thumbnail_url (str): thumbnail of the post
        description (str): description part of the post
                           and includes tags of the post
    """

    discord_embed = DiscordEmbed(
        title=title,
        color='ADD8E6',
        url=link,
        description=description
    )
    if author_image:
        discord_embed.set_author(
            name=author_name,
            icon_url=author_image
        )
    else:
        discord_embed.set_author(name=author_name)
    if thumbnail_url:
        discord_embed.set_image(url=thumbnail_url)
    discord_webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
    discord_webhook.add_embed(discord_embed)
    discord_webhook.execute()


if __name__ == '__main__':
    main()
