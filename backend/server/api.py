from fastapi import FastAPI
from pydantic import BaseModel, validator
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from model.model import RecommendationSystem

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
system = RecommendationSystem()

class RecommendationRequest(BaseModel):
    question: str
    tags: List[str] = None
    n: int = 1

    @validator('tags', pre=True)
    def convert_tags_to_list(cls, value):
        if isinstance(value, str):
            return [tag.strip() for tag in value.split(',')]
        return value

@app.post("/recommend")
def recommend(request: RecommendationRequest):
    stack, medium = system.recommend(request.question, tags=request.tags, n=request.n)
    return {
        "stackoverflow": stack,
        "medium": medium
    }