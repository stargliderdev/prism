
import pyodbc as db
 
#Create connection string to connect DBTest database with windows authentication
con = db.connect('Driver={SQL Server};" "Server=WIN_SERVER\PRIMAVERA;"   "Database=PRIESPIRIDIAO;"                          "Trusted_Connection=yes;"')
cur = con.cursor()

