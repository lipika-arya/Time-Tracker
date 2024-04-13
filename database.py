import sqlite3

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


connection.commit()
connection.close()