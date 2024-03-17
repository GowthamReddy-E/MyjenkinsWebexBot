import requests
import json
from webex_bot.models.command import Command
from webex_bot.models.response import Response

class JenkinsInfo:
    def __init__(self, jenkins_url, username, api_token):
        self.jenkins_url = jenkins_url
        self.username = username
        self.api_token = api_token

    def get_all_jobs_info(self):
        auth = (self.username, self.api_token)
        url = f"{self.jenkins_url}/api/json"
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None

    def get_job_details(self, job_name):
        auth = (self.username, self.api_token)
        url = f"{self.jenkins_url}/job/{job_name}/lastBuild/api/json"
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None

class JenkinsInfoCommand(Command):
    def __init__(self, jenkins_info):
        super().__init__(
            command_keyword="jenkins",
            help_message="Get Jenkins information for all jobs."
        )
        self.jenkins_info = jenkins_info
        self.selected_job = None

    def execute(self, message, teams_message, activity):
        if not self.selected_job:
            # If no job is selected, show all jobs
            return Response(attachments=self.get_adaptive_card())
        else:
            # If a job is selected, display its details
            job_details = self.jenkins_info.get_job_details(self.selected_job)
            if job_details:
                job_info = self.extract_job_info(job_details)
                return Response(text=job_info)
            else:
                return Response(text=f"Error: Could not retrieve information for job '{self.selected_job}'.")

    def process_message(self, message, attachment_actions, activity):
        if attachment_actions.inputs:
            # If a job is selected from the options card, set it as the selected job
            self.selected_job = attachment_actions.inputs['selected_job']
        else:
            # If a job name is provided as a text message, set it as the selected job
            self.selected_job = message.strip()

    def get_adaptive_card(self):
        all_jobs_info = self.jenkins_info.get_all_jobs_info()
        if all_jobs_info:
            card_body = []
            for job in all_jobs_info["jobs"]:
                job_name = job["name"]
                card_body.append({
                    "type": "Action.Submit",
                    "title": job_name,
                    "data": {"selected_job": job_name}
                })
            card = {
                "type": "AdaptiveCard",
                "version": "1.2",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "Select a job:",
                        "size": "Medium",
                        "weight": "Bolder"
                    },
                    {
                        "type": "ActionSet",
                        "actions": card_body
                    }
                ]
            }
            return card
        else:
            return {
                "type": "AdaptiveCard",
                "version": "1.2",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "Error: Could not connect to Jenkins server or retrieve job information."
                    }
                ]
            }

    def extract_job_info(self, job_details):
        # Implement this method to extract job information from job details
        pass
