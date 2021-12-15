"""tbd"""
import json
from logging import log
from dotenv import load_dotenv
from werkzeug.utils import redirect

load_dotenv()

import os
import re
import uuid
import boto3
from dotenv import load_dotenv
from flask import Flask, request, session, render_template
from flask_session import Session
from Crypto.PublicKey import RSA

from models import Setting

app = Flask(
    __name__,
    static_folder='./public',
    static_url_path='/',
    template_folder='templates'
)

app.config["SESSION_PERMANENT"] = False

app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_COOKIE_NAME"] = "g5_oal_session"
app.config["SESSION_COOKIE_PATH"] = "APPLICATION_ROOT"
app.config["SESSION_FILE_DIR"] = "sessions"

app.secret_key = os.environ.get("WEB_SECRET_KEY", "ABCD")

_session = Session()
_session.init_app(app)


@app.route("/", methods=["GET", "POST"])
def home():
    if not session.get('is_permit', False):
        return redirect('/login')
    if not Setting.get('is_setup', False):
        return redirect('setup')

    error = None

    if request.method == "POST":
        if not request.form.get('app_version', False) or \
                not request.form.get('app_user_data', False):
            error = "กรุณากรอกข้อมูลให้ครบถ้วน"
        else:
            current_version = Setting.get("current_version")
            if current_version == request.form.get('app_version'):
                error = "กรุณากรอกเวอร์ชันใหม่"
            else:
                Setting.set('latest_version', request.form.get('app_version'))
                Setting.set('latest_user_data', request.form.get('app_user_data'))
                Setting.set('app_status', 'waiting')

    return render_template("update.html", last_ec2_counts=Setting.get('ec2_prefer_counts', 0, int),
                           current_version=Setting.get("current_version"), error=error)


@app.route("/status")
def status():
    if not session.get('is_permit', False):
        return "", 403

    return {
        "status": Setting.get('app_status', 'error'),
        "version": Setting.get('current_version')
    }


@app.route("/update/amount", methods=["POST"])
def update_amount():
    if not session.get('is_permit', False):
        return redirect('/login')
    if not Setting.get('is_setup', False):
        return redirect('setup')

    if request.form.get('ec2_prefer_amount', False):
        Setting.set('ec2_prefer_counts', request.form.get('ec2_prefer_amount'))

    return redirect('/')


