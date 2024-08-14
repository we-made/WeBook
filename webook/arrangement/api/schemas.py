from typing import Optional
from webook.api.schemas.base_schema import ModelBaseSchema


class AudienceGetSchema(ModelBaseSchema):
    name: str
    name_en: Optional[str]
    