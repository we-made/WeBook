class FormViewModelEnrichedMixin:
    """Enrich a standard form with a model instance
    When using the standard ModelForm in Django you must specify fields in the Meta class.
    This mixin allows injecting instance into form, without requiring that fields are specified.
    """

    def get_object(self, queryset=None):
        if self.model is None:
            raise AttributeError(
                "Model must be specified when using FormViewInstanceEnrichedMixin"
            )

        if slug := self.kwargs.get("slug"):
            return self.model.objects.get(slug=slug)
        elif pk := self.kwargs.get("pk"):
            return self.model.objects.get(pk=pk)
        else:
            raise AttributeError(
                "Either slug or pk must be specified when using FormViewInstanceEnrichedMixin"
            )

    def get_form(self):
        instance = self.get_object()

        if self.form_class is None:
            raise AttributeError(
                "Form class must be specified when using FormViewInstanceEnrichedMixin"
            )

        return self.form_class(instance=instance, **self.get_form_kwargs())
