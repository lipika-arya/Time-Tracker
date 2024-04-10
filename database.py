import sqlite3

# Hosts DB into local enviroment.
connection = sqlite3.connect("employee.db")
# Gets connection.
cur = connection.cursor()
# Creates table into DB.
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



# Closes Connection.
connection.commit()
connection.close()