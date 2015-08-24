# coding=utf-8
import logging
import sqlite3
from pkg_resources import resource_filename


class DatabaseProvider:
    """This object provides a full set of features to interface with a basic session database,
       which includes following tables:
       - storage        | saves the state of the bot and helps against double posting
       - update_threads | storage to store thing_ids which have to be updated by your plugin
       - modules        | persistent module storage
       - userbans       | a table to ban users from being able to trigger certain plugins
       - subbans        | a table to ban subreddits from being able to trigger certain plugins"""
    logger = None   # Logger
    db = None       # Reference to DB session
    cur = None      # Reference to DB cursor

    def __init__(self):
        self.logger = logging.getLogger("database")
        self.db = sqlite3.connect(
            resource_filename("config", "storage.db"),
            check_same_thread=False,
            isolation_level=None
        )
        self.cur = self.db.cursor()
        self.database_init()

    def __del__(self):
        self.db.close()
        self.logger.warning("DB connection has been closed.")

    def database_init(self):
        """Initializes the database and creates necessary tables."""
        info = lambda x: self.logger.info("Table '{}' had to be generated.".format(x))

        if not self.__database_check_if_exists('storage'):
            self.cur.execute(
                'CREATE TABLE IF NOT EXISTS storage (thing_id STR(15), bot_module INT(5), timestamp datetime)'
            )
            info('storage')

        if not self.__database_check_if_exists('update_threads'):
            self.cur.execute(
                'CREATE TABLE IF NOT EXISTS update_threads '
                '(thing_id STR(15) NOT NULL, bot_module INT(5), created DATETIME, '
                'lifetime DATETIME, last_updated DATETIME, interval INT(5))'
            )
            info('update_threads')

        if not self.__database_check_if_exists('modules'):
            self.cur.execute(
                'CREATE TABLE IF NOT EXISTS modules '
                '(module_name STR(50))'
            )
            info('modules')

        if not self.__database_check_if_exists('userbans'):
            self.cur.execute(
                'CREATE TABLE IF NOT EXISTS userbans (username STR(50) NOT NULL, bot_module INT(5))'
            )
            info('userbans')

        if not self.__database_check_if_exists('subbans'):
            self.cur.execute(
                'CREATE TABLE IF NOT EXISTS subbans (subreddit STR(50) NOT NULL, bot_module INT(5))'
            )
            info('subbans')

    def __database_check_if_exists(self, table_name):
        """Helper method, Internal check if a table exists, refrain from using it."""
        self.cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name=(?)', (table_name,))
        return self.cur.fetchone()

    def insert_into_storage(self, thing_id, module):
        """Stores a certain thing (comment or submission) into the storage, which is for session consistency."""
        self.cur.execute('INSERT INTO storage VALUES ((?), (SELECT _ROWID_ FROM modules WHERE module_name=(?)), '
                         'CURRENT_TIMESTAMP)', (thing_id, module))

    def get_all_storage(self):
        """Returns all elements inside the bot storage."""
        self.__error_if_not_exists(module)
        self.cur.execute("""SELECT thing_id, module_name, timestamp FROM storage
                            INNER JOIN modules
                            ON storage.bot_module = modules._ROWID_""")
        return self.cur.fetchall()

    def retrieve_thing(self, thing_id, module):
        """Returns a single thing from the storage - therefore is true if it exists"""
        self.__error_if_not_exists(module)
        self.cur.execute("""SELECT thing_id, bot_module, timestamp FROM storage
                            WHERE thing_id = (?)
                            AND bot_module = (SELECT _ROWID_ FROM modules WHERE module_name=(?))
                            LIMIT 1""",
                         (thing_id, module,))
        return self.cur.fetchone()

    def delete_from_storage(self, min_timestamp):
        """Deletes _all_ items which are older than a certain timestamp"""
        self.cur.execute("DELETE FROM storage WHERE timestamp <= datetime((?), 'unixepoch')", (min_timestamp,))

    def select_from_storage(self, older_than_timestamp):
        """:param older_than_timestamp: Select all elements in the storage that are older than this timestamp."""
        self.cur.execute("SELECT * FROM storage WHERE timestamp <= datetime((?), 'unixepoch')", (older_than_timestamp,))
        return self.cur.fetchall()

    def insert_into_update(self, thing_id, module, lifetime, interval):
        """Inserts a thing (comment or submission) into the update-table, which calls a module for update-actions."""
        self.__error_if_not_exists(module)
        self.cur.execute("""
                        INSERT INTO update_threads (thing_id, bot_module, created, lifetime, last_updated, interval)
                            VALUES (
                                (?),
                                (SELECT _ROWID_ FROM modules WHERE module_name=(?)),
                                CURRENT_TIMESTAMP,
                                datetime('now', '+' || (?) || ' seconds'),
                                CURRENT_TIMESTAMP,
                                (?))
                         """,
                         (thing_id, module, lifetime, interval,))

    def get_all_update(self):
        """Returns all elements inside the update_threads table"""
        self.__error_if_not_exists(module)
        self.cur.execute("""SELECT thing_id, module_name, created, lifetime, last_updated, interval
                            FROM update_threads
                            INNER JOIN modules
                            ON update_threads.bot_module = modules._ROWID_
                            ORDER BY last_updated ASC""")
        return self.cur.fetchall()

    def __select_to_update(self, module):
        """Helper method, refrain from using it."""
        self.__error_if_not_exists(module)
        self.cur.execute("""SELECT thing_id, module_name, created, lifetime, last_updated, interval
                            FROM update_threads
                            INNER JOIN modules
                            ON update_threads.bot_module = modules._ROWID_
                            WHERE modules.module_name = (?)
                            AND CURRENT_TIMESTAMP > (datetime(update_threads.last_updated,
                                                                '+' || update_threads.interval || ' seconds'))
                            ORDER BY last_updated ASC""",
                         (module,))

    def get_latest_to_update(self, module):
        """Returns a single thing (comment or submission) for a module."""
        self.__select_to_update(module)
        return self.cur.fetchone()

    def get_all_to_update(self, module):
        """Returns _all_ things (comments or submissions) for a module."""
        self.__select_to_update(module)
        return self.cur.fetchall()

    def update_timestamp_in_update(self, thing_id, module):
        """Updates the timestamp when a thing was updated last."""
        self.__error_if_not_exists(module)
        self.cur.execute("""UPDATE update_threads
                            SET last_updated=CURRENT_TIMESTAMP
                            WHERE thing_id=(?)
                            AND bot_module = (SELECT _ROWID_ FROM modules WHERE module_name = (?))""",
                         (thing_id, module))

    def delete_from_update(self, thing_id, module):
        """Deletes _all_ things (comments or submissions) for a module when it outlived its lifetime."""
        self.__error_if_not_exists(module)
        self.cur.execute("""DELETE FROM update_threads
                            WHERE thing_id=(?)
                            AND bot_module = (SELECT _ROWID_ FROM modules WHERE module_name = (?))
                            AND CURRENT_TIMESTAMP > lifetime""", (thing_id, module))

    def register_module(self, module):
        """Registers a module (or notifies you if it has been already registered)."""
        if self.__check_if_module_exists(module):
            return
        self.logger.debug("Module {} has been registered.".format(module))
        self.cur.execute('INSERT INTO modules VALUES ((?))', (module,))

    def get_all_userbans(self):
        """Returns all bans stored in the userban table"""
        self.cur.execute('SELECT * FROM userbans')
        return self.cur.fetchall()

    def get_all_bans_per_user(self, username):
        """Returns all bans of a particular user"""
        self.cur.execute('SELECT * FROM userbans WHERE username = (?) LIMIT 1', (username,))
        return self.cur.fetchall()

    def check_user_ban(self, username, module):
        """Checks if a particular user has been banned - searches per module and globally"""
        self.cur.execute('SELECT * FROM userbans '
                         'WHERE username = (?) AND '
                         'bot_module = (SELECT _ROWID_ FROM modules WHERE module_name = (?)) '
                         'LIMIT 1', (username, module))
        if self.cur.fetchone():
            return True

        self.cur.execute('SELECT * FROM userbans '
                         'WHERE username = (?) AND '
                         'bot_module = (SELECT _ROWID_ FROM modules WHERE module_name = NULL    ) '
                         'LIMIT 1', (username,))
        return self.cur.fetchone() is True

    def add_userban_per_module(self, username, module):
        """Ban a user for a certain module."""
        self.cur.execute("INSERT INTO userbans (username, bot_module) "
                         "VALUES ((?), (SELECT _ROWID_ FROM modules WHERE module_name = (?)))", (username, module))

    def add_userban_globally(self, username):
        """Ban a user for all modules."""
        self.cur.execute("INSERT INTO userbans (username, bot_module) "
                         "VALUES ((?), NULL)", (username,))

    def remove_userban_per_module(self, username, module):
        """Remove a ban from a certain module."""
        self.cur.execute("DELETE FROM userbans WHERE username = (?) AND "
                         "bot_module = (SELECT _ROWID_ FROM modules WHERE modules = (?))", (username, module))

    def remove_userban_globally(self, username):
        """Remove ALL bans from a user."""
        self.cur.execute("DELETE FROM userbans WHERE username = (?)", (username,))

    def purge_all_user_bans(self):
        """Remove ALL bans for users - no exception, clears the table."""
        self.cur.execute("DELETE FROM userbans")

    def get_all_banned_subreddits(self):
        """Returns all bans stored in the subreddit ban table"""
        self.cur.execute('SELECT * FROM subbans')
        return self.cur.fetchall()

    def get_all_bans_per_subreddit(self, username):
        """Returns all bans of a particular user"""
        self.cur.execute('SELECT * FROM subbans WHERE subreddit = (?) LIMIT 1', (username,))
        return self.cur.fetchall()

    def check_subreddit_ban(self, username, module):
        """Checks if a particular user has been banned - searches per module and globally"""
        self.cur.execute('SELECT * FROM subbans '
                         'WHERE subreddit = (?) AND '
                         'bot_module = (SELECT _ROWID_ FROM modules WHERE module_name = (?)) '
                         'LIMIT 1', (username, module))
        if self.cur.fetchone():
            return True

        self.cur.execute('SELECT * FROM subbans '
                         'WHERE subreddit = (?) AND '
                         'bot_module = (SELECT _ROWID_ FROM modules WHERE module_name = NULL    ) '
                         'LIMIT 1', (username,))
        return self.cur.fetchone() is True

    def add_subreddit_ban_per_module(self, username, module):
        """Ban a subreddit for a certain module."""
        self.cur.execute("INSERT INTO subbans (subreddit, bot_module) "
                         "VALUES ((?), (SELECT _ROWID_ FROM modules WHERE module_name = (?)))", (username, module))

    def add_subreddit_ban_globally(self, username):
        """Ban a subreddit across all subreddits."""
        self.cur.execute("INSERT INTO subbans (subreddit, bot_module) "
                         "VALUES ((?), NULL)", (username,))

    def remove_subreddit_ban_per_module(self, subreddit, module):
        """Remove a subreddit ban for a certain module."""
        self.cur.execute("DELETE FROM subbans WHERE subreddit = (?) AND "
                         "bot_module = (SELECT _ROWID_ FROM modules WHERE modules = (?))", (subreddit, module))

    def remove_subreddit_ban_globally(self, subreddit):
        """Remove a subreddit ban across all modules."""
        self.cur.execute("DELETE FROM subbans WHERE subreddit = (?)", (subreddit,))

    def purge_all_subreddit_bans(self):
        """Removes all subreddit bans. No exceptions."""
        self.cur.execute("DELETE FROM subbans")

    def __check_if_module_exists(self, module):
        """Helper method to determine if a module has been already registered. Refrain from using it."""
        self.cur.execute('SELECT COUNT(*) FROM modules WHERE module_name = (?)', (module,))
        result = self.cur.fetchone()
        if result[0] == 0:
            return False
        if result[0] == 1:
            return True
        if result[0] > 1:
            raise ValueError("A module was registered multiple times and is therefore inconsistent. Call for help.")

    def __error_if_not_exists(self, module):
        """Helper method for throwing a concrete error if a module has not been registered, yet a critical database
           task should have been accomplished."""
        if not self.__check_if_module_exists(module):
            raise LookupError('The module where this operation comes from is not registered!')

    def get_all_modules(self):
        """Returns all modules that have been registered."""
        self.cur.execute('SELECT _ROWID_, module_name FROM modules')
        return self.cur.fetchall()

    def clean_up_database(self, older_than_unixtime):
        """Cleans up the database, meaning that everything older than the session time and all threads that should
           be updated and outlived their lifetime will be deleted."""
        self.cur.execute("""DELETE FROM storage WHERE timestamp < datetime((?), 'unixepoch')""", (older_than_unixtime,))
        self.cur.execute("""DELETE FROM update_threads WHERE CURRENT_TIMESTAMP > lifetime""")

    def wipe_module(self, module):
        """Wipes a module entirely across from all tables."""
        self.cur.execute("""DELETE FROM storage
                            WHERE bot_module = (SELECT _ROWID_ FROM modules WHERE module_name = (?))""", (module,))
        self.cur.execute("""DELETE FROM update_threads
                            WHERE bot_module = (SELECT _ROWID_ FROM modules WHERE module_name = (?))""", (module,))
        self.cur.execute("""DELETE FROM modules WHERE module_name = (?)""", (module,))


