
import presentation
import logging
import json

def removeToken(token, filePath):
    file = open(filePath)
    tokens = file.readlines()
    file.close()
    
    for t in tokens:
        if t.rstrip() == token:
            tokens.remove(token)
            break
        
    file = open(filePath, 'w')
    file.writelines(tokens)

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

# Set constants 
# ------------------

path = '/var/www/dukestats/files/stats/'

appId = 'x'
appSecret = 'x'
redirect = 'x'

tokenFilePath = 'x'
statsFilePath = 'x'

emailUser = 'x'
emailPassword = 'x'

infoMail = 'x'

# Read tokens and try to build statistics

file = open(tokenFilePath)
lines = file.readlines()
file.close()

finished = list()

for token in lines:
    if not len(token) > 10: continue
    
    token = token.rstrip()
    
    me = None
    
    try:
        me = presentation.buildUserStats(appId, appSecret, redirect, token)
    except Exception as e:
        logging.error('An error ocurred while processing token %s: %s', token, repr(e))
        continue
        
    logging.info('Finished building stats for %s', me['name'])
    
    try:
        content = 'Your statistics have been created. Go check them out at http://dukestats.theduke.at/files/stats/%s/stats.html' % presentation.removeNonAscii(me['name']).replace(' ', '').lower()
        
        presentation.sendMail('DukeStats Statistics created', content, emailUser, emailPassword, me['email'])
        presentation.sendMail('DukeStats Created', 'user %s, token %s' % (me['name'], token), emailUser, emailPassword, infoMail)
    except Exception as e:
        logging.error('Could not send email notifications to user  %s: ', me['name'], repr(e))
    
    # save token to stats file and remove from queue
    
    data = {'username': presentation.removeNonAscii(me['name']), 'token': token}
    
    file = open(statsFilePath, 'a')
    file.write(json.dumps(data) + "\n")
    file.close()
    
    

    