from flask import Flask, request, render_template
from os import chdir, getcwd
from os.path import realpath, dirname, join
import json

import master

# Set current path as working dir
chdir(dirname(realpath(__file__)))

# Init Flask app
app = Flask(__name__, template_folder=join(getcwd(),"templates"), static_folder=join(getcwd(),"static"))

# Home
@app.route("/")
def home():
    return render_template('home.html')

# Switch on mininet network
@app.route("/networkON")
def networkON():
    master.exec_command("start")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

# Switch off mininet network
@app.route("/networkOFF")
def networkOFF():
    master.exec_command("stop")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

# Get network map
@app.route("/mapNetworkScenarios")
def mapNetworkScenarios():
    result = master.exec_command("mapNetworkScenarios")
    return json.dumps(result), 200, {'ContentType':'application/json'}

# Check if the mininet network is online
@app.route("/ping")
def ping():
    result = master.exec_command("ping")
    return result, 200, {'ContentType':'application/json'}

# Change scenario
@app.route("/changeScenario",methods=['POST'])
def changeScenario():
    master.exec_command(f"changeScenario={request.form['scenarioId']}")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

# Run server
app.run()
