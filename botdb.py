import sqlite3 as lite

conn = lite.connect("bot.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS botlog(id INTEGER PRIMARY KEY, 
                  reddit_id TEXT unique, link TEXT)
               ''')

def add_record(reddit_id, link):
    """Insert id and urls into db"""

    try:
        cursor.execute("INSERT INTO botlog (reddit_id,link) \
                        VALUES (?,?)", (reddit_id,link));
        conn.commit()
    except lite.IntegrityError:
        print "Reddit id {} already exists".format(reddit_id)

def check_record(reddit_id):
    """check if given id has been processed previously"""

    cursor.execute("SELECT reddit_id from botlog where reddit_id=?",
                   (reddit_id,))
    return cursor.fetchone()

