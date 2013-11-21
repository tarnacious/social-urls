from twython import TwythonStreamer
import json
from sql import session, Tweet, Event
from time import sleep
import settings
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)


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
        tweet = Tweet(json=json.dumps(data))
        session.add(tweet)

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
    stream.statuses.filter(track='theage,bild,spiegel,reddit')
