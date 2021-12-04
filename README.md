# OAL Management
OAL System
AWS EC2 auto-scaling system using Python

Project Status: `Planning`

## Planned Tools
### Development Tools
- [Python](https://www.python.org/) 3.7 or later
- [AWS SDK](https://aws.amazon.com/th/sdk-for-python/) for Python
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- React.js with [Ant Design](https://ant.design/)
- [ngrok](https://ngrok.com/)

### Deployment Tools
- Docker (_Not yet confirmed_)
- Gunicorn
- caddy

## Planned Working Modules

### Python
- [:x:] Auto create Target Group and ELB
- [:x:] Add Instance to Target Group
- [:x:] Create Instance from template and Create Template for creating instance (We need to figure this out quick)
- [:x:] List all EC2 Instance from `Region` or `Tag`
- [:x:] Terminate Instance
- [:x:] Get EC2 CPU Utilization
- [:x:] All features above but in RestAPI
- [:x:] RestAPI Authentication
- [:x:] Storing Setting to DynamoDB or something else lightweight

### Management Website
- [:x:] Login Page
- [:x:] Auto scaling Management
- [:x:] Instances Mangement
- [:x:] Instance/AS Preferences

## Resources
- [Boto3 (AWS SDK)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Flask Python Deployment](https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/#gunicorn)
- 
![aws-cloud-project drawio_2](https://user-images.githubusercontent.com/50010805/144700709-c93189af-17c9-40a0-9783-4837485e67df.png)



