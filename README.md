# FastAPI_Project

## Brief Description
A sample FastAPI application that uses PostgreSQL for data storage. The application and the database are each containerized with Podman.

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

3. Install the necessary Python packages:

```bash
pip install -r requirements.txt
```

4. Make sure Podman and Podman-compose are installed. These tools are used to create the containers for the application and the database.

5. You need to create a .env file with the following variables:

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


## Common Issues

### PostgreSQL Already Running
If you encounter an error message like `rootlessport listen tcp 0.0.0.0:5432: bind: address already in use`, this means that PostgreSQL is already running on your machine and occupying port 5432. 

You can stop it by running:

```bash
sudo systemctl stop postgresql


