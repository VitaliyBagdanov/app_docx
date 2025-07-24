from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP


Base = declarative_base()

class MfgBot(Base):
    __tablename__ = "mfg_bot"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    voice_path = Column(Text, nullable=True)
    audio_text = Column(Text, nullable=True)
    href_to = Column(Text, nullable=True)
    message_time = Column(TIMESTAMP, nullable=True)
    secretary = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    transcrib_id = Column(Integer, nullable=True)
