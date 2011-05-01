import facebook
import urllib2
import sys, os
import pickle
import logging
import datetime
import math
import operator

class Facebook(object):
    
    def __init__(self):
        
        # either: token, app, login
        self._authMethod = None
        
        self._appId = None
        self._appSecret = None
        self._authcode = None
        
        self._apiToken = None
        
        self._username = None
        self._password = None
        
        self.graph = None
        
    def initGraphByToken(self, token):
        self._authMethod = 'token'
        self.graph = facebook.GraphAPI(token)
    
    def initGraphByApp(self, id, secret, code, redirect='http://www.facebook.com/connect/login_success.html'):
        self._authMethod = 'app'
        
        self._appId = id
        self._appSecret = secret
        self._appRedirectUrl = redirect
        self._authcode = code
        
        token = self.fetchTokenForApp()
        self.graph = facebook.GraphAPI(token)
        
    def fetchTokenForApp(self):
        url =  'https://graph.facebook.com/oauth/access_token?client_id=' + self._appId
        url += '&redirect_uri=' + self._appRedirectUrl
        url += '&client_secret=' + self._appSecret
        url += '&code=' + self._authcode
        
        logging.debug('Trying to get auth_token with url: ' + url)
        
        response = urllib2.urlopen(url)
        data = response.read()
        data = data.replace('access_token=', '')
        
        logging.info('Fetched token %s', data)
        
        return data
        
        
    def getFriends(self, id):
        friends = self.graph.get_connections(id, 'friends', limit=5000)['data']
        return friends
    
    def getFriendIds(self, id):
        friends = self.getFriends(id)

        ids = [item['id'] for item in friends]
        return ids
    
    def getFriendData(self):
        data = self.graph.get_objects(self.getFriendIds('me'))
        
        friendCount = len(data)
        
        i = 1
        
        for id, friend in data.items():
            logging.debug('Getting additional data for user %s (%s of %s', id, str(i), str(friendCount))
            
            friend['albums'] = self.getAllAlbums(id)
            #friend['tags'] = self.getAllTags(id)
            
            i += 1
        
        return data
    
    def getAllAlbums(self, userId):
        data = self.graph.get_connections(userId, 'albums')
        albums = list()
        
        while (True):
            albums.extend(data['data'])
            
            if 'paging' in data and 'next' in data['paging']:
                if data['paging']['next'].find('until=0') != -1:
                    logging.warning('Not following the pager link %s because until=0 was found', data['paging']['next'])
                    break
                
                data = self.graph.request_url(data['paging']['next'])
            else:
                break
        
        return albums
    
    def getAllTags(self, userId, idsOnly=False):
        data = self.graph.get_connections(userId, 'photos')
        tags = list()
        
        while (True):
            for item in data['data']:
                if idsOnly:
                    tags.append(item['id'])
                else:
                    tags.append(item)
            
            if 'paging' in data and 'next' in data['paging']:
                if data['paging']['next'].find('until=0') != -1: 
                    logging.warning('Not following the pager link %s because until=0 was found', data['paging']['next'])
                    break
                
                data = self.graph.request_url(data['paging']['next'])
            else:
                break
        
        return tags
    
    def getWallPosts(self, userId):
        data = self.graph.get_connections(userId, 'feed')
        posts = list()
        
        while (True):
            for item in data['data']:
                posts.append(item)
            
            if 'paging' in data and 'next' in data['paging']:
                if data['paging']['next'].find('until=0') != -1:
                    logging.warning('Not following the pager link %s because until=0 was found', data['paging']['next'])
                    break
                
                data = self.graph.request_url(data['paging']['next'])
            else:
                break
        
        return posts
    
    def getInbox(self, userId):
        data = self.graph.get_connections(userId, 'inbox', limit=1000)
        posts = list()
        
        while (True):
            for item in data['data']: 
                posts.append(item)
                
            if 'paging' in data and 'next' in data['paging']:
                data = self.graph.request_url(data['paging']['next'])
            else:
                break
        
        return posts
    
    def getCompleteInboxMessage(self, message):
        '''Fetch additional paged comments for this message
        THIS DOES NOT WORK AT THE MOMENT SINCE THE API MESSES UP THE PAGER LINKS
        NOT SUPPORTED YET?
        
        CODE UNFINISHED!!
        '''
        
        if not ('comments' in message and 'paging' in message['comments'] and 'next' in message['comments']['paging']): return message
        
        data = self.graph.request_url(message['comments']['paging']['next'])
        
        while (True):
            for item in data['data']: 
                message['comments']['data'].append(item)
                
            if 'paging' in data and 'next' in data['paging']:
                data = self.graph.request_url(message['comments']['paging']['next'])
            else:
                break
            
        return message
        
    
