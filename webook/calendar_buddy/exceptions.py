class FactoryNotFoundException(Exception):
    def __init__(self,
                 context_type,
                 message=None):
        self.context_type = context_type
        self.message = message

        if self.message is None or False:
            self.message = (f"Could not find a context factory for the specified context type"
                       "Make sure that a factory is registered for the given context type "
                       "before you attempt to make any subsequent factory dependent operations.")

        super().__init__(self.message)

