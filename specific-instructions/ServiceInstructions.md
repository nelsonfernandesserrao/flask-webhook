To set up an automatic service on a VPS, first ensure that the relevant packages are installed. 

Notably,

```
pip install flask
pip install python-dotenv
```

Then, create a systemd service, following the format in ```webhook.service```. 

```webhook.service``` should be placed in ```/etc/systemd/system/webhook.service```

The service can then be enabled:

```
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable --now webhook.service
```

Logs can be checked using ```journalctl -u webhook.service -f```
