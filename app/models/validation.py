from pydantic import BaseModel


class ValidationIssue(BaseModel):
    field: str
    message: str
    severity: str


class ValidationResult(BaseModel):
    is_valid: bool
    issues: list[ValidationIssue]