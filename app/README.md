# Drones REST app

In order to run the application.

1. Create a virtual environment:

    ```
    python3 -m venv venv
    ```

2. Activate the virtual environment:
    ```
    source venv/bin/activate
    ```

3. Install the dependencies from requirements file:
    ```
    pip install -r requirements.txt
    ```

4. Change the current directory to "app":
    ```
    cd app
    ```

5. Execute Django migration command to create a SQLite database
    ```
    python manage.py migrate
    ```

6. (Optional) You can create superuser with and follow the instruction, execute:
    ```
    python manage.py createsuperuser
    ```

    So you can access to Django administration dashboard under: "/admin/"

7. Run the development server
    ```
    python manage.py runserver
    ```

8. Open in the webbrowser the URL "http://localhost:8000/api/main/"

9. The tests can be run with:
    ```
    python manage.py test
    ```

    And with code coverage:
    ```
    coverage run --source='.' manage.py test && coverage report
    ```

10. An optional fixture can be imported to the database by running:
    ```
    python manage.py loaddata test_data
    ```

    This fixture is imported when the tests are executed.

11. There is a custom command called "check_drones_baterry" related to the task, can by run:
    ```
    python manage.py check_drones_baterry
    ```


The application has made with:

1. [Python 3.10](https://www.python.org/)
2. [Django 4.1](https://www.djangoproject.com/)
3. [Django REST Framwork 3.14](https://www.django-rest-framework.org/)
