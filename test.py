import requests
import json
import datetime
from webex_bot.models.command import Command

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

    def get_last_successful_build_number(self, job_name):
        auth = (self.username, self.api_token)
        url = f"{self.jenkins_url}/job/{job_name}/lastSuccessfulBuild/api/json"
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            return json.loads(response.text).get("number")
        else:
            return "N/A"

    def get_last_failure_build_number(self, job_name):
        auth = (self.username, self.api_token)
        url = f"{self.jenkins_url}/job/{job_name}/lastFailedBuild/api/json"
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            return json.loads(response.text).get("number")
        else:
            return "N/A"





class JenkinsInfoCommand(Command):
    def __init__(self, jenkins_info):
        super().__init__(
            command_keyword="jenkins",
            help_message="Get Jenkins information for all jobs.",
            card=self.get_adaptive_card(jenkins_info),
        )
        self.jenkins_info = jenkins_info

    def execute(self, message, teams_message, activity):
        # Implement the logic to execute the command here
        # For example:
        # You can send a message with the Jenkins information to the user or room
        pass
    
    
    
    
    def get_adaptive_card(self, jenkins_info):
        all_jobs_info = jenkins_info.get_all_jobs_info()
        if all_jobs_info:
            card_body = []
            for job in all_jobs_info["jobs"]:
                job_name = job["name"]
                job_details = jenkins_info.get_job_details(job_name)
                current_build_number = job_details.get("number", "N/A")
                last_successful_build_number = jenkins_info.get_last_successful_build_number(job_name)
                last_failure_build_number = jenkins_info.get_last_failure_build_number(job_name)
                build_duration_ms = job_details.get("duration", 0)
                build_duration = self.format_duration(build_duration_ms)
                triggering_time_ms = job_details.get("timestamp", 0)
                triggering_time = datetime.datetime.fromtimestamp(triggering_time_ms / 1000).strftime('%d-%m-%Y %H:%M:%S')
                job_status = "🟢" if last_successful_build_number == current_build_number else "🔴"
            
                # Construct the URL for the job details page
                job_url = f"{jenkins_info.jenkins_url}/job/{job_name}/{current_build_number}"
            
                card_body.append({
                    "type": "TextBlock",
                    "text": f"{job_status} > [{job_name}]({job_url}) > {current_build_number} > {last_successful_build_number} > {last_failure_build_number} > {build_duration} > {triggering_time}",
                    "wrap": True
                })
            card = {
                "type": "AdaptiveCard",
                "version": "1.2",
                "body": card_body
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


    
    def format_duration(self, milliseconds):
        if milliseconds == 0:
            return "N/A"

        seconds = milliseconds / 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        duration = []
        if hours > 0:
            duration.append(f"{int(hours)} hr")
        if minutes > 0:
            duration.append(f"{int(minutes)} min")
        if seconds > 0:
            duration.append(f"{seconds:.3f} sec")

        return " ".join(duration)