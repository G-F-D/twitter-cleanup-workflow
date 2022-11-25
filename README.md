# GFD’s Twitter archive cleanup workflow
This is a workflow I made for cleaning up old tweets en masse, using the Twitter API to automate the deletion process.

# FAQ
## What is this repository, exactly?
This describes a workflow and provides some scripts for automation. It is not a complete software package, more of a guide/tutorial for how to use these scripts in combination with other free open‐source software.

## Why would I want to do this?
When people want to get rid of old tweets that may now be compromising, it’s common to use an external tool that deletes all tweets before a certain date. This is not only maximally destructive, but it gives all manner of potentially vulnerable, personal data directly to third‐parties. This workflow instead preserves as much tweet history as possible by only deleting the tweets you specify, and keeps you in full control of your data by using only free open‐source software.

## Why did you make/write this?
It was relatively low‐effort for me to put this workflow together, but this did require specialized knowledge on various tech‐related things. After being asked to help someone else do this exact thing, I decided to put this tutorial together to make this knowledge more accessible to general audiences. (This guide does assume some basic competency like being able to install software.)

## Does this also handle retweets?
Yes, there is no special handling for them necessary. Every retweet is actually just a regular tweet in a fancy disguise, so you can also delete them directly just like any other tweet, rather than having to “unretweet” the source tweet or something.

## How does this handle edits?
**It doesn’t**; this feature didn’t exist when I created this workflow. Depending on how these are stored in the archive (I have no sample data I can check), I assume this will produce one of these outcomes in this workflow:
* The tweet will appear once with its original text;
* The tweet will appear once with its most recent text;
* Each edit will appear as its own tweet.
I also do not know how this will impact the automated deletion process, particularly in the lattermost case.

## How long will this take?
Potentially a very long time, especially if you have 5 figures of tweets or more. There’s both waiting and labour:
* Requesting an account archive often takes many days for Twitter to fulfill.
* Picking out all the individual tweets to delete can take dozens of hours if you want to review them all manually for maximal care.
* Automated deletion of tweets is rate‐limited by Twitter to 200 tweets per hour.

# Requirements
## PC Operating System
All software used here is cross‐platform across Windows, MacOS, and Linux, but this tutorial assumes you are using Windows for instructions on built‐in software, like using Windows File Explorer for browsing files and Windows Powershell for terminal interactions.

