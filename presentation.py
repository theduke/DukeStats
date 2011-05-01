# url = https://www.facebook.com/dialog/oauth?client_id=70894852433&redirect_uri=http://www.facebook.com/connect/login_success.html&scope=ads_management,create_event,create_note,email,export_stream,friends_about_me,friends_activities,friends_birthday,friends_checkins,friends_education_history,friends_events,friends_groups,friends_hometown,friends_interests,friends_likes,friends_location,friends_notes,friends_online_presence,friends_photo_video_tags,friends_photos,friends_relationship_details,friends_relationships,friends_religion_politics,friends_status,friends_videos,friends_website,friends_work_history,manage_friendlists,manage_pages,offline_access,photo_upload,publish_checkins,publish_stream,read_friendlists,read_insights,read_mailbox,read_requests,read_stream,rsvp_event,share_item,sms,status_update,user_about_me,user_activities,user_birthday,user_checkins,user_education_history,user_events,user_groups,user_hometown,user_interests,user_likes,user_location,user_notes,user_online_presence,user_photo_video_tags,user_photos,user_relationship_details,user_relationships,user_religion_politics,user_status,user_videos,user_website,user_work_history,video_upload,xmpp_login 

import fbstats
from fbstats import Facebook
from fbstats import FBStats
import logging
import os
from fbstats import visual

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

v = visual.FBStatsVisualizer()

path = '/Users/theduke/Documents/MIS/'

# JENNY ##code = 'yzPSvOdSpP2bnvYFuZKa8jVMzGTLvAPuR1rUG3bmukQ.eyJpdiI6IjRNbEVEY0d6M09uaEswUTJHcXI2THcifQ.9-UqJJNmZpvZe5TlkyFv9vUqSXcblSnxwQ3iV3Q5KlbSV_frE0-nB66Q94QtC8ccz9yX5WULQKW5aL9bW26nfwnc5fOLL8BzpEGxgW4vcAdmSLfxDoZKLfnnL9u8ZZyE'
# sevim## 
code = 'Wuq6rCmg4cW5SaBE5BolMwmqSGPnghvkmWIgxGOd7lY.eyJpdiI6ImhYRURqVTU0Y1ZYYUM0U1NXMnhMMlEifQ.XuF3roi2dOmfk7hANe9UAZfIvUK5ZFw1yiUzThKASL6ZI0Gzn-ec3Z7DwpZtZV425fTvlEoh-aUbnt01JbRZ9vg0HGadDKD7aXVlKAaELCn9uCtl8Gj5846ZGqZMIWDn'

appId = '70894852433'
appSecret = '2746461daf8cba7e727c32cb4832183c'
redirect = 'http://dukestats.theduke.at/authorized'

fb = Facebook()
fb.initGraphByApp(appId, appSecret, code, redirect)


stats = FBStats()
stats.setFb(fb)

stats.getBaseData(True)

me = stats._data['me']

path += me['name'] + '/'

if not os.path.exists(path):
    os.mkdir(path)
    
html = '<html><body><h1>Facebook Statistics for %s</h1>' % me['name']

visualizer = fbstats.visual.FBStatsVisualizer()

chart = visualizer.buildSexChart(stats.getFriendsSex())
chart.download(path + 'sex.jpeg')
html += '<div class="chart-wrap"><img src="%s" /></div>' % chart.get_url()

chart = visualizer.buildRelatioshipStatusChart(stats.getFriendsRelationshipStatus())
chart.download(path + 'rel_status.jpeg')
html += '<div class="chart-wrap"><img src="%s" /></div>' % chart.get_url()

chart = visualizer.buildCategorizedAgeChart(stats.getAgesCategorized())
chart.download(path + 'ages_cat.jpeg')
html += '<div class="chart-wrap"><img src="%s" /></div>' % chart.get_url()

chart = visualizer.buildCategorizedPicCountChart(stats.getCategorizedPictureCounts())
chart.download(path + 'pic_count.jpeg')
html += '<div class="chart-wrap"><img src="%s" /></div>' % chart.get_url()
####visualizer.buildCategorizedTagCountChart(stats.getCategorizedTagCount()).download(path + 'tag_count.jpeg')

chart = visualizer.buildAgePhotoCountScatterChart(stats.getAgeAndPicCounts(), (0, 2000), (10, 60))
chart.download(path + 'pic_count_age_scatter.jpeg')
html += '<div class="chart-wrap"><img src="%s" /></div>' % chart.get_url()
chart = visualizer.buildAgePhotoCountScatterChart(stats.getAgeAndPicCounts(), (0, 1000), (20, 30))
chart.download(path + 'pic_count_age_scatter2.jpeg')
html += '<div class="chart-wrap"><img src="%s" /></div>' % chart.get_url()

chart = visualizer.buildTopRecordsPieChartFromSortedData(stats.getTagBuddies('me', True), 'Top 5 Tag Buddies')
chart.download(path + 'tag_buddies.jpeg')
html += '<div class="chart-wrap"><img src="%s" /></div>' % chart.get_url()
chart = visualizer.buildTopRecordsPieChartFromSortedData(stats.getWallPostersPostCount('me', True), 'Top 5 Posters on your Wall')
chart.download(path + 'wallposters.jpeg')
html += '<div class="chart-wrap"><img src="%s" /></div>' % chart.get_url()

chart = visualizer.buildTagBuddiesWallPosterScatterChart(stats.getTagBuddyWallPosterCountSet('me'))
chart.download(path + 'tagbuddy_wallpost_scatter.jpeg')
html += '<div class="chart-wrap"><img src="%s" /></div>' % chart.get_url()

chart = visualizer.buildTopRecordsPieChartFromSortedData(stats.getInboxData('me', True)['received'], 'Top Private Message Senders')
chart.download(path + 'msg_senders.jpeg')
html += '<div class="chart-wrap"><img src="%s" /></div>' % chart.get_url()

chart = visualizer.buildTopRecordsPieChartFromSortedData(stats.getInboxData('me', True)['sent'], 'Top Private Message Recipients')
chart.download(path + 'msg_recipients.jpeg')
html += '<div class="chart-wrap"><img src="%s" /></div>' % chart.get_url()

html += '</body></html>'

path += 'stats.html'
file = open(path, 'w')
file.write(html)
file.close()