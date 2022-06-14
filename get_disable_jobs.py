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
    print("Hello you have connected to jenkins. You are using Jenkins version '%s'" % (version))
    return server

def disable_jobs(server):
    #server = jenkins_connection()
    # get all jobs in jenkins
    disabled_jobs = []
    psl_jobs = []
    rhel_jobs = []
    jobs = server.get_jobs()
    total_jobs = len(jobs)
    print("Total jobs - ", total_jobs)
    import pdb
    #pdb.set_trace()
    for job in jobs:
        try:
            if 'color' in job and 'disabled' in job['color']:
                job_name = job['name']
                print("job name >>>> ", job_name)
                if 'PSL_' in job_name:
                    psl_jobs.append(job_name)
                if 'rhel' in job_name.lower():
                    rhel_jobs.append(job_name)
                disabled_jobs.append(job_name)
        except jenkins.JenkinsException as je:
            print(str(je))

    print(disabled_jobs)
    print("Disabled jobs - ", len(disabled_jobs))
    print(psl_jobs)
    print("psl jobs - ", len(psl_jobs))
    print(rhel_jobs)
    print("rhel jobs - ", len(rhel_jobs))



def main():
    server = jenkins_connection()
    disable_jobs(server)

main()
