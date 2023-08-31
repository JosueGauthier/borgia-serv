
How to implement a full logging solution : 

!!!!
tuto complet ::: https://remaster.com/blog/django-centralised-logging-using-elasticsearch-logstash-kibana-elk-filebeat

custom log : https://github.com/gonzalo123/django-logs-filebeat

!!!!

https://github.com/gonzalo123/django-logs

https://github.com/korfuri/django-prometheus

https://github.com/JMousqueton/elk-cec-docker?ref=julien.io

1 Installer un docker grafana 

https://www.techgeeknext.com/tools/docker/install-grafana-using-docker


2 Configurer le Haproxy 

A mettre la config

3 Installer un docker logstash

https://www.elastic.co/fr/downloads/logstash

dans un dossier ~/pipeline/ creer un fichier djangopipeline.conf

et y inserer : 

```conf
input {
  file {
    path => "/borgia-app/Borgia/borgia/log/app.log.json"
    start_position => "beginning"
    codec => "json"
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "app_logs"
  }
}
```


installer elasticsearch 
