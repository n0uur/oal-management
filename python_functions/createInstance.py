import boto3


def createInstance(instanceName="GROUP5-EC2", instanceType="t2.micro", subnetId="", imageID="ami-0ed9277fb7eb570c9", keyName="vockey", volumeSize=10, volumeType="gp2"):
    """Create EC2 Instance
    To be added
    SecurityGroupIds=[]
    """
    ec2Client = boto3.client('ec2')
    userData = """#!/bin/bash
yum update -y
amazon-linux-extras install -y lamp-mariadb10.2-php7.2 php7.2
yum install -y httpd mariadb-server
systemctl start httpd
systemctl enable httpd
usermod -a -G apache ec2-user
chown -R ec2-user:apache /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} \;
find /var/www -type f -exec chmod 0664 {} \;
echo "<?php phpinfo(); ?>" > /var/www/html/phpinfo.php"""

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
        UserData=userData,
        KeyName=keyName,
        SubnetId=subnetId,
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
