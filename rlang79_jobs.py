import jenkins
import lxml
import json
import re
import tqdm
import time
from bs4 import BeautifulSoup
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config-sample.ini")

def jenkins_connection():
    userinfo = config_object["USERINFO"]
    server = jenkins.Jenkins(userinfo["HOSTNAME"], userinfo["USERNAME"], userinfo["PASSWORD"])
    user = server.get_whoami()
    version = server.get_version()
    print()
    print("You have connected to jenkins. You are using Jenkins version '%s'" % (version))
    return server

def get_rhel79_jobs(server):
    rlang_jobs_list = []
    view = config_object["JENKINS_VIEW"]
    # use below 2 lines of logic if jobs to be sent in slots
    rhel79_jobs_list = server.get_jobs(view_name=view["RHEL79_VIEW"])
    rlang_label_expression = "DockerCloud_Rlang_UBI_7.9"
    for job in rhel79_jobs_list:
        try:
            job_name = job['name']
            if re.search('Rlang', job_name, re.IGNORECASE):
                job_config_data = server.get_job_config(job_name)
                job_config_data_xml = BeautifulSoup(job_config_data, 'xml')
                label_expression = job_config_data_xml.find('assignedNode').text
                job_config_data_xml.find('assignedNode').string = rlang_label_expression
                server.reconfig_job(job_name, job_config_data_xml)
                print("Updated label expression for - ", job_name)
                server.build_job(job_name)
                rlang_jobs_list.append(job_name)
                print("rlang_jobs >>>> ", rlang_jobs_list)
                print(len(rlang_jobs_list))
                #exit()
        except jenkins.JenkinsException as je:
            print("In exception >>>> ", job_name)
            print(str(je))

def main():
    server = jenkins_connection()
    rhel79_jobs = get_rhel79_jobs(server)

main()
