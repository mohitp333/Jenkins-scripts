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

def get_rhel83_jobs(server):
    view = config_object["JENKINS_VIEW"]
    # use below 2 lines of logic if jobs to be sent in slots
    #rhel83_jobs_list = server.get_jobs(view_name=view["RHEL83_VIEW"])
    #rhel83_jobs = rhel83_jobs_list[:30]

    # Below 2 jobs are for testing purpose
    rhel83_jobs = [{'_class': 'hudson.model.FreeStyleProject', 'name': 'PSL_narayana-spring-boot_RHEL_8.3', 'url': 'http://129.40.81.8:8080/job/PSL_narayana-spring-boot_RHEL_8.3/', 'color': 'blue', 'fullName': 'PSL_narayana-spring-boot_RHEL_8.3'}, {'_class': 'hudson.model.FreeStyleProject', 'name': 'corset_RHEL_8.3', 'url': 'http://129.40.81.8:8080/job/corset_RHEL_8.3/', 'color': 'blue', 'fullName': 'corset_RHEL_8.3'}]
    #rhel83_jobs1 = [{'_class': 'hudson.model.FreeStyleProject', 'name': 'PSL_narayana-spring-boot_RHEL_8.3', 'url': 'http://129.40.81.8:8080/job/PSL_narayana-spring-boot_RHEL_8.3/', 'color': '    blue', 'fullName': 'PSL_narayana-spring-boot_RHEL_8.3'}]
    rhel83_jobs_count = len(rhel83_jobs)
    print()
    print("Total RHEL 8.3 packages for migration : ", rhel83_jobs_count)
    print()
    print("##### Processing below RHEL 8.3 jobs #####")
    print()
    for j_name in rhel83_jobs:
        print("- "+j_name['name'])
    print()
    print("##########################################")
    return rhel83_jobs

def migrate_jobs(server, rhel83_jobs):
    rhel85_jobs = []
    migrated_jobs_list = []
    root_user_label = "DockerCloud_UBI_8.5_Root"
    jenkins_user_label = "DockerCloud_UBI_8.5_Jenkinsuser"
    print()
    print(".. Migration process started ..")
    print()
    for job in rhel83_jobs:
        try:
            if 'blue' in job['color']:
                job_name = job['name']
                edit_job_name = job_name[:-2]
                new_job_name = edit_job_name + ".5"
                # job_config_data is in string format
                job_config_data = server.get_job_config(job_name)
                # updated_job_config_data is in xml format
                job_config_data_xml = BeautifulSoup(job_config_data, 'xml')
                # 83_label_expression gives label expression of 8.3 job
                label_expression = job_config_data_xml.find('assignedNode').text
                if re.search('root', label_expression, re.IGNORECASE):
                    # updating label expression for root user 
                    job_config_data_xml.find('assignedNode').string = root_user_label
                    print("Updating Label Expression for '%s' "%(new_job_name))

                if re.search('jenkins', label_expression, re.IGNORECASE):
                    # updating label expression for jenkins user 
                    job_config_data_xml.find('assignedNode').string = jenkins_user_label
                    #print("Updating Label Expression for %s"%(new_job_name))
                    print("Updating Label Expression for '%s' "%(new_job_name))
                server.create_job(new_job_name, job_config_data_xml)
                print("Created job '%s' "%(new_job_name))
                print("Buildling job wait for 10 seconds ...")
                server.build_job(new_job_name)
                time.sleep(10)
                print("Job '%s' is build"%(new_job_name))
                server.disable_job(job_name)
                print("Disabling job '%s'"%(job_name))
                print()
                migrated_jobs_list.append(new_job_name)
                print()
        except jenkins.JenkinsException as je:
            print()
            print("In exception >>>> ", job)
            print(str(je))
    print("List of migrated job - ", migrated_jobs_list)
    print()
    print("Total migrated jobs - ", len(migrated_jobs_list))
    return rhel85_jobs

def main():
    server = jenkins_connection()
    rhel83_jobs = get_rhel83_jobs(server)
    migrate_jobs(server, rhel83_jobs)

main()


