import json
import re
from datetime import datetime

import requests
from flask import make_response
from redis import Redis

from .app import cache


class SimpleEncoder(json.JSONEncoder):

    def default(self, o):
        return o.__dict__


def json_response(data, status=200):
    response = make_response(json.dumps(data, cls=SimpleEncoder), status)
    response.mimetype = 'application/json'
    return response


def add_epguides_key_to_redis(epguides_name):
    redis = Redis()
    redis_queue_key = "epguides_api:keys"

    all_keys = list_all_epguides_keys_redis(redis_queue_key=redis_queue_key)

    if epguides_name not in all_keys:
        redis.lpush(redis_queue_key, epguides_name)


def list_all_epguides_keys_redis(redis_queue_key="epguides_api:keys"):
    redis = Redis()

    return [x.decode("utf-8") for x in
            redis.lrange(redis_queue_key, 0, redis.llen(redis_queue_key))]


def format_title(title):
    pattern = "[<a\s\w\=\'\"\:\/\.\-]*>(.*)</a>"

    if title.startswith("<a"):
        parsed_title_groups = re.findall(pattern, title)
        if len(parsed_title_groups) == 1:
            title = parsed_title_groups[0]

    return title.strip()


def parse_date(date):
    strptime = datetime.strptime

    try:
        return strptime(date, "%d %b %y").strftime("%Y-%m-%d")
    except ValueError:
        try:
            return strptime(date, "%d/%b/%y").strftime("%Y-%m-%d")
        except ValueError:
            return None

    return None


@cache.memoize(60 * 60 * 24 * 7)
def parse_epguides_data(url):
    pattern = "([\d]+)[.]?\s*([\d]*)\s?-\s?([\d]*)" \
              "[\s\d]*\s+([\d]+[\s|\/][\w]+[\s|\/][\d]+)\s*(.*)"

    try:
        data = requests.get("http://epguides.com/" + url).text
        episodes = []

        for episode_tuple in re.findall(pattern, data):
            episode = list(episode_tuple)
            episode[4] = format_title(episode[4])

            episodes.append(episode)

    except IndexError:
        return

    return episodes

@cache.memoize(20 * 60 * 60 * 24 * 7)
def parse_imdb_poster_image(imdb_id):
    try:
        url = "http://imdb.com/title/{0}".format(imdb_id)
        data = requests.get(url).text
        return re.findall('img_primary"[^.]*src="(.*)"', data)[0]
    except Exception as e:
        return 


@cache.memoize(60 * 60 * 24 * 7)
def parse_epguides_info(url):
    try:
        data = requests.get("http://epguides.com/" + url).text
        return re.findall('<h1><a href="[\w\:\/\/.]*title\/(.*)">(.*)<\/a>',
                          data)[0]

    except IndexError:
        return
