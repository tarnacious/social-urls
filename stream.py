from twython import TwythonStreamer
import json
from sql import session, Tweet
from time import sleep
import settings


class MyStreamer(TwythonStreamer):
    def on_success(self, tweet):
        try:
            for url in tweet["entities"]["urls"]:
                print "Saving: ", url["expanded_url"]
                entry = Tweet(
                    url = url["expanded_url"],
                    tweet_id = tweet["id"],
                    text = tweet["text"],
                    json = json.dumps(tweet))
                session.add(entry)
            session.commit()
            self.errors = 0
        except:
            print "Processing error:", data

    def on_error(self, status_code, data):
        print "Response error:", status_code, data
        # self.disconnect()


stream = MyStreamer(
    settings.APP_KEY,
    settings.APP_SECRET,
    settings.OAUTH_TOKEN,
    settings.OAUTH_TOKEN_SECRET
)

stream.statuses.filter(track='theage,bild,spiegel,reddit')
