from flask_cors import CORS
from flask import Flask,request,render_template,jsonify,url_for,redirect
import os
import requests
from bs4 import BeautifulSoup
import csv
from flask_compress import Compress
from flask_caching import Cache

app=Flask(__name__)
global folder
CORS(app)
compress=Compress(app)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

@app.route("/scapre-it")
@cache.cached(timeout=4800, key_prefix='scrape-cache')
def scape_it():
    URL="https://www.mohfw.gov.in"
    response=requests.get(URL).content
    soup=BeautifulSoup(response,'html.parser')
    table=soup.select("#cases > div > div > table")[0]
    headings=[row.get_text().strip() for row in table.thead.tr.find_all("th")]
    data=[[column.get_text().strip() for column in row.find_all("td")] for row in table.tbody.find_all("tr")]
    with open("state_cases.csv","w") as file:
        for heading in headings:
            file.write(f"{heading},")
        file.write("\n")
        for row  in data[0:-1]:
            for column in row:
                file.write(f"{column},")
            file.write("\n")
    print("File Written Success")
    return redirect(url_for('index'))

@app.route("/confirm-cases")
@cache.cached(timeout=4800, key_prefix='confirm_cases')
def confirm_cases():
    data=None
    with open("state_cases.csv","r") as file:
        read_csv=list(csv.reader(file,delimiter=","))
        total=read_csv[-1]
        states=read_csv[1:-1]
        data=[[row[1],int(row[2])+int(row[3])] for row in states]
    return jsonify([["Total",int(total[1].strip("#"))+int(total[2])]]+data)

@app.route("/confirm-cases-indian")
@cache.cached(timeout=4800, key_prefix='confirm-cases-indian')
def confirm_cases_indian():
    data=None
    with open("state_cases.csv","r") as file:
        read_csv=list(csv.reader(file,delimiter=","))
        heading=read_csv[0]
        total=read_csv[-1]
        states=read_csv[1:-1]
        data=[[row[1],row[2]] for row in states]
    return jsonify([["Total",total[1].strip("#")]]+data)

@app.route("/confirm-cases-foreign")
@cache.cached(timeout=4800, key_prefix='confirm-cases-foreign')
def confirm_cases_foreign():
    data=None
    with open("state_cases.csv","r") as file:
        read_csv=list(csv.reader(file,delimiter=","))
        heading=read_csv[0]
        total=read_csv[-1]
        states=read_csv[1:-1]
        data=[[row[1],row[3]] for row in states]
    return jsonify([["Total",total[2]]]+data)

@app.route("/confirm-cured")
@cache.cached(timeout=4800, key_prefix='confirm-cured')
def confirm_cured():
    data=None
    with open("state_cases.csv","r") as file:
        read_csv=list(csv.reader(file,delimiter=","))
        heading=read_csv[0]
        total=read_csv[-1]
        states=read_csv[1:-1]
        data=[[row[1],row[4]] for row in states]
    return jsonify([["Total",total[3]]]+data)

@app.route("/confirm-death")
@cache.cached(timeout=4800, key_prefix='confirm-death')
def confirm_death():
    data=None
    with open("state_cases.csv","r") as file:
        read_csv=list(csv.reader(file,delimiter=","))
        heading=read_csv[0]
        total=read_csv[-1]
        states=read_csv[1:-1]
        data=[[row[1],row[5]] for row in states]
    return jsonify([["Total",total[4]]]+data)

@app.route("/")
@cache.cached(timeout=31557600, key_prefix='scrape-cache')
def index():
    links=[("Total Confirm Cases",url_for('confirm_cases')),("Total Confirm Cases (Indians)",url_for('confirm_cases_indian')),
    ("Total Confirm Cases (Foreign)",url_for('confirm_cases_foreign')),
    ("Total Confirm Cured Cases",url_for('confirm_cured')),("Total Confirm Death Cases",url_for('confirm_death')),
    ("Get Latest Data",url_for('scape_it'))]
    return render_template('index.html',links=links)

if __name__=="__main__":
    app.run(debug=True)
