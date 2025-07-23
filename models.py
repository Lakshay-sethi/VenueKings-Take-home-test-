from typing import List
from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str = Field(..., description="A unique identifier for the product.")
    title: str = Field(..., description="The name or title of the product.")
    source: str = Field(..., description="The source or origin of the product data.")
    price: float = Field(
        ..., ge=0.0, description="The price of the product in the specified currency."
    )
    category: str = Field(..., description="The category to which the product belongs.")
    processed_at: str = Field(
        ..., description="The timestamp indicating when the product was processed."
    )


# class ResponseModel(BaseModel):
#     summary: Summary = Field(
#         ...,
#         description="A summary of the processing results, including totals and success rate.",
#     )
#     products: List[Product] = Field(
#         ..., description="A list of products that were successfully processed."
#     )
#     errors: Optional[List[Error]] = Field(
#         None, description="A list of errors encountered during processing, if any."
#     )
