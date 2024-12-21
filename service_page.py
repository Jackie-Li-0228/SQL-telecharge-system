from PyQt6 import QtWidgets, QtGui
from Exception_Classes import *
from src import TelechargeSystem

class CustomerServiceInterface:
    def __init__(self, main_window):
        self.main_window = main_window
        self.system = TelechargeSystem()
        self.setup_ui()

    def setup_ui(self):
        self.customerServicePhoneEdit = self.main_window.findChild(QtWidgets.QLineEdit, 'customerServicePhoneEdit')
        self.customerServiceButton = self.main_window.findChild(QtWidgets.QPushButton, 'customerServiceButton')
        self.customerServiceInfoWidget = self.main_window.findChild(QtWidgets.QWidget, 'customerServiceInfoWidget')
        self.customerServiceTransactionsWidget = self.main_window.findChild(QtWidgets.QWidget, 'customerServiceTransactionsWidget')
        self.allPackagesWidget = self.main_window.findChild(QtWidgets.QWidget, 'allPackagesWidget')
        self.allServicesWidget = self.main_window.findChild(QtWidgets.QWidget, 'allServicesWidget')
        self.main_window.logoutButton_service.clicked.connect(self.logout)
        
        # 展示所有套餐
        self.display_all_packages()

        # 展示所有业务
        self.display_all_services()

        if self.customerServiceButton:
            self.customerServiceButton.clicked.connect(self.fetch_customer_service_info)
        else:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", "找不到customerServiceButton控件")
        
    def show(self):
        self.main_window.tabWidget.setCurrentIndex(4)

    def fetch_customer_service_info(self):
        phone = self.customerServicePhoneEdit.text().strip()
        if not phone:
            QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "请输入电话号码。")
            return
        try:
            user_info = self.system.get_user_info_by_phone(phone)
            transaction_records = self.system.get_transaction_records_by_phone(phone)

            # 展示用户信息
            self.display_user_info(user_info)

            # 展示交易记录
            self.display_transaction_records(transaction_records)

            QtWidgets.QMessageBox.information(self.main_window, "信息获取成功", "已成功获取并展示相关信息。")
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self.main_window, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

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

        list_view = QtWidgets.QListView()
        model = QtGui.QStandardItemModel(list_view)

        for key, value in user_info.items():
            item_text = f"{key}: {value}"
            item = QtGui.QStandardItem(item_text)
            model.appendRow(item)

        list_view.setModel(model)
        layout.addWidget(list_view)

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

    def display_all_packages(self):
        layout = self.allPackagesWidget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout()
            self.allPackagesWidget.setLayout(layout)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        packages = self.system.get_available_packages()
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

    def display_all_services(self):
        layout = self.allServicesWidget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout()
            self.allServicesWidget.setLayout(layout)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        services = self.system.get_available_services()
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

    def logout(self):
        self.main_window.current_user_phone = None
        self.main_window.loginTeleNumberEdit.clear()
        self.main_window.loginSecretEdit.clear()
        self.main_window.tabWidget.setCurrentIndex(0)