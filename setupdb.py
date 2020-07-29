import os
import json
import mysql.connector
import tabulate

config = json.load(open(os.path.join(os.path.dirname(__file__), 'dbconfig.json')))
connection = mysql.connector.connect(host=config['host'], user=config["user"], passwd=config["passwd"], auth_plugin=config["auth_plugin"])
mycursor = connection.cursor(buffered=True)

mycursor.execute('CREATE DATABASE IF NOT EXISTS scrapjango');
mycursor.execute('USE scrapjango');
mycursor.execute('CREATE TABLE IF NOT EXISTS spider (Created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, Category VARCHAR(64), Url_Id INT, Task VARCHAR(128), Format VARCHAR(64), Title VARCHAR(255), Url VARCHAR(512) UNIQUE)')
mycursor.execute('DESCRIBE spider')
table = mycursor.fetchall()

print(tabulate.tabulate(table))

connection.commit()