import requests
import json
import datetime
from webex_bot.models.command import Command


class JenkinsInfoCommand(Command):
    def __init__(self, jenkins_url, username, api_token):
        self.jenkins_url = jenkins_url
        self.username = username
        self.api_token = api_token
        super().__init__(
            command_keyword="jenkins",
            help_message="Get Jenkins information for all jobs.",
            card=self.generate_adaptive_card(),
        )
        

    def execute(self, message, teams_message, activity):
        pass
    
    def generate_adaptive_card(self):
        auth = (self.username, self.api_token)
        url = f"{self.jenkins_url}/api/json"
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            all_jobs_info = json.loads(response.text).get("jobs", [])
            card_body = []

            for job in all_jobs_info:
                job_name = job["name"]
                job_info = {
                    'name': job_name,
                    'last_build_number': None,
                    'last_successful_build_number': None,
                    'last_failure_build_number': None,
                    'last_build_duration': None,
                    'triggering_time': None
                }

                # Get last build details
                last_build_url = f"{self.jenkins_url}/job/{job_name}/lastBuild/api/json"
                last_build_response = requests.get(last_build_url, auth=auth)
                if last_build_response.status_code == 200:
                    last_build_details = json.loads(last_build_response.text)
                    job_info['last_build_number'] = last_build_details.get("number")

                    # Calculate build duration
                    build_duration_ms = last_build_details.get("duration", 0)
                    job_info['last_build_duration'] = self.format_duration(build_duration_ms)

                    # Get triggering time
                    triggering_time_ms = last_build_details.get("timestamp", 0)
                    triggering_time = datetime.datetime.fromtimestamp(triggering_time_ms / 1000).strftime('%d-%m-%Y %H:%M:%S')
                    job_info['triggering_time'] = triggering_time
                
                # Get last successful build number
                success_url = f"{self.jenkins_url}/job/{job_name}/lastSuccessfulBuild/api/json"
                success_response = requests.get(success_url, auth=auth)
                if success_response.status_code == 200:
                    job_info['last_successful_build_number'] = json.loads(success_response.text).get("number")
                
                # Get last failure build number
                failure_url = f"{self.jenkins_url}/job/{job_name}/lastFailedBuild/api/json"
                failure_response = requests.get(failure_url, auth=auth)
                if failure_response.status_code == 200:
                    job_info['last_failure_build_number'] = json.loads(failure_response.text).get("number")
                
                # Construct card body for each job
                job_status = "🟢" if job_info['last_build_number'] == job_info['last_successful_build_number'] else "🔴"
                job_url = f"{self.jenkins_url}/job/{job_name}/{job_info['last_build_number']}"
                card_body.append({
                    "type": "TextBlock",
                    "text": f"{job_status} > [{job_name}]({job_url}) > {job_info['last_build_number']} > {job_info['last_successful_build_number']} > {job_info['last_failure_build_number']} > {job_info['last_build_duration']} > {job_info['triggering_time']}",
                    "wrap": True
                })

            # Construct the adaptive card
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