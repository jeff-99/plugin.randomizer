import re
from jsonclient import VideoLibraryClient
import xbmcaddon
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

        sorted_episodes = sorted(episodes,key=lambda x: x["score"],reverse=True)

        view = DirectoryView(self.handle)

        for episode in sorted_episodes[0:25]:
            view.add_item(episode['title'],episode['file'])

        return view.render()


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
            route_part = re.sub("\(.*\)",str(arg),route_part, 1)


        return "plugin://plugin.randomizer" + route_part
