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

## First server configuration

- All of the following commands must be carried out using `sudo`, except in exceptional cases to the contrary and explicitly indicated below.

- It is preferable that the entire server is configured on a virtual machine (VM) and not on the physical server directly. It can thus easily be copied, saved or reset.

- In order for the guide to be clearer, it is decided to work in a specific folder named `borgia-app` located at the root of the server (`/borgia-app`). It is obviously possible to change this directory, the commands will therefore have to be modified.

## Before starting

### Update the server:

- `apt-get update`
- `apt-get upgrade`

### Remove Apache if installed:

`apt-get purge apache2`

### Install necessary packages for the rest of the installation:

`apt-get install curl apt-transport-https`

### Install basic python packages:

`apt-get install build-essential libpq-dev python-dev libjpeg-dev libssl-dev libffi-dev`

### Installing nginx, postgres & git:

- `apt-get install postgresql postgresql-contrib nginx git`

### Installing pip for python3:

- Ensure that the `python3 --version` command returns a version greater than or equal to `3.5` (default version on Debian 9). If not, reinstall `python3`.
- `apt-get install python3-pip`

TODO A voir ????

---

### Installation de Yarn (cas explicite de Debian, sinon voir [ici](https://yarnpkg.com/lang/en/docs/install/)):

-   `curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -`
-   `echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list`
-   `apt-get update && sudo apt-get install yarn`

---

### Create the Borgia root folder:

`mkdir /borgia-app`

---

## Setting up the Python virtual environment

### Installing `virtualenv`

- `pip3 install virtualenv virtualenvwrapper`
- In `/borgia-app`, create a virtual environment: `virtualenv borgiaenv`.
- If the virtualenv command does not exist, do: `ln -s /usr/local/bin/virtualenv* /usr/bin/`
  
### How the virtual environment works

- In the remainder of the tutorial, when commands are carried out in the virtual environment you must make sure you are there. To be safe, the command prompt indicates the environment name in parentheses (here `(borgiaenv)` for example).
- When requested, the command `source /borgia-app/borgiaenv/bin/activate` allows you to enter the environment. And `deactivate` to exit.

---

## Installation and configuration of the database

**This part should not be done in the virtual environment.**

### Select postgres user

`su - postgres`

The rest of the commands must be carried out in the postgres command prompt. `psql` allows you to activate the prompt and `\q` allows you to exit it. Please note, all commands end with a `;`.

### Creating the database

**DB_PASSWORD** is the password chosen to connect to the database. Be careful to change it in all commands.

In the postgres prompt:

- `CREATE DATABASE borgia;`
- `CREATE USER borgiauser WITH PASSWORD 'MOT_DE_PASSE_DB';`
- `GRANT ALL PRIVILEGES ON DATABASE borgia TO borgiauser;`

---

## Copy of Borgia

In `/borgia-app`:

- `git clone https://github.com/borgia-app/Borgia.git`

Then in `/borgia-app/Borgia`:

- `git checkout tags/RELEASE_TO_UTILISER`
- `git checkout -b production_RELEASE_TO_USE`

---


## Installation of packages necessary for the application

In `/borgia-app/Borgia` and in the virtual environment:

- `pip3 install -r requirements/prod.txt`

And finally, outside the virtual environment:

- `yarn global add less`


--- 

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

---

## Database migration

In `/borgia-app/Borgia/borgia` and in the virtual environment:

- `python3 manage.py makemigrations configurations users shops finances events modules sales stocks`
- `python3 manage.py migrate`
- `python3 manage.py loaddata initial`
- `python3 manage.py collectstatic --clear` by accepting the alert

Then, enter the password for the administrator account (which will be deactivated later):

- `python3 manage.py shell`,
- `from users.models import User`,
- `u = User.objects.get(pk=2)`,
- `u.set_password(NEW_PASSWORD)`.
- `u.save()`
- `exit()`

--- 
## Intermediate test

The command in the virtual environment `python3 manage.py runserver 0.0.0.0:8000` should start the server and should not report any errors. If this is the case, continue to the rest and end of the installation guide.


---

## End of server configuration

The following files may already exist in the copied folder. If so, just modify them.


TODO a modif 
#### Installation de nginx et wsgi

Dans l'environnement virtuel :

-   `pip3 install uwsgi`

-   Copier le fichier `/borgia-app/Borgia/contrib/production/borgia.wsgi` dans `/borgia-app/Borgia/borgia`. Le modifier si vous avez changer le répertoire de base.

-   Copier le fichier `/borgia-app/Borgia/contrib/production/wsgi.py` dans `/borgia-app/Borgia/borgia/borgia` (attention au sous-dossier ici).

-   Copier le fichier `/borgia-app/Borgia/contrib/production/uwsgi_params` dans `/borgia-app/Borgia/borgia`.

-   Copier le fichier `/borgia-app/Borgia/contrib/production/borgia_nginx.conf` dans `/borgia-app/Borgia/borgia`. Modifier les chemins si nécessaire et changer le nom de serveur "SERVEUR_NAME" qui correspond au domaine utilisé (par exemple `.borgia-app.com`).

-   Activer la configuration nginx en créant un lien symbolique :

`ln -s /borgia-app/Borgia/borgia/borgia_nginx.conf /etc/nginx/sites-enabled/`

-   Redémarrer nginx :

`service nginx restart`

#### Test intermédiaire

La commande `uwsgi --socket borgia.sock --module borgia.wsgi --chmod-socket=666` doit lancer le serveur sans problème (à condition d'avoir quelques modules python installés, le virtual env ne sera utilisé qu'ensuite). Si c'est le cas, c'est bientôt terminé !

#### Suite et fin de la configuration de nginx

-   Copier le fichier `/borgia-app/Borgia/contrib/production/borgia_uwsgi.ini` dans `/borgia-app/Borgia/borgia`. Le modifier si vous avez changer le répertoire de base.

-   Ce fichier peut être testé avec la commande `uwsgi --socket borgia.sock --module borgia.wsgi --ini borgia_uwsgi.ini`

#### Mode Empereur de nginx

Ce mode permet à Nginx de gérer automatiquement et de manière dynamique le projet. La suite n'est pas à effectuer dans l'environnement virtuel.

-   `mkdir /etc/uwsgi`
-   `mkdir /etc/uwsgi/vassals`
-   `ln -s /borgia-app/Borgia/borgia/borgia_uwsgi.ini /etc/uwsgi/vassals/`

#### Démarrer uwsgi au démarrage du serveur

Dernier point, toujours en sudo en dehors de l'environnement virtuel.
Ajoutez cette ligne à la fin du fichier (avant le `exit 0`) `/etc/rc.local`:

`/usr/local/bin/uwsgi --emperor /etc/uwsgi/vassals`

### Save to git

Finally, you should save this entire configuration on a production branch (sudo not necessary here):

- `git add.`
- `git commit -m "production"`

**It is not recommended to push this branch as it could contain sensitive information like keys and passwords.**

---