import boto3


def createInstance(instanceName="PROJECT-EC2", instanceType="t2.micro", imageID="ami-04363934db7c747c4", volumeSize=10, volumeType="gp2"):
    """Create EC2 Instance
    To be added
    SecurityGroupIds=[]
    LaunchTemplate={
        'LaunchTemplateId': 'string',
        'LaunchTemplateName': 'string',
        'Version': 'string'
    }
    """
    ec2Client = boto3.client('ec2')

    response = ec2Client.run_instances(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {

                    'DeleteOnTermination': True,
                    'VolumeSize': volumeSize,
                    'VolumeType': volumeType
                },
            },
        ],
        ImageId=imageID,
        InstanceType=instanceType,
        MaxCount=1,
        MinCount=1,
        Monitoring={
            'Enabled': False
        },
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'ict21',
                        'Value': 'group5'
                    },
                    {
                        'Key': 'Name',
                        'Value': instanceName
                    },
                ]
            },
        ],
    )
    return response
