
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

userData = [
  { "id": "admin", "username": "admin", "fullname": "Ian Learnalot", "email": "ilearnalot@gmail.com" },
  { "id": "test1", "username": "test1", "fullname": "Andrew Withirsty", "email": "awit@gmail.com" }
]

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

@frontend.route('/users')
def users():
  return render_template('users.html', users= userData)


@frontend.route('/users/<username>/history')
def userHistory(username):
    payload = [{   
        "$match": {
          "statement.actor.name": username
        }
      }, 
      statementProj,
      {
        "$sort": { "when": -1 }
      }
    ]

    response = queryLRS(payload)

    jsonData = response.json()["result"]
    user = [usr for usr in userData if usr["username"] == username][0]
    return render_template('user_history.html',
        statements= jsonData, 
        user= user)

@frontend.route('/users/<username>/history/<statementId>')
def details(username, statementId):
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

