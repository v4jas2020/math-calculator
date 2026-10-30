from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field\

from app.services.solver import solve_problem
router = APIRouter(prefix="/api")
class CalculatorRequest(BaseModel):
    topic: str = Field(max_length=40)
    equation: str = Field(max_length=160)
@router.post("/calculate")
def calculate(request: CalculatorRequest):
    try:
        return solve_problem(
            request.topic,
            request.equation
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
