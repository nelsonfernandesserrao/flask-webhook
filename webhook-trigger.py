from flask import Flask, request
from dotenv import load_dotenv
import subprocess
import hmac
import hashlib
import logging
import os
import shutil

load_dotenv(dotenv_path=".env")
app = Flask(__name__)

REPOSITORY_DIRECTORY = os.getenv("REPOSITORY_DIRECTORY")
GITHUB_SECRET = os.getenv("GITHUB_SECRET", "").encode()

logging.basicConfig(level=logging.INFO, filename="webhook.log")


def verify_signature(payload, header_signature):
    # Validating GitHub webhooks follow the format and structure avaliable here: https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
    if not header_signature:
        return False
    mac = hmac.new(GITHUB_SECRET, msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, header_signature)


@app.route("/payload", methods=["POST"])
def payload():
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(request.data, signature):
        logging.warning("Invalid signature")
        return "Invalid signature", 403

    git_path = shutil.which("git")
    if git_path is None:
        raise RuntimeError("git not found in PATH")

    logging.info("Webhook received. Starting deployment...")

    try:
        subprocess.run(
            [git_path, "-C", REPOSITORY_DIRECTORY, "reset", "--hard"],
            check=True,
            shell=False,  # nosec B603,
        )

        subprocess.run(
            [git_path, "-C", REPOSITORY_DIRECTORY, "pull"],
            check=True,
            shell=False,  # nosec B603
        )

        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                f"{REPOSITORY_DIRECTORY}/docker-compose.prod.yml",
                "up",
                "-d",
                "--build",
            ],
            check=True,
            shell=False,  # nosec B603,
        )

        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                f"{REPOSITORY_DIRECTORY}/docker-compose.prod.yml",
                "exec",
                "-T",
                "web",
                "python",
                "manage.py",
                "migrate",
                "--noinput",
            ],
            check=True,
            shell=False,  # nosec B603,
        )

        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                f"{REPOSITORY_DIRECTORY}/docker-compose.prod.yml",
                "exec",
                "-T",
                "web",
                "python",
                "manage.py",
                "collectstatic",
                "--no-input",
                "--clear",
            ],
            check=True,
            shell=False,  # nosec B603,
        )

        logging.info("Deployment completed successfully.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Deployment failed: {e}")
        return "Error", 500

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5231)
