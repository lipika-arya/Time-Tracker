import sqlite3
from flask import Flask, request, redirect, url_for, render_template
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

def get_authorization(employeeId):
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute('SELECT authorization FROM employeeInfo WHERE employeeId=?', (employeeId,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None 
    except sqlite3.Error as error:
        print("Error while querying the database:", error)
        return None
    finally:
        if cursor:
            cursor.close()
        if sqliteConnection:
            sqliteConnection.close()


@app.route('/register', methods=['POST', 'GET'])
def register():
    
    message = ''
    if request.method == 'POST':
        try:
            sqliteConnection = sqlite3.connect('employee.db')
            cursor = sqliteConnection.cursor()
            firstname = request.form['firstName']
            lastname = request.form['lastName']
            password = request.form['password']
            authorization = request.form['authorization']
            
            if not firstname or not lastname or not password or not authorization:
                message = 'Please Enter First Name, Last Name, Password, and Authorization'
            elif len(password) < 8:
                message = 'Password should be at least 8 characters long'
            else:
                hashed_password = generate_password_hash(password) 
                cursor.execute(
                    'INSERT INTO employeeInfo (firstName, lastName, password, authorization) VALUES (?, ?, ?, ?)', (firstname, lastname, hashed_password, authorization))  # Insert password
                employeeId = cursor.lastrowid
                sqliteConnection.commit()
                message = 'Your New Employee ID: ' + str(employeeId)
            cursor.close()
        except sqlite3.Error as e:
            sqliteConnection.rollback()
            message = f"Error while inserting Employee Info: {e}"
        finally:
            sqliteConnection.close()
    return render_template("register.html", message=message)

@app.route('/remove_employee/<int:employeeId>', methods=['GET', 'POST'])
def remove_employee(employeeId):
    message = ''
    if request.method == 'POST':
        try:
            if 'employeeId' in request.form and 'password' in request.form:
                remove_employee_id = int(request.form['employeeId'])
                password = request.form['password']

                if employeeId == remove_employee_id:
                    message = "You cannot delete yourself."
                else:
                    print("Form data received:", request.form)
                    sqliteConnection = sqlite3.connect('employee.db')
                    cursor = sqliteConnection.cursor()

                    cursor.execute("SELECT password FROM employeeInfo WHERE employeeId = ?", (employeeId,))
                    stored_password = cursor.fetchone()[0]  
                
                    if check_password_hash(stored_password, password):
                        cursor.execute("DELETE FROM employeeInfo WHERE employeeId = ?", (remove_employee_id,))
                        cursor.execute("DELETE FROM employeeActivity WHERE employeeId = ?", (remove_employee_id,))
                        sqliteConnection.commit()
                        message = f"Employee with ID {remove_employee_id} removed successfully."
                    else:
                        message = "Incorrect password. Please try again."

                    cursor.close()
        except Exception as e:
            print("Error:", e)
            message = f"Error: {e}"

    return render_template("remove.html", employeeId=employeeId, message=message)

@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    message = ''
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        if not request.form:
            return render_template("login.html", message=message)
        employeeId = request.form['employeeId']
        password = request.form['password']
        cursor.execute('SELECT password, authorization FROM employeeInfo WHERE employeeId=?', (employeeId,))
        result = cursor.fetchone()  
        
        if result:
            stored_password, authorization = result
            if check_password_hash(stored_password, password):
                if authorization.lower() == 'employee':
                    return redirect(url_for("dashboard_employee", employeeId=employeeId))
                elif authorization.lower() == 'employer':
                    return redirect(url_for("dashboard_employer", employeeId=employeeId))
                else:
                    message = "Unauthorized access"
            else:
                message = "Incorrect password"
        else:
            message = "User does not exist"
        cursor.close()
    except sqlite3.Error as error:
        print("Error while querying the database:", error)
        message = 'Error while querying the database'
    finally:
        sqliteConnection.close()
    return render_template("login.html", message=message)

   


@app.route("/dashboard_employee/<int:employeeId>", methods=['GET', 'POST'])
def dashboard_employee(employeeId):
    return render_template("dashboard_employee.html", employeeId=employeeId)

@app.route('/dashboard_employer/<int:employeeId>', methods=['GET', 'POST'])
def dashboard_employer(employeeId):
    return render_template("dashboard_employer.html", employeeId=employeeId)

@app.route("/reporttime/<int:employeeId>", methods=['POST', 'GET'])
def reporttime(employeeId):
    authorization = get_authorization(employeeId)
    d = request.form.to_dict(flat=False)
    message = ''
    activityToDo = d.keys()
    if 'startTime' in activityToDo:
        message = startTime(employeeId)
    elif 'endTime' in activityToDo:
        message = endTime(employeeId)
    elif 'startBreakTime' in activityToDo:
        message = startBreakTime(employeeId)
    elif 'endBreakTime' in activityToDo:
        message = endBreakTime(employeeId)
    elif 'startLunchTime' in activityToDo:
        message = startLunchTime(employeeId)
    elif 'endLunchTime' in activityToDo:
        message = endLunchTime(employeeId)
    return render_template("reporttime.html", employeeId=employeeId, authorization=authorization, message=message)

@app.route("/complete_timesheet", methods=['POST', 'GET'])
def complete_timesheet():
    headings = ["employeeId", "Date", "Start Shift", "End Shift",
                "Break Start Time", "Break End Time", "Lunch Start Time", "Lunch End Time"]
    data = []
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            'SELECT employeeId, date, startTime, endTime, startBreakTime, endBreakTime, startLunchTime, endLunchTime FROM employeeActivity')
        data = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as e:
        print("Database error: {}".format(e))
    except Exception as e:
        print("Exception in _query: {}".format(e))
    finally:
        sqliteConnection.close()
    return render_template("timesheet.html", headings=headings, data=data)

@app.route("/employee_info", methods=['POST', 'GET'])
def employee_info():
    headings = ["employeeId", "firstname", "lastname", "authorization"]
    data = []
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            'SELECT employeeId, firstname, lastname, authorization FROM employeeInfo')
        data = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as e:
        print("Database error: {}".format(e))
    except Exception as e:
        print("Exception in _query: {}".format(e))
    finally:
        sqliteConnection.close()
    return render_template("timesheet.html", headings=headings, data=data)

