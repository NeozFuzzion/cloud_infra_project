-- Create the Formula1 database
CREATE DATABASE IF NOT EXISTS f1_module;
USE f1_module;

-- Create the Teams table
CREATE TABLE IF NOT EXISTS Teams (
    TeamID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Year_Founded INT NOT NULL,
    Total_Pole_Positions INT NOT NULL,
    Total_Race_Wins INT NOT NULL,
    Last_Finishing_Position INT NOT NULL,
    Total_Constructors_Titles INT NOT NULL,
    Total_Fastest_Laps INT NOT NULL
);

-- Create the Drivers table
CREATE TABLE IF NOT EXISTS Drivers (
    DriverID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Age INT NOT NULL,
    Total_Pole_Positions INT NOT NULL,
    Total_Race_Wins INT NOT NULL,
    Total_Points_Scored FLOAT NOT NULL,
    Total_World_Titles INT NOT NULL,
    Total_Fastest_Laps INT NOT NULL,
    Team_name VARCHAR(255) NOT NULL,
    Team_id INT,
    FOREIGN KEY (Team_id) REFERENCES Teams(TeamID)
);
