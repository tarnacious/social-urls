from flask import Flask, render_template, request
from sql import Event, aggregated_intervals
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
import settings
import json
app = Flask(__name__,static_folder='assets',static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = settings.POSTGRESQL

db = SQLAlchemy(app)

@app.route('/')
def index():
    events = db.session\
               .query(Event.url,func.sum(Event.count))\
               .group_by(Event.url)\
               .order_by(desc(func.sum(Event.count)))\
               .all()
    return render_template('index.html', events=events)

def map_event(event):
    return {
        "time": str(event["time"]),
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
    mapped_tweets = [map_event(event) for event in aggregated_intervals(tweets)]
    mapped_facebooks = [map_event(event) for event in aggregated_intervals(facebooks)]
    return render_template('details.html',
                           events=events,
                           url=url,
                           json=json.dumps({"tweets": mapped_tweets,
                                            "facebook": mapped_facebooks})
                           )

if __name__ == '__main__':
    app.debug = True
    app.run()
