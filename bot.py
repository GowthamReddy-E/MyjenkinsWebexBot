import os
from webex_bot.webex_bot import WebexBot
from jenkins_info import *

webex_token = os.environ["WEBEX_TOKEN"]
bot = WebexBot(webex_token)

# Registered custom command with the bot:
jenkins_url = "http://localhost:8080"
username = "gowthame"
api_token = "114b5b6cc08800e772f3f7db6e1c268883"

jenkins_info = JenkinsInfo(jenkins_url, username, api_token)
bot.add_command(JenkinsInfoCommand(jenkins_info))  # Pass jenkins_info as an argument

# Connect to Webex & start bot listener:
bot.run()
