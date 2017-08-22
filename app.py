#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

import time

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    intent = req.get("result").get("metadata").get("intentName")
    
    if "hook" in inent:
   
        if "KUSC" in intent:
            return getKUSC(req)

        if "Time" in intent:
            return getTime(req)
        
        if "Weather" in intent:
            return getWeather(req)
    
    speech = "Doodad API got confused"
    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-weather-webhook-sample"
    }

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"

def getKUSC(req):
    speech = ""
    with urllib.request.urlopen("http://schedule.kusc.org/now/KUSC.json") as url:
        data = json.loads(url.read().decode())
        speech = data

    return {
        "speech": speech,
        "displayText": data,
        "source": "apiai-weather-webhook-sample"
    }

def getTime(req):
    result = req.get("result")
    action = result.get("action")
    os.environ['TZ'] = 'US/Pacific'
    time.tzset()
    cTime = time.strftime("%H:%M")
    parameters = result.get("parameters")
    gTime = parameters.get("time")
    if gTime is not None and gTime is not "":
        if cTime in gTime:
            speech = "Correct.  It is currently " + cTime + "."
        else:
            speech = "Current time is " + cTime + " which is not " + gTime
    else:
        speech = "Current time is " + cTime
    
    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-weather-webhook-sample"
    }

def getWeather(req):
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res

def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
