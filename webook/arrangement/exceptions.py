class UserHasNoPersonException(Exception):
    """ 
    Exception raised when one encounters the state of an user without a person in person
    dependent logic. For example when getting events for the logged in user, one needs to have a person associated,
    as events are associated to people, not users.
    """
    pass
