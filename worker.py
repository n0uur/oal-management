"""
Worker thread of OAL Management System
"""
import base64
import threading
import time
import os
import uuid

import boto3
import json
import random
from dotenv import load_dotenv

load_dotenv()

from models import Setting

UPDATE_INTERVAL = int(os.environ.get("WORKER_UPDATE_INTERVAL_SECONDS", 30))


def getTag(service, tag_name):
    try:
        tag = [tag['Value']
               for tag in service.tags if tag['Key'] == tag_name]
        tag = tag[0] if tag else None
    except Exception:
        tag = None
    return tag


def createAMI(instanceId, ami_name="g5_123"):
    """ Create AMIs from an instanceId """
    ec2_client = boto3.client(
        'ec2',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
        region_name=os.environ.get('DATABASE_REGION', 'us-east-1')
    )
    response = ec2_client.create_image(
        InstanceId=instanceId,
        Name=ami_name,
        Description="Template for website G5",
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


NODE_ID = str(uuid.uuid4())


def struggle():
    """struggle thread for master node"""
    print('started struggle thread')
    while True:
        try:
            if Setting.get('master_node') == NODE_ID:
                Setting.set('master_node_last_response', str(time.time()))
                print('response to secondary nodes')
            else:
                if time.time() - Setting.get('master_node_last_response', 0, dataType=float) > 60:
                    Setting.set('master_node', NODE_ID)
                    Setting.set('master_node_last_response', str(time.time()))
                    print('taking over main node')
                    time.sleep(5)
                    if Setting.get('master_node') == NODE_ID:
                        print("winning master node race!")
                    else:
                        print("losing, changing back to secondary node")
        except Exception as e:
            print("struggle thread error: ", e)
            time.sleep(5)

        time.sleep(20)


def main():
    """Main thread of program"""

    try:

        print("starting up...")

        next_update = time.time()

        print("creating struggle thread...")
        struggle_thread = threading.Thread(target=struggle, daemon=True).start()

        if not Setting.get('is_setup', False, bool):
            print("The system is not setup yet.")
            time.sleep(5)  # hold for supervisor to changed into running state
            exit(0)

        while True:
            if time.time() < next_update:
                time.sleep(1)
                continue

            try:

                if Setting.get('master_node') != NODE_ID:
                    time.sleep(1)
                    continue

                time.sleep(15)

                # just need make sure that struggle thread really win the fight
                if Setting.get('master_node') != NODE_ID:
                    time.sleep(1)
                    continue

                ec2_resource = boto3.resource(
                    'ec2',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
                    region_name=os.environ.get('DATABASE_REGION', 'us-east-1')
                )

                ec2_client = boto3.client(
                    'ec2',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
                    region_name=os.environ.get('DATABASE_REGION', 'us-east-1')
                )

                elb_client = boto3.client(
                    'elbv2',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
                    region_name=os.environ.get('DATABASE_REGION', 'us-east-1')
                )

                # ดึง Latest Version และ Current Version จาก Setting
                latest_version = Setting.get('latest_version')
                current_version = Setting.get('current_version')

                # ถ้า Version ล่าสุด กับปัจจุบันไม่ตรงกัน ให้เริม่ Progress Update EC2
                if latest_version != current_version:

                    print("detected version change! updating.... %s >> %s" % (current_version, latest_version))

                    Setting.set('app_status', 'updating')

                    print("creating EC2 for templating... 1/2")
                    # สร้าง AMI Image จาก EC2 -> User Data
                    user_data = Setting.get('latest_user_data')
                    private_subnet = random.choice(json.loads(Setting.get('deploy_public_subnet',
                                                                          dataType=json.loads)))  # dont even ask me what is this doing, I dunno

                    keypair_name = Setting.get('ec2_keypair_name')

                    print("creating EC2 for templating... 2/2")

                    instanceName = "group_5_ec2_temporary"
                    instanceType = "t2.micro"
                    subnetId = private_subnet
                    imageID = "ami-0ed9277fb7eb570c9"  # amazon linux
                    keyName = keypair_name
                    volumeSize = 10
                    volumeType = "gp2"

                    Setting.set('app_status', 'working-ami')

                    prefix_user_data = """#!/bin/bash

exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
ssh-keyscan -H github.com >> /home/ec2-user/.ssh/known_hosts
echo -n '%s' | base64 --decode > /home/ec2-user/.ssh/gitkey
echo -n '%s' | base64 --decode > /home/ec2-user/.ssh/gitkey.pub
echo -n 'SG9zdCBnaXRodWIuY29tCiAgSWRlbnRpdHlGaWxlIH4vLnNzaC9naXRrZXk=' | base64 --decode > /home/ec2-user/.ssh/config
chown ec2-user /home/ec2-user/.ssh/config
chown ec2-user /home/ec2-user/.ssh/known_hosts
chown ec2-user /home/ec2-user/.ssh/gitkey
chown ec2-user /home/ec2-user/.ssh/gitkey.pub
chmod 600 /home/ec2-user/.ssh/config
chmod 400 /home/ec2-user/.ssh/gitkey

""" % (
                        base64.b64encode(Setting.get('ec2_keypair_private').encode('ascii')).decode('ascii'),
                        base64.b64encode(Setting.get('ec2_keypair_public').encode('ascii')).decode('ascii')
                    )

                    ec2_create_response = ec2_client.run_instances(
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
                        SecurityGroupIds=[
                            Setting.get('ec2_security_group')
                        ],
                        InstanceType=instanceType,
                        UserData=prefix_user_data + user_data.replace('\r', ''),
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
                                        'Value': 'group5_temp'
                                    },
                                    {
                                        'Key': 'Name',
                                        'Value': instanceName
                                    },
                                ]
                            },
                        ],
                    )

                    # waiting for creating instance
                    creating_instance_id = ec2_create_response['Instances'][0]['InstanceId']

                    instance_state = ec2_resource.Instance(id=creating_instance_id).state['Name']
                    while instance_state != 'running':
                        instance_state = ec2_resource.Instance(id=creating_instance_id).state['Name']
                        time.sleep(10)

                    print("creating AMI image from EC2... 1/9999")

                    # wait for user-data finished
                    Setting.set('app_status', 'working-ami-userdata')
                    time.sleep(180)

                    ami_id = createAMI(
                        instanceId=creating_instance_id,
                        ami_name="ami-template-%s-%s" % (latest_version, str(uuid.uuid4())[:8])
                    )

                    Setting.set('app_status', 'working-ami')

                    print("creating AMI image from EC2... 15/9999")

                    ami_state = ec2_resource.Image(ami_id).state
                    while ami_state != 'available':
                        ami_state = ec2_resource.Image(ami_id).state
                        # print("AMIs state: ", ami_state)
                        time.sleep(10)

                    Setting.set('ec2_ami_id', ami_id)

                    print("creating AMI image from EC2... 9998/9999")

                    time.sleep(2)

                    print("creating AMI image from EC2... 9999/9999")

                    Setting.set('app_status', 'working-add-ec2')

                    # Terminate temporary ec2
                    ec2_client.terminate_instances(
                        InstanceIds=[
                            creating_instance_id,
                        ],
                    )

                    print("creating new version of EC2... 0/1")

                    desired_ec2_counts = Setting.get('ec2_prefer_counts', 0, dataType=int)

                    for creatingEc2Index in range(desired_ec2_counts):

                        # dont even ask me what is this doing, I dunno
                        private_subnet = random.choice(json.loads(Setting.get('deploy_public_subnet',
                                                                              dataType=json.loads)))

                        instanceName = "group_5_ec2"
                        instanceType = "t2.micro"
                        subnetId = private_subnet
                        imageID = ami_id
                        keyName = keypair_name
                        volumeSize = 10
                        volumeType = "gp2"

                        ec2_create_response = ec2_client.run_instances(
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
                            SecurityGroupIds=[
                                Setting.get('ec2_security_group')
                            ],
                            ImageId=imageID,
                            InstanceType=instanceType,
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
                                            'Key': os.environ.get('EC2_GROUP_TAG', 'ict21'),
                                            'Value': os.environ.get('EC2_GROUP_VALUE', 'group5')
                                        },
                                        {
                                            'Key': 'Name',
                                            'Value': instanceName
                                        },
                                        {
                                            'Key': 'g5_appVersion',
                                            'Value': latest_version
                                        }
                                    ]
                                },
                            ],
                        )

                        creating_instance_id = ec2_create_response['Instances'][0]['InstanceId']

                        time.sleep(10)

                        instance_state = ec2_resource.Instance(id=creating_instance_id).state['Name']
                        while instance_state != 'running':
                            instance_state = ec2_resource.Instance(id=creating_instance_id).state['Name']
                            time.sleep(5)

                        # ใช้ AMI สร้าง EC2 ชุดใหม่ เท่าจำนวนเดิม พร้อม Tag ใหม่ + เพิ่มเข้า Target Group

                        time.sleep(10)

                        target_group_arn = Setting.get('ec2_target_group')

                        elb_client.register_targets(
                            TargetGroupArn=target_group_arn,
                            Targets=[
                                {
                                    'Id': creating_instance_id,
                                },
                            ],
                        )

                    print("creating new version of EC2... 1/1")

                    Setting.set('app_status', 'working-remove-ec2')

                    print("removing old EC2... 1/2")

                    old_ec2 = [
                        _ec2.id for _ec2 in ec2_resource.instances.all()
                        if getTag(_ec2, 'g5_appVersion') == current_version
                    ]

                    if len(old_ec2) > 1:
                        ec2_client.terminate_instances(
                            InstanceIds=old_ec2,
                        )

                    print("removing old EC2... 2/2")

                    # set current version to latest version
                    Setting.set('current_version', latest_version)
                    Setting.set('app_status', 'ok')

                    print("finished upgrade version! :)")

                all_ec2 = [
                    _ec2 for _ec2 in ec2_resource.instances.all() if
                    getTag(_ec2, os.environ.get('EC2_GROUP_TAG', 'ict21')) == os.environ.get('EC2_GROUP_VALUE',
                                                                                             'group5') and
                    _ec2.state['Name'] != 'terminated'
                ]

                ec2_counts = len(all_ec2)

                desired_ec2_counts = Setting.get('ec2_prefer_counts', 0, dataType=int)

                # ตรวจสอบ EC2 ว่ามีจำนวนเท่าไหร่
                # ถ้าเกิน ลบ
                # ถ้าขาด สร้างเพิ่ม
                if ec2_counts != desired_ec2_counts:
                    if ec2_counts > desired_ec2_counts:  # ลบ

                        print("removing unused EC2")

                        ec2_client.terminate_instances(
                            InstanceIds=[e2.id for e2 in all_ec2[:(ec2_counts - desired_ec2_counts)]],
                        )

                        print("removed unused EC2")
                    else:

                        print("creating new EC2")

                        ami_id = Setting.get('ec2_ami_id')
                        keypair_name = Setting.get('ec2_keypair_name')
                        target_group_arn = Setting.get('ec2_target_group')

                        for creatingEc2Index in range(desired_ec2_counts - ec2_counts):
                            # dont even ask me what is this doing, I dunno
                            private_subnet = random.choice(json.loads(Setting.get('deploy_public_subnet',
                                                                                  dataType=json.loads)))

                            instanceName = "group_5_ec2"
                            instanceType = "t2.micro"
                            subnetId = private_subnet
                            imageID = ami_id
                            keyName = keypair_name
                            volumeSize = 10
                            volumeType = "gp2"

                            ec2_create_response = ec2_client.run_instances(
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
                                SecurityGroupIds=[
                                    Setting.get('ec2_security_group')
                                ],
                                ImageId=imageID,
                                InstanceType=instanceType,
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
                                                'Key': os.environ.get('EC2_GROUP_TAG', 'ict21'),
                                                'Value': os.environ.get('EC2_GROUP_VALUE', 'group5')
                                            },
                                            {
                                                'Key': 'Name',
                                                'Value': instanceName
                                            },
                                            {
                                                'Key': 'g5_appVersion',
                                                'Value': latest_version
                                            }
                                        ]
                                    },
                                ],
                            )

                            creating_instance_id = ec2_create_response['Instances'][0]['InstanceId']

                            time.sleep(10)

                            # wait before register target to target group
                            instance_state = ec2_resource.Instance(id=creating_instance_id).state['Name']
                            while instance_state != 'running':
                                instance_state = ec2_resource.Instance(id=creating_instance_id).state['Name']
                                time.sleep(5)

                            time.sleep(10)

                            elb_client.register_targets(
                                TargetGroupArn=target_group_arn,
                                Targets=[
                                    {
                                        'Id': creating_instance_id,
                                    },
                                ],
                            )

                        print("created new EC2")

            except Exception as e:
                print(e)
                time.sleep(5)

            next_update = time.time() + UPDATE_INTERVAL

    except Exception as e:
        print("Error: ", e)
        time.sleep(5)


if __name__ == "__main__":
    main()
