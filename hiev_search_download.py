'''
Python script to perform a HIEv API filter search and then download of the most recent FACE security camera image

Author: Gerard Devine
'''

import os
import json
import urllib2
from datetime import date, datetime, timedelta
import time


# --Set up global values
request_url = 'https://hiev.uws.edu.au/data_files/api_search'
api_token = 'Insert API token'
filename = 'FACE_R1_P0037_SECURPHOT-TERNsnapshot'


# --Open log file for writing and append date/time stamp into file for a new entry
logfile = 'log.txt'
log = open(os.path.join(os.path.dirname(__file__), logfile), 'a')
log.write('\n----------------------------------------------- \n')
log.write('------------  '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'  ------------ \n')
log.write('----------------------------------------------- \n')


# --Begin a log entry for this download
log.write(' -For files being downloaded')

# --Set up the http request
request_headers = {'Content-Type' : 'application/json; charset=UTF-8', 'X-Accept': 'application/json'}
upload_from_date = str(date.today() - timedelta(days=1))
upload_to_date = str(date.today()- timedelta(days=0))
request_data = json.dumps({'auth_token': api_token, 'upload_from_date': upload_from_date, 'upload_to_date': upload_to_date,'filename': filename})

# --Handle the returned response from the HIEv server
request  = urllib2.Request(request_url, request_data, request_headers)
response = urllib2.urlopen(request)
js = json.load(response)
# Grab the latest - in those cases where there are multiple resukts returned
js_latest = (sorted(js, key=lambda k: k['updated_at'], reverse=True))[0] 

# --If there are files to be downloaded, then set up a directory to hold them (if not existing)
if len(js_latest):
    dest_dir = os.path.join(os.path.join(os.path.dirname(__file__), 'data'))
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    # --For each element returned pass the url to the download API and download
    for item in js_latest:
        download_url = item['url']+'?'+'auth_token=%s' %api_token
        request = urllib2.Request(download_url)
        f = urllib2.urlopen(request)

        # --Write the file and close it
        with open(os.path.join(dest_dir, item['filename']), 'w') as local_file:
            local_file.write(f.read())
        local_file.close()

    log.write('  Total files downloaded = %s \n' %len(js_latest))
else:
    log.write('  No files matched the search params \n')


# --Close log file
log.close()
