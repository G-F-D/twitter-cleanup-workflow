api_key = "xxxxxxxxxxxxxxxxxxxxxxxxx"
api_key_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
access_token = "000000000-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
access_token_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

import tweepy, traceback
from time import sleep
client = tweepy.Client(None, consumer_key, consumer_secret, access_token, access_token_secret, wait_on_rate_limit=True)
verbose = False
tweets_deleted = 0
tweets_skipped = 0
retries_5xx = 0
CODE_RETRY = 0
CODE_SUCCESS = 1
CODE_SKIP = 2
CODE_FATALERROR = 3
def try_deleting_tweet(id_str):
		try:
			client.delete_tweet(id_str)
		except tweety.TwitterServerError as e:
			print('Twitter had an internal server error. Waiting a minute before retrying. ('+str(retries_5xx+1)+'/5)')
			sleep(60)
			if retries_5xx > 5-1:
				print('SKIPPING: ' + id_str + ' This tweet deletion has failed too many times. (5/5)')
				for message in e.api_messages:
					print('    More details: ' + message)
				return CODE_SKIP
			else:
				retries_5xx += 1
				return CODE_RETRY
		except tweepy.NotFound:
			print('SKIPPING: ' + id_str + ' Not found (404).')
			for message in e.api_messages:
				print('    More details: ' + message)
			return CODE_SKIP
		except tweepy.BadRequest:
			print('ERROR: Bad request (400).')
			for message in e.api_messages:
				print('    More details: ' + message)
			return CODE_FATALERROR
		except tweepy.Unauthorized:
			print('ERROR: Unauthorized (403).')
			for message in e.api_messages:
				print('    More details: ' + message)
			return CODE_FATALERROR
		except tweepy.Forbidden:
			print('ERROR: Forbidden (403).')
			for message in e.api_messages:
				print('    More details: ' + message)
			return CODE_FATALERROR
		except tweepy.TooManyRequests:
			print('ERROR: Too many requests (429).')
			for message in e.api_messages:
				print('    More details: ' + message)
			return CODE_FATALERROR
		except:
			traceback.print_exc()
			print('ERROR: Unhandled exception (traceback printed above).')
			return CODE_FATALERROR
		if verbose:
			print('Deleted tweet: ' + id_str)
		return CODE_SUCCESS
print('Getting to work.')
with open('ids_to_delete.txt', 'r') as f:
	for line in f:
		if len(line.strip()) > 0:
			retries_5xx = 0
			return_code = CODE_RETRY
			while return_code == CODE_RETRY:
				return_code = try_deleting_tweet(line.strip())
			if return_code == CODE_SUCCESS:
				tweets_deleted += 1
			elif return_code == CODE_SKIP:
				tweets_skipped += 1
				with open('ids_skipped.txt', 'a') as s:
					s.write(line)
			elif return_code == CODE_FATALERROR:
				print('Not sure what to do about the error, so the script will now stop and create "ids_not_deleted.txt" with all statuses not yet known to be deleted.')
				with open('ids_not_deleted.txt', 'w') as n:
					n.write(line)
					n.write(f.read())
				print('Last tweet attempted: ' + line.strip())
				break
			sleep(10)
print('Deleted ' + str(tweets_deleted) + ' tweets')
if tweets_skipped > 0:
	print('Skipped ' + str(tweets_skipped) + ' tweets (the IDs have been written to "ids_skipped.txt")')