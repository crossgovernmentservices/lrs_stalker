
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

username = '53b4c63ea25c4d00d5bb5fc6168e2cfce1f8fc04'
password = '44d9a94cf85d3d2535e91a45817f58c1021eff9a'
url = 'https://lrs.cstools.co.uk/api/v1/statements/aggregate?pipeline=%s'

userData = [
  { "id": "admin", "username": "admin", "fullname": "Ian Learnalot", "email": "ilearnalot@gmail.com" }
  # { "id": "test1", "username": "test1", "fullname": "Andrew Withirsty", "email": "awit@gmail.com" }
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
    return render_template('user_history.html', statements= jsonData, user= user)

@frontend.route('/users/<username>/history/<statementId>')
def details(username, statementId):
  payload = [
    {   
      "$match": {
        "statement.actor.name": username,
        "statement.id": statementId
      }
    },statementProj
  ]
  response = queryLRS(payload)
  jsonData = response.json()["result"][0]
  user = [usr for usr in userData if usr["username"] == username][0]
  return render_template('record.html', record= jsonData, user= user)


def queryLRS(payload):
    requestUrl=url % json.dumps(payload)
    jsonResponse = requests.get(requestUrl, auth=(username, password), verify=False) #params=payload)
    return jsonResponse;

