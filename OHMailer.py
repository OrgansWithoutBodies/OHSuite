
from googleapiclient.discovery import build
from oauth2client import file, client, tools
from httplib2 import Http
from email import mime
from email.mime import text
import base64
import datetime

import logging
def authorizefn(auth):
    SCOPES = 'https://mail.google.com/'
 
    store=file.Storage('newtoken.json')#path of credentials json
    creds=store.get()
    if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(auth, SCOPES)
            creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service
#    print('done')
def makeattr():
    statsfns=Dock.Stats()
    statsfns.retrieveData()
    upto=datetime.datetime.now()-datetime.timedelta(7)#replace w since last read?
    
    
    x=statsfns.savexl(saveloc='test.xls',fn=statsfns.popdatefn(cat=True,ret='full',upto=upto))
#    if x:
##        print(':)')
#    else:
##        print(':(')
        
def loadfileasattach(filenm=None,toadd=None,fradd=None,subj=None):#should return something sendable thru mime
    if filenm is None:
        makeattr()
        filenm='test.xls'
    file=open(filenm,'rb')
    
    
    ament=mime.multipart.MIMEMultipart()
    ament['to'] = toadd
    ament['from'] = fradd
    ament['subject'] =subj
    msg = mime.base.MIMEBase('test','octet-base')
    msg.set_payload(file.read())
    
    file.close()
    
#    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filenm)
    ament.attach(msg)
#    ament.attach(msg)
   
    return {'raw':base64.urlsafe_b64encode(ament.as_bytes()).decode()}

def send(toadd,filenm=None,subj='test',auth=None):#fn where everything comes together
    #check if filename already exists somewhere here
    service=authorizefn(auth)
    fadd='OHWorker@gmail.com'
#    print(service)
    try:
         message=loadfileasattach(filenm,toadd,fadd,subj=subj)
#        print(att)
#         print(message)
         message = (service.users().messages().send(userId="me", body=message).execute())
         return 'scheduled email to '+toadd+' at '+' sent'
    except:
        raise
        return 'scheduled email to '+toadd+' failed at '+''
    
    
def run():#redundant? for testing atm 
   
    send('vsliupas@gmail.com','test.xls')