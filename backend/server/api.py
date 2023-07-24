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
    """
    Request model for the recommendation API.

    Attributes:
        question (str): The user's input question.
        tags (List[str], optional): A list of tags associated with the question. Defaults to None.
        n (int, optional): The number of recommendations to return. Defaults to 1.
    """
    question: str
    tags: List[str] = None
    n: int = 1

    @validator('tags', pre=True)
    def convert_tags_to_list(cls, value):
        """
        Validator to convert tags from a comma-separated string to a list of strings.

        Args:
            value (str or list): The input value representing tags.

        Returns:
            list: The list of tags extracted from the input string or the original list.
        """
        if isinstance(value, str):
            return [tag.strip() for tag in value.split(',')]
        return value

@app.post("/recommend")
def recommend(request: RecommendationRequest):
    """
    API endpoint to get recommendations based on the user's input.

    Args:
        request (RecommendationRequest): The request object containing user input.

    Returns:
        dict: A dictionary containing recommendations from Stack Overflow and Medium.
            The keys are 'stackoverflow' and 'medium', and the values are lists of recommended content.
    """
    stack, medium = system.recommend(request.question, tags=request.tags, n=request.n)
    return {
        "stackoverflow": stack,
        "medium": medium
    }