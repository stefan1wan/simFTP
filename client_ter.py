#coding=utf-8
import socket, sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = '35.201.212.56' 
PORT = 8888
s.connect((HOST, PORT))


current_dir=''

arg1_len='001'
arg1='a'
arg2_len='001'
arg2='b'
number='001'
seq='001'

def get_length(block):
	length_in_str = str(len(block))
	msg_length_in_str = length_in_str.zfill(3)
	return msg_length_in_str

def connect(s):
	state='200'

	while state=='200':
		username=input('Please enter your username: ')
		password=input('Please enter your password: ')
		send_all("007"+get_length(username)+username+get_length(password)+password)
		total_length=int(recv_all(s,3))
		state=recv_all(s,3)
		file_content=recv_all(s,total_length-3)

		if state=='200':
			print("please try again.")
		elif state=='201':
			return False
		else:
		 	return True

def get_dir(s):
	length=int(recv_all(s,3))
	state=recv_all(s,3)
	number=recv_all(s,3)
	seq=recv_all(s,3)
	command=recv_all(s,3)
	current_dir=recv_all(s,length-12)
	return current_dir


def list1(s):

	send_all("000"+arg1_len+arg1+arg2_len+arg2+number+seq)

	length=int(recv_all(s,3))
	#print(length)
	state=recv_all(s,3)
	number2=recv_all(s,3)
	seq2=recv_all(s,3)
	command=recv_all(s,3)
	#print(length-12)
	current_files=recv_all(s,length-12)

	files=current_files.split(";")
	out=''
	for i in files:
		out+=i+'  '

	print(out)


def cd(s,arg):
	len_1=get_length(arg)
	send_all("001"+len_1+arg+arg2_len+arg2+number+seq)

	length=int(recv_all(s,3))
	#print(length)
	state=recv_all(s,3)
	number2=recv_all(s,3)
	seq2=recv_all(s,3)
	command=recv_all(s,3)
	#print(length-12)
	current_dir=recv_all(s,length-12)
	print("now at: ",current_dir)

def add(s,arg):
	content=''
	with open(arg, 'rb') as file:
		content=file.read()

	#告诉服务端要发送文件，以及文件的长度
	arg=arg.split('/')[-1]
	len_1=get_length(arg)
	##第二个参数为发送文件的长度
	arg2=str(len(content))
	arg2_len=get_length(arg2)

	head="002"+len_1+arg+arg2_len+arg2+number+seq
	#head=head.encode("utf-8")
	send_all(head)
	#接收并处理服务端的返回值
	a=receive(s)

	#向服务端发送文件
	send_file(content,len(content))
	#接收服务端的返回
	a=receive(s)
	print("Add file successfully!")
	#print(a)

def delete(s,arg):
	len_1=get_length(arg)
	send_all("003"+len_1+arg+arg2_len+arg2+number+seq)
	a=receive(s)
	#print(a)

def download(s,arg):
	#告诉服务端要下载东西
	len_1=get_length(arg)
	send_all("004"+len_1+arg+arg2_len+arg2+number+seq)

	#接收服务端返回的长度
	length=int(recv_all(s,3))
	#print(length)
	state=recv_all(s,3)
	number2=recv_all(s,3)
	seq2=recv_all(s,3)
	command=recv_all(s,3)
	#print(state)
	#print(length-12)
	#content=recv_all(s,length-12)
	num=recv_all(s,length-12)
	num=int(num)

	if state=="100":
		content=receive_file(s,num)
		#arg=arg.split('/')[-1]
		#len_1=get_length(arg)
		with open("./"+arg, "wb") as file:
			file.write(content)
		file.close()
	else:
		print("the file name may wrong.")
	print("Download file successfully!")
	#print(current)

def close_con(s):
	
	send_all("005"+arg1_len+arg1+arg2_len+arg2+number+seq)
	#a=receive(s)
	length=int(recv_all(s,3))
	#print(length)
	state=recv_all(s,3)
	number2=recv_all(s,3)
	seq2=recv_all(s,3)
	command=recv_all(s,3)
	print(length-12)
	content=recv_all(s,length-12)

	if state=='100':
		print("you are closing the connection~")
	exit()


##发送和接收文件的封装函数:均使用二进制格式
def send_file(tosend,size):
    pac=size//999
    les=size%999

    for i in range(pac):
        content=tosend[999*i:999*(i+1)]
        send_directly(content)
    content=tosend[999*pac:]
    send_directly(content)

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



#发送二进制文件,注意，tosend没有用utf-8编码
def send_directly(tosend):
	msg_length_in_str = str(len(tosend))
	msg_length_in_str = msg_length_in_str.zfill(3)
	abc=msg_length_in_str.encode('utf-8')
	s.sendall(abc+tosend)

#一般的发送函数
def send_all(tosend):
	msg_length_in_str = str(len(tosend))
	msg_length_in_str = msg_length_in_str.zfill(3)
	abc=(msg_length_in_str +tosend).encode('utf-8')
	s.sendall(abc)

#发送二进制文件
def rec_directly(sock,length):
	data = ''.encode()
	while len(data) < length:
		more = sock.recv(length - len(data)) 
		if not more:
			raise EOFError('socket closed %d bytes into a %d-byte message'% (len(data),length))
		data += more
	return data



#接收函数,接收某一长度的报文
def recv_all(sock, length): 
	data=''
	#data = unicode(data1, errors='replace') 
	while len(data) < length:
		more = sock.recv(length - len(data)) 
		if not more:
			raise EOFError('socket closed %d bytes into a %d-byte message'% (len(data),length))
		data+=more.decode("utf-8", errors='replace')	#.decode("utf-8")#, errors='replace')

	return data

#封装的接收包，自动解析长度,默认为3
def receive(sock):
	msg_length = int(recv_all(sock, 3))
	#get the 'real' message with proper length
	message = recv_all(sock, msg_length)
	return message


print("==============================================================\n")
print(" \n")
print("                    welcome to simFTP client               \n")
print("                     Copyright © 2017 Wan JP.           \n")
print("==============================================================\n")

if not connect(s):
	print("sorry, you cannot connect to the Server")
	exit()

current_dir=get_dir(s)
print("Now you are at: "+current_dir)

while True:
	current_dir1=get_dir(s)
	#print(current_dir1)
	pas=current_dir1.split('/')[-1]
	#print(pas)
	command = input(pas+'$ ').split()
	#print(">")
	if command[0]=="list":
		list1(s)
	elif command[0]=="cd":
		arg=command[1]
		cd(s,arg)
	elif command[0]=="add":
		arg=command[1]
		add(s,arg)
	elif command[0]=="delete":
		arg=command[1]
		delete(s,arg)
	elif command[0]=="download":
		arg=command[1]
		download(s,arg)
	elif command[0]=="quit":
		close_con(s)
	elif command[0]=="exit":
		break
	else:
		print("wrong command.")