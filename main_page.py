import sys
import os
import pymysql
from PyQt6 import QtWidgets, uic
from Exception_Classes import *
from src import TelechargeSystem
from user_page import UserInterface
from server_page import CustomerServiceInterface

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

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

        # 初始化系统
        self.system = TelechargeSystem()
        self.current_user_phone = None

        # 初始化界面
        self.user_interface = UserInterface(self)
        self.customer_service_interface = CustomerServiceInterface(self)

        # 登录界面按钮
        self.loginButton.clicked.connect(self.login)
        self.gotoregisterButton.clicked.connect(self.gotoregister)
        
        # 注册界面按钮
        self.registerButton.clicked.connect(self.register)
        self.backtologinButton.clicked.connect(self.backtologin)

    def login(self):
        # 登录逻辑
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
                sql = "SELECT UserTypeID, Password, IsSuspended FROM PhoneAccounts WHERE PhoneNumber=%s"
                cursor.execute(sql, (phone,))
                result = cursor.fetchone()

                if not result:
                    raise UserNotFoundError("用户未找到。")

                if result['Password'] != password:
                    raise ValueError("密码错误。")

                user_status = result.get('IsSuspended', '0')
                if user_status == '1':
                    QtWidgets.QMessageBox.warning(self, "账号已停机。")
                else:
                    user_type_id = result['UserTypeID']
                    cursor.execute("SELECT UserTypeName FROM UserTypes WHERE UserTypeID=%s", (user_type_id,))
                    user_type_result = cursor.fetchone()

                    if not user_type_result:
                        raise UserTypeNotFoundError("用户类型未找到。")

                    user_type = user_type_result['UserTypeName']

                    if user_type == '普通用户':
                        self.user_interface.show()
                    elif user_type == '客服':
                        self.customer_service_interface.show()
                    else:
                        raise ValueError("未知的用户类型。")

                    self.current_user_phone = phone

        except UserNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "登录失败，用户不存在", str(e))
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "登录失败", str(e))
        except pymysql.MySQLError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "未知错误，请联系技术人员解决", str(e))
        finally:
            connection.close()

    def gotoregister(self):
        self.tabWidget.setCurrentWidget(self.findChild(QtWidgets.QWidget, 'tab_register'))

    def register(self):
        # 注册逻辑
        phone = self.registerteleNumberEdit.text().strip()
        password = self.registersecretEdit.text().strip()
        name = self.nameEdit.text().strip()
        id_card = self.idCardEdit.text().strip()
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

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