class FBStats(object):
    
    def __init__(self):
        self.fb = None
        
        # data cache
        self._data = dict()
    
    def setFb(self, fb):
        self.fb = fb
    
    def getBaseData(self, useCache=False):
        self._data['me'] = self.fb.graph.get_object('me')
        
        userId = self._data['me']['id']
        cachePath = os.path.expanduser('~') + '/.fbstats'
        if not os.path.exists(cachePath): os.makedirs(cachePath)
        
        cacheFile = cachePath + '/' + userId
        
        if useCache and os.path.exists(cacheFile):
            self._data = pickle.load(open(cacheFile))
            if self._data: return
        
        
        self._data['me']['tags'] = self.fb.getAllTags('me')
        self._data['me']['wallposts'] = self.fb.getWallPosts('me')
        self._data['me']['inbox'] = self.fb.getInbox('me')
        
        self._data['friends'] = self.fb.getFriendData()
        
        if useCache:
            pickle.dump(self._data, open(cacheFile, 'w'))
        
    def getFriendsSex(self):
        male = 0
        female = 0
        unknown = 0
        
        for id, friend in self._data['friends'].items():
            if not 'gender' in friend: unknown += 1
            elif friend['gender'] == 'male': male += 1
            elif friend['gender'] == 'female': female += 1
            
        return {'male': male, 'female': female}
    
    def getFriendsRelationshipStatus(self):
        data = {'not given': 0}

        for id, friend in self._data['friends'].items():
            if 'relationship_status' in friend: 
                status = friend['relationship_status']
                if not status in data: data[status] = 0
                
                data[status] += 1
            else:
                data['not given'] += 1
            
        return data
    
    def getBirthday(self, user):
        if not 'birthday' in user: return None
            
        l = len(user['birthday'])
        
        # if no year set set year to 1
        if l == 5: user['birthday'] += '/0001'
        
        bd = datetime.datetime.strptime(user['birthday'], '%m/%d/%Y')
        
        return bd
    
    def getAge(self, user):
        bd = self.getBirthday(user)
        if not bd or bd.year == 1: return None
        
        return datetime.datetime.now().year - bd.year
    
    def getBirthdays(self):
        birthdays = list()
        
        for id, friend in self._data['friends'].items():
            bd = self.getBirthday(friend)
            
            if bd: birthdays.append(bd)
            
        return birthdays
    
    def getAges(self):
        bds = self.getBirthdays()
        ages = list()
        
        now = datetime.datetime.now()
        
        for bd in bds:
            # skip bds that have no year set
            if bd.year == 1: continue
            ages.append(now.year - bd.year)
            
        return ages
    
    def getAgesCategorized(self):
        ages = self.getAges()
        
        brackets = [('0-10', 10), ('11-14', 14), ('15-17', 17), ('18-22', 22), ('23-27', 27), ('28-35', 35), ('36-45', 45), ('46-60', 60), ('60-x', 99999)]
        data = self.categorizeAndCount(ages, brackets)

        return data
    
    def getPictureCount(self, user):
        if not 'albums' in user: return 0
        
        count = 0
        for album in user['albums']:
            if not 'count' in album: continue
            
            count += album['count']
            
        return count
    
    def getPictureCounts(self):
        counts = list()
        
        for user in self._data['friends'].values():
            counts.append(self.getPictureCount(user))
            
        return counts
    
    def getCategorizedPictureCounts(self):
        counts = self.getPictureCounts()
        
        brackets = [('0-20', 20), ('21-60', 60), ('61-150', 150), ('151-500', 500), ('501-1000', 1000), ('1001-2500', 2500), ('2500-5000', 5000), ('5000-x', 9999999999999)]
        data = self.categorizeAndCount(counts, brackets)
        
        return data
    
    def getAgeAndPicCounts(self):
        data = list()
        
        for friend in self._data['friends'].values():
            age = self.getAge(friend)
            picCount = self.getPictureCount(friend)
            
            data.append({'age': age, 'count': picCount})
            
        return data
    
    def getAgeAndTagCount(self):
        data = list()
        
        for friend in self._data['friends'].values():
            if 'tags' in friend:
                age = self.getAge(friend)
                tagCount = len(friend['tags'])
                
                
                if age: data.append({'age': age, 'count': tagCount})
            
        return data
    
    def getCategorizedTagCount(self):
        tags = list()
        
        for user in self._data['friends']:
            if 'tags' in user:
                tags.append(len(user['tags']))
                
        brackets = {'0-10': 10, '11-20': 20, '21-60': 60, '61-100': 100, '101-150': 150, '151-300': 300, '301-500': 500, '501-x': 999999999999}
        data = self.categorizeAndCount(tags, brackets)
        
        return data
    
    def getTagBuddies(self, id, getSorted=False):
        '''Get list of people who appear most often together with you in photos'''
        
        data = dict()
        
        if id != 'me':
            me = self.fb.graph.get_object(id)
            pictures = self.fb.getAllTags(id)
        else:
            me = self._data['me']
            pictures = me['tags']
        
        for pic in pictures:
            if 'tags' in pic:
                for tag in pic['tags']['data']:
                    if not tag['name'] in data: data[tag['name']] = 0
                    
                    data[tag['name']] += 1
                    
        del data[me['name']]
         
        if getSorted:
            data = sorted(data.iteritems(), key=operator.itemgetter(1), reverse=True)
         
        return data
    
    def getWallPostersPostCount(self, userId, getSorted=False):
        posters = dict()
        
        if userId != 'me':
            me = self.fb.graph.get_object(userId)
            wallPosts = self.fb.getWallPosts(userId)
        else:
            me = self._data['me']
            wallPosts = me['wallposts']
        
        for post in wallPosts:
            name = post['from']['name']
            
            #skip your own posts
            if name == me['name']: continue
            
            if not name in posters: posters[name] = 0
            posters[name] += 1
        
        
        if getSorted:
            posters = sorted(posters.iteritems(), key=operator.itemgetter(1), reverse=True)
            
        return posters
    
    def getInboxData(self, userId, getSorted=False):
        ''' Return a per person counter for sent and received private messages'''
        
        data = {'sent': dict(), 'received': dict()}
        
        if True:
            me = self.fb.graph.get_object(userId)
            inbox = self.fb.getInbox(userId)
        else:
            me = self._data['me']
            inbox = me['inbox']
        
        userId = me['id']
        
        for message in inbox:
            msgData = self.getMessageInfo(message, userId)
            
            for type, name in msgData:
                if not name in data[type]: data[type][name] = 0
                data[type][name] += 1
        
        if getSorted:
            data['sent'] = sorted(data['sent'].iteritems(), key=operator.itemgetter(1), reverse=True)
            data['received'] = sorted(data['received'].iteritems(), key=operator.itemgetter(1), reverse=True)
            
        return data
                        
    def getMessageInfo(self, message, userId):
        data = list()
        
        isSender = False
        isRecipient = False
        otherPartyNames = list()
        
        if not message['from']: return data
        
        senderId = message['from']['id']
        
        if senderId == userId:
            isSender = True
            
            for recipient in message['to']['data']:
                if not recipient:
                    logging.warning('Empty recipient %s', str(recipient))
                    continue
                
                if recipient['id'] == userId: continue
                
                data.append(('sent', recipient['name']))
                
                otherPartyNames.append(recipient['name'])
        else:
            for recipient in message['to']['data']:
                if not recipient: 
                    logging.warning('Empty recipient %s', str(recipient))
                    continue
                
                if recipient['id'] == userId:
                    senderName = message['from']['name']
                    
                    data.append(('received', senderName))
                    
                    otherPartyNames.append(senderName)
                    
                    isRecipient = True
                    break
        
        if (isSender or isRecipient) and 'comments' in message:
            data.extend(self.getMessageCommentsInfo(message['comments']['data'], userId, otherPartyNames))
        
        return data
    
    def getMessageCommentsInfo(self, comments, userId, otherPartyNames):
        data = list()
        
        for comment in comments:
            if not comment or not comment['from']:
                logging.warning('Faulty comment: %s', repr(comment))
                continue
            
            if comment['from']['id'] == userId:
                for name in otherPartyNames:
                    data.append(('sent', name))
            else:
                for name in otherPartyNames:
                    data.append(('received', name))
                    
        return data
    
    def getMessageSenderRecipientScatterData(self, userId):
        data = list()
        inboxData = self.getInboxData(userId)
        
        for name, count in inboxData['sent'].items():
            if not name in inboxData['received']: continue
            
            data.append({'y': count, 'x': inboxData['received'][name]})
            
        return data
    
    def getTagBuddyWallPosterCountSet(self, userId):
        data = dict()
        
        tagBuddies = self.getTagBuddies(userId)
        wallPosters = self.getWallPostersPostCount(userId)
        
        for name, tags in tagBuddies.items():
            posts = wallPosters[name] if name in wallPosters else 0
            data[name] = [tags, posts]
            
        for name, posts in wallPosters.items():
            if name in data: continue
            data[name] = [0, posts]
            
        return data
        
    
    def categorize(self, items, brackets):
        data = dict()
        
        for name, boundry in brackets: data[name] = list()
        
        for item in items:
            bracketName = self.determineBracket(item, brackets)
            if bracketName: data[bracketName].append(item)
            
            continue
            
        return data
    
    def determineBracket(self, value, brackets):
        for bracketName, upperBoundry in brackets:
            if value <= upperBoundry:
                return bracketName
            
        return None
        
    
    def categorizeAndCount(self, items, brackets):
        data = self.categorize(items, brackets)
        countData = dict()
        
        for key, value in data.items():
            countData[key] = len(value)
            
        return countData
    
    def mean(self, nums):
        if len(nums):
            return float( sum(nums) / len(nums))
        else:
            return 0.0
        
    def median(self, nums):
        return nums[len(nums) / 2]
        
        