@app.route("/timesheet/<int:employeeId>", methods=['POST', 'GET'])
def timesheet(employeeId):
    headings = ["employeeId", "Date", "Start Shift", "End Shift",
                "Break Start Time", "Break End Time", "Lunch Start Time", "Lunch End Time"]
    data = []
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            'SELECT employeeId, date, startTime, endTime, startBreakTime, endBreakTime, startLunchTime, endLunchTime FROM employeeActivity WHERE employeeId= ?',
            (employeeId,))
        data = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as e:
        print("Database error: {}".format(e))
    except Exception as e:
        print("Exception in _query: {}".format(e))
    finally:
        sqliteConnection.close()
    return render_template("timesheet.html", employeeId=employeeId, headings=headings, data=data)

def startTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    newShiftAllowed = "False"
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            'SELECT * FROM employeeActivity WHERE employeeId = ? AND date = ?', (employeeId, todayDate))
        allShifts = cursor.fetchall()
        temp = tuple(
            filter(lambda shift: shift[-1] == "False", allShifts)
        )
        update = True
        if len(temp) > 0:
            update = False
            message = "Can't start shift because of active shift"
        if update:
            cursor.execute('INSERT INTO employeeActivity (employeeId, date, startTime, newShiftAllowed) VALUES (?, ?, ?, ?)',
                           (employeeId, todayDate, time, newShiftAllowed))
            sqliteConnection.commit()
            message = f"Successfully clocked in! Employee ID: {employeeId}"
        cursor.close()
    except sqlite3.Error as e:
        sqliteConnection.rollback()
        message = f'Error while logging start shift: {e}'
    except Exception as e:
        sqliteConnection.rollback()
        message = f'Exception while logging start shift: {e}'
    finally:
        sqliteConnection.close()
    return message

def endTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    newShiftAllowed = "True"
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            'SELECT * FROM employeeActivity WHERE employeeId = ? AND date = ? AND newShiftAllowed = ?',
            (employeeId, todayDate, "False"))
        currentShift = cursor.fetchone()
        if currentShift is None:
            message = f"There is no active shift for Employee ID: {employeeId}"
        elif currentShift[4] is not None and currentShift[5] is None:
            message = "Cannot end shift because break time is still active."
        elif currentShift[6] is not None and currentShift[7] is None:
            message = "Cannot end shift because lunch time is still active."
        else:
            cursor.execute(
                'UPDATE employeeActivity SET endTime = ?, newShiftAllowed = ? WHERE employeeId = ? AND date = ? AND startTime = ?',
                (time, newShiftAllowed, employeeId, todayDate, currentShift[2]))
            sqliteConnection.commit()
            message = f"Successfully clocked out for Employee ID: {employeeId}"
        cursor.close()
    except sqlite3.Error as e:
        sqliteConnection.rollback()
        message = f"Database error while logging end shift: {e}"
    except Exception as e:
        sqliteConnection.rollback()
        message = f"Exception while logging end shift: {e}"
    finally:
        sqliteConnection.close()
    return message

def startBreakTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            'SELECT * FROM employeeActivity WHERE employeeId = ? AND date = ? AND newShiftAllowed = ?',
            (employeeId, todayDate, "False"))
        currentShift = cursor.fetchone()
        if currentShift is None:
            message = "There is no active shift for Employee ID: {}".format(employeeId)
        elif currentShift[4] is not None:
            message = "Cannot start break more than once."
        else:
            cursor.execute(
                'UPDATE employeeActivity SET startBreakTime = ? WHERE employeeId = ? AND date = ? AND startTime = ?',
                (time, employeeId, todayDate, currentShift[2]))
            sqliteConnection.commit()
            message = "Successfully started a break for Employee ID: {}".format(employeeId)
        cursor.close()
    except sqlite3.Error as e:
        sqliteConnection.rollback()
        message = "Database error while starting break: {}".format(e)
    except Exception as e:
        sqliteConnection.rollback()
        message = "Exception while starting break: {}".format(e)
    finally:
        sqliteConnection.close()
    return message


def endBreakTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            'SELECT * FROM employeeActivity WHERE employeeId = ? AND date = ? AND newShiftAllowed = ?',
            (employeeId, todayDate, "False"))
        currentShift = cursor.fetchone()
        if currentShift is None:
            message = "There is no active shift for Employee ID: {}".format(employeeId)
        elif currentShift[4] is None:
            message = "Cannot end inactive break."
        elif currentShift[5] is not None:
            message = "Break is already ended."
        else:
            cursor.execute(
                'UPDATE employeeActivity SET endBreakTime = ? WHERE employeeId = ? AND date = ? AND startTime = ?',
                (time, employeeId, todayDate, currentShift[2]))
            sqliteConnection.commit()
            message = "Successfully ended a break for Employee ID: {}".format(employeeId)
        cursor.close()
    except sqlite3.Error as e:
        sqliteConnection.rollback()
        message = "Database error while ending break: {}".format(e)
    except Exception as e:
        sqliteConnection.rollback()
        message = "Exception while ending break: {}".format(e)
    finally:
        sqliteConnection.close()
    return message


def startLunchTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            'SELECT * FROM employeeActivity WHERE employeeId = ? AND date = ? AND newShiftAllowed = ?',
            (employeeId, todayDate, "False"))
        currentShift = cursor.fetchone()
        if currentShift is None:
            message = "There is no active shift for Employee ID: {}".format(employeeId)
        elif currentShift[6] is not None:
            message = "Cannot start lunch more than once."
        else:
            cursor.execute(
                'UPDATE employeeActivity SET startLunchTime = ? WHERE employeeId = ? AND date = ? AND startTime = ?',
                (time, employeeId, todayDate, currentShift[2]))
            sqliteConnection.commit()
            message = "Successfully started lunch for Employee ID: {}".format(employeeId)
        cursor.close()
    except sqlite3.Error as e:
        sqliteConnection.rollback()
        message = "Database error while starting lunch break: {}".format(e)
    except Exception as e:
        sqliteConnection.rollback()
        message = "Exception while starting lunch break: {}".format(e)
    finally:
        sqliteConnection.close()
    return message


def endLunchTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            'SELECT * FROM employeeActivity WHERE employeeId = ? AND date = ? AND newShiftAllowed = ?',
            (employeeId, todayDate, "False"))
        currentShift = cursor.fetchone()
        if currentShift is None:
            message = "There is no active shift for Employee ID: {}".format(employeeId)
        elif currentShift[6] is None:
            message = "Cannot end lunch without starting it."
        elif currentShift[7] is not None:
            message = "Lunch time already ended."
        else:
            cursor.execute(
                'UPDATE employeeActivity SET endLunchTime = ? WHERE employeeId = ? AND date = ? AND startTime = ?',
                (time, employeeId, todayDate, currentShift[2]))
            sqliteConnection.commit()
            message = "Successfully ended lunch for Employee ID: {}".format(employeeId)
        cursor.close()
    except sqlite3.Error as e:
        sqliteConnection.rollback()
        message = "Database error while ending lunch time: {}".format(e)
    except Exception as e:
        sqliteConnection.rollback()
        message = "Exception while ending lunch time: {}".format(e)
    finally:
        sqliteConnection.close()
    return message



