# import urllib.request
#
# print('Beginning file download with urllib2...')
#
# url = 'https://elibrary.trf.or.th/fullP/SRI61X0602/SRI61X0602_full.pdf'
# urllib.request.urlretrieve(url, '/Users/Kim/Downloads/SRI61X0602_full.pdf')

import os

local_path = "/Users/Kim/Documents/TestDownloadFiles/"

for root, dirs, files in os.walk(local_path, topdown=False):
   for name in files:
      print(os.path.join(root, name))
   print("==============================")
   for name in dirs:
      print(os.path.join(root, name))