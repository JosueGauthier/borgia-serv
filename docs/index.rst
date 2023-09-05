Welcome to borgia's documentation!
==================================

.. image:: ./_static/img/borgia-logo-light.png
   :width: 400
   :alt: Borgia logo


| Current Version : 5.2.0 Licence :
| Master branch: |Build Status|
| Develop branch: |Build Status|

Introduction
============

Borgia is a software to help you manage your student association. 
With it, you can sell products, organize events, keep track of your stocks, etc… 
It will be your best ally to develop your possibilities for your student association.

Borgia has currently been used by several thousand students for more than 2 years, particularly in Arts et Métiers centers <https://artsetmetiers.fr/>`__.
We are actively looking for people to participate in this great adventure, do not hesitate to contact us directly. We have big plans for Borgia (a mobile application, new features, etc.)!

Finally, if you have an idea or have noticed a bug, don't hesitate to open an `issue <https://github.com/borgia-app/Borgia/issues>`__ or even a `pull request< https://github.com/borgia-app/Borgia/pulls>`__.

Installation
============

-  Development :
   `here <https://github.com/borgia-app/Borgia-docs/blob/master/tutorials/dev_install.md>`__
-  Production :
   `here <https://github.com/borgia-app/Borgia-docs/blob/master/tutorials/prod_install.md>`__

Documentation
=============

Documentation are currently in writing-phase. Some ressources are
available `here <https://github.com/borgia-app/Borgia-docs>`__.

Dependency
==========

Borgia base dependency :

-  Django : Borgia run with the django framework
-  django-bootstrap-form : To use bootstrap with django
-  django-static-precompiler : For static files
-  djangorestframework : For API
-  openpyxl : For excel manipulation
-  Pillow : For users images

Developing and Contributing
===========================

We'd love to get contributions from you! For a quick guide to getting your system setup for developing, take a look at the section “To Start”
Once you are up and running, take a look at the `CONTRIBUTING.md <https://github.com/borgia-app/Borgia/CONTRIBUTING.md>`__ to see how to get your changes merged in.


.. |Build Status| image:: https://github.com/borgia-app/Borgia/actions/workflows/main.yml/badge.svg?branch=master


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   test
   tutorial/shop_tutorial
   install/install_dev
   install/install_prod
   getstarted/getstarted


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
