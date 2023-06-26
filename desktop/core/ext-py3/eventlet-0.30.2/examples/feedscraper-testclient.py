from eventlet.green.urllib.request import urlopen

big_list_of_feeds = """
http://blog.eventlet.net/feed/
http://rss.slashdot.org/Slashdot/slashdot
http://feeds.boingboing.net/boingboing/iBag
http://feeds.feedburner.com/RockPaperShotgun
http://feeds.penny-arcade.com/pa-mainsite
http://achewood.com/rss.php
http://raysmuckles.blogspot.com/atom.xml
http://rbeef.blogspot.com/atom.xml
http://journeyintoreason.blogspot.com/atom.xml
http://orezscu.blogspot.com/atom.xml
http://feeds2.feedburner.com/AskMetafilter
http://feeds2.feedburner.com/Metafilter
http://stackoverflow.com/feeds
http://feeds.feedburner.com/codinghorror
http://www.tbray.org/ongoing/ongoing.atom
http://www.zeldman.com/feed/
http://ln.hixie.ch/rss/html
"""

url = 'http://localhost:9010/'
result = urlopen(url, big_list_of_feeds)
print(result.read())
