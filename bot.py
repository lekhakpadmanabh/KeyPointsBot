####################
## Author: Padmanabh
## License: GPLv3
####################

import keyptsummarizer as smrzr
import logging
import management as mgmt
import praw
import botdb
from time import sleep 


logging.basicConfig(filename='keyptbot.log', level=logging.ERROR)

UNAME, PASS = mgmt.get_creds()
USERAGENT = mgmt.get_settings()
SUBREDDITS = ("worldnews",)

COMMENT_NS =\
u"""
**Key Points**\n ---
{keypoints}\n --- 
^I'm ^a ^bot \
^| [^Message ^Creator](http://www.reddit.com/message/compose/?to=padmanabh) ^| \
[^Code](https://github.com/lekhakpadmanabh/KeyPointsBot)
"""

COMMENT_S = u"**Summary**: {summary}\n" + COMMENT_NS

if __name__ == '__main__':

    r = praw.Reddit(user_agent=USERAGENT)
    r.login(UNAME, PASS)

    for sub in SUBREDDITS:

        subr = r.get_subreddit(sub)
        posts = subr.get_new(limit=50)

        for p in posts:

            if botdb.check_record(p.id):
                """skip if record has been processed"""
                continue

            try:
                summ, kpts = smrzr.summarize_url(p.url, fmt="md")

                if not kpts:
                    continue

                if summ:
                    COMMENT = COMMENT_S
                    comm_dict = {'summary':summ, 'keypoints':kpts}
                else:
                    COMMENT = COMMENT_NS
                    comm_dict = {'keypoints':kpts}

                while True:
                    try:
                        p.add_comment(COMMENT.format(**comm_dict))
                        botdb.add_record(p.id, p.url)
                        pr = p.title[:100] if len(p.title)>100 else p.title
                        print pr
                        break
                    except praw.errors.RateLimitExceeded:
                        print "Rate limit exceeded, sleeping 8 mins"
                        sleep(8*60)

            except smrzr.ArticleExtractionFail:
                #to not pollute logs
                #botdb.add_record(p.id, p.url)
                logging.error("Extraction Failed, check fails.txt")
                with open('fails.txt','a') as f:
                    f.write(p.url+'\n')

            except Exception as e:
                print "[ERROR] check logs -- ", p.title
                logging.error("Smrzr ({0}) {1}".format(p.url, e))
                #logging.exception("EXCEPT:")
                continue