@app.route("/setup", methods=["GET", "POST"])
def setup():
    if not session.get('is_permit', False):
        return redirect('/login')
    if Setting.get('is_setup', False):
        return redirect('/')

    error = None

    if not os.environ.get('WEB_SECRET_KEY') or \
            not os.environ.get('WEB_LOGIN_SECRET') or \
            not os.environ.get('AWS_ACCESS_KEY') or \
            not os.environ.get('AWS_SECRET_KEY') or \
            not os.environ.get('DATABASE_SETTING_TABLE'):
        error = "กรุณาตั้งค่าระบบก่อน ด้วยการตั้งค่า Environment"
        return render_template("nosetup.html", error=error)

    try:
        if not Setting.exists():
            Setting.create_table(wait=True)
    except:
        error = "Access Key หรือ Secret Key ของ AWS ไม่ถูกต้อง  "
        return render_template("nosetup.html", error=error)

    ec2 = boto3.client('ec2',
                       aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
                       region=os.environ.get('DATABASE_REGION', 'us-east-1')
                   )

    if request.method == "POST":

        try:

            # save config and go to management page

            if not all([
                request.form.get('app_name', False),
                request.form.get('app_version', False),
                request.form.get('app_user_data', False),
                request.form.get('app_vpc', False),
                request.form.get('app_public_subnets', False),
                request.form.get('app_private_subnets', False),
            ]):
                error = "กรุณากรอกข้อมูลให้ครบถ้วน"
            else:
                app_name = re.sub(r'(?<!^)(?=[A-Z])', '_', request.form.get('app_name')).lower().strip().replace(' ',
                                                                                                                 '_')

                Setting.set('app_name', request.form.get('app_name'))
                Setting.set('latest_version', request.form.get('app_version'))
                Setting.set('current_version', 'initial-' + request.form.get('app_version'))
                Setting.set('latest_user_data', request.form.get('app_user_data'))
                Setting.set('ec2_prefer_counts', "0")

                Setting.set('app_status', "initializing")  # initializing, ok, working/updating

                vpc_id = request.form.get('app_vpc')
                public_subnets = request.form.get('app_public_subnets')
                private_subnets = request.form.get('app_private_subnets')

                Setting.set('deploy_vpc_id', vpc_id)
                Setting.set('deploy_public_subnet', json.dumps(public_subnets))
                Setting.set('deploy_private_subnet', json.dumps(private_subnets))

                # create Security group

                security_group = ec2.create_security_group(
                    GroupName='EC2_G5_%s' % app_name,
                    Description='Allow SSH and HTTP for Load Balancing',
                    VpcId=vpc_id,
                    TagSpecifications=[
                        {
                            'ResourceType': 'security-group',
                            'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': 'EC2_G5_%s' % app_name
                                },
                            ]
                        },
                    ],
                )

                ec2.authorize_security_group_ingress(
                    CidrIp='0.0.0.0/0',
                    IpProtocol='tcp',
                    FromPort=22,
                    ToPort=22,
                    GroupId=security_group['GroupId'],
                )

                ec2.authorize_security_group_ingress(
                    CidrIp='0.0.0.0/0',
                    IpProtocol='tcp',
                    FromPort=80,
                    ToPort=80,
                    GroupId=security_group['GroupId'],
                )

                # security_group.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)
                # security_group.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=80, ToPort=80)

                Setting.set('ec2_security_group', security_group['GroupId'])

                # create target group (for instance) => vpc_id

                res = boto3.client(
                    'elbv2',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
                    region=os.environ.get('DATABASE_REGION', 'us-east-1')
                ).create_target_group(
                    Name=("%s-TG" % app_name).replace('_', '-'),
                    Protocol="HTTP",
                    Port=80,
                    VpcId=vpc_id,
                    TargetType='instance',
                    IpAddressType='ipv4',
                )

                created_target_group = res['TargetGroups'][0]

                Setting.set('ec2_target_group', created_target_group['TargetGroupArn'])

                # print(res)

                # print("-----------------------------------------------")

                # create ELB
                # print(public_subnets)
                # print(json.loads(public_subnets))

                res = boto3.client(
                    'elbv2',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
                    region=os.environ.get('DATABASE_REGION', 'us-east-1')
                ).create_load_balancer(
                    Name=('%s-ELB' % app_name).replace('_', '-'),
                    Subnets=list(json.loads(public_subnets)),
                    Scheme='internet-facing',
                    Type='application',
                    IpAddressType='ipv4',
                    SecurityGroups=[
                        security_group['GroupId']
                    ]
                )

                boto3.client(
                    'elbv2',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
                    region=os.environ.get('DATABASE_REGION', 'us-east-1')
                ).create_listener(
                    DefaultActions=[
                        {
                            'TargetGroupArn': created_target_group['TargetGroupArn'],
                            'Type': 'forward',
                        },
                    ],
                    LoadBalancerArn=res['LoadBalancers'][0]['LoadBalancerArn'],
                    Port=80,
                    Protocol='HTTP',
                )

                # print(res)

                Setting.set('ec2_elb', res['LoadBalancers'][0]['LoadBalancerArn'])

                Setting.set('is_setup', "True")

                return redirect('/')

        except Exception as e:
            print(e)
            error = "เกิดข้อผิดพลาดระหว่างกำลังทำงาน"

    public_key = Setting.get('ec2_keypair_public', False)

    if not public_key:
        # create keypair
        keypair_name = "g5_keypair-%s" % uuid.uuid4().hex.upper()[0:6]
        Setting.set("ec2_keypair_name", keypair_name)

        # ec2 = boto3.client('ec2', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'), aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'))
        keypair = ec2.create_key_pair(KeyName=keypair_name)
        Setting.set("ec2_keypair_private", keypair['KeyMaterial'])

        public_key = RSA.import_key(keypair['KeyMaterial']).publickey().export_key('OpenSSH').decode('utf-8')
        Setting.set("ec2_keypair_public", public_key)

    return render_template(
        "setup.html",
        error=error,
        public_key=public_key,
        vpcs=json.dumps(ec2.describe_vpcs().get('Vpcs', [])),
        subnets=json.dumps(ec2.describe_subnets().get('Subnets', []))
    )


@app.route("/login", methods=['POST', 'GET'])
def login():
    error = None
    if request.method == "POST":
        password = os.environ.get('WEB_LOGIN_SECRET', False)
        if not password:
            return redirect('/login')

        if request.form.get('app_password') == password:
            session["is_permit"] = True
            return redirect('/')

        error = "รหัสผ่านไม่ถูกต้อง"

    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session["is_permit"] = False


if __name__ == "__main__":
    app.run(debug=True)
