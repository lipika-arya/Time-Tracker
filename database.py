import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect("employee.db")
cur = connection.cursor()
cur.execute('''CREATE TABLE employeeInfo(employeeId INTEGER PRIMARY KEY AUTOINCREMENT,
                                        firstName TEXT,
                                        lastName TEXT,
                                        password TEXT,
                                        authorization TEXT )''')
cur.execute('''CREATE TABLE employeeActivity(employeeId INTEGER,
                                            date TEXT ,
                                            startTime TEXT,
                                            endTime TEXT, 
                                            startBreakTime TEXT, 
                                            endBreakTime TEXT,
                                            startLunchTime TEXT,
                                            endLunchTime TEXT, 
                                            newShiftAllowed TEXT,
                                            PRIMARY KEY (employeeId, date, startTime))''')

admin_firstname = 'Admin'
admin_lastname = 'Admin'
admin_password = 'admin_password1'
admin_authorization = 'employer'

hashed_admin_password = generate_password_hash(admin_password)

cur.execute('''INSERT INTO employeeInfo (firstName, lastName, password, authorization)
               VALUES (?, ?, ?, ?)''', (admin_firstname, admin_lastname, hashed_admin_password, admin_authorization))

connection.commit()
connection.close()