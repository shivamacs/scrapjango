from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
import os
import signal
import json
import psutil
import socket
import mysql.connector
from datetime import datetime
from .forms import SelectionForm
from scrapyd_api import ScrapydAPI
from django.views.decorators.csrf import csrf_exempt
from subprocess import Popen, PIPE
from ast import literal_eval as make_tuple
import pdb

scrapyd = ScrapydAPI('http://localhost:6800')
config = json.load(open(os.path.join(os.path.dirname(__file__), '../dbconfig.json')))
scrprocess = Popen("cd CDScraper; scrapyd", shell=True, stdin=PIPE, stdout=PIPE, close_fds=True, preexec_fn=os.setsid)

def wait_for_scrapyd_connection():
    print("Connecting to scrapyd service at http://127.0.0.1:6800/...")
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if(s.connect_ex(('localhost', 6800)) == 0):
                        print('Connected to scrapyd service.')
                        break
        
@csrf_exempt
def mainview(request):
    wait_for_scrapyd_connection();
 
    urlData = json.load(open(os.path.join(os.path.dirname(__file__), 'urlchoices.json')))
    urlchoices = ()

    if(len(urlData['urls']) != 0):
        urlchoices = tuple(make_tuple(f"('{url['id']}~{url['value']}', '{url['value']}')") 
                     for url in json.load(open(os.path.join(os.path.dirname(__file__), 'urlchoices.json')))['urls'])
  
    if request.method == 'POST':
        if request.POST.get("newurl"):
                newurl = request.POST.get("newurl")
                
                if newurl not in [url['value'] for url in urlData["urls"]]:
                        last_id = 0
                        if(len(urlData["urls"]) != 0):
                                last_id = urlData["urls"][len(urlData["urls"]) - 1]['id']
                        
                        urlData["urls"].append({"id": last_id + 1, "value": newurl})
                        
                        with open(os.path.join(os.path.dirname(__file__), 'urlchoices.json'), "w") as f:
                                json.dump(dict(urlData), f)

                urlchoices = tuple(make_tuple(f"('{url['id']}~{url['value']}', '{url['value']}')") 
                             for url in json.load(open(os.path.join(os.path.dirname(__file__), 'urlchoices.json')))['urls'])
                
                form = SelectionForm(urlchoices=urlchoices)
                return redirect('mappingsite:main')

        if request.POST.get('remove-url'):
                delurl = request.POST.get('remove-url')
                remid, remurl = delurl.split('~')

                urlData = json.load(open(os.path.join(os.path.dirname(__file__), 'urlchoices.json')))

                if(len(urlData["urls"]) != 0):
                        for url in urlData["urls"]:
                                if url['value'] == remurl:
                                        urlData['urls'].remove(url)
                                        break

                        with open(os.path.join(os.path.dirname(__file__), 'urlchoices.json'), "w") as f:
                                json.dump(dict(urlData), f)
 
                        uid = remid
                        connection = mysql.connector.connect(host=config['host'], user=config["user"], passwd=config["passwd"], database=config["database"], auth_plugin=config["auth_plugin"])
                        mycursor = connection.cursor()
                        mycursor.execute(f'DELETE FROM spider where Url_id={uid}')
                        connection.commit()

                        urlchoices = tuple(make_tuple(f"('{url['id']}~{url['value']}', '{url['value']}')") 
                                     for url in json.load(open(os.path.join(os.path.dirname(__file__), 'urlchoices.json')))['urls'])

                        form = SelectionForm(urlchoices=urlchoices)
                        return redirect('mappingsite:main')

        else:
                form = SelectionForm(request.POST, urlchoices=urlchoices)
                if form.is_valid():
                        data = form.cleaned_data
                        urldata = data.get('urlchoice')
                        urlid = urldata.split('~')[0]
                        fmt = data.get('formatchoice')
                        depth = data.get('depth')
                        settings = { 'DEPTH_LIMIT': depth }
                        task = scrapyd.schedule('default', 'crawlsites', reqformat=fmt, url=urldata, settings=settings)
                        status = 'started'
                        return HttpResponseRedirect(reverse('mappingsite:check', kwargs={'task':task, 'urlid':urlid, 'fmt': fmt}))
                
    else:
        form = SelectionForm(urlchoices=urlchoices)
        return render(request, 'mappingsite/inputform.html', {'form':form})

