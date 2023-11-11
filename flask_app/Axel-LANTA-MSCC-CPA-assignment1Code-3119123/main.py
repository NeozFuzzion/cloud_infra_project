import datetime
from flask import Flask, render_template, request, redirect, url_for

import google.oauth2.id_token
from google.auth.transport import requests

import mysql.connector
import os

app = Flask(__name__)

# Access MySQL connection details from environment variables
mysql_host = os.environ.get("MYSQL_HOST", "localhost")
mysql_port = os.environ.get("MYSQL_PORT", 3306)
mysql_database = os.environ.get("MYSQL_DATABASE", "f1_module")
mysql_user = os.environ.get("MYSQL_USER", "axel")
mysql_password = os.environ.get("MYSQL_PASSWORD", "axel")

# Establish a MySQL connection
db_config = {
    'host':mysql_host,
    'port':mysql_port,
    'database':mysql_database,
    'user':mysql_user,
    'password':mysql_password
}




# get access to a request adapter for firebase as we will need this to authenticate users
firebase_request_adapter = requests.Request()




def createDriver(driver_info):
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    try:
        # Check if the driver name already exists
        query = "SELECT * FROM Drivers WHERE Name = %s"
        cursor.execute(query, (driver_info["Driver_name"],))
        existing_driver = cursor.fetchone()

        if existing_driver:
            return -1  # If an entity with the same name exists, return -1

        # Check if the team exists
        query = "SELECT * FROM Teams WHERE TeamID = %s"
        cursor.execute(query, (int(driver_info["Team_id"]),))
        team = cursor.fetchone()

        if not team:
            return 0  # If the team doesn't exist, return 0

        # Create a new driver entity
        query = """
            INSERT INTO Drivers (Name, Age, Total_Pole_Positions, Total_Race_Wins,
                                 Total_Points_Scored, Total_World_Titles,
                                 Total_Fastest_Laps, Team_name, Team_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            driver_info['Driver_name'],
            int(driver_info['Age']),
            int(driver_info["Total_Pole_Positions"]),
            int(driver_info["Total_Race_Wins"]),
            float(driver_info["Total_Points_Scored"]),
            int(driver_info["Total_World_Titles"]),
            int(driver_info["Total_Fastest_Laps"]),
            team["Name"],
            team["TeamID"]
        )
        cursor.execute(query, values)

        # Commit the changes to the database
        cnx.commit()

        return 1  # Successfully created the driver

    except Exception as e:
        print(f"Error creating driver: {e}")
        return -2  # An error occurred
    finally:
        # Close the cursor and MySQL connection
        cursor.close()
        cnx.close()

def createTeam(team_info):
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    try:
        # Check if the team name already exists
        query = "SELECT * FROM Teams WHERE Name = %s"
        cursor.execute(query, (team_info["Name"],))
        existing_team = cursor.fetchone()

        if existing_team:
            return -1  # If an entity with the same name exists, return -1

        # Create a new team entity
        query = """
            INSERT INTO Teams (Name, Year_Founded, Total_Pole_Positions, Total_Race_Wins,
                               Last_Finishing_Position, Total_Constructors_Titles,
                               Total_Fastest_Laps)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            team_info['Name'],
            int(team_info["Year_Founded"]),
            int(team_info["Total_Pole_Positions"]),
            int(team_info["Total_Race_Wins"]),
            int(team_info["Last_Finishing_Position"]),
            int(team_info["Total_Constructors_Titles"]),
            int(team_info["Total_Fastest_Laps"]),
        )
        cursor.execute(query, values)

        # Commit the changes to the database
        cnx.commit()

        return 1  # Successfully created the team

    except Exception as e:
        print(f"Error creating team: {e}")
        return -2  # An error occurred
    finally:
        # Close the cursor and MySQL connection
        cursor.close()
        cnx.close()


def retrieveDriverInfo():
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    try:
        # Retrieve all driver entities from the MySQL database
        query = "SELECT * FROM Drivers"
        cursor.execute(query)
        drivers = cursor.fetchall()

        return drivers

    except Exception as e:
        print(f"Error retrieving driver information: {e}")
        return None
    finally:
        # Close the cursor and MySQL connection
        cursor.close()
        cnx.close()

