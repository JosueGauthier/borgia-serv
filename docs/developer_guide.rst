Developer Guide
================

Welcome to the Borgia developer guide. 
These documents teach you how to use Borgia as a developer.

You will learn in this guide : 

- Installation for development
- Installation for a production solution
- How to use production Ansible script
- Installation of a logging and monitoring solution based on Grafana
- Structure and organization of the project

Borgia basic dependencies are : 

- Django : Borgia run with the django framework
- django-bootstrap-form : To use bootstrap with django
- django-static-precompiler : For static files
- djangorestframework : For API
- openpyxl : For excel manipulation
- Pillow : For users images

If you want to develop your own solution or extension from Borgia, do not hesitate to make a fork of this project, it is under the GNU GPL v3 license.

The basic concepts to know before embarking on development are:

- Principles of web development
- Web development tools: HTML, CSS, JavaScript
- Basics of Python and the Django framework.
- Knowledge of databases (PostgreSQL)

But no problem if you don't master everything, Borgia is a great learning opportunity.

.. toctree::
   install/install_dev
   install/install_prod
   grafana/install