def checkview(request, **kwargs):
        task = kwargs.get('task')
        urlid = kwargs.get('urlid')
        fmt = kwargs.get('fmt')
        date = datetime.today().strftime("%Y-%-m-%d")

        if request.method == 'GET':
                try:
                        status = scrapyd.job_status('default', task)
                except:
                        status = 'finished'

        if request.method == 'POST':
                if request.POST.get('date') or request.POST.get('format') or request.POST.get('task'):
                        flag = False
                        date = request.POST.get('date')
                        fmt = request.POST.get('format')
                        task = request.POST.get('task')
                        connection = mysql.connector.connect(host=config['host'], user=config["user"], passwd=config["passwd"], database=config["database"], auth_plugin=config["auth_plugin"])
                        mycursor = connection.cursor(buffered=True)
                        
                        mycursor.execute(f'SELECT DISTINCT Task from spider where DATE(Created) = "{date}" and Url_id = {urlid}')                
                        if task and task in [i[0] for i in mycursor]:                     
                                flag = True
                                                
                        if flag == False:
                                mycursor.execute(f'SELECT DISTINCT Task from spider where DATE(Created) = "{date}" and Url_id = {urlid} LIMIT 1')
                                task = None                        
                                for i in mycursor:
	                                task = i[0]
	                                break
                                        
                else:
                        for proc in psutil.process_iter(attrs=["pid"]):
                                if proc.info["pid"] == scrprocess.pid:
                                        os.killpg(os.getpgid(scrprocess.pid), signal.SIGTERM)

                status = 'finished'
                        
        if status == 'finished':
                for proc in psutil.process_iter(attrs=["pid"]):
                        if proc.info["pid"] == scrprocess.pid:
                                os.killpg(os.getpgid(scrprocess.pid), signal.SIGTERM)

                return HttpResponseRedirect(reverse('mappingsite:display', kwargs={'task':task, 'urlid':urlid, 'fmt':fmt, 'date':date}))
        else:
                return render(request, 'mappingsite/load.html', {'task':task, 'urlid':urlid, 'fmt':fmt})

def displayview(request, **kwargs):
        connection = mysql.connector.connect(host=config['host'], user=config["user"], passwd=config["passwd"], database=config["database"], auth_plugin=config["auth_plugin"])
        mycursor = connection.cursor()
        task = kwargs.get('task')
        urlid = kwargs.get('urlid')
        fmt = kwargs.get('fmt')
        date = kwargs.get('date')
        tasks = []
        mycursor.execute(f'SELECT DISTINCT Task from spider where DATE(Created) = "{date}" and Url_id = "{urlid}"')
        for i in mycursor:
                tasks.append(i[0])

        if task not in tasks:
                mycursor.execute("INSERT IGNORE INTO spider VALUES(%s, %s, %s, %s, %s, %s, %s)", (date, "", urlid, task, "", "", ""))
                tasks.append(task)
		 
        if fmt == 'all':
                mycursor.execute(f'SELECT Created, Title, Url FROM spider where DATE(Created) = "{date}" and Url_id = {urlid} and Task = "{task}" and Category = "general" ORDER BY Created desc')
        else:
                mycursor.execute(f'SELECT Created, Title, Url FROM spider where DATE(Created) = "{date}" and Url_id = {urlid} and Format = "{fmt}" and Task = "{task}" and Category = "general"')
        return render(request, 'mappingsite/content.html', {'task':task, 'urlid':urlid, 'fmt':fmt, 'tasks':tasks, 'mycursor':mycursor, 'date':date})
