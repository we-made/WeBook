from typing import Optional

from django.forms.widgets import MultipleHiddenInput, SelectMultiple


class TableMultiSelectWidget(SelectMultiple):
    """An override/derivision from the SelectMultiple widget, creating a table instead of a select"""

    def __init__(self, attrs=None) -> None:
        super().__init__(attrs)

        if (
            "class" not in self.attrs
        ):  # We don't want to mess with the class if consumer has defined anything
            self.attrs["class"] = "table"

    template_name = "widgets/table_multi_select.html"
    option_template_name = "widgets/table_multi_select_option.html"
