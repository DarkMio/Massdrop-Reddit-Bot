from core.BaseClass import Base
from configparser import ConfigParser
from pkg_resources import resource_filename
from urllib.request import urlopen
from urllib.error import HTTPError
from datetime import datetime
from json import loads as json_loads
import re
from praw.objects import Comment
from misc.mutliple_strings import multiple_of


class Massdrop(Base):

    def __init__(self, database):
        super().__init__(database)
        super().factory_config()
        self.BOT_NAME = 'MassdropBot'
        self.DESCRIPTION = self.config.get(self.BOT_NAME, 'description')
        self.USERNAME = self.config.get(self.BOT_NAME, 'username')
        self.OAUTH_FILENAME = self.config.get(self.BOT_NAME, 'oauth')
        self.REGEX = re.compile(r"(?P<url>https?:\/\/(?:www\.)?massdrop\.com\/buy\/[^\s;,.\])]*)", re.UNICODE)
        self.factory_reddit(config_file=resource_filename("config", self.OAUTH_FILENAME))
        self.responses = MassdropText("bot_config.ini")

        self.RE_DATASET = re.compile('"DropsStore":({.*?}),"StatsStore"', re.UNICODE)

    def execute_comment(self, comment):
        url = self.REGEX.findall(comment.body)
        if url:
            response, time_ends_in = self.generate_response(url)
            if response:
                self.oauth.refresh()
                generated = self.session._add_comment(comment.fullname, response)
                if time_ends_in:
                    self.database.insert_into_update(generated.name, self.BOT_NAME,
                                                     time_ends_in.seconds + 13*60*60, 43200)
                return True
        return False

    def execute_submission(self, submission):
        url = self.REGEX.findall(submission.selftext)
        if url:
            response, time_ends_in = self.generate_response(url)
            if response:
                self.oauth.refresh()
                generated = self.session._add_comment(submission.name, response)
                if time_ends_in:
                    self.database.insert_into_update(generated.name, self.BOT_NAME,
                                                     time_ends_in.seconds + 13*60*60, 43200)
                return True
        return False

    def execute_link(self, link_submission):
        link = self.REGEX.findall(link_submission.url)
        if link:
            response, time_ends_in = self.generate_response(link)
            if response:
                self.oauth.refresh()
                generated = self.session._add_comment(link_submission.name, response)
                if time_ends_in:
                    self.database.insert_into_update(generated.name, self.BOT_NAME,
                                                     time_ends_in.seconds + 13*60*60, 43200)
                return True
        return False

    def execute_titlepost(self, title_only):
        pass

    def update_procedure(self, thing_id, created, lifetime, last_updated, interval):
        self.oauth.refresh()
        comment = self.session.get_info(thing_id=thing_id)
        if comment.score < -5:
            comment.delete()
            self.database.delete_from_update(thing_id, self.BOT_NAME)
            return

        if isinstance(comment, Comment):
            url = self.REGEX.findall(comment.body)
            if url:
                response, time_left = self.generate_response(url, from_update=True)
                comment.edit(response)
                return

    def on_new_message(self, message):
        self.standard_ban_procedure(message)

    def execute_textbody(self, string):
        url = self.REGEX.findall(string)
        if url:
            response, time_ends_at = self.generate_response(url)
            print(response)

    def generate_response(self, massdrop_links, time_left=None, from_update=False):
        """Takes multiple links at once, iterates, generates a response appropiately.
           Idea is to take into account: Title, Price, Running Drop, Time left"""
        drop_field = []
        textbody = ""
        fixed_urls = 0
        time_ends_in = None
        will_update = False
        for url in massdrop_links:
            # if that is already a fixed url, we may ignore it.
            fix_url = url
            if 'mode=guest_open' in url and not from_update:
                continue
            if not from_update:
                fix_url = fix_url + ('?', '&')['?' in url] + 'mode=guest_open'
                self.logger.debug('Trying to open {} .'.format(fix_url))
            try:
                content = urlopen(fix_url).read().decode('utf-8')
                drop_data = self.RE_DATASET.search(content).groups()[0]
                drop_data = json_loads(drop_data)
                product_name = drop_data['drop']['name']
                if drop_data['drop']['statusCode'] == 1:
                    current_price = "${:.2f}".format(drop_data['drop']['currentPrice'])
                    prices = [x['price'] for x in drop_data['drop']['steps']]
                    prices = massdrop_pricer(current_price, prices)
                    time_ends_at = datetime.strptime(drop_data['drop']['endAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    time_ends_in = time_ends_at - datetime.utcnow()
                    time_left = " / " + self.time_formatter(time_ends_in)
                    will_update = True
                else:
                    time_left = "drop has ended"
                    current_price, prices = "", ""
                drop_field.append({"title": product_name, 'current_price': current_price, 'prices': prices,
                                   "time_left": time_left, 'fix_url': fix_url})
                fixed_urls += 1
            except HTTPError as e:
                self.logger.error("HTTPError:", e.msg)
                pass
            except Exception as e:
                self.logger.error("Oh noes, an unexpected error happened:", e)

        if len(drop_field) == 0:
            return None, None

        # item is a dictionary that fits on the right binding - saves time, is short
        for item in drop_field:
            textbody += self.responses.product_binding.format(**item)

        update_string = ['', ' ^| ^This ^comment ^updates ^every ^12 ^hours.'][will_update]

        textbody = self.responses.intro_drop.format(products=('product', 'products')[fixed_urls > 1]) + \
                   textbody + self.responses.outro_drop.format(update=update_string)

        return textbody.replace('\\n', '\n'), time_ends_in

    @staticmethod
    def time_formatter(time_left):
        if time_left.days > 0:
            days = time_left.days
            return "{} {} left".format(days, multiple_of(days, "day", "days"))
        hours = time_left.seconds//3600
        return "{} {} left".format(hours, multiple_of(hours, "hour", "hours"))


class MassdropText:
    intro = ""
    product_binding = ""
    outro_drop = ""
    update_binding = ""

    def __init__(self, filename):
        ch = ConfigParser()
        ch.read(resource_filename("config", filename))
        self.intro = ch.get('MassdropBot', 'intro')
        self.intro_drop = ch.get('MassdropBot', 'intro_drop')
        self.product_binding = ch.get('MassdropBot', 'product_binding')
        self.update_binding = ch.get('MassdropBot', 'update_binding')
        self.outro_drop = ch.get('MassdropBot', 'outro_drop')

    def __repr__(self):
        p = "\n\t"
        return "Fields:" + p + self.intro + p + self.intro_drop + p + self. product_binding + p + self.update_binding \
               + p + self.outro_drop


def massdrop_pricer(price, pricelist):
    if isinstance(price, str) and price.startswith("$"):
        price = price[1:].replace(',', '')
    pricelist = [float(x) for x in pricelist if float(x) < float(price)]
    if len(pricelist) > 1:
        pricestring = "${:.2f}".format(pricelist[0])
        for item in pricelist[1:]:
            pricestring += "/${:.2f}".format(item)
        return ': drops to ' + pricestring
    elif len(pricelist) == 1:
        return ': drops to ' + "${:.2f}".format(pricelist[0])
    else:
        return ""


def init(database):
    """Init Call from module importer to return only the object itself, rather than the module."""
    return Massdrop(database)

if __name__ == "__main__":
    from core.DatabaseProvider import DatabaseProvider
    mt = MassdropText("bot_config.ini")
    print(mt)
    db = DatabaseProvider()
    md = Massdrop(db)

    print(md.execute_textbody('https://www.massdrop.com/buy/creative-aurvana-live-2'))

    # print(md.update_procedure("t1_ctv1673", 0, 0, 0, 0))
