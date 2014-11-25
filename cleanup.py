import management as mgmt
import praw

m = mgmt.ConfigManager("samachar.ini")
r = praw.Reddit(user_agent=m.agent)
r.login(m.user, m.pwd)

unread = r.get_unread(limit=None)

for msg in unread:

    if msg.author == msg.submission.author:
        if 'samachardelete' in msg.body.lower():
            print "Deleting comment"
            parent_comment = r.get_info(thing_id=msg.parent_id)
            parent_comment.delete()
