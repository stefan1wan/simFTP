#coding=utf-8
import socket, sys

class client():
	def __init__(self,host,port):
		self.current_dir=''
		self.arg1_len='001'
		self.arg1='a'
		self.arg2_len='001'
		self.arg2='b'
		self.number='001'
		self.seq='001'
		self.conn=False
		self.state=False
		self.username=''
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.HOST =host 
		self.PORT =port
		#self.acess_socket()

	#外部直接访问只是得到类的值，并不能得到实例改变后的值
	def get_self_dir(self):
		return self.current_dir

	def get_self_state(self):
		return self.state

	def get_self_conn(self):
		return self.conn	

	def get_self_username(self):
		return self.username


	def acess_socket(self):
		if self.conn==False:
			#同时抛弃原来的socket，建立一个新的socket
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.conn=True
			self.s.connect((self.HOST, self.PORT))
			

	def get_dir(self):
		length=int(self.recv_all(3))
		state=self.recv_all(3)
		number=self.recv_all(3)
		seq=self.recv_all(3)
		command=self.recv_all(3)
		current_dir=self.recv_all(length-12)
		return current_dir
	
	def get_length(self,block):
		length_in_str = str(len(block))
		msg_length_in_str = length_in_str.zfill(3)
		return msg_length_in_str

	#一次连接尝试
	def login(self,username,password):
		if self.state==False:
			self.state=True
			self.send_all("007"+self.get_length(username)+username+self.get_length(password)+password)
			total_length=int(self.recv_all(3))
			state=self.recv_all(3)
			file_content=self.recv_all(total_length-3)

			cur_dir=self.get_dir()
			self.current_dir=cur_dir

			if state=='200':
				self.username=username
				#self.state=True	
				#print(cur_dir)
				return True
			else:
				return False

	def list1(self):

		self.send_all("000"+self.arg1_len+self.arg1+self.arg2_len+self.arg2+self.number+self.seq)
		length=int(self.recv_all(3))
		#print(length)
		state=self.recv_all(3)
		number2=self.recv_all(3)
		seq2=self.recv_all(3)
		command=self.recv_all(3)
		#print(length-12)
		current_files=self.recv_all(length-12)

		files=current_files.split(";")
		out=''
		for i in files:
			out+=i+'  '
		#print(out)
		return current_files


	def cd(self,arg):
		len_1=self.get_length(arg)
		self.send_all("001"+len_1+arg+self.arg2_len+self.arg2+self.number+self.seq)

		length=int(self.recv_all(3))
		#print(length)
		state=self.recv_all(3)
		number2=self.recv_all(3)
		seq2=self.recv_all(3)
		command=self.recv_all(3)
		#print(length-12)
		current_dir=self.recv_all(length-12)
		self.current_dir=current_dir
		print("now at: ",current_dir)
		return current_dir

	def add(self,arg):
		content=''
		with open(arg, 'rb') as file:
			content=file.read()

		#告诉服务端要发送文件，以及文件的长度
		arg=arg.split('/')[-1]
		len_1=self.get_length(arg)
		##第二个参数为发送文件的长度
		arg2=str(len(content))
		arg2_len=self.get_length(arg2)

		head="002"+len_1+arg+arg2_len+arg2+self.number+self.seq
		#head=head.encode("utf-8")
		self.send_all(head)
		#接收并处理服务端的返回值
		a=self.receive()

		#向服务端发送文件
		self.send_file(content,len(content))

		a=self.receive()
		print("Add file successfully!")

	def delete(self,arg):
		len_1=self.get_length(arg)
		self.send_all("003"+len_1+arg+self.arg2_len+self.arg2+self.number+self.seq)
		a=self.receive()
		print("Delete file successfully!")

	def download(self,arg):
		#告诉服务端要下载东西
		len_1=self.get_length(arg)
		self.send_all("004"+len_1+arg+self.arg2_len+self.arg2+self.number+self.seq)

		#接收服务端返回的长度
		length=int(self.recv_all(3))
		#print(length)
		state=self.recv_all(3)
		number2=self.recv_all(3)
		seq2=self.recv_all(3)
		command=self.recv_all(3)
		num=self.recv_all(length-12)
		if num=='':
			num=0
		else:
			num=int(num)

		if state=="100":
			content=self.receive_file(num)
			#arg=arg.split('/')[-1]
			#len_1=get_length(arg)
			with open("./"+arg, "wb") as file:
				file.write(content)
			file.close()
		else:
			print("the file name may wrong.")
		print("Download file successfully!")
		#print(current)

	def close_con(self):
		
		self.send_all("005"+self.arg1_len+self.arg1+self.arg2_len+self.arg2+self.number+self.seq)
		#a=receive(s)
		length=int(self.recv_all(3))
		#print(length)
		state=self.recv_all(3)
		number2=self.recv_all(3)
		seq2=self.recv_all(3)
		command=self.recv_all(3)
		print(length-12)
		content=self.recv_all(length-12)

		if state=='100':
			print("you are closing the connection~")
		self.s.close()
		self.conn=False
		#exit()


	##发送和接收文件的封装函数:均使用二进制格式
	def send_file(self,tosend,size):
	    pac=size//999
	    les=size%999

	    for i in range(pac):
	        content=tosend[999*i:999*(i+1)]
	        self.send_directly(content)
	    content=tosend[999*pac:]
	    self.send_directly(content)

	def receive_file(self,size):
	    sum_bytes=0
	    mess=''.encode()
	    while sum_bytes<size:
	        msg_length = int(self.recv_all(3))
	        #get the 'real' message with proper length
	        message = self.rec_directly(msg_length)
	        sum_bytes+=len(message)
	        mess+=message
	    return mess



	#发送二进制文件,注意，tosend没有用utf-8编码
	def send_directly(self,tosend):
		msg_length_in_str = str(len(tosend))
		msg_length_in_str = msg_length_in_str.zfill(3)
		abc=msg_length_in_str.encode('utf-8')
		self.s.sendall(abc+tosend)

	#一般的发送函数
	def send_all(self,tosend):
		msg_length_in_str = str(len(tosend))
		msg_length_in_str = msg_length_in_str.zfill(3)
		abc=(msg_length_in_str +tosend).encode('utf-8')
		self.s.sendall(abc)

	#发送二进制文件
	def rec_directly(self,length):
		data = ''.encode()
		while len(data) < length:
			more = self.s.recv(length - len(data)) 
			if not more:
				raise EOFError('socket closed %d bytes into a %d-byte message'% (len(data),length))
			data += more
		return data

	#接收函数,接收某一长度的报文
	def recv_all(self,length): 
		data=''
		#data = unicode(data1, errors='replace') 
		while len(data) < length:
			more = self.s.recv(length - len(data)) 
			if not more:
				raise EOFError('socket closed %d bytes into a %d-byte message'% (len(data),length))
			data+=more.decode("utf-8", errors='replace')	#.decode("utf-8")#, errors='replace')

		return data

	#封装的接收包，自动解析长度,默认为3
	def receive(self):
		msg_length = int(self.recv_all(3))
		#get the 'real' message with proper length
		message = self.recv_all(msg_length)
		return message

