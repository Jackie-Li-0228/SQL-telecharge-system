from PyQt6 import QtWidgets, QtCore
from Exception_Classes import *
from src import TelechargeSystem

class UserInterface:
    def __init__(self, main_window):
        self.main_window = main_window
        self.system = TelechargeSystem()
        self.setup_ui()

    def setup_ui(self):
        self.main_window.myPackageButton.clicked.connect(self.show_my_package)
        self.main_window.balanceButton.clicked.connect(self.show_balance)
        self.main_window.callBalanceButton.clicked.connect(self.show_call_balance)
        self.main_window.rechargeButton.clicked.connect(self.switch_to_recharge)
        self.main_window.billInquiryButton.clicked.connect(self.switch_to_bill_inquiry)
        self.main_window.businessHandlingButton.clicked.connect(self.switch_to_business_handling)
        self.main_window.logoutButton_user.clicked.connect(self.logout)

    def show(self):
        self.main_window.tabWidget.setCurrentIndex(3)

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

    def switch_to_recharge(self):
        self.main_window.tabWidget.setCurrentWidget(self.main_window.findChild(QtWidgets.QWidget, 'tab_recharge'))

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

    def logout(self):
        self.main_window.current_user_phone = None
        self.main_window.loginTeleNumberEdit.clear()
        self.main_window.loginSecretEdit.clear()
        self.main_window.tabWidget.setCurrentIndex(0)
