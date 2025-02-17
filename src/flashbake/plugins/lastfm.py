#    copyright 2011 Og Maciel
#    copyright 2009 Thomas Gideon
#
#    This file is part of flashbake.
#
#    flashbake is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    flashbake is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with flashbake.  If not, see <http://www.gnu.org/licenses/>.

'''  lastfm.py - Plugin that pulls latest n items from your last.fm account. '''

from flashbake.plugins import AbstractMessagePlugin
import urllib.request
import json
import logging

PLUGIN_SPEC = 'flashbake.plugins.lastfm:LastFM'
LASTFM = "http://ws.audioscrobbler.com/2.0/?method="

class LastFM(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, True)
        self.define_property('user_name', required=True)
        self.define_property('api_key', required=True)
        self.define_property('limit', int, False, 5)

    def addcontext(self, message_file, config):
        """ Add the matching items to the commit context. """

        # last n items for m creator
        url = "%suser.getrecentTracks&user=%s&api_key=%s&limit=%s&format=json" % (LASTFM, self.user_name, self.api_key, self.limit)
        logging.debug('API call: %s' % url)
        raw_data = self._fetch_data(url)

        if raw_data:
            tracks = raw_data['recenttracks']['track']
            if not type(tracks) == list:
                tracks = [tracks]
            for trackdic in tracks:
                track =  (trackdic['name']).encode("utf-8").decode("utf-8")
                artist = (trackdic['artist']['#text']).encode("utf-8").decode("utf-8")
                message_file.write("Track from Last.fm: %s by %s\n" % (track, artist))
        else:
            message_file.write('Couldn\'t fetch data from lastfm, %s.\n' % url)

    def _fetch_data(self, url):
        try:
            raw_data = urllib.request.urlopen(url)
            data = json.loads(raw_data.read())

            return data
        except urllib.error.HTTPError as e:
            logging.error('Failed with HTTP status code %d' % e.code)
            return None
        except urllib.error.URLError as e:
            logging.error('Plugin, %s, failed to connect with network.' % self.__class__)
            logging.debug('Network failure reason, %s.' % e.reason)
            return None
