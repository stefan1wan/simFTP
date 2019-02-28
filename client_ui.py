#coding=utf-8
import socket, sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import client
from functools import partial

class MyButtonDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(MyButtonDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            button_read = QPushButton(
                self.tr('读'),
                self.parent(),
                clicked=self.parent().cellButtonClicked
            )
            button_write = QPushButton(
                self.tr('写'),
                self.parent(),
                clicked=self.parent().cellButtonClicked
            )
            button_read.index = [index.row(), index.column()]
            button_write.index = [index.row(), index.column()]
            h_box_layout = QHBoxLayout()
            h_box_layout.addWidget(button_read)
            h_box_layout.addWidget(button_write)
            h_box_layout.setContentsMargins(0, 0, 0, 0)
            h_box_layout.setAlignment(Qt.AlignCenter)
            widget = QWidget()
            widget.setLayout(h_box_layout)
            self.parent().setIndexWidget(
                index,
                widget
            )


class simFTP(QWidget):
	def __init__(self):
		super().__init__()
		self.host='35.201.212.56'
		self.port=8888
		self.username='0'
		self.password='0'

		self.initUI()
		self.get_port_name()
		self.client=client.client(self.host,self.port)


	def get_port_name(self):
		self.port=int(self.port_edit.text())
		self.host=self.host_edit.text()
		self.username=self.username_edit.text()
		self.password=self.password_edit.text()

	def connect(self):
		self.client.acess_socket()
		self.client.login(self.username, self.password)
		print('clickCallbackone be called')

		self.cur_dir.setText(self.client.get_self_dir())
		self.cur_dir.adjustSize()

		QMessageBox.information(self,"Information","FTP连接成功！")
		self.flash()

	def judge_conn(self):
		pass
	def login(self):
		pass
	def log_out(self):
		pass
	def cut_conn(self):
		pass
	def add_file(self):
		fileName1, filetype = QFileDialog.getOpenFileName(self,
                                    "选取文件",
                                    "./",
                                    "All Files (*);;Text Files (*.txt)")   #设置文件扩展名过滤,注意用双分号间隔
		#print(fileName1,filetype)
		self.add_file_name.setText(fileName1)
		#QMessageBox.information(self,"Information","FTP连接成功！")
		

	def add_file2(self):

		if self.client.get_self_state():
			cur_dir=self.client.get_dir()
			# self.cur_dir.setText(cur_dir)
			# self.cur_dir.adjustSize()
			arg=self.add_file_name.text()
			self.client.add(arg)
			QMessageBox.information(self,"Information","文件上传成功！")
			self.flash()
		else:
			QMessageBox.information(self,"Information","FTP未连接！")


	def delete_file(self):
		if self.client.get_self_state():
			arg=self.delete_in.text()
			#print(arg)
			cur_dir=self.client.get_dir()
			# self.cur_dir.setText(cur_dir)
			# self.cur_dir.adjustSize()
			self.client.delete(arg)
			QMessageBox.information(self,"Information","文件删除成功！")
			self.flash()
		else:
			QMessageBox.information(self,"Information","FTP未连接！")


	def download_file(self):
		if self.client.get_self_state():
			arg=self.Download_in.text()
			#print(arg)
			cur_dir=self.client.get_dir()
			# self.cur_dir.setText(cur_dir)
			# self.cur_dir.adjustSize()
			self.client.download(arg)
			QMessageBox.information(self,"Information","文件下载成功！")
		else:
			QMessageBox.information(self,"Information","FTP未连接！")


	def cd(self):
		if self.client.get_self_state():
			cur_dir=self.client.get_dir()
			# self.cur_dir.setText(cur_dir)
			# self.cur_dir.adjustSize()
			arg=self.cd_in.text()

			cur_dir=self.client.cd(arg)

			self.cur_dir.setText(self.client.get_self_dir())
			self.cur_dir.adjustSize()
			self.flash()
		else:
			QMessageBox.information(self,"Information","FTP未连接！")

	def Return(self):
		if self.client.get_self_state():
			cur_dir=self.client.get_dir()
			# self.cur_dir.setText(cur_dir)
			# self.cur_dir.adjustSize()
			arg=".."

			cur_dir=self.client.cd(arg)
			self.cur_dir.setText(self.client.get_self_dir())
			self.cur_dir.adjustSize()
			self.flash()
		else:
			QMessageBox.information(self,"Information","FTP未连接！")

	def flash(self):
		if self.client.get_self_state():
			cur_dir=self.client.get_dir()
			# self.cur_dir.setText(cur_dir)
			# self.cur_dir.adjustSize()
			#print(cur_dir)
			current_files=self.client.list1()
			files=current_files.split(";")

			self.model = QStandardItemModel(self.tableView)
		#self.model.setRowCount(17)
			self.model.setColumnCount(3)
	          
			self.model.setHeaderData(0,Qt.Horizontal,u"文件名")  
			self.model.setHeaderData(1,Qt.Horizontal,u"下载/进入") 
			self.model.setHeaderData(2,Qt.Horizontal,u"删除/添加") 

			for i in range(len(files)):
				self.model.setItem(i,0,QStandardItem(files[i]))
				self.model.item(i,0).setForeground(QBrush(QColor(0, 0, 0)))  
				self.model.item(i,0).setTextAlignment(Qt.AlignCenter)  

				  
				self.model.setItem(i,1,QStandardItem("下载"))   
				self.model.item(i,1).setForeground(QBrush(QColor(0, 0, 0)))  
				self.model.item(i,1).setTextAlignment(Qt.AlignCenter)
	  
				self.model.setItem(i,2,QStandardItem("删除"))  
				self.model.item(i,2).setForeground(QBrush(QColor(0, 0, 0)))  
				self.model.item(i,2).setTextAlignment(Qt.AlignCenter)  
				#self.setItemDelegateForColumn(2, MyButtonDelegate(self))
	              
			self.tableView.setModel(self.model)  
          

			#for i in files:
			#files=self.client.list1()
			print(self.client.get_self_dir())
			print(files)
		else:
			QMessageBox.information(self,"Information","FTP未连接！")

	def clickCallback3(self):
		QCoreApplication.instance().quit()

	def initUI(self):
		rect = QRect(800, 800, 500, 500)
		self.setGeometry(rect)
		self.setWindowTitle('simFTP')

		pe = QPalette()  
		#pe.setColor(QPalette.WindowText,Qt.red)#设置字体颜色  
		self.setAutoFillBackground(True)#设置背景充满，为设置背景颜色的必要条件  
		#pe.setColor(QPalette.Window,Qt.darkGreen)#设置背景颜色  QColor(192,253,123) RGB
		#pe.setColor(QPalette.Window,QColor(50,50,50) )
		#pe.setColor(QPalette.Background,Qt.blue)<span style="font-family: Arial, Helvetica, sans-serif;">#设置背景颜色，和上面一行的效果一样  
		self.setPalette(pe)  

#端口 以及 host
		self.host_l=QLabel("host: ",self)
		self.host_l.move(10, 30)

		self.host_edit=QLineEdit('35.201.212.56',self)
		self.host_edit.move(80, 30)


		self.port_l=QLabel("port: ",self)
		self.port_l.move(250, 30)

		self.port_edit=QLineEdit("8888",self)
		self.port_edit.move(320, 30)

#用户名及密码
		self.username_l=QLabel("username: ",self)
		self.username_l.move(10, 55)

		self.username_edit=QLineEdit('12345',self)
		self.username_edit.move(80, 55)


		self.password_l=QLabel("password: ",self)
		self.password_l.move(250, 55)

		self.password_edit=QLineEdit("00000",self)
		self.password_edit.move(320, 55)
		self.password_edit.setEchoMode(QLineEdit.Password) 


		bu2=QPushButton("QUIT",self)
		bu2.move(400, 450)
		#bu2.clicked.connect(self.closeEvent)
		bu2.clicked.connect(self.clickCallback3)
		bu2.setIcon(QIcon("close.png"))

		bu3=QPushButton("Connect",self)
		bu3.move(330, 80)
		bu3.clicked.connect(self.connect)
		bu3.setIcon(QIcon("conn.jpeg"))
		#bu3.setColor(QPalette.Background,Qt.Blue)


		self.cd_in = QLineEdit(self)
		self.cd_in.move(192, 85)

		bu9=QPushButton("Change Directory",self)
		bu9.move(40, 80)
		bu9.clicked.connect(self.cd)

		bu10=QPushButton("Return",self)
		bu10.move(20, 110)
		bu10.clicked.connect(self.Return)


		self.delete_in = QLineEdit(self)
		self.delete_in.move(170, 360)

		bu4=QPushButton("Delete File",self)
		bu4.move(40, 360)
		bu4.clicked.connect(self.delete_file)

		self.Download_in = QLineEdit(self)
		self.Download_in.move(170, 390)


		bu5=QPushButton("Download File",self)
		bu5.move(40, 390)
		#bu5.clicked.connect(partial(self.download_file,lineEdit.text())
		bu5.clicked.connect(self.download_file)

		bu5=QPushButton("Add File",self)
		bu5.move(40, 420)
		#bu5.clicked.connect(partial(self.download_file,lineEdit.text())
		bu5.clicked.connect(self.add_file)

		self.add_file_name=QLineEdit(self)
		self.add_file_name.move(170, 420)
		#bu5.clicked.connect(partial(self.download_file,lineEdit.text())
		#self.add_file.clicked.connect(self.add_file)

		bu6=QPushButton("Send",self)
		bu6.move(310, 420)
		#bu5.clicked.connect(partial(self.download_file,lineEdit.text())
		bu6.clicked.connect(self.add_file2)

		bu4=QPushButton("list files",self)
		bu4.move(95, 110)
		bu4.clicked.connect(self.flash)

		# self.for_list=QTextEdit(self)
		# self.for_list.move(30, 140)

		self.dir_l=QLabel("current directory: ",self)
		self.dir_l.move(190, 120)

		self.cur_dir=QLabel(self)
		self.cur_dir.move(300, 120)

		##关于文件的显示,按钮： 添加 删除 下载/ 进入
		self.tableView = QTableView(self)
		self.tableView.setGeometry(QRect(5, 30, 320, 200))
		self.tableView.setObjectName("tableView") 
		self.tableView.move(30, 140)

		##外面：添加文件、返回

		#添加表头：  
		self.model = QStandardItemModel(self.tableView)
		#self.model.setRowCount(17)
		self.model.setColumnCount(3)
          
		self.model.setHeaderData(0,Qt.Horizontal,u"文件名")  
		self.model.setHeaderData(1,Qt.Horizontal,u"下载/进入") 
		self.model.setHeaderData(2,Qt.Horizontal,u"删除/添加") 
          
		self.tableView.setModel(self.model)

		#设置列宽  
		self.tableView.setColumnWidth(0,140)  
		self.tableView.setColumnWidth(1,78)  
		self.tableView.setColumnWidth(2,78)

if  __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = simFTP()
	ex.show()
	sys.exit(app.exec_())