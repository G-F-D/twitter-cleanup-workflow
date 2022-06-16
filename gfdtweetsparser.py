import json, datetime, re, html
with open('./tweet.js', 'r', encoding='utf-8') as src_file:
	# skip variable assignment text “window.YTD.tweet.part0 = ” since it’s not json
	# ASSUMPTION: file starts with exactly the aforementioned string (it has for many years now)
	src_file.seek(25)
	json_data = json.loads(src_file.read())
with open('./tweet.csv', 'w', encoding='utf-8') as csv_file:
	csv_record = (
		"ID;"
		"Date;"
		"Source URL;"
		"Source name;"
		"♥;"
		"🔁;"
		"Type;"
		"Other user;"
		"🖼;"
		"Full text;"
		"Media file 1;"
		"Media file 2;"
		"Media file 3;"
		"Media file 4;"
	)
	csv_file.write(csv_record + '\n')
	for tweet in json_data:
		tweet = tweet['tweet']
		# these fields are considered useless
		# ASSUMPTION: several (variable usefulness and contents)
		tweet.pop('retweeted', None) # always false
		tweet.pop('truncated', None) # always false
		tweet.pop('favorited', None) # always false
		tweet.pop('possibly_sensitive', None) # “an indicator that the URL contained in the Tweet may contain content or media identified as sensitive content”; seems useless
		tweet.pop('id_str', None) # same as ‘id’
		tweet.pop('in_reply_to_user_id_str', None) # same as ‘in_reply_to_user_id’
		tweet.pop('in_reply_to_status_id_str', None) # same as ‘in_reply_to_status_id’
		tweet['entities'].pop('hashtags', None) # just any text preceded by # in ‘full_text’
		tweet['entities'].pop('symbols', None)  # just any text preceded by $ in ‘full_text’
		tweet['entities'].pop('display_text_range', None) # just [0, len(tweet['full_text'])]
		tweet.pop('lang', None) # Twitter gets this dead wrong WAY too often for it to be useful
		# add some fields
		tweet['type'] = ''
		tweet['other_user'] = ''
		# try to figure out if this is a reply or a retweet. this is wrong on occasion, but there seems to be no definitive way to tell from the data given what Twitter’s backend considers it to be?
		if re.search('^@[a-zA-Z0-9_]', tweet['full_text']):
			tweet['type'] = '@' # often overwritten by 💬︎ types
			tweet['other_user'] = tweet['full_text'].split(' ', 1)[0][1:]
		elif re.search('^RT @[a-zA-Z0-9_]+?: ', tweet['full_text']):
			tweet['type'] = '🔁'
			tweet['other_user'] = tweet['full_text'].split(':', 1)[0][4:]
		if 'in_reply_to_user_id' in tweet:
			if 'in_reply_to_status_id' in tweet:
				tweet['type'] = '💬'
			else:
				# weird to have a reply to a user but not a status, but happens sometimes regardless. i assume these are also just mentions? but you can change the label here if you have need to
				tweet['type'] = '@'
			if 'in_reply_to_screen_name' in tweet:
				tweet['other_user'] = tweet['in_reply_to_screen_name']
		tweet['source_url']  = tweet['source'].split('"', 2)[1]
		tweet['source_name'] = tweet['source'].split('>', 1)[1].replace('</a>', '') # look whatever i’m not getting paid for this
		tweet['media_files'] = []
		# edit some fields
		tweet['created_at'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
		tweet['created_at'] = tweet['created_at'].astimezone().strftime('%Y-%m-%d %H:%M:%S')
		for url in tweet['entities']['urls']:
			edit = tweet['full_text'].replace(url['url'], url['expanded_url'])
			if edit == tweet['full_text']:
				print(f"Shortened URL substitution failed on tweet ID {tweet['id']} (duplicate URL?)")
			else:
				tweet['full_text'] = edit
		tweet['full_text'] = html.unescape(tweet['full_text'])
		# ASSUMPTION: 'extended_entities' always has 'media' entry
		if 'extended_entities' in tweet:
			media_list = tweet['extended_entities']['media']
		elif 'media' in tweet['entities']:
			media_list = tweet['entities']['media']
		else:
			media_list = []
		edit_urls = {}
		for media in media_list:
			if media['url'] not in edit_urls:
				edit_urls[media['url']] = []
			if 'variants' in media:
				bitrate = -1
				for variant in variants:
					if variant['content_type'] == 'video/mp4' and int(variant['bitrate']) > bitrate:
						best_url = variant['url']
						bitrate = int(variant['bitrate'])
			else:
				best_url = media['media_url_https']
			edit_urls[media['url']].append(best_url)
			tweet['media_files'].append(tweet['id'] + '-' + best_url.split('/')[-1])
		for url, new_urls in edit_urls.items():
			edit = tweet['full_text'].replace(url, ' '.join(map(str, new_urls)))
			if edit == tweet['full_text']:
				print(f"media edit failed on {tweet['id']}")
			else:
				tweet['full_text'] = edit
		tweet['full_text'] = tweet['full_text'].replace('"', '""') # escape tweet text
		csv_record = (
			f'"{tweet["id"]}";'
			f'{tweet["created_at"]};'
			f'"{tweet["source_url"]}";'
			f'"{tweet["source_name"]}";'
			f'{tweet["favorite_count"]};'
			f'{tweet["retweet_count"]};'
			f'"{tweet["type"]}";'
			f'"{tweet["other_user"]}";'
			f'{len(tweet["media_files"])};'
			f'"{tweet["full_text"]}";'
		)
		for media in tweet['media_files']:
			csv_record += f'"{media}";'
		csv_file.write(csv_record + '\n')
print(f'tweet.csv produced from {len(json_data)} tweets.')