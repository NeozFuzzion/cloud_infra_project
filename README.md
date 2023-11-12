# Flask App with Nginx Load Balancing - Docker Compose Project

This Docker Compose project sets up a production-ready environment for a Flask-based website with Nginx for load balancing. Additionally, it includes a working environment with a volume mapped to the local folder for easy development.

## Getting Started

1. Clone this repository to your local machine

2. Run the following command to launch the project:

    ```bash
    docker-compose up
    ```

    This command will build the necessary Docker images and start the containers.

3. Open your web browser and navigate to [http://localhost:80](http://localhost:80) to access the Flask website.

4. Open your web browser and navigate to [http://0.0.0.0:5005](http://0.0.0.0:5005) to access the Flask website on the working environment.

## Project Structure

- `flask_app/`: Contains the Flask application code and the Dockerfile.
- `mysql/`: Contains the dbinit.sql and the Dockerfile for mysql.
- `nginx.conf`: Nginx configuration files.
- `docker-compose.yml`: Docker Compose configuration file.