def retrieveTeamInfo():
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    try:
        # Retrieve all team entities from the MySQL database
        query = "SELECT * FROM Teams"
        cursor.execute(query)
        teams = cursor.fetchall()

        return teams

    except Exception as e:
        print(f"Error retrieving team information: {e}")
        return None
    finally:
        # Close the cursor and MySQL connection
        cursor.close()
        cnx.close()

def updateDriver(driver_info, driver_id):
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    try:
        # Check if the target driver exists
        query = f"SELECT * FROM Drivers WHERE DriverID = {driver_id}"
        cursor.execute(query)
        existing_driver = cursor.fetchone()
        
        if not existing_driver:
            return -3  # Driver not found
        
        # Check if the new driver name already exists for a different driver
        query = f"SELECT * FROM Drivers WHERE Name = '{driver_info['Driver_name']}' AND DriverID != {driver_id}"
        cursor.execute(query)
        duplicate_name = cursor.fetchone()
        
        if duplicate_name:
            return -1  # Duplicate driver name
        
        # Check if the target team exists
        query = f"SELECT * FROM Teams WHERE TeamID = {driver_info['Team_id']}"
        cursor.execute(query)
        target_team = cursor.fetchone()
        
        if not target_team:
            return 0  # Team not found
        
        # Update the driver's information
        update_query = f"""
            UPDATE Drivers
            SET Name = '{driver_info['Driver_name']}',
                Age = {int(driver_info['Age'])},
                Total_Pole_Positions = {int(driver_info['Total_Pole_Positions'])},
                Total_Race_Wins = {int(driver_info['Total_Race_Wins'])},
                Total_Points_Scored = {float(driver_info['Total_Points_Scored'])},
                Total_World_Titles = {int(driver_info['Total_World_Titles'])},
                Total_Fastest_Laps = {int(driver_info['Total_Fastest_Laps'])},
                Team_name = '{target_team['Name']}',
                Team_id = {target_team['TeamID']}
            WHERE DriverID = {driver_id}
        """
        cursor.execute(update_query)
        cnx.commit()

        return 1  # Successfully updated

    except Exception as e:
        print(f"Error updating driver information: {e}")
        return -4 # Error MySQL
    finally:
        # Close the cursor and MySQL connection
        cursor.close()
        cnx.close()

def updateTeam(team_info, team_id):
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    try:
        # Check if the target team exists
        query = f"SELECT * FROM Teams WHERE TeamID = {team_id}"
        cursor.execute(query)
        existing_team = cursor.fetchone()
        
        if not existing_team:
            return -2  # Team not found
        
        # Check if the new team name already exists for a different team
        query = f"SELECT * FROM Teams WHERE Name = '{team_info['Name']}' AND TeamID != {team_id}"
        cursor.execute(query)
        duplicate_name = cursor.fetchone()
        
        if duplicate_name:
            return -1  # Duplicate team name
        
        # Update the team's information
        update_query = f"""
            UPDATE Teams
            SET Name = '{team_info['Name']}',
                Year_Founded = {int(team_info['Year_Founded'])},
                Total_Pole_Positions = {int(team_info['Total_Pole_Positions'])},
                Total_Race_Wins = {int(team_info['Total_Race_Wins'])},
                Last_Finishing_Position = {int(team_info['Last_Finishing_Position'])},
                Total_Constructors_Titles = {int(team_info['Total_Constructors_Titles'])},
                Total_Fastest_Laps = {int(team_info['Total_Fastest_Laps'])}
            WHERE TeamID = {team_id}
        """
        cursor.execute(update_query)
        
        # Update the team name for drivers in the same team
        if existing_team['Name'] != team_info['Name']:
            update_driver_query = f"""
                UPDATE Drivers
                SET Team_name = '{team_info['Name']}'
                WHERE Team_id = {team_id}
            """
            cursor.execute(update_driver_query)
            
        cnx.commit()

        return 1  # Successfully updated

    except Exception as e:
        print(f"Error updating team information: {e}")
        return -4
    finally:
        # Close the cursor and MySQL connection
        cursor.close()
        cnx.close()


