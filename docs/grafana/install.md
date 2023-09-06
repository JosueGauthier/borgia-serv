# Grafana monitoring

A Grafana instance to monitor a django application

This installation guide allows you to monitor a django application with Prometheus and analyze its logs with Pormtail and Loki.

> This installation is suitable for any Django application. Notes are added in the case of an installation for the Borgia application


##  Installation of libraries

Inside the virtual environment running your Django application do an installation of the requirements.txt file.

```sh
pip -r requirements.txt
```

## Django application log system

Copy the log folder to the folder containing your entire application

> Borgia : copy it under: /borgia-app/Borgia/borgia

In the settings.py file of your Django application, copy the following lines:

```py

import os
from log.logger import CustomisedJSONFormatter

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(asctime)s] %(levelname)s|%(name)s|%(module)s|%(funcName)s|%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": CustomisedJSONFormatter,
        },
    },
    "handlers": {
        "applogfile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "PATH_TO_YOUR_APP_LOG_FILE/app.log",
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "json",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["applogfile", "console"],
        "level": "DEBUG",
    },
}

```
At the line: "filename": "PATH_TO_YOUR_APP_LOG_FILE/app.log" replace the PATH_TO_YOUR_APP_LOG_FILE with the path to your app.log file.

> Borgia : /borgia-app/Borgia/borgia/log/app.log

Also be careful to include the logger.py file.

Once all these actions have been carried out, you can check that your Django application writes its logs in the desired format and in the app.log file.

To write a log from a your django app :

```py 
import logging
logger = logging.getLogger(__name__)
logger.debug("This is a debug log")
logger.critical("This is a critical log")
```

## Install Grafana

To install Grafana, several options are available to you, an installation bare-metal directly on the OS, via Docker or via a Docker compose file.

```
docker run -d --name=grafana -p 3000:3000 grafana/grafana
```

This command allows you to install grafana in a docker.

Once the container is launched, a grafana server must be available at http://localhost:3000/ 

