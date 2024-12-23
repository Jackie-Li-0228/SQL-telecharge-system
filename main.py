import sys
import os
import pymysql
from PyQt6 import QtWidgets, uic, QtGui, QtCore
from decimal import Decimal, InvalidOperation
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
            
        # 初始化TelechargeSystem实例
        self.system = TelechargeSystem()
        self.current_user_phone = None

        # 登录界面按钮
        self.loginButton.clicked.connect(self.login)
        self.gotoregisterButton.clicked.connect(self.gotoregister)
        
        # 注册界面按钮
        self.registerButton.clicked.connect(self.register)
        self.backtologinButton.clicked.connect(self.backtologin)

        # 用户界面组件
        self.myPackageButton.clicked.connect(self.show_my_package)
        self.balanceButton.clicked.connect(self.show_balance)
        self.callBalanceButton.clicked.connect(self.show_call_balance)
        self.rechargeButton.clicked.connect(self.switch_to_recharge)
        self.billInquiryButton.clicked.connect(self.switch_to_bill_inquiry)
        self.businessHandlingButton.clicked.connect(self.switch_to_business_handling)
        
        self.accountStatusLabel = self.findChild(QtWidgets.QLabel, 'accountStatusLabel_user')
        if self.accountStatusLabel:
            self.accountStatusLabel.setText("状态: ")
        else:
            QtWidgets.QMessageBox.critical(self, "错误", "找不到accountStatusLabel_user控件")
        
        self.logoutButton_user = self.findChild(QtWidgets.QPushButton, 'logoutButton_user')
        if self.logoutButton_user:
            self.logoutButton_user.clicked.connect(self.logout)
        else:
            QtWidgets.QMessageBox.critical(self, "错误", "找不到logoutButton_user控件")
            
        # 客服界面组件
        self.customerServicePhoneEdit = self.findChild(QtWidgets.QLineEdit, 'customerServicePhoneEdit')
        self.customerServiceButton = self.findChild(QtWidgets.QPushButton, 'customerServiceButton')
        self.customerServiceInfoWidget = self.findChild(QtWidgets.QWidget, 'customerServiceInfoWidget')
        self.customerServiceTransactionsWidget = self.findChild(QtWidgets.QWidget, 'customerServiceTransactionsWidget')
        self.allPackagesWidget = self.findChild(QtWidgets.QWidget, 'allPackagesWidget')
        self.allServicesWidget = self.findChild(QtWidgets.QWidget, 'allServicesWidget')

        if self.customerServiceButton:
            self.customerServiceButton.clicked.connect(self.fetch_customer_service_info)
        else:
            QtWidgets.QMessageBox.critical(self, "错误", "找不到customerServiceButton控件")


        # 充值界面按钮
        self.confirmRechargeButton.clicked.connect(self.confirm_recharge)
        self.backToUserButton_recharge.clicked.connect(self.back_to_user)

        # 账单查询界面按钮
        self.backToUserButton_billInquiry.clicked.connect(self.back_to_user)

        # 业务办理界面按钮
        self.handleBusinessButton.clicked.connect(self.handle_business)
        self.backToUserButton_businessHandling.clicked.connect(self.back_to_user)

        # 加载注册界面的套餐数据
        self.load_packages()

    def load_packages(self):
        try:
            packages = self.system.get_available_packages()
            self.taocancombox.clear()
            for package in packages:
                self.taocancombox.addItem(package['PackageName'], package['PackageID'])
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"加载套餐数据失败：{str(e)}")


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
                # 查询用户类型、密码和状态
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
                    if hasattr(self, 'accountStatusLabel'):
                        self.accountStatusLabel.setText("状态: 停机")
                else:
                    if hasattr(self, 'accountStatusLabel'):
                        self.accountStatusLabel.setText("状态: 正常")


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
        phone = self.registerteleNumberEdit.text().strip()
        password = self.registersecretEdit.text().strip()
        name = self.nameEdit.text().strip()
        id_card = self.idCardEdit.text().strip()
        package_id = self.taocancombox.currentData()

        # 输入验证
        if not phone or not password or not name or not id_card:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请填写所有必填项。")
            return

        # 格式验证
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

    # 套餐查询
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
            balance_info = self.system.get_package_details(phone)
            # info = f"话费余额: {balance_info['AccountBalance']}元\n本月消费: {balance_info['consumed_balance']}元"
            info = f"话费余额: {balance_info['AccountBalance']}元\n"
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
            call_balance_info = self.system.get_package_details(phone)
             # info = f"本月剩余语音配额: {call_balance_info['VoiceBalance']}分钟\n本月通话时长: {call_balance_info['call_duration']}分钟"
            info = f"本月剩余语音配额: {call_balance_info['VoiceBalance']}分钟\n"
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
            self.billTableWidget = self.findChild(QtWidgets.QTableWidget, 'billTableWidget')
            if self.billTableWidget is None:
                self.billTableWidget = QtWidgets.QTableWidget()
                self.billTableWidget.setObjectName('billTableWidget')
                self.billTableLayout = self.findChild(QtWidgets.QVBoxLayout, 'billTableLayout')
                if self.billTableLayout:
                    self.billTableLayout.addWidget(self.billTableWidget)
                else:
                    QtWidgets.QMessageBox.critical(self, "错误", "找到账单表格布局billTableLayout")
                    return
            headers = ['交易ID', '时间', '项目', '金额']
            self.billTableWidget.setColumnCount(len(headers))
            self.billTableWidget.setHorizontalHeaderLabels(headers)
            self.billTableWidget.setRowCount(len(transaction_records))
            for row, record in enumerate(transaction_records):
                self.billTableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(record['TransactionID'])))
                self.billTableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(record['TransactionTime'])))
                self.billTableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(record['PurchasedItem']))
                self.billTableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{record['Amount']}元"))
            # 设置表格为只读
            self.billTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            self.billTableWidget.horizontalHeader().setStretchLastSection(True)
            self.billTableWidget.resizeColumnsToContents()
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

            self.selected_service = None
            self.selected_package = None

            # 服务表格
            self.servicesTableWidget = self.findChild(QtWidgets.QTableWidget, 'servicesTableWidget')
            if self.servicesTableWidget is None:
                self.servicesTableWidget = QtWidgets.QTableWidget()
                self.servicesTableWidget.setObjectName('servicesTableWidget')
                self.servicesTableLayout = self.findChild(QtWidgets.QVBoxLayout, 'servicesTableLayout')
                if self.servicesTableLayout:
                    self.servicesTableLayout.addWidget(self.servicesTableWidget)
                else:
                    QtWidgets.QMessageBox.critical(self, "错误", "找不到服务表格布局servicesTableLayout")
                    return
            service_headers = ['选择', '业务ID', '业务名称', '价格', '额度', '生效方式']
            self.servicesTableWidget.setColumnCount(len(service_headers))
            self.servicesTableWidget.setHorizontalHeaderLabels(service_headers)
            self.servicesTableWidget.setRowCount(len(services))
            for row, service in enumerate(services):
                select_item = QtWidgets.QTableWidgetItem()
                select_item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                select_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                self.servicesTableWidget.setItem(row, 0, select_item)
                self.servicesTableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(service['ServiceID'])))
                self.servicesTableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(service['ServiceName']))
                self.servicesTableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{service['Price']}元"))
                self.servicesTableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{service['Quota']}"))
                self.servicesTableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(service.get('ActivationMethod', '未知')))
            self.servicesTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            self.servicesTableWidget.horizontalHeader().setStretchLastSection(True)
            self.servicesTableWidget.resizeColumnsToContents()
            self.servicesTableWidget.itemChanged.connect(self.service_item_changed)

            # 套餐表格
            self.packagesTableWidget = self.findChild(QtWidgets.QTableWidget, 'packagesTableWidget')
            if self.packagesTableWidget is None:
                self.packagesTableWidget = QtWidgets.QTableWidget()
                self.packagesTableWidget.setObjectName('packagesTableWidget')
                self.packagesTableLayout = self.findChild(QtWidgets.QVBoxLayout, 'packagesTableLayout')
                if self.packagesTableLayout:
                    self.packagesTableLayout.addWidget(self.packagesTableWidget)
                else:
                    QtWidgets.QMessageBox.critical(self, "错误", "找不到套餐表格布局packagesTableLayout")
                    return
            package_headers = ['选择', '套餐ID', '套餐名称', '价格', '合约期', '语音额度', '超套标准']
            self.packagesTableWidget.setColumnCount(len(package_headers))
            self.packagesTableWidget.setHorizontalHeaderLabels(package_headers)
            self.packagesTableWidget.setRowCount(len(packages))
            for row, package in enumerate(packages):
                select_item = QtWidgets.QTableWidgetItem()
                select_item.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                select_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                self.packagesTableWidget.setItem(row, 0, select_item)
                self.packagesTableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(package['PackageID'])))
                self.packagesTableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(package['PackageName']))
                self.packagesTableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{package['PackagePrice']}元"))
                self.packagesTableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{package['ContractDuration']}个月"))
                self.packagesTableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(f"{package['VoiceQuota']}分钟"))
                self.packagesTableWidget.setItem(row, 6, QtWidgets.QTableWidgetItem(f"{package['OverQuotaStandard']}元/分钟"))
            self.packagesTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            self.packagesTableWidget.horizontalHeader().setStretchLastSection(True)
            self.packagesTableWidget.resizeColumnsToContents()
            self.packagesTableWidget.itemChanged.connect(self.package_item_changed)

            self.tabWidget.setCurrentWidget(self.findChild(QtWidgets.QWidget, 'tab_businessHandling'))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"加载业务办理界面失败：{str(e)}")

    # 充值
    def confirm_recharge(self):
        phone = self.rechargePhoneEdit.text().strip()
        amount_text = self.rechargeAmountEdit.text().strip()
        payment_method = self.rechargeMethodEdit.text().strip()
        if not phone or not amount_text or not payment_method:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请填写所有必填项。")
            return
        
        try:
            amount = Decimal(amount_text)
        except InvalidOperation:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请输入有效的金额。")
            return

        try:
            if amount <= 0 or amount > 1000:
                QtWidgets.QMessageBox.warning(self, "输入错误", "充值金额必须大于0且小于等于1000。")
                return
        except InvalidOperation:
            QtWidgets.QMessageBox.warning(self, "数值异常", "请输入有效的金额。")
            return

        # 检查小数位数
        if amount.as_tuple().exponent < -2:
            QtWidgets.QMessageBox.warning(self, "输入错误", "充值金额最多有两位小数。")
            return

        confirmation = QtWidgets.QMessageBox.question(
            self, "确认充值", f"确定要充值{amount}元到号码{phone}吗？",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if confirmation == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                self.system.make_payment(phone, float(amount),  payment_method)
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
                
    # 套餐办理
    def handle_business(self):
        if self.selected_service:
            # 办理业务
            service = self.selected_service
            details = (
                f"业务ID: {service['ServiceID']}\n"
                f"业务名称: {service['Name']}\n"
                f"价格: {service['Price']}元\n"
                f"额度: {service['Quota']}\n"
                f"生效方式: {service['ActivationMethodName']}"
            )
            confirmation = QtWidgets.QMessageBox.question(
                self, "确认办理", f"确定要办理以下业务吗？\n\n{details}",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            if confirmation == QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    self.system.subscribe_service(self.current_user_phone, service['ServiceID'])
                    QtWidgets.QMessageBox.information(self, "办理成功", "业务办理成功！")
                    self.switch_to_business_handling()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "办理失败", str(e))
        elif self.selected_package:
            # 办理套餐
            package = self.selected_package
            details = (
                f"套餐ID: {package['PackageID']}\n"
                f"套餐名称: {package['PackageName']}\n"
                f"价格: {package['PackagePrice']}元\n"
                f"合约期: {package['ContractDuration']}个月\n"
                f"语音额度: {package['VoiceQuota']}分钟\n"
                f"超套标准: {package['OverQuotaStandard']}元/分钟"
            )
            confirmation = QtWidgets.QMessageBox.question(
                self, "确认办理", f"确定要办理以下套餐吗？\n\n{details}",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            if confirmation == QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    self.system.change_phone_package(self.current_user_phone, package['PackageID'])
                    QtWidgets.QMessageBox.information(self, "办理成功", "套餐办理成功！")
                    self.switch_to_business_handling()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "办理失败", str(e))
        else:
            QtWidgets.QMessageBox.warning(self, "提示", "请选择要办理的业务或套餐！")

    # 返回用户界面
    def back_to_user(self):
        self.tabWidget.setCurrentWidget(self.tab_user)
        
        # 限制服务表格只选一项,需要分别处理
    def service_item_changed(self, item):
        if item.column() == 0:
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                # 取消套餐表格的所有选择
                for row in range(self.packagesTableWidget.rowCount()):
                    package_item = self.packagesTableWidget.item(row, 0)
                    package_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                # 取消服务表格其他行的选择
                for row in range(self.servicesTableWidget.rowCount()):
                    if row != item.row():
                        other_item = self.servicesTableWidget.item(row, 0)
                        other_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                # 记录选择的服务
                self.selected_service = {
                    'ServiceID': self.servicesTableWidget.item(item.row(), 1).text(),
                    'Name': self.servicesTableWidget.item(item.row(), 2).text(),
                    'Price': self.servicesTableWidget.item(item.row(), 3).text(),
                    'Quota': self.servicesTableWidget.item(item.row(), 4).text(),
                    'ActivationMethodName': self.servicesTableWidget.item(item.row(), 5).text()
                }
                self.selected_package = None
            else:
                self.selected_service = None

    def package_item_changed(self, item):
        if item.column() == 0:
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                # 取消服务表格的所有选择
                for row in range(self.servicesTableWidget.rowCount()):
                    service_item = self.servicesTableWidget.item(row, 0)
                    service_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                # 取消套餐表格其他行的选择
                for row in range(self.packagesTableWidget.rowCount()):
                    if row != item.row():
                        other_item = self.packagesTableWidget.item(row, 0)
                        other_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                # 记录选择的套餐
                self.selected_package = {
                    'PackageID': self.packagesTableWidget.item(item.row(), 1).text(),
                    'PackageName': self.packagesTableWidget.item(item.row(), 2).text(),
                    'Price': self.packagesTableWidget.item(item.row(), 3).text(),
                    'ContractDuration': self.packagesTableWidget.item(item.row(), 4).text(),
                    'VoiceQuota': self.packagesTableWidget.item(item.row(), 5).text(),
                    'OverQuotaStandard': self.packagesTableWidget.item(item.row(), 6).text()
                }
                self.selected_service = None
            else:
                self.selected_package = None

    def logout(self):
        self.current_user_phone = None
        self.loginTeleNumberEdit.clear()
        self.loginSecretEdit.clear()
        if hasattr(self, 'accountStatusLabel'):
            self.accountStatusLabel.setText("状态: ")
            self.accountStatusLabel.setStyleSheet("color: black;")
        self.tabWidget.setCurrentIndex(0)
    
    # 客服界面功能
    def fetch_customer_service_info(self):
        phone = self.customerServicePhoneEdit.text().strip()
        if not phone:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请输入电话号码。")
            return
        try:
            user_info = self.system.get_user_info_by_phone(phone)
            transaction_records = self.system.get_transaction_records_by_phone(phone)
            packages = self.system.get_available_packages()
            services = self.system.get_available_services()

            # 展示用户信息
            self.display_user_info(user_info)

            # 展示交易记录
            self.display_transaction_records(transaction_records)

            # 展示所有套餐
            self.display_all_packages(packages)

            # 展示所有业务
            self.display_all_services(services)

            QtWidgets.QMessageBox.information(self, "信息获取成功", "已成功获取并展示相关信息。")
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", str(e))

    def display_user_info(self, user_info):
        layout = self.customerServiceInfoWidget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout()
            self.customerServiceInfoWidget.setLayout(layout)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        for key, value in user_info.items():
            label = QtWidgets.QLabel(f"{key}: {value}")
            layout.addWidget(label)

    def display_transaction_records(self, transaction_records):
        layout = self.customerServiceTransactionsWidget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout()
            self.customerServiceTransactionsWidget.setLayout(layout)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        table = QtWidgets.QTableWidget()
        headers = ['TransactionID', 'Time', 'Item', 'Amount']
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(transaction_records))
        for row, record in enumerate(transaction_records):
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(record['TransactionID'])))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(record['TransactionTime'])))
            table.setItem(row, 2, QtWidgets.QTableWidgetItem(record['PurchasedItem']))
            table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{record['Amount']}元"))
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()
        layout.addWidget(table)

    def display_all_packages(self, packages):
        layout = self.allPackagesWidget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout()
            self.allPackagesWidget.setLayout(layout)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        table = QtWidgets.QTableWidget()
        headers = ['PackageID', 'PackageName', 'PackagePrice', 'LaunchTime', 'ExpirationTime', 'ContractDuration',     'VoiceQuota', 'OverQuotaStandard']
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(packages))
        for row, package in enumerate(packages):
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(package['PackageID']))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(package['PackageName']))
            table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{package['PackagePrice']}元"))
            table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(package['LaunchTime'])))
            table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(package['ExpirationTime'])))
            table.setItem(row, 5, QtWidgets.QTableWidgetItem(f"{package['ContractDuration']}个月"))
            table.setItem(row, 6, QtWidgets.QTableWidgetItem(f"{package['VoiceQuota']}分钟"))
            table.setItem(row, 7, QtWidgets.QTableWidgetItem(f"{package['OverQuotaStandard']}元/分钟"))
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()
        layout.addWidget(table)

    def display_all_services(self, services):
        layout = self.allServicesWidget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout()
            self.allServicesWidget.setLayout(layout)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        table = QtWidgets.QTableWidget()
        headers = ['ServiceID', 'ServiceName', 'Price', 'Quota', 'ActivationMethodID']
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(services))
        for row, service in enumerate(services):
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(service['ServiceID']))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(service['ServiceName']))
            table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{service['Price']}元"))
            table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{service['Quota']}"))
            table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(service['ActivationMethodID'])))
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()
        layout.addWidget(table)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())