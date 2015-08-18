from core.BaseClass import Base
from pkg_resources import resource_filename


class FilterExampleFull(Base):
    """This example features the most common settings you want for a logged in bot, doing tasks on Reddit."""

    def __init__(self, database):
        super().__init__(database)
        self.BOT_NAME = 'YourBotName'
        self.DESCRIPTION = 'Sampletext'
        self.OAUTH_FILENAME = 'Foo/Bar'
        self.factory_reddit(config_path=resource_filename("config", self.OAUTH_FILENAME))
        self.USERNAME = 'testuser'
        self.REGEX = r'string'

    def execute_comment(self, comment):
        pass

    def execute_titlepost(self, title_only):
        pass

    def execute_link(self, link_submission):
        pass

    def execute_submission(self, submission):
        pass

    def update_procedure(self, thing_id, created, lifetime, last_updated, interval):
        pass

    def on_new_message(self, message):
        self.standard_ban_procedure()
        pass


def init(database):
    """Init Call from module importer to return only the object itself, rather than the module."""
    return FilterExampleFull(database)
