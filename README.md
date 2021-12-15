# OAL Management
OAL System
AWS EC2 group rolling update system using Python boto3, Flask and friends

Project Status: `Finished`

![aws-cloud-project drawio (1)](https://user-images.githubusercontent.com/50010805/144700727-8ed46fd7-9bb4-49a2-b02d-0a6434207274.png)

## Disclaimer
This project code just not good as it should be due to time limit.
Do not use this project as production service but you can still use this project as a concept or for designing your own system.

## Information

### Goals (Pros)
- lightweight can be deploy on anywhere any resource size
- support multiple backup nodes (redundancy)
- auto recovery when error eccoured
- less user's config as much as possible
- Support deployment from private Github Repository

### Cons
- Slow due to system need to wait every resource to create/update synchronously
- Deployment Server need to support `Docker` visualization
- Need to learn about creating deployment `User Data`
- `User Data` hard to test (AWS's problem ?)
- Not support `HTTPS`, recommend to use `Cloudfront`

### Deployment
#### Requirements
- AWS IAM User with `Access Key` and `Secret Key`
- AWS IAM User permission allow to access resource `DynamoDB`, `EC2`, `VPC` and `ELBv2`
- Pre-created `VPC` with at least 2 `Public Subnet`
- Website application with `User Data` that using `HTTP` port `80`
- Internet connection that can be connect to AWS console

#### Setup
1. Clone this repository (aka. Download)
2. setup your `.env` by copy `.env.example` to `.env`
3. Build docker image using `Dockerfile`
```
docker build -t oal-management <this repository path on your system>
```
4. Run Docker image on your system _Recommend to use webserver like nginx as reverseproxy or caddy_
```
docker run -p 80:8000 -d oal-management
```
5. Open Web browser using your server IP Address (default protocol is `http` port `80`)
6. Setup your system :)

#### Example User Data
```
yum update -y
amazon-linux-extras install -y php7.2
yum install -y httpd git
systemctl start httpd
systemctl enable httpd
usermod -a -G apache ec2-user
chown -R ec2-user:apache /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} \;
find /var/www -type f -exec chmod 0664 {} \;

sudo su ec2-user -c "git clone git@github.com:n0uur/sample-website-007.git /var/www/html/"
```

## Tools
### Development Tools
- [Python](https://www.python.org/) 3.7 or later
- [AWS SDK](https://aws.amazon.com/th/sdk-for-python/) for Python
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)

### Deployment Tools
- Docker
- Gunicorn

## Planned Working Modules

### Python
- [:white_check_mark:] Auto create Target Group and ELB
- [:white_check_mark:] Add Instance to Target Group
- [:white_check_mark:] Create Key pair
- [:white_check_mark:] Create Instance from template and Create Template for creating instance (We need to figure this out quick)
- [:white_check_mark:] List all EC2 Instance from `Region` or `Tag`
- [:white_check_mark:] Terminate Instance
- [:white_check_mark:] All features above but in RestAPI
- [:white_check_mark:] RestAPI Authentication
- [:white_check_mark:] Storing Setting to `DynamoDB`

### Management Website
- [:white_check_mark:] Login Page
- [:white_check_mark:] Auto scaling Management
- [:white_check_mark:] Instances Mangement
- [:white_check_mark:] Instance Setup Preferences

## Resources
- [Boto3 (AWS SDK)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Flask Python Deployment](https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/#gunicorn)

## Developers (in Thai)

| รหัสนักศึกษา | ชื่อ-นามสกุล | Github |
|--|--|--|
| 62070002 | นายกฤตณัฏฐ์ ศิริพรนพคุณ | [n0uur](https://github.com/n0uur) |
| 62070016 | นายกิตติภัค พนารินทร์ | [hikariz01](https://github.com/hikariz01) |
| 62070085 | นายธเนศ สุขได้พึ่ง | [Tanate62070085](https://github.com/Tanate62070085) |
| 62070088 | นายธวัชชัย ฮานอน | [Hanon088](https://github.com/Hanon088) |
| 62070091 | นายธัชวุฒิ วิจิตรบรรจง | [FuMiRiO](https://github.com/FuMiRiO) |

<hr>

__Introduction to Cloud Technology__ (06016335)

_Faculty of Information Technology, King Mongkut's Institute of Technology Ladkrabang_ 

_2021_
