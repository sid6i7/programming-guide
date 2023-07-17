from fastapi import FastAPI
from pydantic import BaseModel
from model.model import RecommendationSystem

app = FastAPI()
system = RecommendationSystem()

class RecommendationRequest(BaseModel):
    sentence: str
    tag: str = None
    n: int = 1

@app.post("/recommend")
def recommend(request: RecommendationRequest):
    stack, medium = system.recommend(request.sentence, tag=request.tag, n=request.n)
    return {
        "stackoverflow": stack,
        "medium": medium
    }