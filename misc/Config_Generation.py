from argparse import ArgumentParser
from configparser import ConfigParser


"""Simple wizard for bot config generation. Run itself get infos + walkthrough."""


class BotConfig:
    def __init__(self, name=None, description=None, logged_in=False, username=None, oauth_path=None):
        self.name, self.description, self.logged_in, self.username, self.oauth_path = name, description, logged_in, \
                                                                                      username, oauth_path
        pass

def oauth_userguide():
    print('We will generate a full set of OAuth credentials.')
    section_generated = input('Have you already generated a config section? (y/n)')
    if section_generated.lower() == 'n':
        should_be_generated = input('Do you want to auto generate this now? (y/n)')
        if should_be_generated.lower() == 'y':
            bc = BotConfig()


def config_gen():
    # @TODO: Staging config
    pass


if __name__ == '__main__':
    arguments_exist = True
    bot_name = input("Please enter your bots finite name: ")
    cp = ConfigParser
    cp.read('../config/bot_comfig.ini')
    sections = cp.sections()
    if bot_name in cp.sections():
        exists = input("It appears that your bot has already bits of configuration. Is that correct? (y/n)")
        if exists.lower() == 'y':
            arguments_exist = True
            config_gen()

    if not arguments_exist:
        running = True
        while running:
            oauth_userguide()
else:
    raise ImportError('This script is supposed to be executed.')














