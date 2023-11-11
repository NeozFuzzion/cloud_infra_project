# Use the official MySQL image as the base image
FROM mysql:latest

# Environment variables for MySQL
ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_DATABASE=f1_module

# Expose port 3306 for MySQL
EXPOSE 3306

# SQL script to initialize the database
COPY ./dbinit.sql /docker-entrypoint-initdb.d/

