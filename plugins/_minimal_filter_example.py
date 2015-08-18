from core.BaseClass import Base


class FilterExample(Base):
    """This template features the least needed implementations to get the plugin properly loaded."""

    def __init__(self):
        super().__init__(None)
        self.BOT_NAME = 'YourBotName'
        self.DESCRIPTION = 'Foo/Bar'

    def execute_comment(self, comment):
        pass

    def execute_submission(self, submission):
        pass

    def execute_link(self, link_submission):
        pass

    def execute_titlepost(self, title_only):
        pass

    def update_procedure(self, thing_id, created, lifetime, last_updated, interval):
        pass

    def on_new_message(self, message):
        pass


def init(database):
    """Init Call from module importer to return only the object itself, rather than the module."""
    return FilterExample()
