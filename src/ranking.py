import mysql.connector

mydb = mysql.connector.connect(
    host="sql7.freemysqlhosting.net",
    user="sql7295023",
    passwd="cumK3iFAa4",
    database="sql7295023"
)

mycursor = mydb.cursor()
formula = "insert into ranking (name, score) values (%s,%s)"
