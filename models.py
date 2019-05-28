from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class Pitch(Base):
    __tablename__ = 'pitch_data'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    pitcher = Column(Integer)
    hitter = Column(Integer)
    stand = Column(String(1))
    outcome = Column(String)
    start_speed = Column(Float)
    end_speed = Column(Float)
    sz_top = Column(Float)
    sz_bot = Column(Float)
    pfx_x = Column(Float)
    pfx_z = Column(Float)
    px = Column(Float)
    pz = Column(Float)
    x0 = Column(Float)
    z0 = Column(Float)
    pitch_type = Column(String)
    zone = Column(Integer)
    spin_dir = Column(Float)
    spin_rate = Column(Float)


engine = create_engine('sqlite:///pitch_fx.db')
Base.metadata.create_all(engine)
