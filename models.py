from sqlalchemy import Column, Integer, String, Text, ForeignKey, text
from pgvector.sqlalchemy import Vector
from database import Base, engine

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    industry_category = Column(String)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    author_agent_id = Column(String)
    title = Column(String)
    content = Column(Text)
    embedding = Column(Vector(384))

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_agent_id = Column(String)
    content = Column(Text)