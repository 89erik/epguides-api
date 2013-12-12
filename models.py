import datetime
from epguides import get_seriedata


class EpisodeNotFoundException(Exception):
    pass


class Episode(object):
    def __init__(self, show, season_number, episode_data):
        self.show = show
        self.season = int(season_number)
        self.number = int(episode_data['number'])
        self.title = episode_data['title']
        self.release_date = episode_data['release_date']

    def __serialize__(self):
        return self.__dict__

    def released(self):
        release_date = datetime.datetime.strptime(self.release_date, "%Y-%m-%d")

        if datetime.datetime.now() - datetime.timedelta(hours=32) > release_date:
            return True

        return False

    def next(self):
        episodes = self.show.get_episodes()

        for ep in episodes[self.season]:
            if ep.number == self.number + 1:
                return ep

        if self.season + 1 in episodes:

            for ep in episodes[self.season + 1]:
                if ep.number == 1:
                    return ep

        return None


class Show(object):
    def __init__(self, show_name):
        self.show_name = show_name

    def next_episode(self):
        show_data = self.get_episodes()
        season_number = len(show_data.keys())
        for episode in show_data[season_number]:
            if not episode.released():
                return episode

        raise EpisodeNotFoundException()

    def last_episode(self):
        show_data = self.get_episodes()
        season_number = len(show_data.keys())
        last_episode_released = None

        for episode in show_data[season_number]:
            if episode.released():
                last_episode_released = episode

        if last_episode_released:
            return last_episode_released

        raise EpisodeNotFoundException()

    def get_episode(self, season_number, episode_number):
        show_data = self.get_episodes()

        if season_number in show_data:
            for episode in show_data[season_number]:
                if episode.number == episode_number:
                    return episode

        raise EpisodeNotFoundException()

    def episode_released(self, season_number, episode_number):
        return self.get_episode(season_number, episode_number).released()

    def get_episodes(self):
        episodes = {}

        for episode_data in get_seriedata(self.show_name):

            season_number = int(episode_data[1])

            if season_number not in episodes:
                episodes[season_number] = []

            episode = Episode(self, season_number, {
                'number': episode_data[2],
                'title': episode_data[4],
                'release_date': datetime.datetime.strptime(
                    episode_data[3],
                    "%d/%b/%y"
                ).strftime("%Y-%m-%d")
            })

            episodes[season_number].append(episode)

        return episodes
