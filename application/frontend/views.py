
from flask import (
    Blueprint,
    render_template,
    json,
    jsonify,
    url_for,
    redirect,
    current_app as app
)


# from application.config import Config
import requests

frontend = Blueprint('frontend', __name__, template_folder='templates')

userData = [
  { "id": "admin", "username": "admin", "fullname": "Ian Learnalot", "email": "ianlearnalot@learninglocker.net" }
  # { "id": "test1", "username": "test1", "fullname": "Andrew Withirsty", "email": "awit@gmail.com" }
]

userStatementProj = {
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
    user = [usr for usr in userData if usr["username"] == username][0]
  
    payload = [{   
        "$match": {
          "statement.actor.mbox": "mailto:%s" % user["email"]
        }
      }, 
      userStatementProj,
      {
        "$sort": { "when": -1 }
      }
    ]

    response = queryLRS(payload)

    jsonData = response.json()["result"]
    return render_template('user_history.html', statements= jsonData, user= user)


@frontend.route('/users/<username>/history/<statementId>')
def details(username, statementId):
  user = [usr for usr in userData if usr["username"] == username][0]
  
  payload = [
    {   
      "$match": {
        "statement.actor.mbox": "mailto:%s" % user["email"],
        "statement.id": statementId
      }
    },userStatementProj
  ]
  response = queryLRS(payload)
  recordJsonData = response.json()["result"][0]

  payload_details= [
    {
       "$match": {
        "statement.object.actor.mbox": "mailto:%s" % user["email"],
        "statement.context.contextActivities.grouping": { 
          "$elemMatch": { 
            "id": "%s" % recordJsonData["object"]["id"]
          } 
        }    
      }
    }
  ]

  responseDetails = queryLRS(payload_details)
  detailsJsonData = responseDetails.json()["result"]

  return render_template('record.html', record= recordJsonData, details= detailsJsonData, user= user)


@frontend.route('/dev-corner')
def defCorner():
  return render_template('dev_corner.html')



def queryLRS(payload):
  username = app.config["LRS_USER"]
  password = app.config["LRS_PASS"]
  url = '%s/api/v1/statements/aggregate?pipeline=%s'

  requestUrl=url % (app.config["LRS_URL"], json.dumps(payload))
  jsonResponse = requests.get(requestUrl, auth=(username, password), verify=False) #params=payload)
  return jsonResponse;

