import csv
import logging
import re

import requests
import feedparser
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook

from config import (DISCORD_WEBHOOK_URL,
                    DEFAULT_THUMBNAIL_IMAGE_URL)


def main():
    with open('feeds.txt', 'r') as feeds_file:
        feeds = feeds_file.read().splitlines()

    for feed in feeds:
        new_rows = []

        response = requests.get(url=feed, timeout=15)

        if response.status_code == 200:
            feed_content = feedparser.parse(response.text)
        else:
            logging.error(
                f'Status code: {response.status_code} ==> URL: {feed}')
            return None

        for post in feed_content.entries:
            is_exist = None

            feed_data = data_extractor(post)

            if feed_data is None:
                continue

            with open('db.csv', 'r') as db_file:
                db = csv.reader(db_file)

                for row in db:
                    if feed_data[0:4] == row:
                        is_exist = True

            if is_exist is None:
                discord_message_sender(feed_data[0], feed_data[1],
                                       feed_data[3], feed_data[2],
                                       feed_data[4], feed_data[5],
                                       feed_data[6])

                new_rows += feed_data[0:4],

        with open('db.csv', 'a') as db_file:
            csv_writer = csv.writer(db_file)
            csv_writer.writerows(new_rows)


def data_extractor(post):
    """Extract data from the 'feedparser' result

    Args:
        post: a single result of the 'feedparser'

    Returns:
        dict: the data of the post
    """

    logging.info(f'INFO: Data extracting from {post.link}')

    tags = '\n\n'
    for tag in post.tags:
        tags += f"#{tag['term']} "

    try:
        post_content = requests.get(post.link)
        author_image = re.search(f'img alt="{post.author}" .+? src="(.*?)" ',
                                 post_content.text).group(1)

    except Exception:
        logging.warning(
            f'an exception occurred when tried connect to: {post.link}'
        )
        return None

    if post.description:
        try:
            thumbnail_url = re.search(
                '(https://cdn-images-1.medium.com/max/.*)?" ',
                post.description).group(1).split('"')[0]
            soup = BeautifulSoup(post.description, features="html.parser")
            description = soup.find(
                'p', {'class': 'medium-feed-snippet'}).text + tags

        except AttributeError:
            thumbnail_url = DEFAULT_THUMBNAIL_IMAGE_URL
            description = ''
    else:
        thumbnail_url = DEFAULT_THUMBNAIL_IMAGE_URL

    return [post.title, post.link, post.author, post.date, author_image,
            thumbnail_url, description]


def discord_message_sender(title, link, date, author_name, author_image,
                           thumbnail_url, description):
    """Send a write-up to the discord channel by the discord webhook URL

    Args:
        title (str): title of the post
        link (str): link of the post
        date (datetime): published date of the post
        author_name (str): author of the post
        author_image (str): the image of the post
        thumbnail_url (str): thumbnail of the post
        description (str): description part of the post
                           and includes tags of the post
    """

    discord_embed = DiscordEmbed(
        title=title, color=808080,
        timestamp=date,
        url=link,
        description=description
    )
    discord_embed.set_author(name=author_name,
                             icon_url=author_image)
    discord_embed.set_image(url=thumbnail_url)
    discord_webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
    discord_webhook.add_embed(discord_embed)
    discord_webhook.execute()


if __name__ == '__main__':
    main()
