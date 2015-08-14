import warnings


def ignore():
    """Surpresses some warnings of praw."""
    # Even if, the bot is called massdropbot. Jesus.
    warnings.filterwarnings('ignore', 'The keyword `bot` in your user_agent may be problematic.')
    # And the socket gets closed.
    warnings.filterwarnings('ignore', 'unclosed*')