from core.BaseClass import Base


class ${NAME}(Base):

    def __init__(self, database):
        super().__init__(database, '${NAME}')

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
        self.standard_ban_procedure(message)
        pass


def init(database):
    """Init Call from module importer to return only the object itself, rather than the module."""
    return ${NAME}(database)
