import requests
import json
from logger import log

class Pushbullet(object):
  api_key = ""
  api_url = ""
  websocket_url = ""
  api_pushes = ""
  latest_push = ""
  sonarr_iden = ""

  def __init__(self, key):
    self.api_key = key
    self.api_url = "https://api.pushbullet.com/v2"
    self.websocket_url = "wss://stream.pushbullet.com/websocket/" + self.api_key
    self.api_pushes = self.api_url + "/pushes"
    self.latest_push = self.getFirstPush()
    self.sonarr_iden = "udbNjsjAksBaF0uW"

  def getFirstPush(self):
    payload = {"limit": 1, "active": "true"}
    r = requests.get(self.api_pushes, auth=(self.api_key, ''), params=payload)
    return r.json()['pushes'][0]

  def getLatestPush(self):
    payload = {"limit": 1, "active": "true", "modified_after": self.latest_push['modified']} 
    r = requests.get(self.api_pushes, auth=(self.api_key, ''), params=payload)
    return r.json()['pushes'][0]

  def sendPush(self, title, message, push_from, push_to):
    log("Sending message to: " + push_to, "INFO")
    payload = {"type": "note", "title": title, "body": message, "source_device_iden": push_from, "device_iden": push_to}
    r = requests.post(self.api_pushes, auth=(self.api_key, ''), data=payload)
    if r.status_code == 200:
      log("Message sent", "INFO")
    else:
      log("Something went wrong: {0} '{1}'".format(r.status_code, r.text), "ERROR")
