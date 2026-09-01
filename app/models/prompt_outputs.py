from typing import Optional, Literal

from pydantic import BaseModel, Field

class SummaryOutput(BaseModel):

    summary: str = Field(
        ...,
        min_length=1,
        description="Generated summary"
    )



class ExtractionOutput(BaseModel):
    document_id: Optional[str] = None

    customer_name: Optional[str] = None

    invoice_number: Optional[str] = None

    invoice_date: Optional[str] = None

    amount: Optional[str] = None



class ClassificationOutput(BaseModel):

    label: Literal[
        "Complaint",
        "Inquiry",
        "Feedback",
        "Request",
    ]

    reason: str = Field(
        ...,
        min_length=1,
        description="Short explanation"
    )






class GroundedAnswerOutput(BaseModel):

    answer: str = Field(
        ...,
        min_length=1,
        description="Grounded answer generated from the provided context"
    )

    status: Literal[
        "answered",
        "insufficient_evidence",
    ]

    citations: list[str] = Field(
        default_factory=list,
        description="Source chunk labels cited by the answer"
    )
