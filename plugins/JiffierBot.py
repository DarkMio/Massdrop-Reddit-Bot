# coding=utf-8
from core.BaseClass import Base
from pkg_resources import resource_filename
from configparser import ConfigParser
from requests import get as requests_get
import re


class JiffierBot(Base):
    def __init__(self, database):
        super().__init__(database)
        self.BOT_NAME = 'JiffierBot'
        self.DESCRIPTION = 'Fixes GFYCAT links and gives a witty response.'
        self.OAUTH_FILENAME = 'JiffierBot_OAuth.ini'
        self.factory_reddit(config_path=resource_filename('config', self.OAUTH_FILENAME))
        self.USERNAME = 'JiffierBot'
        self.REGEX = re.compile(r'https?:\/\/(?:giant|fat|zippy).gfycat.com\/([\w]*)\.gif', re.UNICODE)
        self.API_URL = 'http://gfycat.com/cajax/get/{}'
        self.FIX_URL = 'http://gfycat.com/{}'
        self.responses = JifferText('bot_config.ini')

    def execute_comment(self, comment):
        return self.general_action(comment.body, comment.fullname)

    def execute_titlepost(self, title_only):
        pass

    def execute_link(self, link_submission):
        return self.general_action(link_submission.url, link_submission.name)

    def execute_submission(self, submission):
        return self.general_action(submission.selftext, submission.name)

    def update_procedure(self, thing_id, created, lifetime, last_updated, interval):
        pass

    def on_new_message(self, message):
        self.standard_ban_procedure(message)

    def general_action(self, body, thing_id):
        result = set(self.REGEX.findall(body))  # Clear out all doubles
        if result:
            response = self.generate_response(result)
            if response:
                self.oauth.refresh()
                self.session._add_comment(thing_id, response)
                return True
        return False

    def generate_response(self, gfy_urls):
        carebox = []
        textbody = ''
        for url in gfy_urls:
            fix_url = self.FIX_URL.format(url)
            result = requests_get(self.API_URL.format(url))
            if result.ok:
                gfy_item = result.json()['gfyItem']
                size = '{:.1f}'.format(gfy_item['gifSize'] / gfy_item['webmSize'])
                title = [fix_url, gfy_item['title']][gfy_item['title'] is True]
                reddit = gfy_item['redditId']
                carebox.append({'fix_url': fix_url, 'size': size, 'title': title, 'reddit': reddit})

        for gfycat in carebox:
            textbody += self.responses.gfycat_binding.format(**gfycat)
            if gfycat['reddit']:
                origin = self.session.get_submission(submission_id=gfycat['reddit'])
                caredict = {'upvote': origin.upvote_ratio * 100, 'title': origin.title,
                            'url': 'https://np.reddit.com/{}/'.format(gfycat['reddit'])}
                textbody += self.responses.original_submission.format(**caredict)

        textbody = self.responses.intro + textbody + self.responses.outro
        return textbody.replace('\\n', '\n')


class JifferText:
    intro = ""
    gfycat_binding = ""
    original_submission = ""
    outro = ""

    def __init__(self, filename):
        ch = ConfigParser()
        ch.read(resource_filename("config", filename))
        self.intro = ch.get('JiffierBot', 'intro')
        self.gfycat_binding = ch.get('JiffierBot', 'gfycat_binding')
        self.original_submission = ch.get('JiffierBot', 'original_submission')
        self.outro = ch.get('JiffierBot', 'outro')

    def __repr__(self):
        p = "\n\t"
        return "Fields:" + p + self.intro + p + self.gfycat_binding + p + self.original_submission \
               + p + self.outro


def init(database):
    """Init Call from module importer to return only the object itself, rather than the module."""
    return JiffierBot(database)


if __name__ == '__main__':
    JiffierBot(None)
