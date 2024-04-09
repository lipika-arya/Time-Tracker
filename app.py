import sqlite3
from flask import Flask, request, redirect, url_for, render_template
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)


@app.route('/register', methods=['POST', 'GET'])
def register():
    message = ''
    if request.method == 'POST':
        try:
            sqliteConnection = sqlite3.connect('employee.db')
            cursor = sqliteConnection.cursor()
            firstname = request.form['firstName']
            lastname = request.form['lastName']
            password = request.form['password']  # New line to get password from form

            if not firstname or not lastname or not password:
                message = 'Please Enter First Name, Last Name, and Password'
            else:
                hashed_password = generate_password_hash(password)  # Hash the password
                cursor.execute(
                    'INSERT INTO employeeInfo (firstName, lastName, password) VALUES (?, ?, ?)', (firstname, lastname, hashed_password))  # Insert password
                employeeId = cursor.lastrowid
                sqliteConnection.commit()
                message = 'Your New Employee ID: ' + str(employeeId)
            cursor.close()
        except:
            sqliteConnection.rollback()
            message = "Error while inserting Employee Info"
        finally:
            sqliteConnection.close()
    return render_template("register.html", message=message)


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
#def login():
#    employeeExist = False
#    message = ''
#    try:
#        sqliteConnection = sqlite3.connect('employee.db')
#        cursor = sqliteConnection.cursor()
#        if not request.form:
#            return render_template("login.html", message=message)
#        employeeId = request.form['employeeId']
#        password = request.form['password'] #password
#        cursor.execute(
#            'SELECT EXISTS (SELECT * FROM employeeInfo WHERE employeeId=? AND password=?)', (employeeId, generate_password_hash(password)))
#        employeeExist = cursor.fetchone()[0] == 1
#        cursor.close()
#    except:
#        sqliteConnection.rollback()
#        message = 'Error while inserting Employee Info'
#    finally:
#        sqliteConnection.close()
#    if not employeeExist:
#        message = "User doesn't exist or password is incorrect!"
#        return render_template("login.html", message=message)
#    return redirect(url_for("dashboard", employeeId=employeeId))

def login():
    employeeExist = False
    message = ''
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        if not request.form:
            return render_template("login.html", message=message)
        employeeId = request.form['employeeId']
        password = request.form['password']
        cursor.execute('SELECT password FROM employeeInfo WHERE employeeId=?', (employeeId,))
        stored_password = cursor.fetchone()  # Fetch hashed password from the database
        if stored_password and check_password_hash(stored_password[0], password):
            employeeExist = True
        cursor.close()
    except sqlite3.Error as error:
        print("Error while querying database:", error)
        message = 'Error while querying database'
    finally:
        sqliteConnection.close()
    if not employeeExist:
        message = "User doesn't exist or password is incorrect!"
        return render_template("login.html", message=message)
    return redirect(url_for("dashboard", employeeId=employeeId))

   


@app.route("/dashboard/<int:employeeId>", methods=['GET', 'POST'])
def dashboard(employeeId):
    return render_template("dashboard.html", employeeId=employeeId)


@app.route("/activity/<int:employeeId>", methods=['POST', 'GET'])
def activity(employeeId):
    d = request.form.to_dict(flat=False)
    message = ''
    activityToDo = d.keys()
    if 'startTime' in activityToDo:
        message = startTime(1)
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
    return render_template("activity.html", employeeId=employeeId, message=message)


@app.route("/data/<int:employeeId>", methods=['POST', 'GET'])
def data(employeeId):
    headings = ["employeeId", "Date", "Start Shift", "   End Shift",
                "Break Start Time", "Break End Time", "Lunch Start Time", "Lunch End Time"]
    data = []
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            'SELECT employeeId,date,startTime,endTime,startBreakTime,endBreakTime,startLunchTime,endLunchTime FROM employeeActivity WHERE employeeId= ?', (employeeId,))
        allEmployeeInfo = cursor.fetchall()
        data = allEmployeeInfo
        sqliteConnection.commit()
        cursor.close()
    except:
        sqliteConnection.rollback()
    finally:
        sqliteConnection.close()
    return render_template("data.html", employeeId=employeeId, headings=headings, data=data)


def startTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M")
    newShiftAllowed = "False"
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            'SELECT * FROM employeeActivity WHERE employeeId= ? AND date=?', (employeeId, todayDate))
        allShifts = cursor.fetchall()
        temp = tuple(
            filter(lambda shift: shift[-1] == "False", allShifts)
        )
        update = True
        if len(temp) > 0:
            update = False
            message = "Can't Start Shift Because of Active Shift"
        if update:
            cursor.execute('INSERT INTO employeeActivity (employeeId, date, startTime, newShiftAllowed) VALUES (?, ?, ?, ?)',
                           (employeeId, todayDate, time, newShiftAllowed))
            sqliteConnection.commit()
            message = "Successfully Clocked In!"
        cursor.close()
    except:
        sqliteConnection.rollback()
        message = 'Error While Logging Your Start Shift!'
    finally:
        sqliteConnection.close()
    return message


def endTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M")
    newShiftAllowed = "True"
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute('SELECT * FROM employeeActivity WHERE employeeId= ? AND date=? AND newShiftAllowed=?',
                       (employeeId, todayDate, "False"))
        currentShift = cursor.fetchone()
        update = True
        if currentShift is None:
            update = False
            message = "There is No Active Shift"
        if update and currentShift[4] is not None and currentShift[5] is None:
            update = False
            message = "Can't End Shift Because Break Time is Still Active!"
        if update and currentShift[6] is not None and currentShift[7] is None:
            update = False
            message = "Can't End Shift Because Lunch Time is Still Active!"
        if update:
            cursor.execute('UPDATE employeeActivity SET endtime = ?, newShiftAllowed = ? WHERE employeeId= ? AND date=? AND startTime=?',
                           (time, newShiftAllowed, employeeId, todayDate, currentShift[2]))
            sqliteConnection.commit()
            message = "Successfully Clocked Out"
        cursor.close()
    except:
        sqliteConnection.rollback()
        message = 'Error While Logging your End Shift!'
    finally:
        sqliteConnection.close()
    return message


def startBreakTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M")
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute('SELECT * FROM employeeActivity WHERE employeeId= ? AND date=? AND newShiftAllowed=?',
                       (employeeId, todayDate, "False"))
        currentShift = cursor.fetchone()
        update = True
        if currentShift is None:
            update = False
            message = "There Is No Active Shift"
        if update and currentShift[4] is not None:
            update = False
            message = "Can't take Break More than Once"
        if update:
            cursor.execute('UPDATE employeeActivity SET startBreakTime = ? WHERE employeeId= ? AND date=? AND startTime=?',
                           (time, employeeId, todayDate, currentShift[2]))
            sqliteConnection.commit()
            message = "Successfully Started A Break"
        cursor.close()
    except:
        sqliteConnection.rollback()
        message = 'Error While Starting A Break'
    finally:
        sqliteConnection.close()
    return message


def endBreakTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M")
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute('SELECT * FROM employeeActivity WHERE employeeId= ? AND date=? AND newShiftAllowed=?',
                       (employeeId, todayDate, "False"))
        currentShift = cursor.fetchone()
        update = True
        if currentShift is None:
            update = False
            message = "There is No Active Shift"
        if update and currentShift[4] is None:
            update = False
            message = "Can't End Inactive Break"
        if update and currentShift[5] is not None:
            update = False
            message = "Break is Already Ended"
        if update:
            cursor.execute('UPDATE employeeActivity SET endBreakTime = ? WHERE employeeId= ? AND date=? AND startTime=?',
                           (time, employeeId, todayDate, currentShift[2]))
            sqliteConnection.commit()
            message = "Successfully Ended A Break"
        cursor.close()
    except:
        sqliteConnection.rollback()
        message = 'Error While Ending A Break'
    finally:
        sqliteConnection.close()
    return message


def startLunchTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M")
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute('SELECT * FROM employeeActivity WHERE employeeId= ? AND date=? AND newShiftAllowed=?',
                       (employeeId, todayDate, "False"))
        currentShift = cursor.fetchone()
        update = True
        if currentShift is None:
            update = False
            message = "There Is No Active Shift"
        if update and currentShift[6] is not None:
            update = False
            message = "Can't take Lunch More than Once"
        if update:
            cursor.execute('UPDATE employeeActivity SET startLunchTime = ? WHERE employeeId= ? AND date=? AND startTime=?',
                           (time, employeeId, todayDate, currentShift[2]))
            sqliteConnection.commit()
            message = "Successfully Started A Lunch time"
        cursor.close()
    except:
        sqliteConnection.rollback()
        message = 'Error While Starting Lunch Break'
    finally:
        sqliteConnection.close()
    return message


def endLunchTime(employeeId):
    todayDate = datetime.today().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M")
    try:
        sqliteConnection = sqlite3.connect('employee.db')
        cursor = sqliteConnection.cursor()
        cursor.execute('SELECT * FROM employeeActivity WHERE employeeId= ? AND date=? AND newShiftAllowed=?',
                       (employeeId, todayDate, "False"))
        currentShift = cursor.fetchone()
        update = True
        if currentShift is None:
            update = False
            message = "There Is No Active Shift"
        if update and currentShift[6] is None:
            update = False
            message = "Can't End Lunch Without Starting It"
        if update and currentShift[7] is not None:
            update = False
            message = "Lunch Time Already Ended "
        if update:
            cursor.execute('UPDATE employeeActivity SET endLunchTime = ? WHERE employeeId= ? AND date=? AND startTime=?',
                           (time, employeeId, todayDate, currentShift[2]))
            sqliteConnection.commit()
            message = "Successfully Ended A Lunch time"
        cursor.close()
    except:
        sqliteConnection.rollback()
        message = 'Error While Ending A Lunch time'
    finally:
        sqliteConnection.close()
    return message