## Your Twitter archive
[Request an archive here.](https://twitter.com/settings/download_your_data) When you get an email (probably from notify@twitter.com) that your data is ready, return there to download it. While waiting for that, you can work on the rest of these requirements.

## Twitter API keys
While logged into the account you’ll be deleting tweets from, [sign up for API access here.](https://developer.twitter.com/en/portal/petition/essential/basic-info) You will need to answer some questions. Be aware that users within some countries (e.g. apparently Russia) may be required to go through additional processes before being approved for API access. For the “use case” question, you might consider “Exploring the API” or “Making a bot” to be most relevant to you. Then review and agree to the developer agreement & policy, and confirm your e‐mail address. You’ll technically be making a new Twitter App, so next you’ll have to name it — I just called mine “GFD’s assistant”.

You’ll now be shown several “keys” (they look like randomized passwords, which they kind of are) and told to save them somewhere, but you don’t need to right now — in fact, _not_ saving them anywhere will be more secure for now, since if anyone were to find these they could use them to wreak havoc on your account. Instead, we’ll generate new keys later when you’re ready to start deleting tweets.

On the dashboard page, there will be a section for the “Project App” you just created, including its name. Click the blue gear icon on the right side there, then click the “Edit” button under “User authentication settings”. Enable “OAuth 1.0a”, and under “App permissions” below, choose “Read and write”. Further down, your callback URI / redirect URL can just be `http://localhost` (i.e. nowhere), and the website URL can just be any URL to represent yourself with. Then click “Save” at the bottom. (Read/write access to your account is not actually enabled yet; we’ll do that later.)

## Python 3
You’ll need Python to run the scripts I made, so we’ll check if you already have a usable Python install (there’s a decent chance you do). Open Windows Powershell and enter/paste `py --version`. If you get some red text in response, you need to install Python. Otherwise, check that the version number is at least 3.7 (as of this writing). If this version is lower, you need to install the latest Python. Otherwise, enter/paste `py -m pip --version`. If you don’t get a response that starts with something like “pip 22.1.2”, you need to re‐install Python.

[The latest Python installer is available here](https://www.python.org/downloads/); look for the rounded yellow download button. Redo the above steps after installation to make sure it’s been installed properly (be sure to open a new Powershell window after finishing the installation).

## Tweepy
Enter/paste `py -m pip install tweepy` into Powershell. ([Tweepy](https://www.tweepy.org/) will help us use the Twitter API.)

## Spreadsheet software
This uses LibreOffice Calc, which is free open‐source software. [Installers are available here](https://www.libreoffice.org/download/download/); look for the yellow download buttons (either one should work fine).

Other spreadsheet software probably works just as well, but I didn’t want to give Google all my Twitter data through Google Sheets, and I don’t pay for Microsoft Office.

# Process
## Creating the spreadsheet
Extract your Twitter archive .zip file (right‐click on it → “Extract All...”). Download these two script files I made to the “data” subfolder, by right‐clicking these two links and selecting “Save Link As...”: [gfdtweetsparser.py](https://github.com/G-F-D/twitter-cleanup-workflow/raw/main/gfdtweetsparser.py) and [gfdtweetdeletionbot.py](https://github.com/G-F-D/twitter-cleanup-workflow/raw/main/gfdtweetdeletionbot.py). Hold shift and right‐click on some empty space in the folder (i.e. not on a file) and choose “Open Powershell window here”, and then enter `py gfdtweetsparser.py`. This will generate “tweet.csv”; open it in LibreOffice Calc. In the “Text Import” dialogue that appears, make sure “Separator Options” only has “Semicolon” checked, that the “String delimiter” is `"`, and that “Format quoted field as text” is checked. When saving the spreadsheet, choose “Use ODF Format” on the dialogue that appears.

## Using the spreadsheet
The spreadsheet will have many columns, with labels in the first row:
* “ID” is the tweet’s unique number identifier, which we will use later to delete them with the API.
* “Date” is the date and time the tweet was posted (this was automatically adjusted to your PC’s local time, including DST adjustments)
* “Source URL” and “Source name” are what was used to post the tweet (e.g. “Twitter Web Client”, “Twitter for Android”, “Tweetdeck”, etc. along with links to them).
* “♥︎” is how many likes the tweet has.
* “🔁︎” is how many retweets the tweet has.
* “Type” tries to indicate what kind of tweet this is:
    * A regular tweet (blank);
    * A reply (“💬︎”);
    * A mention that doesn’t seem to be a reply (“@”);
    * A retweet (“🔁︎”). (Note that this is also applied if you’ve manually made a tweet that starts with “RT @username: ” because of how Twitter stores tweets. It also fails to be applied to the very esoteric case of retweets from accounts that were “[Mysteriously Unnamed](https://old.reddit.com/r/Twitter/comments/niuctx/mysteriously_unnamed_accounts/)” at the time.)
* “Other user”, when applicable, is the user being replied to / @ mentioned / retweeted (depending on the type of tweet). (This can differ from what appears after the @ in the tweet text if that user’s handle has changed since the tweet was made.)
* “🖼︎” is how many media files are attached to the tweet.
* “Full text” is the actual text content of the tweet (all URLs in the tweet are expanded from their t.co shortened forms).
* “Media file 1–4” are the filenames of the different media files attached to the tweet, if applicable. These are in the form of the tweet ID followed by a dash and an alphanumeric identifier (which will be wrong if what’s attached to the tweet is a video, but the link in the tweet text will include “video_thumb“ in the URL).

The Twitter archive does not give us tweets in chronological order, so you will have to sort them yourself. To do this, press Ctrl+A, then select “Data” → “Sort...”. Ensure “Range contains column labels” is checked under the “Options” tab, choose the “Date” column for “Sort Key 1” under the main “Sort Criteria” tab, and click “OK”.

It will be easier to read the data as you scroll down the spreadsheet if you “freeze” the first row of column labels so they are always visible. To do this, click on cell A2, then select “View” → “Freeze Rows and Columns”. You can also make the labels easier to read in general by selecting the first row (e.g. by clicking its header) and then bolding and centring the text.

To start marking tweets for deletion as you go through the spreadsheet, create a new column by right‐clicking a column header and choosing “Insert Column Before/After”. (I put mine before the “Full text” column and labelled it with a 🗑︎ “Wastebasket” emoji.) If you create a column and it’s too wide or short, you can fill in the label in the first row, right‐click the header, and choose “Optimal width...” to automatically resize it. You can use anything you like to mark tweets for deletion in this column — only blank cells will mean to leave it alone. You can even use different letters or symbols to mark different deletion reasons if you want to keep it super organized.

You may want to open tweets in your web browser on occasion to see replies and to more easily view threads. To create hyperlinks in the spreadsheet for doing this, insert a new column by right‐clicking a column header and choosing “Insert Column Before/After”. Click on the cell in row 2 of this new column, and first make sure before entering a formula that the cell isn’t formatted as text by selecting select “Format” → “Cells...” and choosing category “Number” and format “General”. Then enter `=HYPERLINK(CONCAT("https://twitter.com/username/status/", A2))` into the cell (replacing “username” with your own username, and assuming the IDs column is still column A). Now copy that cell, select all the cells below it in that column, and paste (to fill the rest of that column with that formula). You can now Ctrl+click on these cells to open the tweets in your default web browser.

For tweets with attached media, you don’t need to open them in a web browser to view the media. Your Twitter archive includes lower‐resolution copies of all tweeted media in the “tweet_media” folder, so if you’re reviewing your tweets sorted by ID you can just flip through the images from that folder in tandem. (For full‐resolution copies of tweet media, see the “Notes on media preservation” section below.)

You may find it easier to read the like, retweet, and media counts if you make the zero values invisible. To do this, select those columns (hold Ctrl and click each column header), select “Format” → “Cells...”, and under “Format Code” enter `#`.

If there are columns you do not find useful (e.g. “Source URL”), you can hide them from view by right‐clicking the column header and selecting “Hide Columns”. (Be sure to un‐hide all columns before sorting data, as hidden columns may not be sorted properly.)

If the “Full text” column is too wide to fit on your screen at once, you can make the cells smaller horizontally and taller vertically. Select the column and choose “Format” → “Text” → “Wrap Text”. Then select everything (Ctrl+A), right‐click a row header, and select “Optimal Height”. 

If you’re noticing annoying dashed lines showing up between cells at random intervals, that’s LibreOffice Calc showing you the page break locations. You can disable this by unchecking “Tools” → “Options” → “LibreOffice Calc” → “View” → “Visual Aids” → “Page breaks”

### Conditional formatting
To make it easier to skim through the spreadsheet, you may find it helpful to highlight cells in different colours depending on their contents. For instance, you may want to highlight the full text of tweets that contain certain keywords to ensure you mark them for deletion. You can do this using conditional formatting. For this keyword highlighting example, select the “Full text” column, choose “Format” → “Conditional” → “Manage...”, then click “Add”.

If you only have a few keywords to look for, you can simply change “is equal to” to “contains”, and put some text between quotation marks in the text field. The style is how the cell matching the condition will be highlighted; there are some included defaults, or you can create your own by choosing “New Style...”, giving it a name, and using the “Font Effects” and “Background” tabs to change font and cell colours. Use the buttons below the conditions to add or delete conditions, or rearrange them (the upper conditions take priority for applying styles over lower ones when multiple conditions match one cell).

If you need greater control over your keyword searching, you can use a SEARCH formula with regular expressions. Before this will work, you must go to “Tools” → “Options” → “LibreOffice Calc” → “Calculate” and choose “Enable regular expressions in formulae”. Change your condition from “Cell value” to “Formula is”, and enter something like `SEARCH("keyword1|keyword2", L2)` into the text field, replacing `L2` with what appears before the colon under “Range”. Between the quotation marks, you can have multiple searches separated by `|` vertical bar characters. There are also some more tricks you can use:
* You can make terms only match if they are not preceded or followed by a letter or number by putting `(?<!\w)` or `(?!\w)` at the start and end of a search respectively; for example, `(?<!\w)bob` will match “**bob**” and “**bob**by” but not “discom**bob**ulate”
* A `?` question mark makes the preceding character optional; for example, `colou?r` matches both “color” and “colour”.
* Putting multiple characters in a pair of `[]` brackets will match one of those the characters at that position; for example, `defen[sc]e` matches both “defense” and “defence”.
* Putting multiple terms between `()` parentheses separated by `|` vertical bars will match one of those terms at that position; for instance, `(football|soccer) stadium` matches both “football stadium” and “soccer stadium”.
* To search for these characters `\^$.|?*+(){}` literally, put a `\` backslash before them. (Yes, this means searching for one backslash will use 2 in a row, like this `\\`.)

If all conditional formatting suddenly disappears and it’s not due to a syntax error in your search formatting, the formula has probably become too long (the limit seems to be around 1000 characters), and you’ll have to split up your search terms into multiple conditions.

Conditional formatting can also be used to more prominently highlight when you’ve marked a tweet row for deletion: add a new condition for the deletion column range, change the condition to “Formula is”, and enter `NOT(ISBLANK(K2))` into the text field, replacing `K2` with what appears before the colon under “Range”. You can also use conditional formatting to highlight like and retweet counts according to some formula (e.g. “Cell value” “is greater than” “0”), or colourize the type (e.g. “Cell value” “contains” `"🔁︎"`)

If you want alternating row colours, the easiest way to add this in LibreOffice Calc is also to use conditional formatting. For a range covering the whole sheet, use “Formula is” `ISEVEN(ROW())`; the chosen style will apply to every even row on the sheet now. You want this to be the last conditional format range you’ve defined, as the ranges defined first will take priority over ones defined later, so this would cover up any formatting on any even rows in ranges that you define later.

Having a lot of extremely complex conditional formatting will make your spreadsheet take longer to load when you open it, and may slow down some other operations as well (like sorting).

## Notes on media preservation
If you’re deleting any tweets with images, be aware that your Twitter archive will downscale large images into JPEGs no more than 1200 pixels wide/tall (and images seemingly posted before 2014‐11‐01 are downscaled further to 600 pixels wide/tall). It might have downscaled the videos as well. If you no longer have other copies of this media, you may want to pull max‐resolution media from Twitter to better preserve it.

I just copied hyperlinks for all the tweets with media I was deleting into JDownloader 2. This is also free open‐source software, but it’s admittedly not great — the GUI is very messy, and their main download page serves installers bundled with adware. However, it’s also very functional for a very wide variety of sites and content, so I often default to using it. [You can download adware‐free installers here](https://jdownloader.org/jdownloader2) (the top one in the list for each platform is probably the one you want).

There are more JDownloader 2 tutorials available online, but here’s a very basic walkthrough. Open the “LinkGrabber” tab and press Ctrl+L. In the window that pops up, you can paste links in the top textbox (it also pre‐populates with text from the clipboard, if there is any) and choose a folder to download to with the “Browse” button to the right of the second field. You then have to wait for it to load and parse the tweets to add the text and media from them to the download list. I would uncheck “Document File” on the right side to hide the text files in the list, as you don’t need them. Once all the links have been parsed (and so no more are appearing at the bottom of the list), you can click the blue ▶︎ play button in the top‐left to start downloading; this moves everything to the “Downloads” tab, where you can review progress.

Twitter will start restricting your IP address if you’re trying to download a whole lot of tweets and media. For media already in the “Downloads” tab, JDownloader 2 will wait out rate limits or let you retry downloads later, but parsing tweet links will silently fail if it can’t load the tweet in the first place as it doesn’t retry this. For this reason, I would only add ~100 tweet links at a time. You may also want to double‐check when you’re all done that you have as many media files as you’re expecting to; however, you may have a few tweets where Twitter has screwed up and lost/deleted one or more pieces of media from a tweet (but not the tweet itself), and you can’t do anything about that.

## Deleting tweets
We’re going to put the IDs of only the tweets you want to delete into a text file. First unhide all columns in your spreadsheet; in LibreOffice Calc, this can be done by pressing Ctrl+A to select everything, right‐clicking any column header, and selecting “Show Columns”. (This is to make sure all columns get sorted properly.) Then select “Data” → “Sort...”. Ensure “Range contains column labels” is checked under the “Options” tab, choose the deletion marker column for “Sort Key 1” under the main “Sort Criteria” tab, and click “OK”. Click the top cell in the deletion marker column and press Ctrl+↓ to jump to the last not‐blank cell in that column. Use the arrow keys to move horizontally to the IDs column, then press Ctrl+Shift+↑ and Shift+↓ to select the IDs of the tweets marked for deletion. Open Notepad and copy/paste these IDs into it, then save that file in the “data” folder as “ids_to_delete.txt”. To be clear, this text file should only have a list of numbers in it; the URL part, like “https⁠://twitter.com/username/status/”, must not be included.

Now we can actually start deleting tweets. Be aware that there are no upcoming prompts to make sure you want to start deleting tweets, so only proceed if you are certain you want to begin that process immediately.

Open “gfdtweetdeletionbot.py” in a plain text editor (like Notepad), and open the [Twitter developer portal dashboard](https://developer.twitter.com/en/portal/dashboard) in a web browser. On the dashboard, click the blue key to the right of your app’s name. To the right of “API Key and Secret”, click “Regenerate”. Copy the API key and secret and paste them into the text editor between the quotes that come after `api_key` and `api_key_secret` respectively at the top of the file. To the right of “Access Token and Secret”, click “Generate”, and copy and paste those keys between the quotes that come after `access_token` and `access_token_secret` respectively. (To be sure you copied these to the right spots, make sure they’re the same length as the  filler text of x’s and stuff that they’re replacing.) Save the file, and close the editor and browser tab.

In your file explorer, open the data folder, hold shift and right‐click on some empty space, and choose “Open Powershell window here” (like before). Enter `py gfdtweetdeletionbot.py`. The bot will now start deleting tweets, going through the IDs listed in “ids_to_delete.txt” in order. Periodically you’ll see messages pop up saying “Rate limit reached”, which is normal; it will wait out the rate limits Twitter imposes on API usage automatically (50 tweets every 15 minutes). If anything goes wrong, it should tell you and create one or more text files with any tweet IDs that gave it problems or otherwise didn’t get deleted; you can then use those text files to change the list of IDs in “ids_to_delete.txt” before trying to run the script again.

When you’re totally all done using the API, go back to the [Twitter developer portal dashboard](https://developer.twitter.com/en/portal/dashboard), click the blue key to the right of your app’s name, click “Regenerate” next to “API Key and Secret” and don’t save them anywhere, then click “Revoke” next to “Access Token and Secret”. This is for security purposes — now you cannot control your account with the API anymore until you generate new keys, but neither can anyone else.

# Support / legal
If you’re having difficulties, you can try contacting me on [Twitter](https://twitter.com/Gee_Eff_Dee) or [Mastodon](https://mastodon.social/@GFD), but I do not guarantee support and may be unable or unwilling to assist with individual cases.

If your issues are at all related to Twitter denying you access to API keys or otherwise taking action against your account, I cannot help you with that. I assume no legal liability for any outcomes of following any parts of this guide, and any advice comes with no warranty.

Issues/PRs on this repository should only be used for things that you can confirm need fixing, like broken script behaviour or outdated instructions (e.g. due to changes on Twitter’s end, or UI changes in LibreOffice Calc). Additional features and enhancements are not being considered. If you’re just going to be annoying and make a pull to replace all the tabbed indentation with spaces then you should know that you’re wrong and PEP8 is wrong.