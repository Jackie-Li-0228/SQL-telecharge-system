import sys
import os
from PyQt6 import QtWidgets, uic
import pymysql
from Exception_Classes import (
    DatabaseError,
    UserNotFoundError,
    ValueError,
    UserTypeNotFoundError,
)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # 构建UI文件的绝对路径
        ui_path = os.path.join(os.path.dirname(__file__), 'src', 'telecharge.ui')
        if not os.path.exists(ui_path):
            QtWidgets.QMessageBox.critical(self, "错误", f"找不到UI文件: {ui_path}")
            sys.exit(1)

        # 加载UI文件
        uic.loadUi(ui_path, self)

        # 获取tabWidget并隐藏Tab栏
        self.tabWidget = self.findChild(QtWidgets.QTabWidget, 'tabWidget')
        if self.tabWidget:
            self.tabWidget.tabBar().setVisible(False)
            self.tabWidget.setCurrentIndex(0)  
        else:
            QtWidgets.QMessageBox.critical(self, "错误", "找不到tabWidget控件")
            sys.exit(1)

        self.loginButton.clicked.connect(self.login) 
        self.gotoregisterButton.clicked.connect(self.gotoregister)
        self.registerButton.clicked.connect(self.register)
        self.backtologinButton.clicked.connect(self.backtoLogin)

    def login(self):
        phone = self.loginTeleNumberEdit.text().strip()  
        password = self.loginSecretEdit.text().strip()    

        if not phone or not password:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请输入手机号码和密码。")
            return

        try:
            connection = pymysql.connect(
                host="localhost",    
                user="root", 
                password="123123", 
                database="telecharge",
                cursorclass=pymysql.cursors.DictCursor
            )
            with connection.cursor() as cursor:
                # 查询用户类型和密码
                sql = "SELECT UserTypeID, Password FROM PhoneAccounts WHERE PhoneNumber=%s"
                cursor.execute(sql, (phone,))
                result = cursor.fetchone()

                if not result:
                    raise UserNotFoundError("用户未找到。")

                if result['Password'] != password:
                    raise ValueError("密码错误。")

                user_type_id = result['UserTypeID']

                # 根据UserTypeID查询UserTypeName
                cursor.execute("SELECT UserTypeName FROM UserTypes WHERE UserTypeID=%s", (user_type_id,))
                user_type_result = cursor.fetchone()

                if not user_type_result:
                    raise UserTypeNotFoundError("用户类型未找到。")

                user_type = user_type_result['UserTypeName']

                # 根据用户类型切换到对应的Tab页
                if user_type == '普通用户':
                    self.tabWidget.setCurrentIndex(3) 
                elif user_type == '客服':
                    self.tabWidget.setCurrentIndex(4) 
                elif user_type == '超级管理员':
                    self.tabWidget.setCurrentIndex(5) 
                else:
                    raise ValueError("未知的用户类型。")

        except UserNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "登录失败", str(e))
        except pymysql.MySQLError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", str(e))
        finally:
            connection.close()
            
    def gotoregister(self):
        self.tabWidget.setCurrentIndex(2)
        
    def register(self):
        print("注册")
        
    def backtoLogin(self):
        self.tabWidget.setCurrentIndex(0)
        
            
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())