import sys
import os
import pymysql
from PyQt6 import QtWidgets, uic, QtGui, QtCore
from Exception_Classes import *
from src import TelechargeSystem

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

        # 连接登录和注册按钮
        self.loginButton.clicked.connect(self.login)
        self.gotoregisterButton.clicked.connect(self.gotoregister)
        self.registerButton.clicked.connect(self.register)
        self.backtologinButton.clicked.connect(self.backtoLogin)

        # 连接用户界面按钮
        self.myPackageButton.clicked.connect(self.show_my_package)
        self.balanceButton.clicked.connect(self.show_balance)
        self.callBalanceButton.clicked.connect(self.show_call_balance)
        self.rechargeButton.clicked.connect(self.switch_to_recharge)
        self.billInquiryButton.clicked.connect(self.switch_to_bill_inquiry)
        self.businessHandlingButton.clicked.connect(self.switch_to_business_handling)

        # 连接充值界面按钮
        self.confirmRechargeButton.clicked.connect(self.confirm_recharge)
        self.backToUserButton_recharge.clicked.connect(self.back_to_user)

        # 连接账单查询界面按钮
        self.backToUserButton_billInquiry.clicked.connect(self.back_to_user)

        # 连接业务办理界面按钮
        self.handleBusinessButton.clicked.connect(self.handle_business)
        self.backToUserButton_businessHandling.clicked.connect(self.back_to_user)

        # 初始化TelechargeSystem实例
        self.system = TelechargeSystem()

        # 加载套餐数据
        self.load_packages()

    def load_packages(self):
        try:
            packages = self.system.get_available_packages()
            self.taocancombox.clear()
            for package in packages:
                self.taocancombox.addItem(package['PackageName'], package['PackageID'])
        except pymysql.MySQLError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", f"无法加载套餐数据: {str(e)}")

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
            QtWidgets.QMessageBox.warning(self, "登录失败，用户不存在", str(e))
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "登录失败，密码错误", str(e))
        except pymysql.MySQLError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "未知错误，请联系技术人员解决", str(e))
        finally:
            connection.close()

    def gotoregister(self):
        self.tabWidget.setCurrentWidget(self.findChild(QtWidgets.QWidget, 'tab_register'))

    def register(self):
        phone = self.registerteleNumberEdit.text().strip()
        password = self.registersecretEdit.text().strip()
        name = self.nameEdit.text().strip()
        id_card = self.idCardEdit.text().strip()
        package_id = self.taocancombox.currentData()

        # 输入验证
        if not phone or not password or not name or not id_card:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请填写所有必填项。")
            return

        # 进一步验证电话号码和身份证号格式
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
            self.backtoLogin()
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "注册失败", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except InformationNotMatchError as e:
            QtWidgets.QMessageBox.warning(self, "注册失败", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", str(e))

    def backtoLogin(self):
        self.tabWidget.setCurrentWidget(self.findChild(QtWidgets.QWidget, 'tab_login'))

    # 我的套餐
    def show_my_package(self):
        phone = self.loginTeleNumberEdit.text().strip()
        try:
            package_info = self.system.get_package_details(phone)
            info = "\n".join([f"{key}: {value}" for key, value in package_info.items()])
            QtWidgets.QMessageBox.information(self, "我的套餐", info)
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", str(e))

    # 话费余额
    def show_balance(self):
        phone = self.loginTeleNumberEdit.text().strip()
        try:
            balance_info = self.system.get_balance_info(phone)
            info = f"当前话费余额: {balance_info['current_balance']}元\n本月已消费话费量: {balance_info['consumed_balance']}元"
            QtWidgets.QMessageBox.information(self, "话费余额", info)
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", str(e))

    # 通话余额
    def show_call_balance(self):
        phone = self.loginTeleNumberEdit.text().strip()
        try:
            call_balance_info = self.system.get_call_balance_info(phone)
            info = f"本月剩余语音配额: {call_balance_info['remaining_voice_quota']}分钟\n本月通话时长: {call_balance_info['call_duration']}分钟"
            QtWidgets.QMessageBox.information(self, "通话余额", info)
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", str(e))

    # 切换到充值界面
    def switch_to_recharge(self):
        self.tabWidget.setCurrentWidget(self.findChild(QtWidgets.QWidget, 'tab_recharge'))

    # 切换到账单查询界面
    def switch_to_bill_inquiry(self):
        phone = self.loginTeleNumberEdit.text().strip()
        try:
            transaction_records = self.system.get_transaction_records_by_phone(phone)
            records_text = "\n".join([
                f"交易ID: {record['TransactionID']}, 时间: {record['TransactionTime']}, 项目: {record['PurchasedItem']}, 金额: {record['Amount']}€"
                for record in transaction_records
            ])
            self.billTextEdit.setPlainText(records_text)
            self.tabWidget.setCurrentWidget(self.findChild(QtWidgets.QWidget, 'tab_billInquiry'))
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", str(e))

    # 切换到业务办理界面
    def switch_to_business_handling(self):
        try:
            services = self.system.get_available_services()
            packages = self.system.get_available_packages()
            services_text = "\n".join([f"服务ID: {s['ServiceID']}, 名称: {s['ServiceName']}" for s in services])
            packages_text = "\n".join([f"套餐ID: {p['PackageID']}, 名称: {p['PackageName']}" for p in packages])
            self.availableServicesTextEdit.setPlainText(services_text)
            self.availablePackagesTextEdit.setPlainText(packages_text)
            self.tabWidget.setCurrentWidget(self.findChild(QtWidgets.QWidget, 'tab_businessHandling'))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", str(e))

    # 充值
    def confirm_recharge(self):
        phone = self.rechargePhoneEdit.text().strip()
        amount_text = self.rechargeAmountEdit.text().strip()
        payment_method = self.rechargeMethodEdit.text().strip()

        if not phone or not amount_text or not payment_method:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请填写所有必填项。")
            return

        amount = float(amount_text)
        confirmation = QtWidgets.QMessageBox.question(
            self, "确认充值", f"确定要充值{amount}元到号码{phone}吗？",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if confirmation == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                self.system.make_payment(phone, amount, payment_method)
                QtWidgets.QMessageBox.information(self, "充值成功", "话费充值成功！")
                self.back_to_user()
            except PhoneNumberNotFoundError as e:
                QtWidgets.QMessageBox.warning(self, "错误", str(e))
            except PaymentProcessingError as e:
                QtWidgets.QMessageBox.critical(self, "支付错误", str(e))
            except ValueError as e:
                QtWidgets.QMessageBox.warning(self, "输入错误", str(e))
            except DatabaseError as e:
                QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "错误", str(e))

    # 账单查询
    def handle_business(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("办理业务或套餐")
        layout = QtWidgets.QVBoxLayout()

        type_label = QtWidgets.QLabel("请选择办理类型:")
        layout.addWidget(type_label)

        type_combo = QtWidgets.QComboBox()
        type_combo.addItems(["业务", "套餐"])
        layout.addWidget(type_combo)

        name_label = QtWidgets.QLabel("请选择项目名称:")
        layout.addWidget(name_label)

        name_combo = QtWidgets.QComboBox()
        layout.addWidget(name_combo)

        # 动态加载项目名称
        def load_names():
            selected_type = type_combo.currentText()
            name_combo.clear()
            if selected_type == "业务":
                services = self.system.get_available_services()
                name_combo.addItems([s['ServiceName'] for s in services])
            elif selected_type == "套餐":
                packages = self.system.get_available_packages()
                name_combo.addItems([p['PackageName'] for p in packages])

        type_combo.currentIndexChanged.connect(load_names)
        load_names()

        confirm_button = QtWidgets.QPushButton("确认办理")
        layout.addWidget(confirm_button)

        # 确认按钮事件
        def confirm_handle():
            selected_type = type_combo.currentText()
            selected_name = name_combo.currentText()
            confirmation = QtWidgets.QMessageBox.question(
                dialog, "确认办理", f"确定要办理{selected_type}：{selected_name}吗？",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            if confirmation == QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    if selected_type == "业务":
                        self.system.handle_service(self.loginTeleNumberEdit.text().strip(), selected_name)
                    elif selected_type == "套餐":
                        self.system.change_phone_package(self.loginTeleNumberEdit.text().strip(), selected_name)
                    QtWidgets.QMessageBox.information(dialog, "办理成功", f"{selected_type}办理成功！")
                    dialog.accept()
                except DatabaseError as e:
                    QtWidgets.QMessageBox.critical(dialog, "数据库错误", str(e))
                except Exception as e:
                    QtWidgets.QMessageBox.critical(dialog, "错误", str(e))

        confirm_button.clicked.connect(confirm_handle)

        dialog.setLayout(layout)
        dialog.exec()

    # 返回用户界面
    def back_to_user(self):
        self.tabWidget.setCurrentWidget(self.findChild(QtWidgets.QWidget, 'tab_user'))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())