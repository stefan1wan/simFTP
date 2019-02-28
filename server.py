# encoding: utf-8
from multiprocessing import Process
import socket, sys
import os
import signal
import json
import _thread
from multiprocessing import Process
from multiprocessing import Pool
#import ctypes

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = '127.0.0.1' #localhost 
PORT = 8888
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
linsen_num=10


right="100"
wrong="200"
wrong1="201"	#下载的时候，有找不到文件和无法打开文件两种情况
number="001"
seq="001"

#current_users=[]
#从json文件中读取用户信息
def login(username,password):
	#global current_users
	with open("user.json") as f:
		users = json.load(f)
		for i in users:
			if username==i[0] and password==i[1]:
				pid=os.getpid()
				#x=i
				#x.append(pid)
				#current_users.append(x)
				#print(current_users)
				print("username:",i[0]," password:",i[1],"pid: ",pid)
				f.close()
				return True
		f.close()
	return False

def get_command(sock):
	
	msg_length = int(recv_all(sock, 3))
	command=recv_all(sock,3)

	arg1_length= int(recv_all(sock, 3))
	arg1=recv_all(sock,arg1_length)

	arg2_length= int(recv_all(sock, 3))
	arg2=recv_all(sock,arg2_length)

	return command, arg1, arg2, msg_length-9-arg1_length-arg2_length


def connect(sock):
	global right,wrong,wrong1,number,seq
	msg_length = int(recv_all(sock, 3))
	command=recv_all(sock,3)

	arg1_length= int(recv_all(sock, 3))
	username=recv_all(sock,arg1_length)

	arg2_length= int(recv_all(sock, 3))
	password=recv_all(sock,arg2_length)

	if login(username,password):
		send_all(sock,right+number+seq+command)
		return True
	else:
		send_all(sock,wrong+number+seq+command)
		return False

def give_dir(sock):
	global right,wrong,wrong1,number,seq
	cwd=os.getcwd()
	strr=right+number+seq+'006'+cwd
	#print(strr)
	send_all(sock,strr)

def evalu(sock,command,arg1,arg2,length):
	global right,wrong,wrong1,number,seq
	if command=="000":
		list1(sock,command,arg1,arg2,length)
	elif command=="001":
		 cd(sock,command,arg1,arg2,length)
	elif command=="002":
		 add(sock,command,arg1,arg2,length)
	elif command=="003":
		 delete(sock,command,arg1,arg2,length)
	elif command=="004":
		 download(sock,command,arg1,arg2,length)
	elif command=="005":
		 say="%d are quiting"%(os.getpid())
		 print(say)
		 send_all(sock,right+number+seq+command)
		 file_content=recv_all(sock,length)
		 sc.close()
		 return False
	else:
		#send_all(sock,"wrong operation")
		file_content=recv_all(sock,length)
	return True

def list1(sock,command,arg1,arg2,length):
	global right,wrong,wrong1,number,seq
	try:
		dir_list=os.listdir()
		print(dir_list)
		str_tem=''
		print(dir_list[2])
		#print(charset.)
		for i in range(len(dir_list)):
			str_tem+=dir_list[i]+';'
		str_tem=str_tem[:-1]
		send_all(sock,right+number+seq+command+str_tem)


	except IOError:
		send_all(sock,wrong+number+seq+command)
	file_content=recv_all(sock,length)

def cd(sock,command,arg1,arg2,length):
	global right,wrong,wrong1,number,seq
	if os.path.exists ('./'+arg1):
		os.chdir('./'+arg1)
		cwd=os.getcwd()
		send_all(sock,right+number+seq+command+cwd)
	else:
		send_all(sock,wrong+number+seq+command)
	file_content=recv_all(sock,length)
	

def add(sock,command,arg1,arg2,length):
	global right,wrong,wrong1,number,seq

	#获取待传文件大小
	file_size=int(arg2)
	recv_all(sock,length)

	#告诉客户端,作好了接收准备
	send_all(sock,right+number+seq+command)

	try:
		file=open("./"+arg1, 'wb')
		#file_content=recv_all(sock,length)
		file_content=receive_file(sock,file_size)
		file.write(file_content)
	except IOError:
		send_all(sock,wrong+number+seq+command)
	else:
		file.close()
		send_all(sock,right+number+seq+command)

