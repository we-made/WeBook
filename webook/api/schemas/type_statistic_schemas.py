from typing import List, Optional
from webook.api.schemas.base_schema import BaseSchema


class StatisticSchema(BaseSchema):
    total_arrangements: int
    total_expected_visitors: int
    total_actual_visitors: int
    total_activities: int
    total_non_repeating_activities: int
    total_series: int


class TypeMonthStatisticSchema(BaseSchema):
    month: int
    month_name: str

    statistics: StatisticSchema


class YearStatisticSchema(BaseSchema):
    year: int
    whole_year: StatisticSchema
    months: List[TypeMonthStatisticSchema]


class AudienceCreateSchema(BaseSchema):
    name: str
    name_en: str
    parent_id: Optional[int] = None
    icon_class: Optional[str] = None


class MetaTypeDistributionSchema(BaseSchema):
    name: str
    count: int


class MetaTypeStatisticSummarySchema(BaseSchema):
    total_arrangements: int
    total_activities: int
    arrangement_distribution: List[MetaTypeDistributionSchema]
    activity_distribution: List[MetaTypeDistributionSchema]
