from werkzeug.utils import redirect

from .app import app
from .exceptions import EpisodeNotFoundException, SeasonNotFoundException
from .models import get_show_by_key
from .utils import json_response, list_all_epguides_keys_redis, parse_imdb_poster_image

@app.route("/")
def redirect_to_docs():
    return redirect("https://epguides-api.readthedocs.org/en/latest/")


@app.route('/show/')
def discover_shows():
    result = []

    for epguides_name in list_all_epguides_keys_redis():
        try:
            show = get_show_by_key(epguides_name)

            if not show:
                continue

            show.episodes = "{0}show/{1}/".format(
                app.config['BASE_URL'], epguides_name)
            show.first_episode = "{0}show/{1}/first/".format(
                app.config['BASE_URL'], epguides_name)
            show.next_episode = "{0}show/{1}/next/".format(
                app.config['BASE_URL'], epguides_name)
            show.last_episode = "{0}show/{1}/last/".format(
                app.config['BASE_URL'], epguides_name)
            show.epguides_url = "http://www.epguides.com/{0}".format(
                epguides_name)
            result.append(show)
        except EpisodeNotFoundException:
            continue

    return json_response(result)

@app.route('/show/<string:show>/poster/')
def view_show_poster(show):
    try: 
        show = get_show_by_key(show)
        data = parse_imdb_poster_image(show.imdb_id)
        return json_response({'url': data})
    except Exception as e:
        print(e)
        return json_response({'error': 'Show not found'}, 404)

@app.route('/show/<string:show>/')
def view_show(show):
    try:
        return json_response(get_show_by_key(show).get_show_data())
    except EpisodeNotFoundException:
        return json_response({'error': 'Show not found'}, 404)
    except SeasonNotFoundException:
        return json_response({'error': 'Season not found'}, 404)


@app.route('/show/<string:show>/info/')
def view_show_info(show):
    try:
        return json_response(get_show_by_key(show))
    except EpisodeNotFoundException:
        return json_response({'error': 'Show not found'}, 404)
    except SeasonNotFoundException:
        return json_response({'error': 'Season not found'}, 404)


@app.route('/show/<string:show>/<int:season>/<int:episode>/')
def episode(show, season, episode):
    try:
        show = get_show_by_key(show)
        return json_response({
            'episode': show.get_episode(int(season), int(episode))
        })
    except EpisodeNotFoundException:
        return json_response({'error': 'Episode not found'}, 404)
    except SeasonNotFoundException:
        return json_response({'error': 'Season not found'}, 404)


@app.route('/show/<string:show>/<int:season>/<int:episode>/released/')
def released(show, season, episode):
    try:
        show = get_show_by_key(show)
        return json_response({
            'status': show.episode_released(int(season), int(episode))
        })
    except EpisodeNotFoundException:
        return json_response({'status': False})
    except SeasonNotFoundException:
        return json_response({'error': 'Season not found'}, 404)


@app.route('/show/<string:show>/<int:season>/<int:episode>/next/')
def next_from_given_episode(show, season, episode):
    try:
        show = get_show_by_key(show)
        return json_response({
            'episode': show.get_episode(int(season), int(episode)).next()
        })
    except EpisodeNotFoundException:
        return json_response({'error': 'Episode not found'}, 404)
    except SeasonNotFoundException:
        return json_response({'error': 'Season not found'}, 404)


@app.route('/show/<string:show>/<int:season>/<int:episode>/next/released/')
def next_released_from_given_episode(show, season, episode):
    try:
        show = get_show_by_key(show)
        next_episode = show.get_episode(season, episode).next()

        if not next_episode:
            raise EpisodeNotFoundException

        return json_response({
            'status': next_episode.released()
        })

    except EpisodeNotFoundException:
        return json_response({'error': 'Episode not found'}, 404)
    except SeasonNotFoundException:
        return json_response({'error': 'Season not found'}, 404)


@app.route('/show/<string:show>/next/')
def next(show):
    try:
        return json_response({
            'episode': get_show_by_key(show).next_episode()
        })
    except EpisodeNotFoundException:
        return json_response({'error': 'Episode not found'}, 404)
    except SeasonNotFoundException:
        return json_response({'error': 'Season not found'}, 404)


@app.route('/show/<string:show>/last/')
def last(show):
    try:
        return json_response({
            'episode': get_show_by_key(show).last_episode()
        })
    except EpisodeNotFoundException:
        return json_response({'error': 'Episode not found'}, 404)
    except SeasonNotFoundException:
        return json_response({'error': 'Season not found'}, 404)


@app.route('/show/<string:show>/first/')
def first(show):
    try:
        return json_response({
            'episode': get_show_by_key(show).first_episode()
        })
    except EpisodeNotFoundException:
        return json_response({'error': 'Episode not found'}, 404)
    except SeasonNotFoundException:
        return json_response({'error': 'Season not found'}, 404)

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
