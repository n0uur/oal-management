""" List All EC2 Instances """
import os

import boto3

os.environ['AWS_SECRET_ACCESS_KEY'] = 'SECRET_KEY'
os.environ['AWS_ACCESS_KEY_ID'] = 'ACCESS_KEY'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
ec2 = boto3.resource('ec2')


def getAllVPCsDetail():
    """ Print VPC Name & Id & state & cidr block
        & subnet
    """
    for vpc in ec2.vpcs.all():
        if getSpecificTag(vpc, 'ict21') == 'group5':
            print(
                "Name: {0}\n Id: {1}\n State: {2}\n Cidr block: {3}\n Subnet: {4}\n".format(
                    vpc.tags[0]['Value'] if vpc.tags else None,
                    vpc.id,
                    vpc.state,
                    vpc.cidr_block,
                    [(subnet.id, getSpecificTag(subnet, 'Name'), subnet.cidr_block)
                     for subnet in vpc.subnets.all()]))


def getSpecificTag(service, tag_name):
    try:
        tag = [tag['Value']
               for tag in service.tags if tag['Key'] == tag_name]
        tag = tag[0] if tag else None
    except Exception:
        tag = None
    return tag


def getInstanceName(instance):
    return getSpecificTag(instance, 'Name')


def getVPCName(instance):
    vpc = ec2.Vpc(instance.vpc_id)
    return getSpecificTag(vpc, 'Name')


def getSubnetName(instance):
    subnet = ec2.Subnet(instance.subnet_id)
    return getSpecificTag(subnet, 'Name')


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
        if getSpecificTag(instance, 'ict21') == 'group5':
            print(
                "Name: {0}\n Id: {1}\n State: {2}\n Public ip: {3}\n Private ip: {4}\n VPC: {5}\n Subnet name: {6}\n  Subnet id: {7}\n  Subnet CIDR Block: {8}\n Security groups: {9}\n".format(
                    getInstanceName(instance),
                    instance.id,
                    instance.state['Name'],
                    instance.public_ip_address,
                    instance.private_ip_address,
                    getVPCName(instance),
                    getSubnetName(instance),
                    instance.subnet.id,
                    instance.subnet.cidr_block,
                    getSecurityGroupsName(instance)
                )
            )


if __name__ == '__main__':
    getInstanceDetails()
    getAllVPCsDetail()
