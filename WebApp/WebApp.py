from flask import Flask, jsonify, request, render_template
import uuid
from os import chdir, getcwd, system
from os.path import realpath, isfile, dirname, join
import json
from datetime import datetime
from time import time, sleep
from threading import Lock
from enum import Enum
import subprocess
import atexit

import master

chdir(dirname(realpath(__file__)))

app = Flask(__name__, template_folder=join(getcwd(),"templates"), static_folder=join(getcwd(),"static"))

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/networkON")
def networkON():
    master.exec_command("start")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route("/networkOFF")
def networkOFF():
    master.exec_command("stop")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/mapNetworkScenarios")
def mapNetworkScenarios():
    result = master.exec_command("mapNetworkScenarios")
    return json.dumps(result), 200, {'ContentType':'application/json'}

@app.route("/ping")
def ping():
    result = master.exec_command("ping")
    return result, 200, {'ContentType':'application/json'}

@app.route("/changeScenario",methods=['POST'])
def changeScenario():
    master.exec_command(f"changeScenario={request.form['scenarioId']}")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

app.run()


