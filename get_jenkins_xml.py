import jenkins
import lxml
import json
import os 
import re
import tqdm
import time
import shutil
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
    print("Hello you have connected to jenkins. You are using Jenkins version '%s'" % (version))
    return server

def get_xml(server):
    #server = jenkins_connection()
    jobs = server.get_jobs()
    #print("jobs >>>> ", jobs)
    print("total jobs >>> ", len(jobs))
    my_job = server.get_job_config('zlib_RHEL_8.5')
    #print("my_job >>>>>>>>>> ", my_job)
    if not os.path.exists(output_data["JENKINS_XML_DATA"]):
        os.mkdir(output_data["JENKINS_XML_DATA"])
        print("Directory '%s' created."%(output_data["JENKINS_XML_DATA"]))
        print()
    else:
        print("Directory '%s' already exists."%(output_data["JENKINS_XML_DATA"]))
        print()
    for job in jobs:
        job_name = job['name']
        print("job_name >>>>", job_name)
        xml_data = server.get_job_config(job_name)
        #print(" xml data >>>>>>>>>>>> ", xml_data)
        job_config_data_xml = BeautifulSoup(xml_data, 'xml')
        #print("job >>>>> ", job)
        #print("job_config_data_xml >>> ", job_config_data_xml)
        with open(os.path.join(output_data["JENKINS_XML_DATA"], job_name + '.xml'), 'w') as file_name:
            #file_name.write(job_build_script[job])
            file_name.write(str(job_config_data_xml))
    shutil.make_archive(output_data["JENKINS_XML_DATA"], 'zip', output_data["JENKINS_XML_DATA"])
    return "Complete"

def main():
    server = jenkins_connection()
    get_xml(server)

main()
