import sys
import os
import time
import pymysql
from PyQt6 import QtWidgets, uic
from Exception_Classes import *
from src import TelechargeSystem
from user_page import UserInterface
from service_page import CustomerServiceInterface
from admin_page import AdminInterface

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(__file__), 'src', 'telecharge.ui')
        if not os.path.exists(ui_path):
            QtWidgets.QMessageBox.critical(self, "错误", f"找不到UI文件: {ui_path}")
            sys.exit(1)

        uic.loadUi(ui_path, self)
        
        # 获取tabWidget并隐藏Tab栏
        self.tabWidget = self.findChild(QtWidgets.QTabWidget, 'tabWidget')
        if self.tabWidget:
            self.tabWidget.tabBar().setVisible(False)
            self.tabWidget.setCurrentIndex(0)  
        else:
            QtWidgets.QMessageBox.critical(self, "错误", "找不到tabWidget控件")
            sys.exit(1)

        # 初始化系统
        self.system = TelechargeSystem()
        self.current_user_phone = None
        self.is_suspended = False

        # 初始化界面
        self.user_interface = UserInterface(self)
        self.service_interface = CustomerServiceInterface(self)
        self.admin_interface = AdminInterface(self)

        # 登录界面元素
        self.loginButton.clicked.connect(self.login)
        self.gotoregisterButton.clicked.connect(self.gotoregister)
        
        # 注册界面元素
        self.registerButton.clicked.connect(self.register)
        self.backtologinButton.clicked.connect(self.backtologin)
        self.load_packages()

    def login(self):
        phone = self.loginTeleNumberEdit.text().strip()
        self.system.check_input_format(phone, 'I')
        password = self.loginSecretEdit.text().strip()
        self.system.check_input_format(password, 'S')

        if not phone or not password:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请输入手机号码和密码。")
            return

        try:
            result = self.system.get_phoneaccount_by_phone(phone)
            if result['Password'] != password:
                raise ValueError("密码错误。")
            self.current_user_phone = phone
            self.is_suspended = result['IsSuspended']

            user_type = self.system.get_user_info_by_phone(phone)['UserType']
            if user_type == '普通用户':
                self.user_interface.show()
            elif user_type == '客服':
                self.service_interface.show()
            elif user_type == '超级管理员':
                self.admin_interface.show()
            else:
                raise ValueError("未知的用户类型。")

        except UserNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "登录失败，用户不存在", str(e))
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "登录失败", str(e))
        except pymysql.MySQLError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "未知错误，请联系技术人员解决", str(e))

    def gotoregister(self):
        self.tabWidget.setCurrentWidget(self.findChild(QtWidgets.QWidget, 'tab_register'))

    def register(self):
        # 注册逻辑
        phone = self.registerteleNumberEdit.text().strip()
        self.system.check_input_format(phone, 'I')
        password = self.registersecretEdit.text().strip()
        self.system.check_input_format(password, 'S')
        name = self.nameEdit.text().strip()
        self.system.check_input_format(name, 'S')
        id_card = self.idCardEdit.text().strip()
        self.system.check_input_format(id_card, 'I')
        package_id = self.taocancombox.currentData()

        if not phone or not password or not name or not id_card:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请填写所有必填项。")
            return

        if not phone.isdigit() or len(phone) != 11:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请输入有效的11位手机号码。")
            return
        if len(id_card) != 18:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请输入有效的18位身份证号。")
            return

        try:
            self.system.create_new_phone_account(
                phone_number=phone,
                name=name,
                id_card_number=id_card,
                password=password,
                package_id=package_id
            )
            QtWidgets.QMessageBox.information(self, "注册成功", "账户注册成功！请登录。")
            self.backtologin()
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "注册失败", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except InformationNotMatchError as e:
            QtWidgets.QMessageBox.warning(self, "注册失败", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", str(e))

    def backtologin(self):
        self.tabWidget.setCurrentWidget(self.findChild(QtWidgets.QWidget, 'tab_login'))
    
    def load_packages(self):
        try:
            packages = self.system.get_available_packages()
            self.taocancombox.clear()
            for package in packages:
                self.taocancombox.addItem(package['PackageName'], package['PackageID'])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"加载套餐数据失败：{str(e)}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
