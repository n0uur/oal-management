""" List All EC2 Instances from a given region """
import os

import boto3

os.environ['AWS_SECRET_ACCESS_KEY'] = 'SecretKey'
os.environ['AWS_ACCESS_KEY_ID'] = 'AccessKey'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
ec2 = boto3.resource('ec2')


def getInstanceName(instance):
    try:
        instance_name = [tag['Value']
                         for tag in instance.tags if tag['Key'] == 'Name']
        instance_name = instance_name[0]
    except Exception:
        instance_name = None
    return instance_name


def getVPCName(instance):
    try:
        vpc = ec2.Vpc(instance.vpc_id)
        vpc_name = [tag['Value'] for tag in vpc.tags if tag['Key'] == 'Name']
        vpc_name = vpc_name[0]
    except Exception:
        vpc_name = None
    return vpc_name


def getSubnetName(instance):
    try:
        subnet = ec2.Subnet(instance.subnet_id)
        subnet_name = [tag['Value']
                       for tag in subnet.tags if tag['Key'] == 'Name']
        subnet_name = subnet_name[0]
    except Exception:
        subnet_name = None
    return subnet_name


def getSecurityGroupsName(instance):
    security_groups_list = [security_group['GroupName']
                            for security_group in instance.security_groups]
    security_groups = ', '.join(
        security_groups_list) if security_groups_list else None
    return security_groups


def getInstanceDetails():
    """ Print EC2 Name & Id & state & public ip
        & private ip & vpc name & subnet name
        & security group name
    """
    for instance in ec2.instances.all():
        print(
            "Name: {0}\n Id: {1}\n State: {2}\n Public IP: {3}\n Private IP: {4}\n "
            "VPC: {5}\n Subnet: {6}\n Security groups: {7}\n".format(
                getInstanceName(instance),
                instance.id,
                instance.state['Name'],
                instance.public_ip_address,
                instance.private_ip_address,
                getVPCName(instance),
                getSubnetName(instance),
                getSecurityGroupsName(instance)))


if __name__ == '__main__':
    getInstanceDetails()
