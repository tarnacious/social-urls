from sql import Event, Tweet, create_session
import json

session = create_session()

def load_json():
    for row in session.query(Tweet).order_by(Tweet.id):
        tweet = json.loads(row.json)
        for url in tweet["entities"]["urls"]:
            print url["expanded_url"]
            print tweet["id"], tweet["text"]


def push_to_queue():
    import redis
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    for row in session.query(Event).order_by(Event.id):
        r.lpush("tweet_urls", row.url)

if __name__ == "__main__":
    push_to_queue()
