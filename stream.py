from twython import TwythonStreamer
import json
from sql import create_session, Tweet, Event
import settings
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)
session = create_session()


class TweetStreamer(TwythonStreamer):

    def on_success(self, data):
        try:
            self.on_tweet(data)
        except Exception as e:
            print "Processing error:", data, e

    def on_error(self, status_code, data):
        print "Response error:", status_code, data

    def on_tweet(self, data):
        # save the tweet
        tweet_json = json.dumps(data)
        tweet = Tweet(json=tweet_json)
        session.add(tweet)
        r.publish('tweets',tweet_json)

        for url in data["entities"]["urls"]:
            print url["expanded_url"]
            # save tweet url event
            event = Event(
                url=url["expanded_url"],
                event='tweet',
                count=1)
            session.add(event)

            # push the url onto tweet_urls
            r.lpush("tweet_urls", url["expanded_url"])

        session.commit()

if __name__ == "__main__":
    # create a tweet streamer
    stream = TweetStreamer(
        settings.APP_KEY,
        settings.APP_SECRET,
        settings.OAUTH_TOKEN,
        settings.OAUTH_TOKEN_SECRET
    )

    # start streaming some stuff
    stream.statuses.filter(track='theage,bild,spiegel,reddit,welt')
