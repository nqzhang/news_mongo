from pymongo import MongoClient
import config
from bson import ObjectId
import time
import datetime
client = MongoClient(config.mongo['url'])[config.mongo['db_name']]
import os
import sys,gzip,re

class RotatingFile(object):
    def __init__(self, directory='', filename='foo', maxlines=50000):
        self.ii = 1
        self.lines = 0
        self.directory, self.filename  = directory, filename
        self.max_lines = maxlines
        self.fh = None
        self.open()
        self.urls = []

    def rotate(self):
        """Rotate the file, if necessary"""

        if self.lines>=self.max_lines:
            self.lines=0
            self.close()
            self.ii += 1
            self.open()

    def open(self):
        if not os.path.exists(os.path.join(os.getcwd(),self.directory, self.filename)):
            os.makedirs(os.path.join(os.getcwd(),self.directory, self.filename))
        self.fh = open(self.filename_template, 'w')

    def write(self, text=""):
        self.fh.write(text)
        self.lines += 1
        self.fh.flush()
        self.rotate()

    def close(self):
        self.fh.close()
        url = config.site_domain + '/' + self.directory + '/' + self.filename + '/' + "%0.2d.txt" % self.ii
        self.urls.append(url)
    @property
    def filename_template(self):
        return os.path.join(os.getcwd(),self.directory, self.filename,  "%0.2d.txt" % self.ii)




def genarate_sitemap(min_time,max_time):
    myfile = RotatingFile(directory="sitemap",filename=min_time.strftime('%Y_%m_%d'),maxlines=50000)
    for post in client.posts.find({ "post_date": {"$gte" : min_time, "$lt": max_time}}):
        t = config.site_domain + '/a/' + str(post['_id'])
        myfile.write('{}\n'.format(t))
    if myfile.lines == 0:
        myfile.close()
        os.remove(myfile.filename_template)
    if myfile.ii == 1:
        urls = [config.site_domain + '/' + myfile.directory + '/' + myfile.filename + '/' + "%0.2d.txt" % myfile.ii]
    else:
        urls = myfile.urls
    return urls
def generate_xml(filename, url_list):
  with open(filename,"w") as f:
    f.write("""<?xml version="1.0" encoding="utf-8"?>
<sitemapindex  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n""")
    for i in url_list:
      f.write("""<sitemap><loc>%s</loc></sitemap>\n"""%i)
    f.write("""</sitemapindex>""")


def append_xml(filename, url_list):
    with open(filename, 'r') as f:
        for each_line in f:
            d = re.findall('<loc>(.+)<\/loc>', each_line)
            url_list.extend(d)
        generate_xml(filename, set(url_list))
def main(days_ago):
    yesterday_min_time = datetime.datetime.combine(datetime.date.today() - datetime.timedelta(days=days_ago),
                                                   datetime.time.min)
    yesterday_max_time = datetime.datetime.combine(datetime.date.today() - datetime.timedelta(days=days_ago),
                                                   datetime.time.max)

    urls = genarate_sitemap(yesterday_min_time,yesterday_max_time)
    return urls
urls = main(2)
append_xml('sitemap/sitemap.xml',urls)
#generate_xml('sitemap/sitemap.xml',urls)