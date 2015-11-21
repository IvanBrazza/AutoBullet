import time

# Log a message with a timestamp to the console window
def log(logmsg, logtype):
  timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
  print "{0} [{1}] {2}".format(timestamp, logtype, str(logmsg))