def queriesDriver(form):
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    attribute_id = int(form["attribute"])
    op_id = int(form["operation"])
    attribute = ""
    op = ""
    
    if attribute_id == 1:
        searching = str(form['searching'])
        attribute = "Name"
    elif attribute_id == 8:
        searching = str(form['searching'])
        attribute = "Team_name"
    else:
        try:
            if attribute_id == 5:
                searching = float(form['searching'])
                attribute = "Total_Points_Scored"
            else:
                searching = int(form['searching'])
                if attribute_id == 2:
                    attribute = "Age"
                elif attribute_id == 3:
                    attribute = "Total_Pole_Positions"
                elif attribute_id == 4:
                    attribute = "Total_Race_Wins"
                elif attribute_id == 6:
                    attribute = "Total_World_Titles"
                elif attribute_id == 7:
                    attribute = "Total_Fastest_Laps"
                else:
                    return -2
        except ValueError:
            return -2
    
    op_mapping = {
        1: '=',
        2: '<',
        3: '>',
        4: '>=',
        5: '<=',
        6: '!='
    }
    
    op = op_mapping.get(op_id, None)
    
    if op is None:
        return -2  # Invalid operation
    
    try:
        query = f"SELECT * FROM Drivers WHERE {attribute} {op} %s"
        cursor.execute(query, (searching,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
        return -2
    finally:
        # Close the cursor and MySQL connection
        cursor.close()
        cnx.close()


def queriesTeam(form):
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    attribute_id = int(form["attribute"])
    op_id = int(form["operation"])
    attribute = ""
    op = ""
    
    if attribute_id == 1:
        attribute = "Name"
        searching = str(form['searching'])
    else:
        try:
            searching = int(form['searching'])
            if attribute_id == 2:
                attribute = "Year_Founded"
            elif attribute_id == 3:
                attribute = "Total_Pole_Positions"
            elif attribute_id == 4:
                attribute = "Total_Race_Wins"
            elif attribute_id == 5:
                attribute = "Last_Finishing_Position"
            elif attribute_id == 6:
                attribute = "Total_Constructors_Titles"
            elif attribute_id == 7:
                attribute = "Total_Fastest_Laps"
            else:
                return -2
        except ValueError:
            return -2
    
    op_mapping = {
        1: '=',
        2: '<',
        3: '>',
        4: '>=',
        5: '<=',
        6: '!='
    }
    
    op = op_mapping.get(op_id, None)
    
    if op is None:
        return -2  # Invalid operation
    
    try:
        query = f"SELECT * FROM Teams WHERE {attribute} {op} %s"
        cursor.execute(query, (searching,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
        return -2
    finally:
        # Close the cursor and MySQL connection
        cursor.close()
        cnx.close()

@app.route('/creator_driver')
def creatorDriverInfo():
    id_token = request.cookies.get("token")
    
    # if we have an ID token then verify it against firebase if it doesn't check out then redirect to root
    if id_token:
        error_message = None
        success_message = None
        teams_data=[]
        error_state=None
        try:   
            google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            if 'state' in request.args:
                error_state=int(request.args['state'])
                if error_state==-2:
                    error_message="An error occurred with the information you provided. \nPlease remember to fill in all fields and only use positive numbers. \nIn addition, the driver must be at least 18 years old to be a F1 driver."
                elif error_state==-1:
                    error_message="The name is already taken by another driver"
                elif error_state==0:
                    error_message="The team has not been found"
                elif error_state==1:
                    success_message="Your driver has been created"
            teams_info = retrieveTeamInfo()
            if teams_info is not None:
                for e in teams_info:
                    teams_data.append([e["TeamID"],e["Name"]])
                
        except ValueError as exc:
            error_message = str(exc)
            return redirect(url_for('root',state=5))
        return render_template('create_driver.html', connected=id_token, teams_data=teams_data, error_message=error_message,success_message=success_message)
    return redirect("/")

@app.route('/creator_team')
def creatorTeamInfo():
    # query firebase for the request token and set other variables to none for now
    id_token = request.cookies.get("token")
    # if we have an ID token then verify it against firebase if it doesn't check out then redirect to root
    if id_token:
        error_message = None
        success_message = None
        error_state=None
        try:
            google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            if 'state' in request.args:
                error_state=int(request.args['state'])
                if error_state==-2:
                    error_message="An error occurred with the information you provided. \nPlease remember to fill in all fields and only use positive numbers. \nIn addition, the team must be established after 1950, the year F1 was founded."
                elif error_state==-1:
                    error_message="The name is already taken by another team"
                elif error_state==1:
                    success_message="Your team has been created"
        except ValueError as exc:
            error_message = str(exc)
            return redirect(url_for('root',state=5))
        # render the template with the last times we have
        return render_template('create_team.html',connected=id_token, error_message=error_message,success_message=success_message)
    return redirect("/")    

@app.route('/create_driver', methods=['POST'])
def createDriverInfo():
    id_token = request.cookies.get("token")
    if id_token:
        try:
            google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
            return redirect(url_for('root',state=5))
        try:
            driver_name = request.form['Driver_name']
            Age = request.form['Age']
            
            if ((driver_name!='' and driver_name!=None) and int(Age)>=18 
                and int(request.form["Total_Pole_Positions"])>=0 and int(request.form["Total_Race_Wins"])>=0 
                and float(request.form["Total_Points_Scored"])>=0.0 and int(request.form["Total_World_Titles"])>=0 
                and int(request.form["Total_Fastest_Laps"])>=0 ):
                state=createDriver(request.form)
            else:
                state=-2
            return redirect(url_for('creatorDriverInfo',state=state))
        except ValueError as exc:
            return redirect(url_for('creatorDriverInfo',state=-2))
    return redirect("/")
    
@app.route('/create_team', methods=['POST'])
def createTeamInfo():
    id_token = request.cookies.get("token")
    state=None
    if id_token:
        try:
            google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)
            return redirect(url_for('root',state=5))
        try:
            if(int(request.form["Year_Founded"])>=1950
                and (request.form["Name"]!='' and request.form["Name"]!=None) 
                and int(request.form["Total_Pole_Positions"])>=0 
                and int(request.form["Total_Race_Wins"])>=0 
                and int(request.form["Last_Finishing_Position"])>=0
                and int(request.form["Total_Constructors_Titles"])>=0
                and int(request.form["Total_Fastest_Laps"])>=0):
                state=createTeam(request.form)
            else:
                state=-2
            return redirect(url_for('creatorTeamInfo',state=state))
        except ValueError:
            return redirect(url_for('creatorTeamInfo',state=-2))
    return redirect("/")

@app.route('/driver/<int:id>')
def driverInfo(id):
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    id_token = request.cookies.get("token")
    update_msg = None

    try:
        query = "SELECT * FROM Drivers WHERE DriverID = %s"
        cursor.execute(query, (id,))
        entity = cursor.fetchone()

        if entity is None:
            return redirect(url_for('root', state=3))

        if id_token:
            if 'state' in request.args:
                if int(request.args['state']) == 1:
                    update_msg = "The driver has been successfully modified"

            # Your token verification logic here

        return render_template('driver.html', connected=id_token, driver_info=entity, driver_edit="/updater_driver/" + str(id),
                               update_msg=update_msg)
    except Exception as e:
        print(f"Error retrieving driver information: {e}")
        return redirect(url_for('root', state=3))
    finally:
        # Close the cursor and MySQL connection
        cursor.close()
        cnx.close()







@app.route('/updater_driver/<int:id>')
def updaterDriverInfo(id):
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    id_token = request.cookies.get("token")
    error_message = None
    teams_data = []

    # if we have an ID token then verify it against firebase
    if id_token:
        try:
            # Your token verification logic here

            query_teams = "SELECT * FROM Teams"
            cursor.execute(query_teams)
            teams_info = cursor.fetchall()

            for e in teams_info:
                teams_data.append([e['TeamID'], e["Name"]]) 

            query_driver = "SELECT * FROM Drivers WHERE DriverID = %s"
            cursor.execute(query_driver, (id,))
            entity = cursor.fetchone()

            if entity is None:
                return redirect("/")

            if 'state' in request.args:
                error_state = int(request.args['state'])
                if error_state == -2:
                    error_message = "An error occurred with the information you provided. \nPlease remember to fill in all fields and only use positive numbers. \nIn addition, the driver must be at least 18 years old to be a F1 driver."
                elif error_state == -3:
                    error_message = "An error occurred, the entity you are trying to update was not found."
                elif error_state == -4:
                    error_message = "An error occurred during the manipulation."
                elif error_state == -1:
                    error_message = "The name is already taken by another driver."
                elif error_state == 0:
                    error_message = "The team has not been found."
        except Exception as e:
            print(f"Error in updaterDriverInfo: {e}")
            return redirect("/")
        finally:
            # Close the cursor and MySQL connection
            cursor.close()
            cnx.close()

        return render_template('update_driver.html', connected=id_token, teams_data=teams_data, driver_info=entity,
                               error_message=error_message, driver="/update_driver/" + str(id))
    return redirect("/")

@app.route('/update_driver/<int:id>', methods=['POST'])
def updateDriverInfo(id):
    
    id_token = request.cookies.get("token")
    if id_token:
        try:
            google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError:
            return redirect(url_for('root',state=5))
        try:
            driver_name = request.form['Driver_name']
            Age = request.form['Age']
            driver_id=id
            state=None
            if ((driver_name!='' and driver_name!=None) and int(Age)>=18 
                and int(request.form["Total_Pole_Positions"])>=0 and int(request.form["Total_Race_Wins"])>=0 
                and float(request.form["Total_Points_Scored"])>=0.0 and int(request.form["Total_World_Titles"])>=0 
                and int(request.form["Total_Fastest_Laps"])>=0 ):
                state=updateDriver(request.form,driver_id)
            else:
                state=-2
            if int(state)==1:
                return redirect(url_for("driverInfo",id=str(id),state=state))
            else:
                return redirect(url_for("updaterDriverInfo",id=str(id),state=state))
        except ValueError:
            return redirect(url_for("updaterDriverInfo",id=str(id),state=-2))
    return redirect("/")


@app.route('/team/<int:id>')
def teamInfo(id):
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    id_token = request.cookies.get("token")
    update_msg = None

    query_team = "SELECT * FROM Teams WHERE TeamID = %s"
    cursor.execute(query_team, (id,))
    entity = cursor.fetchone()

    if entity is None:
        return redirect(url_for('root', state=3))

    if id_token:
        if 'state' in request.args:
            if int(request.args['state']) == 1:
                update_msg = "The team has been successfully modified"
            if int(request.args['state']) == 2:
                update_msg = "The team is always used by some drivers, you can't remove it"

        try:
            # Your token verification logic here
            pass
        except Exception as e:
            print(f"Error in teamInfo: {e}")
            return redirect("/")
        finally:
            # Close the cursor and MySQL connection
            cursor.close()
            cnx.close()

    return render_template('team.html', connected=id_token, team_info=entity,
                           team_edit="/updater_team/" + str(id), update_msg=update_msg)

@app.route('/updater_team/<int:id>')
def updaterTeamInfo(id):
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    id_token = request.cookies.get("token")

    if id_token:
        error_message = None
        try:
            # Your token verification logic here
            google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

            
            query_team = "SELECT * FROM Teams WHERE TeamID = %s"
            cursor.execute(query_team, (id,))
            entity = cursor.fetchone()

            if entity is None:
                return redirect(url_for('root', state=3))

            if 'state' in request.args:
                error_state = int(request.args['state'])
                if error_state == -2:
                    error_message = "An error occurred with the information you provided. \nPlease remember to fill in all fields and only use positive numbers. \nIn addition, the team must be established after 1950, the year F1 was founded."
                elif error_state == -1:
                    error_message = "The name is already taken by another team"
                elif error_state == -4:
                    error_message = "An error occurred during the manipulation."
                elif error_state == -3:
                    error_message = "An error occurred the entity you try to reach and update as not found."
        except ValueError as exc:
            return redirect(url_for('root', state=5))
        finally:
            # Close the cursor and MySQL connection
            cursor.close()
            cnx.close()

        return render_template('update_team.html', connected=id_token, teams_data=entity,
                               driver_info=entity, error_message=error_message, team="/update_team/" + str(id))
    return redirect("/")




@app.route('/update_team/<int:id>', methods=['POST'])
def updateTeamInfo(id):
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    id_token = request.cookies.get("token")
    if id_token:
        state=None
        try:
            google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError:
            return redirect(url_for('root',state=5))
        try:
            if(int(request.form["Year_Founded"])>=1950
                and (request.form["Name"]!='' and request.form["Name"]!=None) 
                and int(request.form["Total_Pole_Positions"])>=0 
                and int(request.form["Total_Race_Wins"])>=0 
                and int(request.form["Last_Finishing_Position"])>=0
                and int(request.form["Total_Constructors_Titles"])>=0
                and int(request.form["Total_Fastest_Laps"])>=0):
                state=updateTeam(request.form,id)
            else:
                state=-2
            if int(state)==1:
                return redirect(url_for("teamInfo",id=str(id),state=state))
            else:
                return redirect(url_for("updaterTeamInfo",id=str(id),state=state))
        except ValueError as exc:
            error_message = str(exc)
            return redirect(url_for("updaterTeamInfo",id=str(id),state=-2))
    return redirect("/")

@app.route('/search_driver',methods = ['POST', 'GET'])
def searchDriver():
    id_token = request.cookies.get("token")
    result=None
    error_message=None
    if request.method == 'POST':
        result=queriesDriver(request.form) 
        if result==-2:
            result=None
            error_message="If you want to search for a team, make sure you use a whole integer for all queries except the name."
    return render_template('searchDriver.html', connected=id_token, searching_result=result, error_message=error_message)


@app.route('/search_team',methods = ['POST', 'GET'])
def searchTeam():
    id_token = request.cookies.get("token")
    result=None
    error_message=None
    if request.method == 'POST':
        result=queriesTeam(request.form)
        if result==-2:
            result=None
            error_message="If you want to search for a team, make sure you use a whole integer for all queries except the name."
    return render_template('searchTeam.html', connected=id_token, searching_result=result, error_message=error_message)



@app.route('/versus_driver', methods=['POST', 'GET'])
def compareDriver():
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    id_token = request.cookies.get("token")
    drivers_data = []
    compare_result = {}
    driver1 = None
    driver2 = None
    error_message = None

    query_drivers = "SELECT * FROM Drivers"
    cursor.execute(query_drivers)
    drivers_info = cursor.fetchall()

    for driver in drivers_info:
        drivers_data.append([driver["DriverID"], driver["Name"]])

    if request.method == 'POST':
        if 'Driver_id1' in request.form and 'Driver_id2' in request.form:
            try:
                driver_id1 = int(request.form["Driver_id1"])
                driver_id2 = int(request.form["Driver_id2"])

                query_driver1 = "SELECT * FROM Drivers WHERE DriverID = %s"
                query_driver2 = "SELECT * FROM Drivers WHERE DriverID = %s"

                cursor.execute(query_driver1, (driver_id1,))
                driver1 = cursor.fetchone()

                cursor.execute(query_driver2, (driver_id2,))
                driver2 = cursor.fetchone()

                if driver1 is not None and driver2 is not None and driver1 != driver2:
                    for key in driver1:
                        if key == "Age":
                            if driver1[key] > driver2[key]:
                                compare_result[key] = 2
                            elif driver1[key] == driver2[key]:
                                compare_result[key] = 0
                            else:
                                compare_result[key] = 1
                        elif key not in ['Name', 'Team_id', 'Team_name']:
                            if driver1[key] < driver2[key]:
                                compare_result[key] = 2
                            elif driver1[key] == driver2[key]:
                                compare_result[key] = 0
                            else:
                                compare_result[key] = 1
                else:
                    error_message = "An error occurred during this comparison, one of the drivers was not found."
            except ValueError as exc:
                error_message = "An error occurred during this comparison, one of the drivers was not found."
        else:
            error_message = "Try filling in the form correctly"

    # Close the cursor and MySQL connection
    cursor.close()
    cnx.close()

    return render_template('compare_driver.html', connected=id_token, drivers_data=drivers_data,
                           compare_result=compare_result, driver1=driver1, driver2=driver2, error_message=error_message)
    
    
@app.route('/versus_team', methods=['POST', 'GET'])
def compareTeam():
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
   
    id_token = request.cookies.get("token")
    teams_data = []
    compare_result = {}
    team1 = None
    team2 = None
    error_message = None

    query_teams = "SELECT * FROM Teams"
    cursor.execute(query_teams)
    teams_info = cursor.fetchall()

    for team in teams_info:
        teams_data.append([team["TeamID"], team["Name"]])

    if request.method == 'POST':
        if 'Team_id1' in request.form and 'Team_id2' in request.form:
            try:
                team_id1 = int(request.form["Team_id1"])
                team_id2 = int(request.form["Team_id2"])

                query_team1 = "SELECT * FROM Teams WHERE TeamID = %s"
                query_team2 = "SELECT * FROM Teams WHERE TeamID = %s"

                cursor.execute(query_team1, (team_id1,))
                team1 = cursor.fetchone()

                cursor.execute(query_team2, (team_id2,))
                team2 = cursor.fetchone()

                if team1 is not None and team2 is not None and team1 != team2:
                    for key in team1:
                        if key == "Last_Finishing_Position" or key == "Year_Founded":
                            if team1[key] > team2[key]:
                                compare_result[key] = 2
                            elif team1[key] == team2[key]:
                                compare_result[key] = 0
                            else:
                                compare_result[key] = 1
                        elif key != 'Name':
                            if team1[key] < team2[key]:
                                compare_result[key] = 2
                            elif team1[key] == team2[key]:
                                compare_result[key] = 0
                            else:
                                compare_result[key] = 1
                else:
                    error_message = "An error occurred during this comparison, one of the teams was not found."
            except ValueError as exc:
                error_message = "An error occurred during this comparison, one of the teams was not found."
        else:
            error_message = "Try filling in the form correctly"

    # Close the cursor and MySQL connection
    cursor.close()
    cnx.close()

    return render_template('compare_team.html', connected=id_token, teams_data=teams_data,
                           compare_result=compare_result, team1=team1, team2=team2, error_message=error_message)
    
    
@app.route('/erase_driver', methods=['POST'])
def eraseDriver():
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    id_token = request.cookies.get("token")
    if id_token:
        try:
            google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            return redirect(url_for('root', state=5))
        try:
            query_delete_driver = "DELETE FROM Drivers WHERE DriverID = %s"
            driver_id = int(request.form["id"])
            cursor.execute(query_delete_driver, (driver_id,))
            cnx.commit()
        except ValueError as exc:
            return redirect(url_for('driverInfo', id=driver_id, state=-2))
        finally:
            # Close the cursor and MySQL connection
            cursor.close()
            cnx.close()

        return redirect(url_for('root', state=60))
    return redirect('/')

@app.route('/erase_team', methods=['POST'])
def eraseTeam():
    # Create a connection to MySQL
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    
    id_token = request.cookies.get("token")
    if id_token:
        in_used = False
        try:
            google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            return redirect(url_for('root', state=5))
        try:
            query_check_drivers = "SELECT * FROM Drivers WHERE Team_id = %s"
            team_id = int(request.form["id"])
            cursor.execute(query_check_drivers, (team_id,))
            drivers = cursor.fetchall()

            if not drivers:
                # No drivers are using this team, safe to delete
                query_delete_team = "DELETE FROM Teams WHERE TeamID = %s"
                cursor.execute(query_delete_team, (team_id,))
                cnx.commit()
                return redirect(url_for('root', state=61))
            else:
                in_used = True
        except ValueError as exc:
            return redirect(url_for('teamInfo', id=team_id, state=-2))
        finally:
            # Close the cursor and MySQL connection
            cursor.close()
            cnx.close()

        if in_used:
            return redirect(url_for('teamInfo', id=team_id, state=2))

    return redirect('/')


@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    success_message = None
    if 'state' in request.args:
        state=int(request.args['state'])
        if state==5:
            error_message="Sorry an error occured, if it happen again try to log out and log back in."
        elif state==3:
            error_message="An error occurred the entity you try to reach was not found."
        if id_token:
            if state==60:
                success_message="The driver has been successfully removed"
            elif state==61:
                success_message="The team has been successfully removed"
    return render_template('index.html', connected=id_token, error_message=error_message, success_message=success_message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
