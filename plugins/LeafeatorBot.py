from core.BaseClass import Base
from pkg_resources import resource_filename
import re


class LeafeatorBot(Base):
    def __init__(self, database):
        super().__init__(database)
        self.BOT_NAME = 'LeafeatorBot'
        self.DESCRIPTION = 'The greatest piece of shitposting for /r/dota2'
        self.OAUTH_FILENAME = 'LeafeatorBot_OAuth.ini'
        self.factory_reddit(config_path=resource_filename('config', self.OAUTH_FILENAME))
        self.USERNAME = 'leafeator-bot'
        self.factory_config()
        self.APPROVE = ['dota2circlejerk', 'dota2', 'dotamasterrace']
        self.RESPONSE = self.config.get('LeafeatorBot', 'response').replace('\\n', '\n')
        self.REGEX = re.compile(
            r'(ancient(?!.*(apparition)).*necro(?!s)|necro.*ancient(?!.*(apparition))|leafeator-bot)',
            re.IGNORECASE)

    def execute_comment(self, comment):
        return self.general_action(comment.body, comment.fullname, comment.subreddit.display_name, comment.author.name)

    def execute_titlepost(self, title_only):
        pass

    def execute_link(self, link_submission):
        pass

    def execute_submission(self, submission):
        return self.general_action(submission.selftext, submission.name, submission.subreddit.display_name,
                                   submission.author.name)

    def update_procedure(self, thing_id, created, lifetime, last_updated, interval):
        pass

    def general_action(self, body, thing_id, subreddit, username):
        if not subreddit.lower() in self.APPROVE or 'leafeator' in username.lower():
            # filtering out all other stuff
            return False

        result = self.REGEX.search(body)
        if result:
            self.logger.info('Trying to comment on {}.'.format(thing_id))
            self.oauth.refresh()
            self.session._add_comment(thing_id, self.RESPONSE)
            return True
        return False

    def on_new_message(self, message):
        pass


def init(database):
    """Init Call from module importer to return only the object itself, rather than the module."""
    return LeafeatorBot(database)


if __name__ == '__main__':
    from praw import Reddit
    r = Reddit(user_agent='Manual Testing')
    cmt = r.get_info(thing_id='t1_cud1yg6')
    lb = LeafeatorBot(None)
    lb.execute_comment(cmt)
