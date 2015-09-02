# coding=utf-8
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
    BOT_NAME = None     # Give the bot a nice name.
    IS_LOGGED_IN = False  # Mandatory bool if this bot features a logged in session
    SELF_IGNORE = True  # Bool if the bot should not react on his own submissions / comments.
    session = None      # a full session with login into reddit.
    oauth = None        # praw-OAuth2Util
    logger = None       # logger for specific module
    config = None       # Could be used for ConfigParser - there is a method for that.
    database = None     # Session to database.

    def __init__(self, database, bot_name, setup_from_config=True):
        self.factory_logger()
        self.database = database
        self.BOT_NAME = bot_name
        self.RE_BANMSG = re.compile(r'ban /([r|u])/([\d\w_]*)', re.UNICODE)
        if setup_from_config:
            self.factory_config()
            self.standard_setup(bot_name)

    def integrity_check(self):
        """Checks if the most important variables are initialized properly.

        :return: True if possible
        :rtype: bool
        """
        assert hasattr(self, 'DESCRIPTION') and hasattr(self, 'BOT_NAME') and hasattr(self, 'IS_LOGGED_IN'), \
            "Failed constant variable integrity check. Check your object and its initialization."
        if self.IS_LOGGED_IN:
            assert hasattr(self, 'USERNAME') and self.USERNAME \
                and hasattr(self, 'session') and self.session \
                and hasattr(self, 'oauth') and self.session, \
                "Plugin is declared to be logged in, yet the session info is missing."
            assert self.session.user.name.lower() == self.USERNAME.lower(), \
                "This plugin is logged in with wrong credentials: \n" \
                "is: {} - should be: {}".format(self.session.user.name, self.USERNAME)
        else:
            assert hasattr(self, 'USERNAME') and self.USERNAME is False and \
                hasattr(self, 'session') and self.session is False and \
                hasattr(self, 'oauth') and self.session is False, \
                "Plugin is declared to be not logged in, yet has a set of credentials."
        return True

    def factory_logger(self):
        """Sets up a logger for the plugin."""
        self.logger = logging.getLogger("plugin")

    def factory_reddit(self, config_path):
        """Sets up a complete OAuth Reddit session

        :param config_path: full / relative path to config file
        :type config_path: str
        """
        multiprocess = handlers.MultiprocessHandler()
        self.session = praw.Reddit(user_agent=self.DESCRIPTION, handler=multiprocess)
        self.oauth = OAuth2Util(self.session, configfile=config_path)

    def factory_config(self):
        """Sets up a standard config-parser to bot_config.ini. Does not have to be used, but it is handy."""
        self.config = ConfigParser()
        self.config.read(resource_filename('config', 'bot_config.ini'))

    def standard_setup(self, bot_name):
        get = lambda x: self.config.get(bot_name, x)
        self.DESCRIPTION = get('description')
        self.IS_LOGGED_IN = self.config.getboolean(bot_name, 'is_logged_in')
        if self.IS_LOGGED_IN:
            self.SELF_IGNORE = self.config.getboolean(bot_name, 'self_ignore')
            self.USERNAME = get('username')
            self.OAUTH_FILENAME = get('oauth_file')
            self.factory_reddit(config_path=resource_filename("config", self.OAUTH_FILENAME))

    def get_unread_messages(self):
        """Runs down all unread messages of a Reddit session."""
        if hasattr(self, "session"):
            self.oauth.refresh()
            msgs = self.session.get_unread()
            for msg in msgs:
                msg.mark_as_read()
                self.on_new_message(msg)

    def standard_ban_procedure(self, message, subreddit_banning_allowed=True, user_banning_allowed=True):
        """An exemplary method that bans users and subs and then replies them that the bot has banned.
           Needs a reddit session, oauth and a database pointer to function properly.

        :param message: a single praw message object
        :type message: praw.objects.Message
        :param subreddit_banning_allowed: can block out the banning of subreddits
        :type subreddit_banning_allowed: bool
        :param user_banning_allowed: can block out the banning of users
        :type user_banning_allowed: bool
        :return:
        """
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

    def __test_single_thing(self, thing_id):
        """If you're used to reddit thing ids, you can use this method directly.
           However, if that is not the case, use test_single_submission and test_single_comment."""
        r = praw.Reddit(user_agent='Bot Framework Test for a single submission.')
        thing = r.get_info(submission_id=thing_id)
        if type(thing) is praw.objects.Submission:
            if thing.is_self and thing.selftext:
                self.execute_submission(thing)
            elif thing.is_self:
                self.execute_titlepost(thing)
            else:
                self.execute_link(thing)
        else:
            self.execute_comment(thing)

    def test_single_submission(self, submission_id):
        """Use this method to test you bot manually on submissions."""
        self.__test_single_thing("t3_{}".format(submission_id))

    def test_single_comment(self, comment_id):
        """Use this method to test your bot manually on a single comment."""
        self.__test_single_thing("t1_{}".format(comment_id))

    def to_update(self, response_object, lifetime):
        """This method is preferred if you want a submission or comment to be updated.

            :param response_object: PRAW returns on a posted submission or comment the resulting object.
            :type response_object: praw.objects.Submission or praw.objects.Comment
            :param lifetime: The exact moment in unixtime utc+0 when this object will be invalid (update cycle)
            :type lifetime: unixtime in seconds
        """
        if not self.database:
            self.logger.error('{} does not have a valid database connection.'.format(self.BOT_NAME))
        else:
            if isinstance(response_object, praw.objects.Submission) or isinstance(praw.objects.Comment):
                self.database.insert_into_update(response_object.fullname, self.BOT_NAME, lifetime)
            else:
                self.logger.error('response_object has an invalid object type.')

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
