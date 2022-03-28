import jenkins
import lxml
import json
import re
import tqdm
import time
from bs4 import BeautifulSoup
from configparser import ConfigParser

#server = jenkins.Jenkins("http://129.40.81.11:8080", username="root", password="L0Phostingpass10")
#server = jenkins.Jenkins("http://129.40.81.8:8080", username="mohit_pawar", password="mohit@123")
#print(server)

def jenkins_connection():
    config_object = ConfigParser()
    config_object.read("config.ini")
    userinfo = config_object["USERINFO"]
    #print(userinfo["username"])
    #print("Password is {}".format(userinfo["password"]))
    server = jenkins.Jenkins(userinfo["HOSTNAME"], userinfo["USERNAME"], userinfo["PASSWORD"])
    #print(server)
    user = server.get_whoami()
    version = server.get_version()
    #print(version)
    #print('Hello %s from Jenkins %s' % (user['fullName'], version))
    print('Hello you have connected to jenkins. You are using Jenkins version %s' % (version))
    return server

def get_job_counts():
    server = jenkins_connection()
    total_jobs = server.jobs_count()
    print("Total jenkin jobs : %s" % (total_jobs))
    return total_jobs

def create_job():
    server = jenkins_connection()
    job_name = "testing_job"
    server.create_job(job_name, jenkins.EMPTY_CONFIG_XML)

def create_job():
    server = jenkins_connection()
    job_name = "testing_job"
    server.delete_job(job_name)

def get_rhel83_jobs():
    server = jenkins_connection()
    rhel83_jobs = server.get_jobs(view_name='Rhel 8.3')
    rhel83_jobs_count = len(rhel83_jobs)
    #print('RHEL 8.3 jobs : %s' % (rhel83_jobs))
    print('RHEL 8.3 jobs count : %s' % (rhel83_jobs_count))
    print(type(rhel83_jobs))
    return rhel83_jobs


def get_rhel85_jobs():
    server = jenkins_connection()
    rhel85_jobs = server.get_jobs(view_name='Rhel 8.5')
    rhel85_jobs_count = len(rhel85_jobs)
    #print('RHEL 8.3 jobs : %s' % (rhel83_jobs))
    print('RHEL 8.5 jobs count : %s' % (rhel85_jobs_count))
    print(type(rhel85_jobs))
    return rhel85_jobs

def build_rhel85_job():
    server = jenkins_connection()
    build_job_name = "testing_job"
    print("Building job..")
    server.build_job(build_job_name)


def enable_rhel85_job():
    server = jenkins_connection()
    enable_job_name = "testing_job"
    print("Enabling job..")
    server.enable_job(enable_job_name)

def disable_rhel85_job():
    server = jenkins_connection()
    disable_job_name = "testing_job"
    print("Disabling job..")
    server.disable_job(disable_job_name)

def copy_job():
    server = jenkins_connection()
    old_job_name = "PSL_narayana-spring-boot_RHEL_8.3"
    new_job_name = "PSL_narayana-spring-boot_RHEL_8.5"
    print("Copying job ..")
    server.copy_job(old_job_name, new_job_name)
    return new_job_name

def updated_label_expression():

    print("Updating label expression")
    data = [{'_class': 'hudson.model.FreeStyleProject', 'name': 'PSL_narayana-spring-boot_RHEL_8.3', 'url': 'http://129.40.81.8:8080/job/PSL_narayana-spring-boot_RHEL_8.3/', 'color': 'blue', 'fullName': 'PSL_narayana-spring-boot_RHEL_8.3'}, {'_class': 'hudson.model.FreeStyleProject', 'name': 'corset_RHEL_8.3', 'url': 'http://129.40.81.8:8080/job/corset_RHEL_8.3/', 'color': 'blue', 'fullName': 'corset_RHEL_8.3'}]
    data1 = [{'_class': 'hudson.model.FreeStyleProject', 'name': 'PSL_narayana-spring-boot_RHEL_8.3', 'url': 'http://129.40.81.8:8080/job/PSL_narayana-spring-boot_RHEL_8.3/', 'color': '    blue', 'fullName': 'PSL_narayana-spring-boot_RHEL_8.3'}]

    server = jenkins_connection()
    for job in data:
        job_name = job['name']
        edit_job_name = job_name[:-2]
        new_job_name = edit_job_name + ".5"
        job_config_data = server.get_job_config(job_name)
        updated_job_config_data = BeautifulSoup(job_config_data, 'xml')
        label_expression = updated_job_config_data.find('assignedNode').text
        root_user_label = "DockerCloud_UBI_8.5_Root"
        jenkins_user_label = "DockerCloud_UBI_8.5_Jenkinsuser"
        if re.search('root',label_expression, re.IGNORECASE):
            updated_job_config_data.find('assignedNode').string = root_user_label
            print("Updating Label Expression for %s "%(new_job_name))
            print()

        if re.search('jenkins',label_expression, re.IGNORECASE):
            updated_job_config_data.find('assignedNode').string = jenkins_user_label
            print("Updating Label Expression for %s"%(new_job_name))
            print()

        server.create_job(new_job_name, updated_job_config_data)
        print("Created job %s "%(new_job_name))
        print()
        print("Buildling job wait 10 seconds for its completion...")
        server.build_job(new_job_name)
        time.sleep(10)
        print()
        print("Job %s is build."%(new_job_name))
    return updated_job_config_data

updated_label_expression()