if __name__ == "__main__":
    db = DatabaseProvider()
    thing_id = "t2_c384fd"
    module = "MassdropBot"
    user = "MioMoto"
    subreddit = "dota2"
#   Commands that work:
#   >> Storage
#   db.insert_into_storage(thing_id, module)
#   print(db.get_all_storage())
#   print(db.select_from_storage(int(time())))
#
#   >> Module Register
#   db.register_module(module)
#   print(db.get_all_modules())
#
#   >> update_threads
#   db.insert_into_update(thing_id, module, 600, 15)
#   print(db.get_latest_to_update('MassdropBot'))
#   print(db.get_all_update())
#   db.update_timestamp_in_update(thing_id, module)
#   db.delete_from_update(thing_id, module)
#
#   >> Cleanup
#   db.clean_up_database(int(time()) - 30)
#   db.wipe_module(module)
#
#   >> Printing out the current state of all tables
#    print(db.get_all_update())
#    print(db.get_all_storage())
#    print(db.get_all_modules())
#
#   >> Subreddit Bans
#   db.purge_all_subreddit_bans()
#   db.add_subreddit_ban_per_module(user, module)
#   db.add_subreddit_ban_globally(user)
#   print(db.check_if_subreddit_is_banned(user, "abc"))
#   print(db.get_all_bans_per_subreddit(user))
#   print(db.get_all_banned_subreddits())
#   db.remove_subreddit_ban_globally(user)
#   print(db.get_all_banned_subreddits())
#
#   >> User Bans
#   db.purge_all_user_bans()
#   db.add_userban_per_module(user, module)
#   db.add_userban_globally(user)
#   print(db.check_if_user_is_banned(user, "abc"))
#   print(db.get_all_bans_per_user(user))
#   print(db.get_all_userbans())
#   db.remove_userban_globally(user)
#   print(db.get_all_userbans())