if  __name__ == '__main__':
	host='35.201.212.56' 
	port=8888
	cli=client(host,port)
	cli.acess_socket()#获取连接

	#连接成功后,self 的状态会变成TRUE，外部访问类时，应当先判断是否连接成功，再执行下面的操作。
	#每次操作之前，也应当检查 socket的连接情况。
	cli.login('0','0')
	cli.get_dir() #必须接收目录

	#while True:
	# cli.get_dir()
	# cli.download("a.txt")
	# cli.get_dir()
	# cli.add("pyqt_test.py")

	cli.get_dir()
	cli.list1()
	# cli.get_dir()
	# cli.delete("pyqt_test.py")
	# cli.get_dir()
	# cli.list1()
	cli.get_dir()
	cli.cd("..")
	# cli.get_dir()
	# cli.close_con()
	#

	# if not connect(s):
	# 	print("sorry, you cannot connect to the Server")
	# 	exit()

	# current_dir=get_dir(s)
	# print("Now you are at: "+current_dir)

	# while True:
	# 	current_dir1=get_dir(s)
	# 	#print(current_dir1)
	# 	pas=current_dir1.split('/')[-1]
	# 	#print(pas)
	# 	command = input(pas+'$ ').split()
	# 	#print(">")
	# 	if command[0]=="list":
	# 		list1(s)
	# 	elif command[0]=="cd":
	# 		arg=command[1]
	# 		cd(s,arg)
	# 	elif command[0]=="add":
	# 		arg=command[1]
	# 		add(s,arg)
	# 	elif command[0]=="delete":
	# 		arg=command[1]
	# 		delete(s,arg)
	# 	elif command[0]=="download":
	# 		arg=command[1]
	# 		download(s,arg)
	# 	elif command[0]=="quit":
	# 		close_con(s)
	# 	elif command[0]=="exit":
	# 		break
	# 	else:
	# 		print("wrong command.")

