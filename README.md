# Airflow on Heroku

[Airflow](https://github.com/airbnb/airflow) is a great tool to help teams
author, schedule and monitor data workflows. One of the biggest benefits is the
ability to define the workflows in code which means that the workflows can now
be versioned, testable, and maintainable. 

We use Airflow at Heroku to manage data workflows. The benefit for us has been
the ability to use features like
[Pipelines](https://devcenter.heroku.com/articles/pipelines) and [Docker](https://devcenter.heroku.com/articles/docker) to build out a fully
scalable data processing platform.

## Prerequisites

Running Airflow on Heroku requires the use of Docker. To get started, please
follow the necessary Docker installation method for your platform:

* [Mac OS X](https://docs.docker.com/installation/mac/)
* [Ubuntu](https://docs.docker.com/installation/ubuntulinux)
* [Windows](https://docs.docker.com/installation/windows/)
* [Other](https://docs.docker.com/installation/)

Once Docker has been installed for your platform, the assumption is that you
already have the Heroku Toolbelt installed. Please do so before continuing.

The final requirement is the Heroku Docker plugin. To install, issue the
following command in the terminal once you've got docker installed and running:

```
$ heroku plugins:install heroku-docker
```

## Getting Started

Once all of the prerequisities have been met, to get started it's as easy as
cloning this repository and creating a Heroku app:

```
$ git clone https://github.com/heroku/heroku-airflow

$ cd heroku-airflow

$ heroku apps:create airflow-production

$ heroku docker:release
```

At this point, we've got the Heroku app created and the containers built and
deployed. We still need to get the Airflow metadata database setup:

```
$ heroku run bash

$ cd /app/user

$ airflow initdb

$ exit
```

Once you've done this, Airflow is set up and ready to go on Heroku. It's
probably a good idea to restart the app just to make sure that the dynos have
the updated schema in the metadata DB.

```
$ heroku ps:restart
```

## Developing DAGs

These aren't necessarily gotchas when developing your workflows on Heroku but
best practices that we've identified to support your development.

### Connections

Based on Heroku's 12factor app development methodology, we highly recommend that
your connection strings not be saved in the metadata database. Instead, when
building operators in your DAGs, use the environment variable to reference the
connection string, as shown in this example DAG snippet:

```python
from airflow import DAG
from airflow.operators import PostgresOperator

dag = DAG(
        'transformation',
        default_args={ 'owner': 'airflow' })

task1 = PostgresOperator(
            sql='dim_get_count.sql',
            task_id='get_count',
            postgres_conn_id='DATABASE_URL',
            dag=dag)
```

The metadata database will encrypt any connection information you do happen to
save.

### Security & Authentication

This reference project already has SSL baked into it. When you launch your application, the webserver
should redirect to the appropriate endpoint.

In terms of authentication, in the ```airflow_plugins``` directory the project will
require users to use Google OAuth to sign in. Contributions for other Oauth
mechanisms are welcome. It is recommended that a whitelist of individuals that
are able to access the project be added to the OAuth plugin, otherwise anyone
with a google account can access your airflow webserver. 

## TODO

* Create a whitelist for users that have access to the project in Oauth
* Heroku OAuth Strategy
* Instructions on how to generate fernet key and rest of config vars
