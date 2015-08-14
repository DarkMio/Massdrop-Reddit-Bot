def multiple_of(value, string_of_single, string_of_multiple, return_with_value=False,
                before_string='', after_string=''):
    """Helps with english. If the word has a form of multiple, you can feed it's value
   and it returns you the appropiate form. (Also has some extra features, in case you have a collection of strings.)

    :param value: Numerical value
    :rtype value: bool or float or int
    :param string_of_single: String representation of a single thing
    :param string_of_multiple: String representation of multiple things
    :param return_with_value: Should it return with the value formatted?
    :rtype return_with_value: bool
    :param before_string: String content before
    :param after_string: String content after
    :return: Complete string representation
    :rtype: str
    """
    cache = ''
    cache += before_string

    if return_with_value:
        cache += str(value) + " "
    if value == 0:
        return
    if value == 1:
        return cache + string_of_single + after_string
    return cache + string_of_multiple + after_string
