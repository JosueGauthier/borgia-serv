<p align="center">
   <img src="../_static/img/borgia-logo-light.png" />
</p>

# Development setup

## Documentation - Installation

Build : 5.1+
Licence : [GNU GPL version 3](https://github.com/borgia-app/Borgia/blob/master/license.txt)

## Introduction

> This guide allows you to install, configure and operate Borgia locally for **development**.

All of the following is independent of the operating system used. It works on Windows, MacOS and Linux.

Be careful, if Python 2 and 3 coexist, python 3 will be called with `python3`. In all cases, check that Python 3 is used for the following commands, by doing: `python --version` or `python3 --version`. Same for `pip` and `pip3` if necessary.

## Installing dependencies

- Python packages: `pip install -r requirements/dev.txt`
- Less: `yarn global add less` or `npm install -g less`

## Configuring `settings.py`

- Copy/paste the `settings.py` file located in `/contrib/development` into `/borgia/borgia`
- Optional : Modify all the variables that must be done by browsing the file.
- Optional : In the case of configuring a Gmail email, with email `GMAIL_EMAIL` and password `GMAIL_PASSWORD`, use:
```python
DEFAULT_FROM_EMAIL = 'GMAIL_EMAIL'
SERVER_EMAIL = 'GMAIL_EMAIL'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'GMAIL_EMAIL'
EMAIL_HOST_PASSWORD = 'GMAIL_PASSWORD'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```
- Optional: Don't forget to configure Gmail to accept "less secure applications".
  
## Migrations and initial data

The following commands must be executed in the `/borgia` application folder.

- `python manage.py makemigrations configurations users shops finances events modules sales stocks`
- `python manage.py migrate`
- `python manage.py loaddata initial`
- `python manage.py collectstatic --clear` indicating "yes" on validation.

Initial data for simulation and development.

- `python manage.py loaddata tests_data`

Changing the password of the first user `AE_ENSAM`:

- `python manage.py shell`
- `from users.models import User`
- `u = User.objects.get(pk=1)`
- `u.set_password("NEW_PASSWORD")`
- `u.save()`
- `exit()`

## Run local server

You can then launch a local development server:

- `python manage.py runserver`

To launch it on a specific port address use:

- `python manage.py runserver localhost:8081`

## Tests

Unit tests are run by `python manage.py test` or `python manage.py test APPLICATION_NAME` to test a particular application.

They must be executed, without errors before each push.