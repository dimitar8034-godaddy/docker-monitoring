# docker-monitoring
Flask App with rest API, deployed on docker containers.

This project consists of a Flask Python app that is purely dedicated on CRUD operations. It is deployed on Docker containers using docker-compose.
It is then monitored using Prometheus for overall metrics, Cadvisor for Docker, MySQL exporter for MySQL and Grafana for visualisation. It also
uses Alertmanager to create alerts and forward them to Slack for notification purposes. It also has API's through which it can execute scripts from
a single Docker container to the host itself using a pipeline. It does not have a web interface (apart from monitoring), so it is usually tested via
Postman. 
