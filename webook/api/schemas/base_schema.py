from typing import Optional
from ninja import Schema
from datetime import datetime
from utils.camelize import camelize


class BaseSchema(Schema):
    class Config(Schema.Config):
        alias_generator = camelize
        populate_by_name = True


class ModelBaseSchema(BaseSchema):
    id: Optional[int]
    created: datetime
    modified: datetime
    is_archived: bool = False
