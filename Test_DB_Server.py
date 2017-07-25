'''
python Test_DB_Server.py
'''
import pymysql
import socket

print("Test_DB_Server")
print("Connecting to Database")
ID='root'
PW = 'apmsetup'
DB = 'messenger_db'
table = 'login_info'
message_table = 'messages'
connDB = pymysql.connect(host='localhost', user=ID, password=PW,db=DB, charset='utf8')
curs = connDB.cursor()
print("Successfully Connected to " +  DB)

print("Server Socket Listening")
HOST = ''
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print ("Connected by " + addr[0])
clientName = "Tmp"

while True :
	data = (conn.recv(1024)).decode('utf-8')
	if data is '1':
		print("Login request")
		isLogin = False
		tmp_id = (conn.recv(1024)).decode('utf-8')
		print("Received ID : " + tmp_id)
		tmp_pw = (conn.recv(1024)).decode('utf-8')
		print("Received PW : " + tmp_pw)
		curs.execute("SELECT * FROM " + table) 
		row = curs.fetchone()
		while row is not None :
			if (tmp_id == row[0]) and (tmp_pw == row[1]) :
				isLogin = True
				break
			row = curs.fetchone()
		if isLogin is True : 
			tmpM = '1'
			conn.sendall(tmpM.encode())
			print("Login Complete from " + tmp_id)
			clientName = tmp_id
			break
		else :
			tmpM = '0'
			conn.sendall(tmpM.encode())
			print("Login Error from " + tmp_id)

	if data is '2':
		print("Registration request")
		canCreate = True
		tmp_id = (conn.recv(1024)).decode('utf-8')
		print("Received ID : " + tmp_id)
		tmp_pw = (conn.recv(1024)).decode('utf-8')
		print("Received PW : " + tmp_pw)
		curs.execute("SELECT * FROM " + table) 
		row = curs.fetchone()
		while row is not None :
			if tmp_id == row[0] :
				canCreate = False
				break
			row = curs.fetchone()
		if canCreate is True : 
			print("Inserting Data to DB...")
			curs.execute("INSERT INTO " + table + " (info_id,info_pw) VALUES (%s,%s)", 
			  (tmp_id,tmp_pw))
			connDB.commit()
			print("Commit Complete!")
			tmpM = '1'
			conn.sendall(tmpM.encode())
			print("Registration Complete from " + tmp_id)
		else :
			tmpM = '0'
			conn.sendall(tmpM.encode())
			print("Registration Error from " + tmp_id)

while True :
	data = (conn.recv(1024)).decode('utf-8')
	if data is '1' :
		print("" + clientName + " has been disconnected")
		break
	if data is '2' :
		tmp_rcv = (conn.recv(1024)).decode('utf-8')
		title = (conn.recv(1024)).decode('utf-8')
		MSG = (conn.recv(1024)).decode('utf-8')
		print("Message Received " + tmp_rcv)
		SQL = "INSERT INTO " + message_table + \
		" (title, message, sender, receiver, send_date, ischeck) VALUES (%s,%s,%s,%s,now(),0)"
		DATA = (title, MSG, tmp_id, tmp_rcv)
		curs.execute(SQL, DATA)
		connDB.commit()
		print("Successfully Received FROM " + tmp_id + " TO " + tmp_rcv)
	if data is '3':
		print("Message Request from " + clientName)
		curs.execute("SELECT * FROM " + message_table + " WHERE receiver = '"
			+ clientName + "' ORDER BY send_date DESC")
		row = curs.fetchone()
		while row is not None :
			conn.sendall(str(row).encode())
			row = curs.fetchone()
		tmpM = '0'
		conn.sendall(tmpM.encode())
		print("Successfully Sended to " + clientName)

conn.close()
