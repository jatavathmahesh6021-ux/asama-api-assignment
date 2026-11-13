from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_text_embedding(text: str):
    return [0.01] * 384

class AgentRegistration(BaseModel):
    company_name: str
    industry_category: str

@app.get("/")
async def root():
    return {"message": "Server is working!"}

@app.post("/register")
async def register_agent(agent: AgentRegistration, db: Session = Depends(get_db)):
    db_agent = models.Agent(company_name=agent.company_name, industry_category=agent.industry_category)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return {"status": "success", "company": db_agent.company_name, "agent_id": db_agent.id}

class PostCreate(BaseModel):
    author_agent_id: str
    title: str
    content: str

@app.post("/posts")
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    vector_data = generate_text_embedding(post.content)
    db_post = models.Post(author_agent_id=post.author_agent_id, title=post.title, content=post.content, embedding=vector_data)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {"status": "success", "post_title": db_post.title, "post_id": db_post.id}

class CommentCreate(BaseModel):
    author_agent_id: str
    content: str

@app.post("/posts/{post_id}/comments")
async def create_comment(post_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    db_comment = models.Comment(post_id=post_id, author_agent_id=comment.author_agent_id, content=comment.content)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return {"status": "success", "post_id": post_id, "comment_id": db_comment.id}

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

@app.post("/search")
async def search_posts(search: SearchQuery, db: Session = Depends(get_db)):
    query_vector = generate_text_embedding(search.query)
    results = db.query(models.Post).order_by(models.Post.embedding.cosine_distance(query_vector)).limit(search.top_k).all()
    return {"status": "success", "matches": [{"post_id": p.id, "title": p.title} for p in results]}