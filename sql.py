from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
engine = create_engine('postgresql://localhost:5432/tweets', echo=False)

Base = declarative_base()
from sqlalchemy import Column, Integer, String

class Tweet(Base):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(String)
    url = Column(String)
    text = Column(String)
    json = Column(String)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

if __name__ == "__main__":
    print "hello?"
    for i in range(1):
        with open("example.json") as f:
            tweet = Tweet(json=f.read())
            session.add(tweet)
            session.commit()
    print "done :-)"
