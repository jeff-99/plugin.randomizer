from urllib2 import Request, urlopen
import json
import hashlib
import base64
from time import time
import xbmc

class VideoLibraryClient():

    def __init__(self, user, passw, url):
        credentials = bytes(user+passw)
        encoded_credentials = base64.b64encode(credentials)
        authorization = b'Basic ' + encoded_credentials

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': authorization
        }

        self.url = url

    def request(self, method ,params):
        json_data = json.dumps({
            "jsonrpc" : "2.0",
            "method" : method,
            "params" : params,
            "id" : method + hashlib.sha1(time().hex()).hexdigest()
        })
        post_data = json_data.encode('utf-8')
        request = Request(self.url, post_data, self.headers)
        result = urlopen(request)

        queried_data = json.loads(result.read())
        try:
            return queried_data["result"]
        except KeyError as e:
            xbmc.log(json.dumps(queried_data))

    def get_tv_shows(self):
        params = {
            "properties": [ "title" ,"file"],
            "sort": { "order": "ascending", "method": "label" }
        }

        return self.request("VideoLibrary.GetTVShows", params)

    def get_episodes(self, show_id, season = None):
        params = {

            "tvshowid": int(show_id),
            "properties": ["title","season","playcount","file"],
            "limits": {"start":0, "end":1000}
        }

        if season is not None:
            params["season"] = int(season)

        return self.request("VideoLibrary.GetEpisodes", params)

    def get_episode(self, episode_id):
        params = {
            "episodeid": int(episode_id),
            "properties": ["title","file"]
        }

        return self.request("VideoLibrary.GetEpisodeDetails", params)
