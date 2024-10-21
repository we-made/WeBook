from django.forms import Widget


class ArbitraryListWidget(Widget):
    # This is a widget for a list of arbitrary items
    # It is beyond me why there is no built-in form field for this
    # Couple with a custom field to make it work

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, return the value
        of this widget or None if it's not provided.
        """
        return data._getlist(name)
