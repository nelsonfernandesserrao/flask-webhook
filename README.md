# Flask Webhook

A lightweight app to automatically deploy a GitHub repository to a VPS. 

## Usage

On commit and pushes to a repository is done, a trigger signal is sent to the Flask app - the app then pulls the contents of the repository afresh, and runs given commands. 

Currently, the commands relate to a Docker Compose build - specifically, Django migrations and the collection of static.  