> Hint : When you establish an SSH connection with the VS Code editor, it is possible with VS Code to use port forwarding:[link](https://code.visualstudio.com/docs/remote/ssh#_forwarding-a-port-creating-ssh-tunnel)
> In your case, create a redirection from port 3000 to port 3000 of your machine.

![image](https://github.com/JosueGauthier/grafana-borgia/assets/20337589/c3ad3042-213f-4099-8ad2-e63ba92736a7)


## Deploy your Grafana instance on the web

To access Grafana from the web it is necessary to use a reverse proxy, NGINX is perfect for this.

Install NGINX:
```sh

sudo apt-get update
sudo apt-get install nginx

```

Create a configuration file, for example, grafana.conf, in the /etc/nginx/sites-available/ directory with the following content:

```
server {
    listen 80;
    server_name grafana.mysite.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    access_log /var/log/nginx/grafana_access.log;
    error_log /var/log/nginx/grafana_error.log;
}
```
Once all this is done create a symlink to /etc/nginx/sites-enabled/

```sh
cd /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/mon_site /etc/nginx/sites-enabled/
```

Check the configuration then restart NGINX, your site should be accessible at the address: grafana.mysite.com
```
sudo nginx -t
sudo systemctl restart nginx
```

--- 

## Virtual machine use case (Proxmox VM)

If you use a virtual machine manager like Proxmox for example, you will need to use a reverse proxy like haproxy to redirect the incoming connection to the site. In haproxy a backend declaration is necessary in haconfig

```cfg
frontend https
        mode http
        # ...
        use_backend grafanamysite if { hdr(host) -i grafana.mysite.com }

# ...

backend grafanamysite
        mode http
        server grafanamysite IPV4_ADRESS_OF_YOUR_VM:80 check source 10.1.0.8

```       
---

## Install Loki and Promtail

Loki is an open source log management system designed to collect, store, and query logs efficiently and scalably.

Promtail is a log harvesting agent developed by Grafana, designed to extract logs from various sources, enrich them, and ship them to Loki. It facilitates centralized collection and search of logs within a cluster or distributed infrastructure.

Promtail is the instance that will fetch the logs in your app.log file and send them to a Loki server which will transmit these logs to a Grafana instance.

For the installation of Loki and Promtail we will use Docker compose.

For this, use the docker-compose.yaml file available in this repo.

In your docker-compose.yaml file you must define the following two volume paths: LOCAL_PATH_TO_YOUR_DJANGO_LOG_FOLDER and PATH_TO_PROMTAIL_CFG.

LOCAL_PATH_TO_YOUR_DJANGO_LOG_FOLDER is the path to your log folder of your django application. PATH_TO_PROMTAIL_CFG is the path to the downloaded promtail-config.yml file.

- LOCAL_PATH_TO_YOUR_DJANGO_LOG_FOLDER/:/log/
- PATH_TO_PROMTAIL_CFG/promtail-config.yml:/etc/promtail/config.yml

This volume binding allows the promtail docker container to use the promtail-config.yml file as a configuration source. This will create a local copy of the file inside your docker container.

The binding of log folders allows promtail to access the log folder dynamically and therefore each time the app.log file is modified, allows promtail to read the changes in this file.

To launch docker compose, go to the folder containing the docker-compose.yaml file and run the command:
```bash
docker-compose -f docker-compose.yaml up
```

If you want to run it in daemon mode (in the background) add -d to the end of the command

If everything goes well when you run the docker ps command, 3 active containers should appear. If nothing is displayed, check if they are not turned off via the docker ps -a command. If one of them is off, there is probably an error, check the logs.

If you try to access the address http://localhost:3100/, a page with: 404 page not found should be displayed

## Add the Grafana container to the loki network

In order to simplify the communication between containers the creation of a bridge between the loki container and the grafana container is necessary. To do this, run the command:

```sh
docker network connect lokigrafana_loki grafana
```

Loki is now visible from the Grafana container. You can test the connection by running the command: ` docker exec -ti containerID1 ping containerID2 `

## Add Loki to Grafana.

Go to your Grafana server page. In the menu access the datasources page, click on add a new datasource, select Loki. In the URL input insert the url containing your loki instance: http://lokigrafana-loki-1:3100. Click on save.

> Be careful, an error may occur and say: "Data source connected, but no labels received. Verify that Loki and Promtail is configured properly"
> This can mean several things:
> - either your Django server has not recently transmitted any logs to Promatail and therefore no logs are detected, to resolve this type of problem simply have Django generate several logs.
> - either your Promtail instance is poorly configured and sending logs in the wrong format. Check your container logs to verify that everything is going well

![image](https://github.com/JosueGauthier/grafana-borgia/assets/20337589/aa2e0851-3bf3-46e9-bab1-8bb973e81640)

![image](https://github.com/JosueGauthier/grafana-borgia/assets/20337589/80c3f7f4-b3f7-4a57-886f-593435fdf871)

You can now access the Explore page and make queries on your logs:


![image](https://github.com/JosueGauthier/grafana-borgia/assets/20337589/92b1dee6-9c63-44b3-b314-c77d57342871)


Here are some simple queries:

This request allows you to display logs in json format
> {job="containerlogs"} | json

This query allows you to filter the logs and display only ERROR level logs.
> {job="containerlogs"} | json json_level="level" | json_level = "ERROR"

This query allows you to filter by displaying logs coming only from the views.py file
> {job="containerlogs"} | json |= "views.py"


If you only want to view a single field for example when django's func_name is = myfunc
Type the query:
> {job="containerlogs"} | json 

Then go to a field or func_name = myfunc click on the icon + this will automatically create the associated query

> {job="containerlogs"} | json | django_funcName=`myfunc` 

![image](https://github.com/JosueGauthier/grafana-borgia/assets/20337589/a4e995fe-f5de-449b-a68c-a54f6faea78b)

---

# Prometheus install 

Like Loki and Promtail, it is possible to install a Prometheus instance in order to monitor the Django application with metrics such as the number of requests per second, response time, latency, etc.

## Install django-prometheus package 

When installing the `requirements.py` file the django-prometheus package was installed [link](https://github.com/korfuri/django-prometheus). To use it, go to the `settings.py` file of your django application.

and modify the following lines:

```py

INSTALLED_APPS = [
   ...
   'django_prometheus',
   ...
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # All your other middlewares go here, including the default
    # middlewares like SessionMiddleware, CommonMiddleware,
    # CsrfViewmiddleware, SecurityMiddleware, etc.
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

```

in the urls.py file:

```py
urlpatterns = [
    ...
    path('', include('django_prometheus.urls')),
]
```
It is also possible to monitor your database. However in my case I get an error.

> Link to Github error: [link](https://github.com/korfuri/django-prometheus/issues/414)

```py

DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

```
Once your django application is correctly configured you can restart your server and go to the url http://your-django-app.com/metrics If everything went correctly you should then observe a list of metrics.

## Prometheus install 

Prometheus can be installed in different ways, a bare-metal installation or via a Docker container or other.

If you are not familiar with Docker, a bare-metal installation is preferred, otherwise install it via Docker: 

`docker run -p 9090:9090 prom/prometheus`

Example of possible bare-metal configuration is as follows.

```cfg
global:
  scrape_interval: 15s
  evaluation_interval: 15s
scrape_configs:
  - job_name: borgiaMonitor
    static_configs:
      - targets:
        - localhost
```

For installation via a docker container you can specify --network="host" to allow the container to access the local network.

docker run --network="host" -d -p 9090:9090 prom/prometheus

You can access the localhost of the machine from the container via the address: 172.17.0.1

> Precision: I encountered quite a few problems accessing http://your-django-app.com/metrics if the site uses HTTPS. To get around this problem I recommend deploying your django application both on the internet and both on the local network. Simply create a new NGINX configuration file with the following content:
```
server {
    listen 80;
    server_name localhost;
    location = /favicon.ico { access_log off; log_not_found off; }
    location /media  {
        alias  PATH_TO_YOUR_APP/static/media;
    }
    location /static {
        alias PATH_TO_YOUR_APP/static/static_root;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}

```

Once your Prometheus server is launched you can see if it responds well by accessing http://localhost:9090/targets
You can now under your grafana panel add a new data source, select Prometheus. In the URL enter: http://172.17.0.1:9090
The address 172.17.0.1 provides access to the machine's local network.

## Add Prometheus data source to Grafana

![image](https://github.com/JosueGauthier/grafana-borgia/assets/20337589/1a81eb5a-da01-4d79-8e29-9831bb937285)


## Creation of the Django monitoring panel
In order to properly visualize the retrieved metrics it is possible to use different dashboards here ready for use:
[link](https://grafana.com/grafana/dashboards/17658-django/)

Simply download it and import it as json into grafana. 

![image](https://github.com/JosueGauthier/grafana-borgia/assets/20337589/7c7c6c88-c2cf-4d9c-8058-cfe5031e2a96)


Select your data source from prometheus and that’s it.

![image](https://github.com/JosueGauthier/grafana-borgia/assets/20337589/1dd09d39-26b7-42db-8480-e07bb9085f7f)

