from flask import Flask, render_template, request
from sql import Event, aggregated_intervals
from datetime import datetime, timedelta
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
import settings
import json
app = Flask(__name__,static_folder='assets',static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = settings.POSTGRESQL

db = SQLAlchemy(app)


@app.template_filter('shortenurl')
def shortenurl(url):
    if len(url) > 40:
        return "%s..." % url[:40]
    return url


def hot(domain, event="tweet", hours=1):
    results = db.session\
                .query(Event.url,func.sum(Event.count))\
                .filter(Event.event == event)\
                .filter(Event.created_on > datetime.now() - timedelta(hours=1))\
                .filter(Event.url.contains(domain))\
                .group_by(Event.url)\
                .order_by(desc(func.sum(Event.count)))\
                .limit(10)
    return results

@app.route('/')
def index():
    hot_tweets = db.session\
               .query(Event.url,func.sum(Event.count))\
               .filter(Event.event == 'tweet')\
               .filter(Event.created_on > datetime.now() - timedelta(hours=1))\
               .group_by(Event.url)\
               .order_by(desc(func.sum(Event.count)))\
               .limit(10)

    hot_facebook = db.session\
               .query(Event.url,func.sum(Event.count))\
               .filter(Event.event == 'facebook')\
               .filter(Event.created_on > datetime.now() - timedelta(hours=1))\
               .group_by(Event.url)\
               .order_by(desc(func.sum(Event.count)))\
               .limit(10)

    hot_bild = hot('bild.de')
    hot_spiegel = hot("spiegel.de")
    hot_theage = hot("theage.com.au")
    hot_welt = hot("welt.de")

    tweets_alltime = db.session.query(func.count(Event.id))\
                       .filter(Event.event == 'tweet')\
                       .scalar()

    tweets_hour = db.session.query(func.count(Event.id))\
                       .filter(Event.event == 'tweet')\
                       .filter(Event.created_on > datetime.now() - timedelta(hours=1))\
                       .scalar()

    facebook_alltime = db.session.query(func.count(Event.id))\
                       .filter(Event.event == 'facebook')\
                       .scalar()

    facebook_hour = db.session.query(func.count(Event.id))\
                       .filter(Event.event == 'facebook')\
                       .filter(Event.created_on > datetime.now() - timedelta(hours=1))\
                       .scalar()

    return render_template('index.html',
                           tweets_alltime = tweets_alltime,
                           tweets_hour = tweets_hour,
                           facebook_alltime = facebook_alltime,
                           facebook_hour = facebook_hour,
                           hot_tweets=hot_tweets,
                           hot_facebook=hot_facebook,
                           hot_bild=hot_bild,
                           hot_spiegel=hot_spiegel,
                           hot_theage=hot_theage,
                           hot_welt=hot_welt
                           )

def map_event(event):
    return {
        "time": event["time"].strftime("%I:%M"),
        "count": event["count"],
    }

@app.route('/url/')
def details():
    url = request.args.get("url")
    events = db.session \
               .query(Event) \
               .filter(Event.url == url) \
               .order_by(Event.id.desc()) \
               .all()
    tweets = [event for event in events if event.event == 'tweet']
    facebooks = [event for event in events if event.event == 'facebook']

    start = datetime.now() - timedelta(hours=1)
    interval = timedelta(hours=1) / 20
    hour_tweets = [map_event(event) for event in aggregated_intervals(tweets, start, interval, 21)]
    hour_facebooks = [map_event(event) for event in aggregated_intervals(facebooks, start, interval, 21)]
    start = datetime.now() - timedelta(hours=48)
    interval = timedelta(hours=48) / 48
    twoday_tweets = [map_event(event) for event in aggregated_intervals(tweets, start, interval, 49)]
    twoday_facebooks = [map_event(event) for event in aggregated_intervals(facebooks, start, interval, 49)]

    return render_template('details.html',
                           events=events,
                           url=url,
                           json=json.dumps({"tweets": hour_tweets,
                                            "facebook": hour_facebooks,
                                            "twoday_tweets": twoday_tweets,
                                            "twoday_facebook": twoday_facebooks,
                                            })
                           )

@app.route('/tweets')
def tweets():
    return render_template('tweets.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
