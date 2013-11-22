from flask import Flask, render_template, request
from sql import Event
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
import settings
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

@app.route('/url/')
def details():
    url = request.args.get("url")
    events = db.session \
               .query(Event) \
               .filter(Event.url == url) \
               .order_by(Event.id.desc()) \
               .all()
    return render_template('details.html',
                           events=events,
                           url=url
                           )

if __name__ == '__main__':
    app.debug = True
    app.run()