def delete(sock,command,arg1,arg2,length):
	global right,wrong,wrong1,number,seq
	if os.path .isfile("./"+arg1):
		os.remove("./"+arg1)
		send_all(sock,right+number+seq+command)
	else :
		send_all(sock,wrong+number+seq+command)
	file_content=recv_all(sock,length)


def download(sock,command,arg1,arg2,length):
	global right,wrong,wrong1,number,seq
	if os.path.isfile("./"+arg1):
		try:
			file=open("./"+arg1, 'rb')
			#print("lalalala")
			file_content=file.read()
			#print("abc")

			#返回文件的长度
			num=str(len(file_content))
			head=right+number+seq+command+num
			#head=head.encode('utf-8')
			send_all(sock,head)

			#发送文件
			send_file(sock,file_content,len(file_content))
			#print("lalalala")
			#send_all(right+number+seq+command+file_content)
		except IOError:
			send_all(sock,wrong1+number+seq+command)
		else:
			file.close()		
	else:
		send_all(sock,wrong+number+seq+command)
	#将客户端发过来的消息读完
	file_content=recv_all(sock,length)



##发送和接收文件的封装函数:均使用二进制格式
def send_file(sock,tosend,size):
    pac=size//999
    les=size%999

    for i in range(pac):
        content=tosend[999*i:999*(i+1)]
        send_directly(sock,content)
    content=tosend[999*pac:]
    send_directly(sock,content)

def receive_file(sock,size):
    sum_bytes=0
    mess=''.encode()
    while sum_bytes<size:
        msg_length = int(recv_all(sock, 3))
        #get the 'real' message with proper length
        message = rec_directly(sock, msg_length)
        sum_bytes+=len(message)
        mess+=message
    return mess


#发送二进制
def send_directly(sc,tosend):
	msg_length_in_str = str(len(tosend))
	msg_length_in_str = msg_length_in_str.zfill(3)
	abc=msg_length_in_str.encode('utf-8')
	sc.sendall(abc+tosend)


#发送字符串类
def send_all(sc,tosend):
	msg_length_in_str = str(len(tosend))
	msg_length_in_str1 = msg_length_in_str.zfill(3)
	#print(msg_length_in_str1)
	#print(tosend)
	abc=(msg_length_in_str1+tosend)
	#print(abc.encode('utf-8'))
	sc.sendall(abc.encode('utf-8'))

#接收二进制
def rec_directly(sock,length):
	global current_users
	data = ''.encode()
	while len(data) < length:
		more = sock.recv(length - len(data)) 
		if not more:
			print("conn't read, client is closed------>from rec_directly")
			sock.close()
			pid=os.getpid()
			os.kill(pid, signal.SIGTERM)
			return data
		data += more
	return data

#接收字符串类
def recv_all(sock, length): 
	global current_users
	data = ''
	while len(data) < length:
		more = sock.recv(length - len(data)) 
		if not more:
			print("conn't read, client is closed----->from recv_all")
			sock.close()
			pid=os.getpid()
			os.kill(pid, signal.SIGTERM)
			return data
		data += more.decode("utf-8")
	return data

#封装的接收函数
def receive(sock):
	msg_length = int(recv_all(sock, 3))
	message = recv_all(sock, msg_length)
	return message

def ser_a_user(sc):
	global right,wrong,wrong1,number,seq

	#一个连接不得同时连3次,但客户端可以一直发连接请求
	#先和用户端连接,如果连接不上，服务端就释放连接
	con_num=0
	while not connect(sc) and con_num<3:
		com_num=con_num+1
		if con_num>3:
			print("sorry, bye~")
			send_all(sc,wrong+number+seq+command)
			sc.close()
			continue

	#连接成功后,服务端给用户发送目前的目录
	give_dir(sc)

	while True:
		#这意味着，用户必须先接收当前的目录，才能继续发送命令
		give_dir(sc)
		command,arg1,arg2,length=get_command(sc)
		if not evalu(sc,command,arg1,arg2,length):
			break

s.listen(linsen_num)
print('Listening at', s.getsockname())
while True:
	sc, sockname = s.accept()
	try:
	    p=Process(target=ser_a_user, args=(sc,))
	    p.start()
	except:
   		print("Error: 无法启动进程")

