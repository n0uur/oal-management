import boto3
import time
import os

os.environ['AWS_SECRET_ACCESS_KEY'] = 'SecretKey'
os.environ['AWS_ACCESS_KEY_ID'] = 'AccessKey'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
INSTANCE_ID = 'INSTANCE_ID'


def createAMI(instanceId):
    """ Create AMIs from an instanceId """
    ec2Client = boto3.client('ec2')
    response = ec2Client.create_image(
        InstanceId=instanceId,
        Name="GitHub-Automation-AMI",
        Description="Created by GitHub-Automation",
        TagSpecifications=[
            {
                'ResourceType': 'image',
                'Tags': [
                    {
                        'Key': 'ict21',
                        'Value': 'group5'
                    },
                ]
            },
        ],
    )
    return response['ImageId']


def main():
    """ Create AMIs from an instanceId 
        after instance is in running state
        and wait for AMI to be available
    """
    ec2 = boto3.resource('ec2')
    instane_state = ec2.Instance(id=INSTANCE_ID).state['Name']
    while instane_state != 'running':
        instane_state = ec2.Instance(id=INSTANCE_ID).state['Name']
        print("Instance state:", instane_state)
        time.sleep(10)
    ami_id = createAMI(instanceId=INSTANCE_ID)
    ami_state = ec2.Image(ami_id).state
    while ami_state != 'available':
        ami_state = ec2.Image(ami_id).state
        print("AMIs state: ", ami_state)
        time.sleep(10)


if __name__ == "__main__":
    main()
