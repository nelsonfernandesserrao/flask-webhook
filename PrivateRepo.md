In order to set up pulling a repository (if that repository is private), SSH authentication is needed. 

## Step 1: Generate SSH Key
On the VPS, generate an SSH key.

```ssh-keygen -t ed25519 -C "vps-GitHub-access-key"```

Accept the default location (usually the path below), and copy the public key. 

```cat ~/.ssh/id_ed25519.pub```

## Step 2: Add key to GitHub

Add a deploy key for the required repository, under Settings > Deploy Keys.

## Step 3: Verify connection

On the VPS, run the following command. 

```ssh -T git@github.com```

## Step 4: Set up repo on VPS

Navigate to location on VPS. 

```git remote set-url origin git@gihub.com:<USERNAME>/<REPOSITORY>.git```
