from flask import Flask, request
from dotenv import load_dotenv
import subprocess, hmac, hashlib, logging, os

load_dotenv(dotenv_path='.env')
app = Flask(__name__)

REPOSITORY_DIRECTORY = os.getenv('REPOSITORY_DIRECTORY')
GITHUB_SECRET = os.getenv('GITHUB_SECRET').encode()

logging.basicConfig(level=logging.INFO, filename='webhook.log')


def verify_signature(payload, header_signature):
    if not header_signature:
        return False
    mac = hmac.new(GITHUB_SECRET, msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, header_signature)


@app.route('/payload', methods=['POST'])
def payload():
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not verify_signature(request.data, signature):
        logging.warning("Invalid signature")
        return 'Invalid signature', 403

    logging.info("Webhook received. Starting deployment...")

    try:
        subprocess.run(["git", "-C", REPOSITORY_DIRECTORY, "reset", "--hard"], check=True)

        subprocess.run(["git", "-C", REPOSITORY_DIRECTORY, "pull"], check=True)

        subprocess.run([
            "docker", "compose", "-f", f"{REPOSITORY_DIRECTORY}/docker-compose.prod.yml",
            "up", "-d", "--build"
        ], check=True)

        subprocess.run([
            "docker", "compose", "-f", f"{REPOSITORY_DIRECTORY}/docker-compose.prod.yml",
            "exec", "-T", "web", "python", "manage.py", "migrate", "--noinput"
        ], check=True)

        subprocess.run([
            "docker", "compose", "-f", f"{REPOSITORY_DIRECTORY}/docker-compose.prod.yml",
            "exec", "-T", "web", "python", "manage.py", "collectstatic", "--no-input", "--clear"
        ], check=True)

        logging.info("Deployment completed successfully.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Deployment failed: {e}")
        return "Error", 500

    return "OK", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5231)
