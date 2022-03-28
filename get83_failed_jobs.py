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

directory_name = "./83_failed_jobs/"

def jenkins_connection():
    userinfo = config_object["USERINFO"]
    server = jenkins.Jenkins(userinfo["HOSTNAME"], userinfo["USERNAME"], userinfo["PASSWORD"])
    user = server.get_whoami()
    version = server.get_version()
    print()
    print("Hello you have connected to jenkins. You are using Jenkins version '%s'" % (version))
    print()
    return server

def get_83_failed_jobs(server):
    rhel83_failed_jobs_list = []
    view = config_object["JENKINS_VIEW"]
    # rhel83_jobs is list of dictionaries
    rhel83_jobs_list = server.get_jobs(view_name=view["RHEL83_VIEW"])
    for job in rhel83_jobs_list:
        # checking jobs with status as failed 
        if job['color'] == "red":
           rhel83_failed_jobs_list.append(job)
    #print("rhel83_failed_jobs_list >>>> ", rhel83_failed_jobs_list)
    print()
    print("Total Failed jobs : ", len(rhel83_failed_jobs_list))
    print()
    # returning list of failed jobs
    return rhel83_failed_jobs_list

def get_build_script(server, rhel83_failed_jobs_list):
    # job_build_script dictionary contains job_name as key & value as script
    job_build_script = {}
    # creating  directory 
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)
        print("Directory '%s' created."%(directory_name))
        print()
    else:
        print("Directory '%s' already exists."%(directory_name))
        print()
    for job in rhel83_failed_jobs_list:
        job_name = job['name']
        #job_name = "PSL_narayana-spring-boot_RHEL_8.3"
        # job_config_data is in string format
        job_config_data = server.get_job_config(job_name)
        # updated_job_config_data is in xml format
        job_config_data_xml = BeautifulSoup(job_config_data, 'xml')
        # fetching build script of the job
        get_script = job_config_data_xml.find('command').text
        job_build_script[job_name] = get_script
    return job_build_script


# Below function stores jobs build script in directory & zip the directory
def store_data(server, job_build_script):
    for job in job_build_script:
        with open(os.path.join(directory_name, job + '.sh'), 'w') as file_name:
            file_name.write(job_build_script[job])
    shutil.make_archive(directory_name, 'zip', directory_name)
    return "Complete"

# Below function generates csv report with its build status 
def generate_report(server):
    job_status_dict = {}
    view = config_object["JENKINS_VIEW"]
    rhel83_jobs = server.get_jobs(view_name=view["RHEL83_VIEW"])
    for job in rhel83_jobs:
        job_name = job['name']
        job_status = job['color']
        if job_status == "red":
            job_status_dict[job_name] = job_status
    with open('mycsvfile.csv', 'w') as f:
        w = csv.writer(f)
        w.writerow(["Job name", "Job status", "Owner", "New Status", "Comments"])
        w.writerows(job_status_dict.items())
    print("job_status_list  >>>>> ", job_status_dict)
    f.close()
    return "CSV file generated"


def main():
    server = jenkins_connection()
    rhel83_failed_jobs_list = get_83_failed_jobs(server)
    job_build_script = get_build_script(server, rhel83_failed_jobs_list)
    store_data(server, job_build_script)
    generate_report(server)

main()


