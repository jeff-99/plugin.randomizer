import re
from jsonclient import VideoLibraryClient
import xbmcaddon, xbmc
from ranker import RandomRanker, PlaycountRanker, LastPlayedRanker
from view import DirectoryView


class Plugin(object):
    def __init__(self, handle):
        self.handle = int(handle)
        self.router = self.init_routing()


        addon = xbmcaddon.Addon()
        self.library_client = VideoLibraryClient(
            addon.getSetting('user'),
            addon.getSetting('password'),
            addon.getSetting('url')
        )

        self.rankers = []
        if addon.getSetting('randomize') == 'true':
            self.rankers.append(RandomRanker)

        if addon.getSetting('playcount') == 'true':
            self.rankers.append(PlaycountRanker)

        if addon.getSetting('last_viewed') == 'true':
            self.rankers.append(LastPlayedRanker)

    def init_routing(self):
        router = Router()
        router.add_route("index","/", self.get_tv_show)
        router.add_route("tvshow","/([0-9]+)", self.get_episodes)
        router.add_route("play_all", "/all/([0-9,]+)",self.play_all)

        return router

    def run(self, url):
        return self.router.match(url)

    def get_tv_show(self):
        result = self.library_client.get_tv_shows()

        view = DirectoryView(self.handle)

        for tvshow in result['tvshows']:
            url = self.router.create_url('tvshow', [tvshow['tvshowid']])
            view.add_directory_item(tvshow['title'],url)

        return view.render()


    def get_episodes(self,show_id):
        episodes = self.library_client.get_episodes(show_id)["episodes"]

        for episode in episodes:
            episode['score'] = 100

        for ranker_class in self.rankers:
            ranker = ranker_class(episodes)
            episodes = ranker.calculate()

        sorted_episodes = sorted(episodes,key=lambda x: x["score"],reverse=True)[0:25]

        view = DirectoryView(self.handle)

        episode_ids = [e["episodeid"] for e in sorted_episodes]
        play_all_url = self.router.create_url("play_all", [episode_ids])
        xbmc.log(play_all_url)
        view.add_item("--------- Play All ----------", play_all_url)

        for episode in sorted_episodes:
            view.add_item(episode['title'],episode['file'])

        return view.render()

    def play_all(self, comma_separeted_ids):
        episode_ids = comma_separeted_ids.split(",")

        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

        for episode_id in episode_ids:
            episode_details = self.library_client.get_episode(episode_id)
            if episode_details is not None:
                playlist.add(episode_details["episodedetails"]["file"])

        player = xbmc.Player()
        player.play(playlist)


class Router(object):

    def __init__(self):
        self.routes = {}

    def add_route(self, name, regex, function):
        self.routes[name] = [regex,function]

    def match(self, url):

        url = url.replace("plugin://plugin.randomizer","")

        for route in self.routes.values():
            pattern = route[0].replace('/','\/') + "$"
            match = re.match(pattern, url)
            if match is not None:
                return route[1](*match.groups())

        raise Exception("No routes matched for " + url)

    def create_url(self,route,args):

        route_part = self.routes[route][0]
        for arg in args:
            if isinstance(arg, list):
                arg = [str(x) for x in arg]
                arg = ",".join(arg)
            route_part = re.sub("\(.*\)",str(arg),route_part, 1)


        return "plugin://plugin.randomizer" + route_part
