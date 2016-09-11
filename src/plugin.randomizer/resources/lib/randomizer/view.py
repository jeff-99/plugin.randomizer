import xbmcplugin
import xbmcgui

class DirectoryView(object):
    def __init__(self, handle):
        self.handle= handle

    def _add(self,title,url, type):
        li = xbmcgui.ListItem(title,title)
        xbmcplugin.addDirectoryItem(
            int(self.handle),
            url,
            li,
            type == 'directory'
        )

    def add_directory_item(self,title, url):
        self._add(title, url,'directory')

    def add_item(self,title, url):
        self._add(title, url,'item')

    def render(self):
        xbmcplugin.endOfDirectory(self.handle)
