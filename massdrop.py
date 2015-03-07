# This code is sloppy and just retries itself without printing any error.
# This works well for a hosted python server, but shouldn't be used on a
# dev-machine, since you will get no errors.
# This bot usually gets after a few hours for a few seconds in trouble,
# restarting one of the streams. That is a connection-error of reddit,
# just ignore it.
# Have fun.


import praw
import datetime
import random
import sqlite3
import threading
import re
import logging
import traceback
import urllib2
import argparse

from linkfix import linkfix

from BeautifulSoup import BeautifulSoup
from time import time, sleep

# Don't reply to these authors
author_blacklist = ('JiffierBot', 'gfy_mirror')

class multithread(object):

	def __init__(self):
		self.running = True
		self.threads = []

		self.r = praw.Reddit(user_agent='Data-Poller for several bot-logins by /u/DarkMio')
		#self.r.login()

		pwd = "HereCouldBeYourPassword"

		self.r_ma = praw.Reddit(user_agent='Massdrop Guest Link Generator by /u/DarkMio')
		self.r_ma.login('MassdropBot', pwd)
		self.r_ji = praw.Reddit(user_agent='Giant GFYCAT Link Fixer by /u/DarkMio')
		self.r_ji.login('JiffierBot', pwd)
		self.r_ss = praw.Reddit(user_agent='Small Sub Mention Bot by /u/DarkMio')
		self.r_ss.login('SmallSubBot', pwd)



		self.subreddit = 'all'
		self.now = int(time())
		# best handling without formatting is to not format it.
		self.comment = "Hi, I am /u/MassdropBot.\n\nI've detected that you posted a great Massdrop offer but unfortunately unregistered people cannot see it. I am here to fix that:\n\n%s"
		self.comment_multiple = "Hi, I am /u/MassdropBot.\n\nI've detected that you posted some great Massdrop offers but unfortunately unregistered people cannot see it. I am here to fix that:\n\n%s"
		self.banwords = ['x-post', 'xpost', 'crosspost', 'cross post', 'x/post', 'x\\post', 'via', 'from', 'hhh']
		self.banauthor = ['removal_rover',]


	def comment_stream(self):
		"""Loads ALL comments from all threads. We watch you fappin'."""
		while True:

			try:
				comment_stream = praw.helpers.comment_stream(self.r, self.subreddit, limit=None, verbosity=0)
				log.info("Opened comment stream successfully.")
				while self.running == True:
					comment = next(comment_stream) # Retrieve the next comment

					if (	"massdrop.com/buy" in comment.body
						and not "mode=guest_open" in comment.body
						and not check(comment.id)
						and not str(comment.author) == 'MassdropBot'
						): # so, we found at least one massdrop-buy link, let's do this!
							
							reply = l.massdrop(str(comment.body))
							if reply:
								try:
									# and reply to it - needs a retry feature soon
									log.info("Found a MASSDROP comment with ID %s, replying and storing." % comment.id)
									self.r_ma._add_comment(comment.fullname, reply)
									# depricated: comment.reply(reply)
									add(comment.id)
								except:
									log.debug(traceback.print_exc())#pass


					if (	"giant.gfycat.com" in comment.body
						and not check(comment.id)
						and not str(comment.author) in author_blacklist
						):
						reply = l.gfycat(comment.body)
						if reply:
							try:
								log.info("Found a giant GFYCAT comment with ID %s, replying and storing." % comment.id)
								self.r_ji._add_comment(comment.fullname, reply)
								# depricated: comment.reply(reply)
								add(comment.id)
							except:
								log.debug(traceback.print_exc())#pass

			except:
				log.info("Comment stream broke. Retrying in 60.")
				log.debug(traceback.print_exc())
				sleep(60)
				pass



	def submission_stream(self):
		"""Checks all submissions. Either they're link.posts or self.posts. Either way, we catch both."""
		while True:

			try:
				submission_stream = praw.helpers.submission_stream(self.r, self.subreddit, limit=None, verbosity=0)
				log.info("Opened submission stream successfully.")
				while self.running == True:
					submission = next(submission_stream) # retrieve the next submission

					for data in [submission.url, submission.selftext]:
					
						if (	"massdrop.com/buy" in data # is massdrop we can use?
							and not check(submission.id) # is it already worked (for quick bot reboots.)
							and not "mode=guest_open" in data
							):	

							if not "reddit" in submission.url:

								reply = l.massdrop(str(submission.url))
								if reply:
									try:
										# it will be only one link, since link.posts can only hold one.
										log.info("Found a MASSDROP link.post with ID %s, adding comment and storing." % submission.id)
										self.r_ma._add_comment(submission.fullname, reply)
										#submission.add_comment(reply)
										add(submission.id)
									except:
										log.debug(traceback.print_exc())#pass


							elif submission.selftext:

								reply = l.massdrop(str(submission.selftext))
								if reply:
									try:
										log.info("Found a MASSDROP self.post with ID %s, adding comment and storing." % submission.id)
										self.r_ma._add_comment(submission.fullname, reply)
										#submission.add_comment(reply)
										add(submission.id)
									except:
										log.debug(traceback.print_exc())#pass


						if (	"giant.gfycat.com" in data
							and not check(submission.id)
							):

							if not "reddit" in submission.url:

								reply = l.gfycat(str(submission.url))
								if reply:
									try:
										log.info("Found a giant GFYCAT link.post with ID %s, adding comment and storing." % submission.id)
										self.r_ji._add_comment(submission.fullname, reply)
										#submission.add_comment(reply)
										add(submission.id)
									except:
										log.debug(traceback.print_exc())#pass
							elif submission.selftext:
								reply = l.massdrop(str(submission.selftext))
								if reply:
									try:
										log.info("Found a giant GFYCAT self.post with ID %s, adding comment an storing" % submission.id)
										self.r_ji._add_comment(submission.fullname, reply)
										#submission.add_comment(reply)
										add(submission.id)
									except:
										log.dself.ebug(traceback.print_exc())#pass


					if (	'r/' in submission.title
						and not any(bans in submission.title.encode('utf-8').lower() for bans in self.banwords)
						and not ('bot' in str(submission.author).lower() or any(bans in str(submission.author).lower() for bans in self.banauthor))
						and not check(submission.id)
						):

						reply = l.subreddit_name(str(submission.title.encode('utf-8')), submission.subreddit, submission.url)
						if reply:
							try:
								log.info("Found a SUBREDDIT title with ID %s, replying and storing." % submission.id)
								self.r_ss._add_comment(submission.fullname, reply)
								#submission.add_comment(reply)
								add(submission.id)
							except:
								log.debug(traceback.print_exc())#pass


			except:
				log.info("Submission stream broke. Retrying in 60.")
				log.debug(traceback.print_exc())
				sleep(60)
				pass
			

	def database_cleaner(self):
		"""Cleans up the database, which contains worked-through IDs."""
		while self.running == True:

			deleteme = cur.execute("SELECT * FROM reddit WHERE time + 86400 < %s" % self.now)
			i = 0
			if deleteme:
				for i, entry in enumerate(cur.fetchall()):
					cur.execute("DELETE FROM reddit WHERE id = '%s'" % entry[1])
					i += 0
				i > 0 and log.info("Cleaned %s entries from the database." % i)

			sleep(3600)


	def close(self):
		db.close()
		log.error("CRITICAL ERROR:")
		log.debug(traceback.print_exc())
		log.info("Established connection to database was closed.")
		raise SystemExit


	#def get_user_input(self):
	#	while True:
	#		x = raw_input("Enter 'e' for exit: ")
	#		if x.lower() == 'e':
	#			self.running = False
	#			break


	def go(self):
		t1 = threading.Thread(target=self.comment_stream)
		t2 = threading.Thread(target=self.submission_stream)
		t3 = threading.Thread(target=self.database_cleaner)
		# Make threads daemonic, i.e. terminate them when main thread
		# terminates. From: http://stackoverflow.com/a/3788243/145400
		t1.daemon = True
		t2.daemon = True
		t3.daemon = True
		t1.start()
		t2.start()
		t3.start()
		self.threads.append(t1)
		self.threads.append(t2)
		self.threads.append(t3)

class NoParsingFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('Resetting')


def join_threads(threads):
	"""
	Join threads in interruptable fashion.
	From http://stackoverflow.com/a/9790882/145400
	"""
	for t in threads:
		while t.isAlive():
			t.join(5)


def check(ID):
	check = cur.execute('SELECT id FROM reddit WHERE id = "%s" LIMIT 1' % ID)
	for line in check:
		sleep(10)
		if line:
			return True

def add(ID):
	cur.execute('INSERT INTO reddit (time, id) VALUES ("%s", "%s")' % (int(time()), ID))



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='MassdropBot parses Links which are more comfy to click in the comment-section.')
	parser.add_argument('--verbose', action='store_true', help='Print mainly tracebacks.')
	args = parser.parse_args()

	# SET UP LOGGER
	logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%X', level=logging.DEBUG if args.verbose else logging.INFO)
	log = logging.getLogger(__name__)
	log.addFilter(NoParsingFilter())

	# SET UP DATABASE
	db = sqlite3.connect('massdrop.db', check_same_thread=False, isolation_level=None)
	cur = db.cursor()

	t = multithread()
	l = linkfix()

	t.go()
	try:
		join_threads(t.threads)
	except KeyboardInterrupt:
		log.info("Stopping process entirely.")
		db.close() # you can't close it enough, seriously.
		log.info("Established connection to database was closed.")