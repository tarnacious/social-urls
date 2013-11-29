from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, func
import settings

Base = declarative_base()

class Tweet(Base):
    __tablename__ = 'tweets'
    id = Column(Integer, primary_key=True)
    json = Column(String)
    created_on = Column(DateTime, default=func.now())


class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    likes = Column(Integer)
    comments = Column(Integer)
    shares = Column(Integer)
    created_on = Column(DateTime, default=func.now())


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    event = Column(String)
    count = Column(Integer)
    created_on = Column(DateTime, default=func.now())


def create_session():
    engine = create_engine(settings.POSTGRESQL, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def aggregated_intervals(events):
    start = events[-1].created_on
    end = events[0].created_on
    interval = (end - start) / 20
    results = []
    for i in range(22):
        time = start + (interval * i)
        count = sum([event.count for event in events if event.created_on <= time])
        results.append({"time": time, "count": count})
    return results


if __name__ == "__main__":
    session = create_session()
    events = session \
               .query(Event) \
               .order_by(Event.id.desc()) \
               .all()
    for interval in aggregated_intervals(events):
        print interval
