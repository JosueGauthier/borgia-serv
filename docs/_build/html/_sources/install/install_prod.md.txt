<p align="center">
   <img src="../_static/img/borgia-logo-light.png" />
</p>

# Production setup

## Documentation - Installation

Build : 5.1+
Licence : [GNU GPL version 3](https://github.com/borgia-app/Borgia/blob/master/license.txt)


## Introduction

This guide allows you to install, configure and operate Borgia on a production web server.

The entire installation is done on a server running Linux. The distribution is not important, but the guide is written for a Debian distribution, if this is not the case certain commands (notably the package installation commands) may need to be adapted.

> **This install version use Gunicorn as replacement of uwsgi/wsgi**

The Gunicorn and Nginx part is strongly inspired from [this very good guide](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04) made by : Erin Glass & Jamon Camisso on Digital Ocean.

## First server configuration

- All of the following commands must be carried out using `sudo`, except in exceptional cases to the contrary and explicitly indicated below.

- It is preferable that the entire server is configured on a virtual machine (VM) and not on the physical server directly. It can thus easily be copied, saved or reset.

- In order for the guide to be clearer, it is decided to work in a specific folder named `borgia-app` located at the root of the server (`/borgia-app`). It is obviously possible to change this directory, the commands will therefore have to be modified.

## Before starting

### Update the server:

- `apt-get update`
- `apt-get upgrade`

### Remove Apache if installed:

- `apt-get purge apache2`

### Install necessary packages for the rest of the installation:

- `apt-get install curl apt-transport-https`

### Install all necessary packages:

- `sudo apt install build-essential libssl-dev libffi-dev libjpeg-dev python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl git`

### Creating the PostgreSQL Database and User

- `sudo -u postgres psql`

Inside the `postgres=#` terminal : 

```
CREATE DATABASE borgia;
CREATE USER myprojectuser WITH PASSWORD 'password';
ALTER ROLE myprojectuser SET client_encoding TO 'utf8';
ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE myprojectuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;
\q

```

### Installation of Yarn 

Explicit case of Debian, otherwise see [here](https://yarnpkg.com/lang/en/docs/install/)

- `curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -`
- `echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list`
- `apt-get update && sudo apt-get install yarn`


### Create the Borgia root folder:

- `mkdir /borgia-app`
- `cd /borgia-app`

## Copy of Borgia

In `/borgia-app`:

- `git clone https://github.com/borgia-app/Borgia.git`

Then in `/borgia-app/Borgia`:

- `git checkout tags/RELEASE_TO_UTILISER`
- `git checkout -b production_RELEASE_TO_USE`

### Creating a Python Virtual Environment for your Project

- `python3 -m venv venv`
- `source venv/bin/activate`

## Installation of packages necessary for the application

In `/borgia-app/Borgia` and in the virtual environment install the `prod.txt` requirement file.

- `pip3 install -r requirements/prod.txt`

And finally, outside the virtual environment:

- `yarn global add less`


## Software configuration

### Vital parameters

Copy the file `/borgia-app/Borgia/contrib/production/settings.py` to `/borgia-app/Borgia/borgia/borgia/settings.py` and:

- Modify the `SECRET_KEY =` line by indicating a random private key. For example, [this site](https://randomkeygen.com/) allows you to generate keys, choose at least "CodeIgniter Encryption Keys", for example: `SECRET_KEY = 'AAHHBxi0qHiVWWk6J1bVWCMdF45p6X9t'`.

- Make sure `DEBUG = False`.

- Modify the `ALLOWED_HOSTS =` line by indicating the domains or subdomains accepted by the application. For example: `ALLOWED_HOSTS = ['sibers.borgia-app.com', 'borgia-me.ueam.net']`.


### Database

In the `/borgia-app/Borgia/borgia/borgia/settings.py` file, modify the part:

```python
DATABASES = {
...
}
```

by indicating the name of the database, the user name and the password defined during the configuration of the latter. For example :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'borgia',
        'USER': 'borgiauser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Mail server

- Create a Google email account via the site [Gmail](https://www.google.com/gmail/) and note the user name **MAIL_USER_NAME** and the password **MAIL_PASSWORD**.

In the `/borgia-app/Borgia/borgia/borgia/settings.py` file:

- Modify the lines `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL` and `EMAIL_HOST_USER` by indicating the email **USER_NAME_MAIL**.

- Modify the `EMAIL_HOST_PASSWORD` line by indicating the correct password **MOT_DE_PASSE_MAIL**.

### Administrators

Administrators receive emails in the event of problems using Borgia. For example, if the database is inaccessible, Borgia will automatically send an email to the administrators. These emails are valuable and allow errors to be corrected. Indeed, the debug interface used in development is not accessible here and emails replace it. It is appropriate to add at least one administrator who will store any error emails to then debug or transfer to the Borgia maintainers team.

To add administrators, indicate the email addresses in the `ADMINS=` line in the `/borgia-app/Borgia/borgia/borgia/settings.py` file.


## Database migration

In `/borgia-app/Borgia/borgia` and in the virtual environment:

- `python3 manage.py makemigrations configurations users shops finances events modules sales stocks`
- `python3 manage.py migrate`
- `python3 manage.py loaddata initial`
- `python3 manage.py collectstatic --clear` by accepting the alert

Then, enter the password for the administrator account (which will be deactivated later):

Changing the password of the first user `AE_ENSAM`:

- `python manage.py shell`
- `from users.models import User`
- `u = User.objects.get(pk=1)`
- `u.set_password("NEW_PASSWORD")`
- `u.save()`
- `exit()`


## Intermediate test

### UFW configuration

If you followed the initial server setup guide, you should have a UFW firewall protecting your server. In order to test the development server, you need to allow access to the port you’ll be using.

Create exception for port 8000 : 

- `sudo ufw allow 8000`

### Run the server

The command in the virtual environment `python3 manage.py runserver 0.0.0.0:8000` should start the server and should not report any errors. If this is the case, continue to the rest and end of the installation guide.

In your web browser, visit your server’s domain name or IP address followed by port 8000 : http://server_domain_or_IP:8000 


## Optionnal : testing Gunicorn’s ability to serve the project

The last thing you need to do before leaving your virtual environment is test Gunicorn to make sure that it can serve the application. You can do this by entering the project directory and using gunicorn to load the project’s WSGI module:

- `cd /borgia-app/Borgia/borgia`
- `gunicorn --bind 0.0.0.0:8000 borgia.wsgi`


## Deactivate the venv 

- `deactivate`


## Creating systemd Socket and Service Files for Gunicorn


You have tested that Gunicorn can interact with our Django application, but you should now implement a more robust way of starting and stopping the application server. To accomplish this, you’ll make systemd service and socket files.

The Gunicorn socket will be created at boot and will listen for connections. When a connection occurs, systemd will automatically start the Gunicorn process to handle the connection.

- `sudo nano /etc/systemd/system/gunicorn.socket`

Inside put the following content : 

```conf 

[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target


```

Next, create and open a systemd service file for Gunicorn with sudo privileges in your text editor. The service filename should match the socket filename with the exception of the extension:

- `sudo nano /etc/systemd/system/gunicorn.service`

```conf
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=josue
Group=www-data
WorkingDirectory=/borgia-app/Borgia/borgia
ExecStart=/usr/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          borgia.wsgi:application

[Install]
WantedBy=multi-user.target
```

You can now start and enable the Gunicorn socket. This will create the socket file at /run/gunicorn.sock now and at boot. When a connection is made to that socket, systemd will automatically start the gunicorn.service to handle it:

- `sudo systemctl start gunicorn.socket`
- `sudo systemctl enable gunicorn.socket`

### Checking for the Gunicorn Socket File

- `sudo systemctl status gunicorn.socket`

You should receive an output like this:

```bash 

Output
● gunicorn.socket - gunicorn socket
     Loaded: loaded (/etc/systemd/system/gunicorn.socket; enabled; vendor preset: enabled)
     Active: active (listening) since Mon 2022-04-18 17:53:25 UTC; 5s ago
   Triggers: ● gunicorn.service
     Listen: /run/gunicorn.sock (Stream)
     CGroup: /system.slice/gunicorn.socket

Apr 18 17:53:25 django systemd[1]: Listening on gunicorn socket.

```

Next, check for the existence of the gunicorn.sock file within the /run directory:

- `file /run/gunicorn.sock`
  
```
Output
/run/gunicorn.sock: socket
```

If the systemctl status command indicated that an error occurred or if you do not find the gunicorn.sock file in the directory, it’s an indication that the Gunicorn socket was not able to be created correctly. Check the Gunicorn socket’s logs by typing:

- `sudo journalctl -u gunicorn.socket`
  
Take another look at your /etc/systemd/system/gunicorn.socket file to fix any problems before continuing.


### Testing Socket Activation

- `sudo systemctl status gunicorn`

```
Output
○ gunicorn.service - gunicorn daemon
     Loaded: loaded (/etc/systemd/system/gunicorn.service; disabled; vendor preset: enabled)
     Active: inactive (dead)
TriggeredBy: ● gunicorn.socket

```

If it's OK you can run : 

- `sudo systemctl daemon-reload`
- `sudo systemctl restart gunicorn`


## Configure Nginx to Proxy Pass to Gunicorn

- `sudo nano /etc/nginx/sites-available/borgia`

```
server {
   
    listen 80;
    server_name YOUR.DOMAINNAME.COM;

    location = /favicon.ico { access_log off; log_not_found off; }


    location /media  {
        alias /borgia-app/Borgia/borgia/static/media;
    }

    location /static {
        alias /borgia-app/Borgia/borgia/static/static_root;
    }

    
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }

}


```

- `sudo ln -s /etc/nginx/sites-available/borgia /etc/nginx/sites-enabled`

Check the nginx configuration : 

- `sudo nginx -t`

- `sudo systemctl restart nginx`

### Allow Nginx through the UFW firewall

- `sudo ufw delete allow 8000`
- `sudo ufw allow 'Nginx Full'`


You should now be able to go to your server’s domain or IP address to view your application.


>Note: After configuring Nginx, the next step should be securing traffic to the server using SSL/TLS. This is important because without it, all information, including passwords are sent over the network in plain text.
>If you have a domain name, the easiest way to get an SSL certificate to secure your traffic is using Let’s Encrypt. Follow [this guide](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-22-04) to set up Let’s Encrypt with Nginx on Ubuntu 22.04. 
>Follow the procedure using the Nginx server block you created in this guide.


## Save to git

Finally, you should save this entire configuration on a production branch (sudo not necessary here):

- `git add.`
- `git commit -m "production"`

> **It is not recommended to push this branch as it could contain sensitive information like keys and passwords.**
