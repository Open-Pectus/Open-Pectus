.. role:: console(code)
   :language: console

Deployment
==========
Open Pectus comprises of two pieces of software:

#. Engine running on a computer which is connected to process equipment
#. Aggregator running centrally

The deployment of these components is described in the following.

.. contents:: Table of Contents
  :local:
  :depth: 3


Deployment of Engines
---------------------
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _Sentry: https://sentry.io

Installation
^^^^^^^^^^^^
Open Pectus supports Windows and Linux and can be installed as follows:

#. Download and install Miniconda_
#. Create a Conda environment, activate it and install Open Pectus by opening the Miniconda prompt and running:

   .. code-block:: console

      conda env create --name openpectus python==3.11
      conda activate openpectus
      pip install openpectus

#. (Optional) Set the :console:`SENTRY_DSN` environment variable:

   To enable the Sentry_ logger, the :console:`SENTRY_DSN` environment variable needs to be set.
   Save the value as an environment variable on your developer pc:

   :console:`setx SENTRY_DSN value`

Running an Engine
^^^^^^^^^^^^^^^^^
With Open Pectus installed it is possible to start an engine using the Miniconda prompt with the :console:`pectus-engine` command.

The following example starts an engine using a UOD at :console:`C:\\process_uod.py` and connects to an aggregator running at :console:`openpectus.com` with SSL encryption.

.. code-block:: console

   conda activate openpectus
   pectus-engine -s -ahn openpectus.com -uod C:\process_uod.py


See :ref:`pectus_engine_command_reference` for documentation of the :console:`pectus-engine` command.



Deployment of Aggregator
------------------------
.. _provided Docker image: https://github.com/Open-Pectus/Open-Pectus/pkgs/container/open-pectus

While it is possible to run an aggregator instance as-is it is highly recommended to use the `provided Docker image`_.

The following instructions assume that the host system runs Ubuntu although Docker is available on many platforms.

Installation
^^^^^^^^^^^^
.. _letsencrypt: https://letsencrypt.org/

Install Docker, nginx and certbot. Docker is used to run the container, nginx is a reverse proxy with SSL support and certbot provides free SSL certificates through letsencrypt_.

A domain name and SSL certificate are not specifically required by Open Pectus. The :ref:`user_authorization` integration does depend on encryption (which requires a domain name) though.

.. code-block:: console

   sudo apt update
   sudo apt install curl apt-transport-https ca-certificates software-properties-common
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt update
   sudo apt install docker-ce nginx-full certbot -y

Configuration
^^^^^^^^^^^^^

Permissions
```````````
To allow non-root user :console:`azureuser` to use Docker:

.. code-block:: console

   sudo usermod -aG docker azureuser
   newgrp

Close terminal session. In a new session the user will be allowed. Test by issuing :console:`docker version`.

Firewall
````````
On systems with :console:`ufw` http and https traffic might be blocked unless allowed:

.. code-block:: console

   sudo ufw allow http
   sudo ufw allow https

Nginx
`````
Edit :console:`/etc/nginx/sites-enabled/default` to be something like :numref:`nginx_configuration`. Restart nginx afterwards to load the configuration :console:`sudo /etc/init.d/nginx restart`.


.. _nginx_configuration:
.. code-block:: yaml
   :caption: Nginx configuration :console:`/etc/nginx/sites-enabled/default`

    server {
        # Delete from here <--
        if ($host = openpectus.com) {
            return 301 https://$host$request_uri;
        } # managed by Certbot
        # --> to here if you do not use ssl.
        listen 80;
        server_name openpectus.com;
        location / {
            proxy_pass http://127.0.0.1:8300;
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }
    }

    server {
        listen 443 ssl;
        server_name openpectus.com;
        ssl_certificate /etc/letsencrypt/live/openpectus.com/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/openpectus.com/privkey.pem; # managed by Certbot
        location / {
            proxy_pass http://127.0.0.1:8300;
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }
    }

Certbot
```````
Acquire SSL certificates using certbot:

.. code-block:: console

   certbot certonly --manual --preferred-challenges dns --register-unsafely-without-email

This command should be run periodically to avoid expiration.

Running an Aggregator
^^^^^^^^^^^^^^^^^^^^^
Commands to pull latest image and run it are given below. The :console:`docker run` command options are:

* :console:`--name openpectus-prd`, allows reference to the the container by name :console:`openpectus-prd` in other Docker commands.
* :console:`-h AZR-PECTUS-PRD`, sets the hostname. The aggregator host name appears in the :ref:`csv_file_format` metadata.
* :console:`-v /home/azureuser/data_prd:/usr/src/app/data`, mounts the directory containing the database to :console:`/home/azureuser/data_prd` on the host. This is necessary in order to persist the database across different versions of the Docker image.
* :console:`-e AZURE_APPLICATION_CLIENT_ID='...'`, :console:`-e AZURE_DIRECTORY_TENANT_ID='...'` and :console:`-e ENABLE_AZURE_AUTHENTICATION='true'` configure the :ref:`user_authorization` integration.
* :console:`-p 0.0.0.0:8300:8300/tcp`, maps port :console:`8300` of the container to the host.
* :console:`6aa`, specifies which image to run. This value is unique for each version of the image.

.. code-block:: console

   # Pull image
   docker pull ghcr.io/open-pectus/open-pectus:main
   # List docker images. Note image id.
   docker image ls
   # In this example the image id started with "6aa"
   docker run --name openpectus-prd \
   -h AZR-PECTUS-PRD \
   -v /home/azureuser/data_prd:/usr/src/app/data
   -e AZURE_APPLICATION_CLIENT_ID='...' \
   -e AZURE_DIRECTORY_TENANT_ID='...' \
   -e ENABLE_AZURE_AUTHENTICATION='true' \
   -p 0.0.0.0:8300:8300/tcp \
   6aa

* List running containers using :console:`docker ps`
* To attach to a running container :console:`docker attach openpectus-prd`
  To detach press :console:`<CTRL>+P+Q`
* To stop the container :console:`docker stop openpectus-prd`
* To delete the container :console:`docker rm openpectus-prd`
* To delete the image :console:`docker image rm 6aa`

Aggregator Database Backup
``````````````````````````

It is possible to do a database backup of a running aggregator by executing the following command on the host running the Docker container:

.. code-block:: console
   
   sqlite3 /home/azureuser/data_prd/open_pectus_aggregator.sqlite3 ".backup '/home/azureuser/tmp.sqlite3'"; mv /home/azureuser/tmp.sqlite3 /home/azureuser/open_pectus_aggregator_prd-$(date +"%Y-%m-%d").sqlite3