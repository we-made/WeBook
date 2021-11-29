class MediativeResource:
    """
        MediativeResource is the bare minimum a resource type for a context must implement. 
        It serves as the "common tongue" that CalendarBuddy understands, and can work with.
        The kwargs attribute allows you to specify extra attributes, and through the use of translators
        in your context implementation you should be able to build a fully fledged resource that matches
        the context domain.
    """

    def __init__(self, id, title: str, **kwargs):
        self.id = id
        self.title = title
        self.kwargs = kwargs
