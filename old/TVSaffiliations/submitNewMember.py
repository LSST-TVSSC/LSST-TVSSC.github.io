import sys
import requests
from formid_config import *

url = 'https://docs.google.com/forms/d/e/' + formid + '/formResponse'

#for k in newmembers:
#    print (k, newmembers[k])
def submitMember(newmembers, myname):        
    user_agent = {'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
    r = None
    for k in newmembers.iterkeys():
    
        print (k, newmembers)
        form_data = {'emailAddress':myemail,
                     'entry.742675133':k,
                     'entry.907787863':newmembers[k]['email'],
                     'entry.1080841204':newmembers[k]['affiliation'],
                     'entry.549140788':myname,
                     'entry.2036761272':'Transients and Variable Stars'}
    
        print (form_data)
        r = requests.post(url, data=form_data)#, headers=user_agent)
        print (r)


if __name__ == '__main__':
    myname = sys.argv[1]
    f = open("application.txt").readlines()    
    newmembers = {}
    i = 0
    
    for i,l in enumerate(f):
        if len(l.split()) < 1:
            continue
        if "Name:" in l.split()[0]:
            name = " ".join(l.split()[1:]) 
            newmembers[name] = {}
        if "Email:" in l.split()[0]:
            newmembers[name]['email']=l.split()[1]
        if "Affiliation:" in l.split()[0]:
            newmembers[name]['affiliation'] = " ".join(l.split()[1:])

    submitMember(newmembers, myname)
