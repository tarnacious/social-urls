from flask import Flask, render_template
from sql import Event
from flask.ext.sqlalchemy import SQLAlchemy
import settings
app = Flask(__name__,static_folder='assets',static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = settings.POSTGRESQL

db = SQLAlchemy(app)

@app.route('/')
def index():
    events = db.session.query(Event).order_by(Event.id.desc()).limit(100).all()
    return render_template('index.html', events=events)

@app.route('/url/<url>')
def show_user_profile(url):
    # show the user profile for that user
    return 'User %s' % url

if __name__ == '__main__':
    app.debug = True
    app.run()
