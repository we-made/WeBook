import datetime
from typing import Any, List, Union

from django import forms
from django.core import validators

from webook.arrangement.forms.widgets.arbitrary_list import ArbitraryListWidget


class DateListField(forms.Field):
    def __init__(
        self,
        *args,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.error_messages["invalid"] = "Enter a list of dates."

    widget = ArbitraryListWidget

    def to_python(self, value: Union[str, List[str]]) -> List[datetime.date]:
        if value in validators.EMPTY_VALUES:
            return []

        if isinstance(value, str):
            value = [value]

        dates = []
        for date in value:
            if isinstance(date, str):
                try:
                    dates.append(datetime.datetime.strptime(date, "%Y-%m-%d"))
                except ValueError:
                    print("Failed parsing date", date)
                    raise forms.ValidationError("Failed parsing date")

        return dates

    def clean(self, value: Union[str, List[str]]) -> List[datetime.date]:
        return self.to_python(value)

    def validate(self, value):
        if self.required and not value:
            raise forms.ValidationError(self.error_messages["required"])

        if value in validators.EMPTY_VALUES:
            return

        if isinstance(value, str):
            print("Value is a string")
            value = [value]

        for date in value:
            if isinstance(date, str):
                try:
                    datetime.datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    print("Failed parsing date", date)
                    raise forms.ValidationError("Failed parsing date")
            elif date and not isinstance(date, datetime.date):
                raise forms.ValidationError(self.error_messages["invalid"])
