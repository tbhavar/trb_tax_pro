from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class TaxBaseModel(BaseModel):
    """
    Base configuration for all tax models ensuring immutability
    and clean validation across years for parsed data.
    """
    model_config = ConfigDict(
        frozen=True,
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid"
    )
