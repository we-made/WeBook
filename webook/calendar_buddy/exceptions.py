class FactoryNotFoundException(Exception):
    """
        Exception to be raised when a factory has been requested, but it could not be found.
        For instance, if one tries to register a hook to a factory that has not been registered yet.
    """
    def __init__(self,
                 context_type,
                 message=None):
        self.context_type = context_type
        self.message = message

        if self.message is False:
            self.message = (f"Could not find a context factory for the specified context type" 
                       "Make sure that a factory is registered for the given context type " 
                       "before you attempt to make any subsequent factory dependent operations.")

        super().__init__(self.message)