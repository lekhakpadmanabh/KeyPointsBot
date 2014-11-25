####################
## Author: Padmanabh
## License: Apache
####################

import smrzr
import logging
import management as mgmt
import praw
import botdb
from time import sleep 

logging.basicConfig(filename='keyptbot.log', level=logging.ERROR)

m = mgmt.ConfigManager("samachar.ini")
comment_ns =\
u"""
**Key Points**\n ---
{keypoints}\n --- 
^I'm ^a ^bot \
^| ^OP ^can ^reply ^with ^"samachardelete" ^| [^Message ^Creator](http://www.reddit.com/message/compose/?to=padmanabh) \
^| [^Source](https://github.com/lekhakpadmanabh/KeyPointsBot)
"""
comment_s = u"**Summary**: {summary}\n" + comment_ns

from requests.exceptions import ConnectionError
try:
    r = praw.Reddit(user_agent=m.agent)
    r.login(m.user, m.pwd)
except ConnectionError:
    raise SystemExit("Couldn't Connect, exiting...")

for sub in mgmt.get_subs():

    subr = r.get_subreddit(sub)
    posts = subr.get_new(limit=40)

    for p in posts:

        if p.domain not in mgmt.get_domain_whitelist():
            continue

        if str(p.subreddit) == 'india' and p.score <3:
            continue

        if botdb.check_record(p.id):
            """skip if record has been processed"""
            continue

        try:
            summ, kpts = smrzr.summarize_url(p.url)



            maxlen = max([len(pt) for pt in kpts])
            minlen = min([len(pt) for pt in kpts])
            if maxlen > 330:
                raise ValueError("Keypoint too long")
            if minlen < 30:
                raise ValueError("Keypoint too short")



            intrsc = len(set.intersection(set(summ.split(" ")),\
                      set(kpts[0].split(" "))))
            if intrsc >8:
                kpts[0] = summ
                summ = ''

            kpts = smrzr.formatters.Formatter(kpts,'md').frmt()


            if summ:
                comment = comment_s
                comm_dict = {'summary':summ, 'keypoints':kpts}
            else:
                comment = comment_ns
                comm_dict = {'keypoints':kpts}



            while True:
                try:
                    p.add_comment(comment.format(**comm_dict))
                    botdb.add_record(p.id, p.url)
                    pr = p.title[:100] if len(p.title)>100 else p.title
                    print p.score, p.subreddit, pr
                    break

                except praw.errors.RateLimitExceeded:
                    print "Rate limit exceeded, sleeping 8 mins"
                    sleep(8*60)

        except Exception as e:
            logging.error("({0}) {1}".format(p.id, e))

