import jenkins
import lxml
import json
import re
import tqdm
import time
import os
import shutil
import csv
from bs4 import BeautifulSoup
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config-sample.ini")

output_data = config_object["OUTPUT"]

def jenkins_connection():
    userinfo = config_object["USERINFO"]
    server = jenkins.Jenkins(userinfo["HOSTNAME"], userinfo["USERNAME"], userinfo["PASSWORD"])
    user = server.get_whoami()
    version = server.get_version()
    print()
    print("You are using Jenkins version '%s'" % (version))
    print()
    return server

# Below function generates csv file with job-name, build-status, distro-version, status for all Jenkins jobs except currency jobs.
def generate_report(server):
    job_status_list = []
    jenkins_jobs = server.get_jobs()
    print("Total jenkins jobs - ", len(jenkins_jobs))
    for job in jenkins_jobs:
        if 'Currency' not in job['name']:
            github_url = " "
            job_name = job['name']
        try:
            job_status = job['color']
        except KeyError:
            continue
        job_url = job['url']
        splitted = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', job_name),flags=re.IGNORECASE).split()[-1]
        job_distro = splitted.replace(r'/','')
        try:
            job_config_data = server.get_job_config(job_name)
            job_config_data_xml = BeautifulSoup(job_config_data, 'xml')
            github_url = re.search("(?P<url>https?://github.com/[^\s][^\n<>]+)", job_config_data).group("url")
        except AttributeError as error:
            print(error)
        job_status_list.append([job_name, job_status, github_url, job_distro])
    with open(output_data["All_JENKINS_JOBS_STATUS"], 'w') as f:
        w = csv.writer(f)
        w.writerow(["Job name", "Job status", "Github url", "Distro"])
        w.writerows(job_status_list)
    #print("job_status_list  >>>>> ", job_status_list)
    f.close()
    return "CSV file generated"

def main():
    server = jenkins_connection()
    generate_report(server)

main()


