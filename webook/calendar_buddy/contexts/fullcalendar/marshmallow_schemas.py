from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from .models import EventDisplay

class BusinessHoursSchema(Schema):
    startTime = fields.Time()
    endTime = fields.Time()

    daysOfWeek = fields.List(fields.Str())

class EventSchema(Schema):
    id = fields.Str()
    groupId = fields.Str()
    allDay = fields.Bool() 
    start = fields.Date()
    end = fields.Date()
    startStr = fields.Str()
    endStr = fields.Str()
    title = fields.Str()
    url = fields.Str()
    classNames = fields.List(fields.Str())
    editable = fields.Bool()
    startEditable = fields.Bool() 
    durationEditable = fields.Bool()
    resourceEditable = fields.Bool()
    display = EnumField(EventDisplay, by_value=True)
    overlap = fields.Bool()
    constraint = fields.Nested(BusinessHoursSchema())
    backgroundColor = fields.Str()
    borderColor = fields.Str()
    textColor = fields.Str()
    extendedProps = fields.List(fields.Str())
    source = fields.Str()
    

class ResourceSchema(Schema):
    id = fields.Str()
    title = fields.Str()
    extendedProps = fields.List(fields.Str())
    eventConstraint = fields.Nested(BusinessHoursSchema())
    eventOverlap = fields.Bool()
    eventAllow = fields.Bool()
    eventBackgroundColor = fields.Str()
    eventBorderColor = fields.Str()
    eventTextColor = fields.Str()
    eventClassNames = fields.Str()