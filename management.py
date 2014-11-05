try:
    import configparser as cfg
except ImportError:
    import ConfigParser as cfg

#get configs
conf = cfg.ConfigParser()
conf.read("config.ini")

def get_creds():
    return conf.get('reddit','username'),\
           conf.get('reddit','password')

def get_settings():
    return conf.get('general','useragent')
