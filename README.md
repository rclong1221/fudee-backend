# fudee

fudee, a social planning application for the bar and restaurant industry.  Made by industry workers, for industry workers.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/django/django/)
[![Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Basic Commands

### Setting Up Your Users

-   To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

-   To create a **superuser account**, use this command:

        ``` bash
        python manage.py createsuperuser
        ```

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    ``` bash
    mypy fudee
    ```

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    ``` bash
    coverage run -m pytest
    coverage html
    open htmlcov/index.html
    ```


#### Running tests with pytest

    ``` bash
    pytest
    ```

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

### Celery

This app comes with Celery.

To run a celery worker:

``` bash
cd fudee
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.

### Email Server

In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server [MailHog](https://github.com/mailhog/MailHog) with a web interface is available as docker container.

With MailHog running, to view messages that are sent by your application, open your browser and go to `http://127.0.0.1:8025`

### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

## Deployment

The following details how to deploy this application.

### Docker

#### Development

Build and run
``` bash
docker-compose -f local.yml build
docker-compose -f local.yml up -d
```

Python Django Shell
``` bash
docker-compose -f local.yml run --rm django python manage.py shell
```

Check logs
``` bash
docker-compose -f local.yml logs
```

Scale application
``` bash
docker-compose -f local.yml up --scale django=4
docker-compose -f local.yml up --scale celeryworker=2
```

#### Production

Build and run
``` bash
docker-compose -f production.yml build
docker-compose -f production.yml up -d
```

Python Django Shell
``` bash
docker-compose -f production.yml run --rm django python manage.py shell
```

Check logs
``` bash
docker-compose -f production.yml logs
```

Scale application
``` bash
docker-compose -f production.yml up --scale django=4
docker-compose -f production.yml up --scale celeryworker=2
```

### Example

![Search](https://raw.githubusercontent.com/rclong1221/project-assets/main/fudee-backend/search.png)