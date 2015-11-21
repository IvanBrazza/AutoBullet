import websocket
import logging
import json
import pushbullet
import sonarr
from logger import log
logging.basicConfig()

SONARR_API_KEY = "49f8d133b0ed429e9890e959d969d0f0"
PB_API_KEY = "7b364932bbbcbff68bac56c72b05c42e"
pb = 0

def init():
  global pb, sonarr
  pb = pushbullet.Pushbullet(PB_API_KEY)
  sonarr = sonarr.Sonarr(SONARR_API_KEY)
  
  log("Last message was at " + str(pb.latest_push['modified']), "INFO")
  log("Root folder is " + str(sonarr.root_folder), "INFO")

  websocket.enableTrace(False)
  ws = websocket.WebSocketApp(pb.websocket_url, on_message = OnPBMessage)
  ws.on_open = OnPBStart
  ws.run_forever()

# When a connection to the Pushbullet websocket is established,
# log and get all available Pushbullet devices
def OnPBStart(ws):
  log("Connected to Pushbullet WebSocket", "INFO")

# Whenever something happens in the Pushbullet websocket.
def OnPBMessage(ws, message):
  global pb
  log(message, "INFO")
  message   = json.loads(message)
  if message['type'] == "tickle" and message['subtype'] == "push": # A new push was sent, fetch it!
    pb.latest_push = pb.getLatestPush()
    #log(push, "INFO")
    if 'target_device_iden' in pb.latest_push:
      if pb.latest_push['target_device_iden'] == pb.sonarr_iden:
        sonarr.parseMessage(pb)

init()
