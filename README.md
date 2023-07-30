# FastAPI_Project

## Brief Description
A sample FastAPI application that uses PostgreSQL for data storage. The application and the database are each containerized with Podman.
# INFO FOR SUPERVISORS - RESULTS OF THE TESTS ARE IN JSON FILE
## Prerequisites
- Python 3.8 or later
- Podman
- Podman-compose
- An environment that supports .env files

## Installation Steps

1. Clone the repository:

```bash
git clone https://github.com/humanityshallprevail/FastAPI_Project.git
```

2. Navigate to the cloned project's directory:

```bash
cd FastAPI_Project
```
3. Set up a virtual environment:

```bash
python3 -m venv venv
```

4. Install the necessary Python packages:

```bash
pip install -r requirements.txt
```

5. Make sure Podman and Podman-compose are installed. These tools are used to create the containers for the application and the database.

6. You need to create a .env file with the following variables:

```env
DB_USER=<Your Database User>
DB_PASSWORD=<Your Database Password>
DB_NAME=<Your Database Name>
```

Remember to replace `<Your Database User>`, `<Your Database Password>`, and `<Your Database Name>` with your actual database credentials.

## How to Run/Use the Project

1. Build and start the containers:

```bash
podman-compose up
```

2. Navigate to `http://localhost:8000` in your web browser to interact with the FastAPI application.

# Tests

In our project, we've implemented various tests to ensure the proper functioning of our application. These tests can be found in the `test_api.py` file, and are run automatically within a container when the application is started.

## Test Coverage

1. **Test to create new dish in a submenu**: We have a test to ensure the POST request `/menu/{menu_id}/{submenu_id}` is working correctly. The test simulates the creation of a new dish in a submenu and checks if the response is 200 (OK) and the returned dish is the same as the one we created.

2. **Test to get all menus**: This test sends a GET request to the `/menus` endpoint. It checks if the response status is 200 (OK) and that the response body contains a list of menus.

3. **Test to get a specific menu**: This test sends a GET request to the `/menus/{menu_id}` endpoint with a specific menu_id. It verifies that the status is 200 (OK) and the returned menu matches the menu_id requested.

4. **Test to get all dishes in a submenu**: The test sends a GET request to the `/menu/{menu_id}/{submenu_id}` endpoint. It checks if the response status is 200 (OK) and the returned dishes are indeed from the requested submenu.

5. **Test to check the number of submenus and dishes**: This test ensures that the count functions for submenus and dishes are correctly implemented. It verifies that the returned count from these functions matches the expected count.

6. **Test to check Postman Collection**: We have also integrated our tests with Postman Collection. This enables the third party to easily run the tests by importing the collection into Postman.

## Running the Tests

The tests are run in a container which is started by the command `podman-compose up`. This means that no additional steps are necessary to run the tests - they will automatically be run when the application is started.

## Test Start Time

Our tests are configured to start 30 seconds after the application is up and running. This delay is to allow sufficient time for the application and database to fully initialize and be ready to accept connections and requests.

This is achieved by using the command `sleep 30 && pytest` in our Docker Compose file for the `test` service.

## Test Output

After running the tests, you should see an output in your console similar to this:

```bash
============================= test session starts ==============================
platform linux -- Python 3.11.4, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /app
collected 1 item                                                               

test_api.py .                                                            [100%]

============================== 1 passed in 0.12s ===============================
```
## Common Issues

### PostgreSQL Already Running
If you encounter an error message like `rootlessport listen tcp 0.0.0.0:5432: bind: address already in use`, this means that PostgreSQL is already running on your machine and occupying port 5432. 

You can stop it by running:

```bash
sudo systemctl stop postgresql
```
### Issue: The application doesn't start up at the first podman-compose up command.

Solution:

Sometimes, Docker/Podman services can fail to start if they're not ready yet or if there's a transient error. If you encounter this issue, simply try running podman-compose down followed by podman-compose up again.

Always ensure that you have the latest versions of Podman/Docker and Podman-compose/Docker-compose installed on your system, as this can help avoid some common issues.


