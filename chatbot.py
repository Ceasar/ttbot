from __future__ import division
from pprint import pprint

from bot import Bot
from settings import AUTH, USERID, ROOMID, MASTER


bot = Bot(AUTH, USERID, ROOMID)


class EventListener(object):
    """An event listener."""
    def __init__(self, bot, event):
        self.bot = bot
        self.event = event

    def __call__(self, func):
        self.bot.on(self.event, func)


class Session(object):
    """A series of tracks."""
    def __init__(self):
        self.tracks = []

    @property
    def average(self):
        try:
            return sum(score for _, score in self.tracks) / (len(self) + 1)
        except:
            pass

    def add_track(self, track, score):
        self.tracks.append((track, score))

    def __len__(self):
        return len(self.tracks)


SESSION = Session()


@EventListener(bot, 'roomChanged')
def roomChanged(data):
    pprint(data)


@EventListener(bot, 'speak')
def speak(data):
    if data['userid'] == USERID:
        return
    if 'average' in data['text']:
        bot.speak("The average for the last %s songs is %s" % (len(SESSION), SESSION.average))


@EventListener(bot, 'endsong')
def endsong(data):
    upvotes = data['room']['metadata']['upvotes']
    downvotes = data['room']['metadata']['downvotes']
    song = data['room']['metadata']['current_song']
    dj = song['djid']
    # should use some kind of bayesian stats
    print upvotes, downvotes
    score = int(upvotes) / (int(downvotes) + 1)
    SESSION.add_track(song, score)
    if dj != USERID:
        if score > SESSION.average: 
            # bot.speak("nice track!")
            bot.playlistAdd(song['_id'])
        else:
            # bot.speak("less than average!")
            pass


@EventListener(bot, 'pmmed')
def pmmed(data):
    pprint(data)
    if data['senderid'] != MASTER:
        bot.speak("You are not Master %s %s" % (MASTER, data['senderid']), data['userid'])
        bot.pm("You are not master", data['senderid'])
        return
    tokens = data['text'].split()
    try:
        getattr(bot, tokens[0])(*tokens[1:])
    except AttributeError:
        bot.pm("Failed", data['senderid'])


@EventListener(bot, 'update_votes')
def updateVotes(data):
    pass


@EventListener(bot, 'registered')
def registered(data):
    pass

bot.start()
