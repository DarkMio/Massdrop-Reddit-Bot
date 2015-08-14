from abc import ABCMeta, abstractmethod
import logging
import praw
from praw import handlers
from OAuth2Util import OAuth2Util
from pkg_resources import resource_filename
from configparser import ConfigParser
import re


class Base(metaclass=ABCMeta):
    DESCRIPTION = None  # user_agent: describes the bot / function / author
    USERNAME = None     # reddit username
    OAUTH_FILENAME = None  # password of reddit username
    REGEX = None        # most basic regex string - pre-filters incoming threads
    BOT_NAME = None     # Give the bot a nice name.
    session = None      # a full session with login into reddit.
    oauth = None        # praw-OAuth2Util
    logger = None       # logger for specific module
    config = None       # Could be used for ConfigParser - there is a method for that.
    database = None     # Session to database.

    def __init__(self, database):
        self.factory_logger()
        self.database = database
        self.RE_BANMSG = re.compile(r'ban /([r|u])/([\d\w_]*)', re.UNICODE)

    def integrity_check(self):
        assert self.USERNAME and self.OAUTH_FILENAME and self.DESCRIPTION, \
            "Failed constant variable integrity check. Check your object and its initialization."
        return True

    def factory_logger(self):
        self.logger = logging.getLogger("plugin")

    def factory_reddit(self, config_file):
        multiprocess = handlers.MultiprocessHandler()
        self.session = praw.Reddit(user_agent=self.DESCRIPTION, handler=multiprocess)
        self.oauth = OAuth2Util(self.session, configfile=config_file)

    def factory_config(self):
        self.config = ConfigParser()
        self.config.read(resource_filename('config', 'bot_config.ini'))

    def get_unread_messages(self):
        if hasattr(self, "session"):
            self.oauth.refresh()
            msgs = self.session.get_unread()
            for msg in msgs:
                msg.mark_as_read()
                self.on_new_message(msg)
        return

    def standard_ban_procedure(self, message, subreddit_banning_allowed=True, user_banning_allowed=True):
        if message.author:
            author, human = message.author.name.lower(), True
        else:
            author, human = message.subreddit.display_name.lower(), False
        if not message.was_comment and author in message.body.lower():
            regex_result = self.RE_BANMSG.search(message.body)
            if regex_result:
                sub, result = self.RE_BANMSG.search(message.body).groups()
            else:
                return
            # check if a user wants to ban a user or a sub wants to ban a sub.
            type_consistency = (sub.lower() == 'r' and not human) or (sub.lower() == 'u' and human)
            if author == result.lower() and type_consistency:
                if human and user_banning_allowed:
                    at, bn = message.author.name, self.BOT_NAME
                    self.database.add_userban_per_module(at, bn)
                    message.reply("Successfully banned /u/{} from {}. "
                                  "The bot should ignore you from now on.\n\n"
                                  "Have a nice day!".format(at, bn))
                    self.logger.info("Banned /u/{} from {} on message request.".format(at, bn))
                elif subreddit_banning_allowed:
                    sb, bn = message.subreddit.display_name, self.BOT_NAME
                    self.database.add_subreddit_ban_per_module(sb, bn)
                    message.reply("Successfully banned /r/{} from {}. "
                                  "The bot should ignore this subreddit from now on."
                                  "\n\nHave a nice day!".format(sb, bn))
                    self.logger.info("Banned /r/{} from {} on message request".format(sb, bn))

    @abstractmethod
    def execute_submission(self, submission):
        pass

    @abstractmethod
    def execute_link(self, link_submission):
        pass

    @abstractmethod
    def execute_titlepost(self, title_only):
        pass

    @abstractmethod
    def execute_comment(self, comment):
        pass

    @abstractmethod
    def update_procedure(self, thing_id, created, lifetime, last_updated, interval):
        pass

    @abstractmethod
    def on_new_message(self, message):
        pass
