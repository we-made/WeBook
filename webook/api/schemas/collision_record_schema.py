from datetime import datetime
from typing import Optional, Union
from webook.api.schemas.base_schema import BaseSchema


class CollisionRecordSchema(BaseSchema):
    event_a_title: str
    event_a_start: datetime
    event_a_end: datetime
    event_b_id: Optional[Union[str, int]] = None
    event_b_title: str
    event_b_start: datetime
    event_b_end: datetime
    contested_resource_id: int
    contested_resource_name: str
    is_rigging: bool = False
    is_resolution: bool = False
    my_serie_position_hash: Optional[str] = None
    parent_serie_position_hash: Optional[str] = None
