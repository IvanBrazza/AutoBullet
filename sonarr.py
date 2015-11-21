from logger import log
import re
import requests
import json

class Sonarr(object):
  api_key = ""
  api_url = ""
  api_search = ""
  api_root_folder = ""
  api_series = ""
  headers = ""
  last_search = ""
  last_push_search = ""
  last_show = ""
  root_folder = ""

  def __init__(self, key):
    self.api_key = key
    self.api_url = "https://sonarr.brazza.me/api"
    self.api_search = self.api_url + "/series/lookup"
    self.api_root_folder = self.api_url + "/RootFolder"
    self.api_series = self.api_url + "/Series"
    self.headers = {"X-Api-Key": self.api_key}
    self.root_folder = self.getRootFolder()

  def getRootFolder(self):
    r = requests.get(self.api_root_folder, headers=self.headers)
    return r.json()[0]['path']

  def parseMessage(self, pb):
    push = pb.latest_push

    if push['body'].lower() == "help":
      self.showHelp(pb, push)
    elif push['body'].lower().startswith("search"):
      self.search(pb, push)
    elif push['body'].lower().startswith("details"):
      self.searchDetails(pb, push)
    elif push['body'].lower().startswith("add show"):
      self.addShow(pb, push, self.last_show)
    else:
      self.unknownCommand(push, pb.sonarr_iden)

  def unknownCommand(self, push, device_iden):
    title = "Unknown command"
    message = "Send 'help' to find out what I can do"
    pb.sendPush(title, message, device_iden, push['source_device_iden'])

  def showHelp(self, pb, push):
    title = "Usage"

    message = (
      "Help: displays this help message.\n\n"
      "Search <search string>: searches Sonarr for the specified search string."
    )

    pb.sendPush(title, message, pb.sonarr_iden, push['source_device_iden'])

  def search(self, pb, push):
    matches = re.match("^[sS]earch: (.+)$", push['body'])
    if matches:
      query = matches.group(1)
    else:
      title = "Search Failed"
      message = "Unable to find your search query"
      pb.sendPush(title, message, pb.sonarr_iden, push['source_device_iden'])
      return

    payload = {"term": query}
    r = requests.get(self.api_search, headers=self.headers, params=payload)

    if r.status_code is not 200:
      title = "Search Failed"
      message = "Unable to search Sonarr: {1} '{2}'".format(r.status_code, r.text)
      log(message, "ERROR")
      pb.sendPush(title, message, pb.sonarr_iden, push['source_device_iden'])
      return

    if len(r.json()) == 0:
      title = "No results found for '{0}'".format(query)
      pb.sendPush(title, "", pb.sonarr_iden, push['source_device_iden'])
      return

    title = "Search Results for '{0}'".format(query)
    message = ""
    count = 1

    for show in r.json():
      message = "{0}{1}. {2}\n\n".format(message, count, show['title'])
      count += 1

    message = message + "To get more details about a show, reply with 'Details: <number>' e.g. 'Details: 1'."
    pb.sendPush(title, message, pb.sonarr_iden, push['source_device_iden'])

    self.last_search = r.json()
    self.last_push_search = push

  def searchDetails(self, pb, push):
    matches = re.match("^[dD]etails: (\d+)$", push['body'])
    if matches:
      number = matches.group(1)
    else:
      title = "Error"
      message = "Details command not recognized"
      pb.sendPush(title, message, pb.sonarr_iden, push['source_device_iden'])
      return

    show = self.last_search[int(number) - 1]
    title = show['title']
    message = (
      "Seasons: " + str(show['seasonCount']) + "\n"
      "Satus: " + str(show['status']) + "\n"
      "Year: " + str(show['year']) + "\n"
      "Monitored: " + str(show['monitored']) + "\n"
      "Overview: " + str(show['overview']) + "\n\n"
      "To add this show to Sonarr, reply with 'Add show standard' to add with default settings"
    )
    
    pb.sendPush(title, message, pb.sonarr_iden, push['source_device_iden'])
    self.last_show = show

  def addShow(self, pb, push, show):
    matches = re.match("^[aA]dd show (standard|custom)", push['body'])
    if matches:
      addType = matches.group(1)
    else:
      title = "Error"
      message = "Add command not recognized"
      pb.sendPush(title, message, pb.sonarr_iden, push['source_device_iden'])
      return

    if addType == "standard":
      qualityProfile = 3 # 720p
      seasons = [Season(1, True).__dict__]
    elif addType == "custom":
      matches = re.match("", push['body']

    payload = {"tvdbId": show['tvdbId'], "title": show['title'], "qualityProfileId": qualityProfile, "titleSlug": show['titleSlug'], "seasons": seasons, "path": self.root_folder + show['title']}
    r = requests.post(self.api_series, headers=self.headers, data=json.dumps(payload))

    if r.status_code == 200:
      title = "Show added"
      message = show['title']
    else:
      title = "Failed to add show"
      message = "{0} '{1}'".format(r.status_code, r.text)

    pb.sendPush(title, message, pb.sonarr_iden, push['source_device_iden'])

class Season(object):
  seasonNumber = 0
  monitored = False

  def __init__(self, number, monitored):
    self.seasonNumber = number
    self.monitored = monitored
