# Scrapjango - A Web Crawling Utility
Crawl any site to get a list of links according to the desired URL type which can be pdf, html, images (png, jpg, jpeg, svg), jsp, rss, etc.
This project is developed in **Python** using [Django](https://www.djangoproject.com/) framework and [Scrapy](https://scrapy.org/) library.

>![Demo](https://github.com/shivamacs/scrapjango/blob/master/demo/demo.gif)

## Features
- Runs on localhost
- Local scraping database that runs on MySQL
- Add or remove source sites
- URL filters and crawler depth selection
- Stop the crawler anytime
- UI for querying the results
- Batch management of results for each source site

## Set Up

### Prequisites
- Python 3.7

### Installation
**Clone this repository**
```
~$ git clone https://github.com/shivamacs/scrapjango.git
~$ cd scrapjango
```
**Activate Virtual Environment**
```
~/scrapjango$ source scraper/bin/activate
(scraper) ~/scrapjango$
```
**Install Requirements**
```
(scraper) ~/scrapjango$ pip install -r requirements.txt
```
**Setup Database User**
- Create **mysql** superuser. ([Getting Started With MySQL](https://dev.mysql.com/doc/mysql-getting-started/en/))
- Assuming you have mysql superuser privileges, edit the scrapjango/dbconfig.json file:
```
    { 
        "host": "localhost",
        "user": "your-mysql-username", 
        "passwd": "your-mysql-password",
        "database": "scrapjango", 
        "auth_plugin": "mysql_native_password"
    }
```
- Replace "your-mysql-username" and "your-mysql-password" by your original mysql username and password (as strings).

**Configure Database**
```
(scraper) ~/scrapjango$ python setupdb.py
(scraper) ~/scrapjango$ python manage.py migrate 
```

## Run
```
(scraper) ~/scrapjango$ python manage.py runserver
```
Navigate to http://127.0.0.1:8000/ (localhost) and crawl websites!

## The Scrapyd Web Interface
- [Scrapyd](https://scrapyd.readthedocs.io/en/stable/) is an application (typically runs as a daemon) that listens to requests for spiders to run and spawns a process for each one.
- It comes with a minimal web interface (for monitoring running processes and accessing logs) which can be accessed at http://127.0.0.1:6800/
- Scrapyd API is used in this project for communication between the localhost ports **8000** and **6800**.
- Navigate to http://127.0.0.1:6800/jobs to get detailed information on the spider jobs.
