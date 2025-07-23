from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Summary(BaseModel):
    total_products: int = Field(
        ..., ge=0, description="The total number of products processed."
    )
    processing_time_seconds: float = Field(
        ...,
        ge=0.0,
        description="The total time taken to process the products, in seconds.",
    )
    success_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="The success rate of processing, represented as a value between 0 and 1.",
    )
    sources: List[str] = Field(
        ..., description="A list of data sources used for processing. API links."
    )


class Product(BaseModel):
    id: str = Field(..., description="A unique identifier for the product.")
    title: str = Field(..., description="The name or title of the product.")
    source: str = Field(..., description="The source or origin of the product data.")
    price: float = Field(
        ..., ge=0.0, description="The price of the product in the specified currency."
    )
    category: str = Field(..., description="The category to which the product belongs.")
    processed_at: datetime = Field(
        ..., description="The timestamp indicating when the product was processed."
    )


class Error(BaseModel):
    endpoint: str = Field(..., description="The API endpoint where the error occurred.")
    error: str = Field(..., description="A description of the error encountered.")
    timestamp: datetime = Field(
        ..., description="The timestamp when the error occurred."
    )


class ResponseModel(BaseModel):
    summary: Summary = Field(
        ...,
        description="A summary of the processing results, including totals and success rate.",
    )
    products: List[Product] = Field(
        ..., description="A list of products that were successfully processed."
    )
    errors: Optional[List[Error]] = Field(
        None, description="A list of errors encountered during processing, if any."
    )
