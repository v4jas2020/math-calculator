from urllib import request

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.solver import solve_problem
router = APIRouter(prefix="/api")
class Calculator(BaseModel):
    topic: str = Field(max_length=40)
    equation: str = Field(max_length=160)

@router.post("/calculate")
def calculate(requests: CalculatorRequest):
    try:
        return solve_problem(
            request.topic,
            request.equation
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error
