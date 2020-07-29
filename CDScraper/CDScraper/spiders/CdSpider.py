import scrapy
import os
import json
import mysql.connector
from datetime import datetime
from scrapy.conf import settings
from urllib.parse import quote

class SiteCrawler(scrapy.Spider):
    '''
    To crawl/scrape sites
    '''
    name="crawlsites"
    counter = 0
    extensions = ['in', 'com','php', 'htm', 'asp', 'aspx', 'axd', 'asx', 'asmx', 'ashx', 'css', 'cfm', 'xhtml', 'jsp', 'jspx', 'xml', 'rss', 'svg']
    
    config = json.load(open(os.path.join(os.path.dirname(__file__), '../../../dbconfig.json')))
    connection = mysql.connector.connect(host=config['host'], user=config["user"], passwd=config["passwd"], database=config["database"], auth_plugin=config["auth_plugin"])
    mycursor = connection.cursor()
    sqlFormula = 'INSERT IGNORE INTO spider (Created, Category, Url_id, Task, Format, Title, Url) VALUES (%s, %s, %s, %s, %s, %s, %s)'

    custom_settings = {
        'DEPTH_LIMIT': '5',
        'CONCURRENT_ITEMS':'100',
        'CONCURRENT_REQUESTS':'12',
        'CONCURRENT_REQUESTS_PER_DOMAIN':'4',
        'DEPTH_PRIORITY':1,
    }
    
    def __init__(self, *args, **kwargs):
        self.task = os.environ['SCRAPY_JOB']
        self.url = kwargs.get('url')
        self.reqformat = kwargs.get('reqformat')

    def start_requests(self):
        exam_url = [self.url]
        
        for url_holder in exam_url:
            urls = url_holder.split('~')
            url = urls[1]
            url_id=int(urls[0])
            category='general'

            if not url.endswith("/"):
                url = url.replace("http://",'').split("/")[0]+"/"

            if not url.startswith('http'):
                url =  'http://' + url
                
            yield scrapy.Request(url=url, callback=self.parse, meta={'root_url': url,'category':category,'url_id':url_id})
    
    def parse(self, response):
        entry = False
        print('counter: ', self.counter)
        self.counter = self.counter + 1 
        
        root_url =  response.meta.get('root_url')
        category =  response.meta.get('category')
        url_id = response.meta.get('url_id')
        
        for link in response.css('a'):
            
            item = {
                'text': link.css('::text').get(),
                'href': link.css('::attr(href)').get()
            }
            url = response.urljoin(item['href']).split('#')[0].replace('../','')
                    
            if url == '/' or ('<script>' in url) or ("<script type='text/javascript'>" in url) or ('mailto' in url) or ('javascript:void(0)' in url) or ('calander' in url) or ('calendar' in url) or ('booking' in url):
                continue

            if url.count('/') > 20:
                continue

            if self.reqformat in ['html', 'all']:
                for i in self.extensions:
                    if url.lower().endswith('.'+i):
                        entry = True
            
            if self.reqformat in url.lower() or self.reqformat == 'all' or entry == True:
                if self.reqformat == 'all':
                    for i in ['pdf', 'jpg', 'jpeg', 'png', 'html']:
                        if i in url.lower():
                            url_format = i
                            entry = False
                            break
                        else:
                            url_format = 'html'
                    
                if entry == True:
                    url_format = 'html'
                
                if self.reqformat != 'all' and entry == False:   
                    url_format = self.reqformat.lower()
                
                if item['text'] == None or item['text'] == ' ': item['text'] = "Untitled"
                elif item['text']: item['text'] = (" ").join(item['text'].replace('\n', '').split())

                self.mycursor.execute(self.sqlFormula, (datetime.today().strftime('%Y-%m-%d %H:%M:%S'), category, url_id, self.task, url_format, item['text'].strip(), url))
                self.connection.commit()    
    
            if url.endswith('.jpg') or ('pdf') in url.lower() or url.endswith('.pdf') or url.endswith('.jpeg') or url.endswith('.png') or url.endswith('.JPG') or url.endswith('.JPEG') or url.endswith('.PNG'):
                continue
            else:           
                yield response.follow(url, self.parse, meta={'root_url': root_url,'category':category,'url_id':url_id})
