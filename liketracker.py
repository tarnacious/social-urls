from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from datetime import timedelta, datetime
from urllib import quote
import json
import tornadoredis
import momoko
import settings


def like_url(url):
    base = "".join(["https://graph.facebook.com/fql?q=select%20",
           "like_count%2Ccomment_count%2Cshare_count%2C",
           "click_count%20from%20link_stat%20where%20url="])
    url2 = quote(url.encode("utf-8"))
    return base + url2.join(["\"", "\""])


def compare_likes(previous, new):
    return score_like(new) - score_like(previous)


def score_like(data):
    info = data["data"][0]
    return info["comment_count"] + info["like_count"] + info["share_count"]


class LikeTracker(object):
    def __init__(self, ioloop=None):
        self.total_requests = 0
        self.current_requests = 0
        self._ioloop = ioloop or IOLoop.instance()
        self.urls = {}
        self.added = 0
        self.r = tornadoredis.Client()
        self.r.connect()
        self.db = momoko.Pool(dsn=settings.DSN, size=4)
        self.start_queue()
        self.status()

    def _fetch(self, url):
        if self.current_requests > 8:
            #print "Exceeding current request, wait 2 seconds:", url
            self._wait(url, interval=timedelta(seconds=0.5),
                       decrement=False)
            return

        self.total_requests = self.total_requests + 1
        self.current_requests = self.current_requests + 1
        #print "Fetching..", url
        request = HTTPRequest(like_url(url))
        http_client = AsyncHTTPClient()
        http_client.fetch(request,
                          callback=lambda res: self._fetch_complete(url, res))

    def _fetch_complete(self, url, response):
        self.current_requests = self.current_requests - 1
        #print "Fetch complete:", url
        try:
            result = json.loads(response.body)
            self.save_like(url, result)
            if 'result' in self.urls[url]:
                #print "We have a previous result"
                match = compare_likes(result, self.urls[url]["result"])
                if match != 0:
                    #print "Results have changed"
                    self.save_event(url, match)
                    self.urls[url]["repeats"] = 3
                else:
                    #print "Results are the same"
                    pass
            else:
                #print "New result"
                self.urls[url]["result"] = result

        except Exception as e:
            print "Error parsing:", url, e, response.body
        self._wait(url)

    def _wait(self, url, interval=timedelta(minutes=10), decrement=True):
        def wait_complete():
            #print "Wait complete:", url
            self._fetch(url)
        if self.urls[url]["repeats"] > 0:
            if decrement:
                self.urls[url]["repeats"] = self.urls[url]["repeats"] - 1
            self._ioloop.add_timeout(interval, wait_complete)
        else:
            del self.urls[url]
            print "Droping url", url

    def add_url(self, url):
        #print "New:", url
        if url not in self.urls:
            print "Adding:", url
            self.urls[url] = {"repeats": 3}
            self._fetch(url)
        else:
            print "Already added:", url
            self.urls[url]["repeats"] = 3

    def _queue_callback(self, response):
        if response:
            #print "Queue:", response
            self.add_url(response)
            self.start_queue()
        else:
            #print "No Queue, waiting."
            self._ioloop.add_timeout(timedelta(milliseconds=2000),
                                     self.start_queue)

    def status(self):
        print ""
        print "*" * 40
        print "Tracking:", len(self.urls.keys())
        print "Total Requests:", self.total_requests
        print "Current Requests:", self.current_requests
        print "*" * 40
        self._ioloop.add_timeout(timedelta(seconds=10), self.status)

    def start_queue(self):
        #print "Check queue"
        self.r.rpop("tweet_urls", callback=self._queue_callback)

    def save_like(self, url, data):
        def callback(cursor, error):
            if error:
                print "DB Response Error:", url, error

        r = data["data"][0]
        try:
            self.db.execute('INSERT INTO likes \
                            (url,likes,comments,shares,created_on) \
                            VALUES (%s,%s,%s,%s,%s)',
                            (url,
                             r["like_count"],
                             r["comment_count"],
                             r["share_count"],
                             datetime.now(),),
                            callback=callback)
        except Exception as e:
            print "DB Query Error:", e, data

    def save_event(self, url, count):
        def callback(cursor, error):
            if error:
                print "DB Response Error:", url, error
        try:
            self.db.execute('INSERT INTO events (url,event,count,created_on) \
                            VALUES (%s,%s,%s,%s)',
                            (url, 'facebook', count, datetime.now(),),
                            callback=callback)
        except Exception as e:
            print "DB Query Error:", e, url


def try_url(url):
    import requests
    l = like_url(url)
    res = requests.get(l)
    print res.text

if __name__ == "__main__":
    print "Starting facebook url tracking"
    like_finder = LikeTracker()
    IOLoop.instance().start()
    #try_url("http://www.reddit.com/r/mildlyinteresting/search?q=mildlyinteresting&sort=relevance&restrict_sr=on&t=week")
    #try_url("www.theage.com.au")
