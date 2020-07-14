import datetime
import logging
from msrestazure.azure_active_directory import MSIAuthentication
from pprint import pprint
from pprint import pformat
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
groups = ['resourcegroup-1', 'resourcegroup-2']
subscription_id = 'your-subscription-id'
key = 'environment'
key_value = 'dev'
def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    #credentials = DefaultAzureCredential()
    credentials = MSIAuthentication()
    compute_client = ComputeManagementClient(credentials, subscription_id)
     # List VM in resource group
    print('\nList VMs in resource group')
    for group in groups:
        for vm in compute_client.virtual_machines.list(group):
            logging.info("\tVM: {}".format(vm.name))
            jsonStr = json.dumps(vm.tags)
            logging.info(jsonStr)
            logging.info(vm.id)
            temp_id_list=vm.id.split('/')
            resource_group=temp_id_list[4]
            statuses = compute_client.virtual_machines.instance_view(group, vm.name).statuses
            status = len(statuses) >= 2 and statuses[1]
            if vm.tags is not None:
                if key in vm.tags:
                    if key_value in vm.tags[key]:
                        if status and status.code != 'PowerState/running':
                            logging.info('This VM is not running %s', vm.name)
                            async_vm_start = compute_client.virtual_machines.start(group, vm.name)
                            async_vm_start.wait()
                            logging.info('Start command executed for %s', vm.name)
