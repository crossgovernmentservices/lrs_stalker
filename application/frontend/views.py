
from flask import (
    Blueprint,
    render_template,
    json,
    jsonify,
    url_for,
    redirect
)

import requests

frontend = Blueprint('frontend', __name__, template_folder='templates')

username = '8ef61e005f6f2a6df69d827d3a79fe3e3dadb978'
password = '28f6f89ea6c7bd58b002f84bbaf8b9e04e42bb11'
url = 'http://csl-lrs.ddns.net/api/v1/statements/aggregate?pipeline=%s'
statementProj = {
    "$project": {
      "statementId": "$statement.id",
      "actor": {
        "id": { "$ifNull": [ "$statement.actor.account.name", "$statement.actor.mbox" ] },
        "name": "$statement.actor.name",
        "mbox": "$mailto"
      },
      "verb": {
        "id": "$statement.verb.id",
        "name": { "$ifNull": [ "$statement.verb.display.en", "$statement.verb.display.en-US" ] }
      },
      "object": {
        "id": "$statement.object.id",
        "name": { "$ifNull": [ "$statement.object.definition.name.en", "$statement.object.definition.name.en-US" ] }
      },
      "when": "$statement.timestamp",
      "result": {
        "score": "$statement.result.score",
        "duration": "$statement.result.duration"
      },
      "activities": { 
          "$map": { 
            "input": "$statement.context.contextActivities.grouping",
            "as": "activity",
            "in": { 
              "id": "$$activity.id",
              "name": "$$activity.definition.name.en"
            } 
          }
        }
    }
}


@frontend.route('/stalk')
def index():
    payload = [{ }, statementProj]

    response = queryLRS(payload)
    jsonData = response.json()["result"]
    stalkJsonUrl = url_for('frontend.indexJson')

    return render_template('index.html', 
        statements=jsonData, 
        apiUrl=url % json.dumps(payload), 
        stalkJsonUrl=stalkJsonUrl, 
        username=username)


@frontend.route('/stalk-json')
def indexJson():
    payload = [{ }, statementProj]

    response = queryLRS(payload)
    return jsonify(response.json())

@frontend.route('/stalk/<statementId>')
def details(statementId):
    payload = [
      {   
        "$match": {
          "statement.id": statementId
        }
      },
      {
        "$project": {
          "_id": 0,
          "statement": 1
        }  
      }
    ]
    response = queryLRS(payload)
    return jsonify(response.json())


def queryLRS(payload):
    requestUrl=url % json.dumps(payload)
    jsonResponse = requests.get(requestUrl, auth=(username, password)) #params=payload)
    return jsonResponse;

