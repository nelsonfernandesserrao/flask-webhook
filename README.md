# Flask Webhook

A lightweight app to automatically deploy a GitHub repository to a VPS. 

## Usage

On commit and pushes to a repository is done, a trigger signal is sent to the Flask app - the app then pulls the contents of the repository afresh, and runs given commands. 

Currently, the commands relate to a Docker Compose build - specifically, Django migrations and the collection of static.  

## GitHub setting

On the relevant repository, navigate to:
- Settings
- Webhooks
- Add webhook

For the payload URL, enter ```http://<VPS-ID>:<PORT-NUMBER>/payload```

e.g. ```http://123.123.123.123:5432/payload```

For content type, select 'application/json'

For events, select 'just the push event'

For additional security, specify a GitHub secret - which must then be added to the .env file

## VPS

On your VPS, either the port selected above needs to be directly exposed via your domain or IP - or a reverse proxy, like Nginx can be used. 

## Private repositories

Private repositories will require slightly different instructions with regard to pulling the repository. 
