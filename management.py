try:
    import configparser as cfg
except ImportError:
    import ConfigParser as cfg

try:
    import ujson as json
except ImportError:
    import json


class ConfigManager:
    conf = cfg.ConfigParser()

    def __init__(self, filename):
        ConfigManager.conf.read(filename)
        self.user, self.pwd = self._get_creds()
        self.agent = self._get_settings()

    def _get_creds(self):
        return ConfigManager.conf.get('reddit', 'username'), \
               ConfigManager.conf.get('reddit', 'password')

    def _get_settings(self):
        return ConfigManager.conf.get('general', 'useragent')


with open('globals.json', 'rb') as f:
    bot_globals = json.load(f)

with open('locals.json', 'rb') as f:
    bot_locals = json.load(f)


def check_sub(sub):
    if sub in bot_globals['permission']:
        return False
    if sub in bot_globals['disallowed']:
        return False
    if sub in bot_globals['disallowed']:
        return False
    return True


def get_subs():
    subs = bot_locals['subreddits']
    for sub in subs:
        if not check_sub(sub):
            raise ValueError("Subreddit {} not allowed".format(sub))
    return subs


def get_dnd_users():
    return bot_locals['dnd_users']


def get_domain_whitelist():
    return bot_locals['domain_whitelist']

