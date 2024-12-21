from PyQt6 import QtWidgets, QtCore, QtGui
from Exception_Classes import *
from src import TelechargeSystem

class AdminInterface:
    def __init__(self, main_window):
        self.main_window = main_window
        self.system = TelechargeSystem()
        self.selected_package_id = None
        self.selected_service_id = None
        self.setup_ui()

    def setup_ui(self):
        self.adminPhoneEdit = self.main_window.findChild(QtWidgets.QLineEdit, 'adminPhoneEdit')
        self.adminFetchButton = self.main_window.findChild(QtWidgets.QPushButton, 'adminFetchButton')
        self.adminInfoWidget = self.main_window.findChild(QtWidgets.QWidget, 'adminInfoWidget')
        self.adminTransactionsWidget = self.main_window.findChild(QtWidgets.QWidget, 'adminTransactionsWidget')
        self.adminAllPackagesWidget = self.main_window.findChild(QtWidgets.QWidget, 'adminAllPackagesWidget')
        self.adminAllServicesWidget = self.main_window.findChild(QtWidgets.QWidget, 'adminAllServicesWidget')

        self.publishPackageButton = self.main_window.findChild(QtWidgets.QPushButton, 'publishPackageButton')
        self.publishServiceButton = self.main_window.findChild(QtWidgets.QPushButton, 'publishServiceButton')
        self.removePackageButton = self.main_window.findChild(QtWidgets.QPushButton, 'removePackageButton')
        self.removeServiceButton = self.main_window.findChild(QtWidgets.QPushButton, 'removeServiceButton')
        self.main_window.logoutButton_admin.clicked.connect(self.logout)
        
        if self.adminFetchButton:
            self.adminFetchButton.clicked.connect(self.fetch_admin_info)
        else:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", "找不到adminFetchButton控件")
        if self.publishPackageButton:
            self.publishPackageButton.clicked.connect(self.publish_package)
        if self.removePackageButton:
            self.removePackageButton.clicked.connect(self.remove_package)
        if self.publishServiceButton:
            self.publishServiceButton.clicked.connect(self.publish_service)
        if self.removeServiceButton:
            self.removeServiceButton.clicked.connect(self.remove_service)
            
        self.display_all_packages()
        self.display_all_services()

    def show(self):
        self.main_window.tabWidget.setCurrentIndex(5)
        self.refresh_admin_page()

    def refresh_admin_page(self):
        # 重新加载相关数据
        self.display_all_packages()
        self.display_all_services()

    def fetch_admin_info(self):
        phone = self.adminPhoneEdit.text().strip()
        self.system.check_input_format(phone, 'I')
        if not phone:
            QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "请输入电话号码。")
            return
        try:
            user_info = self.system.get_user_info_by_phone(phone)
            transaction_records = self.system.get_transaction_records_by_phone(phone)

            self.display_user_info_admin(user_info)
            self.display_transaction_records(transaction_records)

            QtWidgets.QMessageBox.information(self.main_window, "信息获取成功", "已成功获取并展示相关信息。")
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self.main_window, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

    def display_user_info_admin(self, user_info):
        layout = self.adminInfoWidget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout()
            self.adminInfoWidget.setLayout(layout)
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
        layout = self.adminTransactionsWidget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout()
            self.adminTransactionsWidget.setLayout(layout)
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
        layout = self.adminAllPackagesWidget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout()
            self.adminAllPackagesWidget.setLayout(layout)
        else:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        packages = self.system.get_available_packages()
        self.packagesTableWidget = QtWidgets.QTableWidget()
        headers = ['选择', 'PackageID', 'PackageName', 'PackagePrice', 'LaunchTime', 'ExpirationTime',
                   'ContractDuration', 'VoiceQuota', 'OverQuotaStandard']
        self.packagesTableWidget.setColumnCount(len(headers))
        self.packagesTableWidget.setHorizontalHeaderLabels(headers)
        self.packagesTableWidget.setRowCount(len(packages))
        for row, package in enumerate(packages):
            # 第一列勾选框
            check_item = QtWidgets.QTableWidgetItem()
            check_item.setFlags(check_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            check_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.packagesTableWidget.setItem(row, 0, check_item)

            self.packagesTableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(package['PackageID'])))
            self.packagesTableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(package['PackageName'])))
            self.packagesTableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(package['PackagePrice'])))
            self.packagesTableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(str(package['LaunchTime'])))
            self.packagesTableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(str(package['ExpirationTime'])))
            self.packagesTableWidget.setItem(row, 6, QtWidgets.QTableWidgetItem(str(package['ContractDuration'])))
            self.packagesTableWidget.setItem(row, 7, QtWidgets.QTableWidgetItem(str(package['VoiceQuota'])))
            self.packagesTableWidget.setItem(row, 8, QtWidgets.QTableWidgetItem(str(package['OverQuotaStandard'])))

        self.packagesTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.packagesTableWidget.horizontalHeader().setStretchLastSection(True)
        self.packagesTableWidget.resizeColumnsToContents()
        self.packagesTableWidget.itemChanged.connect(self.package_item_changed)
        layout.addWidget(self.packagesTableWidget)

    def display_all_services(self):
        layout = self.adminAllServicesWidget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout()
            self.adminAllServicesWidget.setLayout(layout)
        else:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        services = self.system.get_available_services()
        self.servicesTableWidget = QtWidgets.QTableWidget()
        headers = ['选择', 'ServiceID', 'ServiceName', 'Price', 'Quota', 'ActivationMethodID']
        self.servicesTableWidget.setColumnCount(len(headers))
        self.servicesTableWidget.setHorizontalHeaderLabels(headers)
        self.servicesTableWidget.setRowCount(len(services))
        for row, service in enumerate(services):
            # 第一列勾选框
            check_item = QtWidgets.QTableWidgetItem()
            check_item.setFlags(check_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            check_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.servicesTableWidget.setItem(row, 0, check_item)

            self.servicesTableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(service['ServiceID'])))
            self.servicesTableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(service['ServiceName'])))
            self.servicesTableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(service['Price'])))
            self.servicesTableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(str(service['Quota'])))
            self.servicesTableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(str(service['ActivationMethodID'])))

        self.servicesTableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.servicesTableWidget.horizontalHeader().setStretchLastSection(True)
        self.servicesTableWidget.resizeColumnsToContents()
        self.servicesTableWidget.itemChanged.connect(self.service_item_changed)
        layout.addWidget(self.servicesTableWidget)

    def package_item_changed(self, item):
        if item.column() == 0:  # 只处理勾选列
            row_count = self.packagesTableWidget.rowCount()
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                # 先取消其他行的勾选
                for r in range(row_count):
                    if r != item.row():
                        chk = self.packagesTableWidget.item(r, 0)
                        if chk and chk.checkState() == QtCore.Qt.CheckState.Checked:
                            chk.setCheckState(QtCore.Qt.CheckState.Unchecked)
                # 记录当前选中的packageID
                package_id_item = self.packagesTableWidget.item(item.row(), 1)
                if package_id_item:
                    self.selected_package_id = package_id_item.text()
            else:
                # 取消勾选时，如果就是当前行，则清空
                if self.selected_package_id:
                    package_id_item = self.packagesTableWidget.item(item.row(), 1)
                    if package_id_item and package_id_item.text() == self.selected_package_id:
                        self.selected_package_id = None

    def service_item_changed(self, item):
        if item.column() == 0:  # 只处理勾选列
            row_count = self.servicesTableWidget.rowCount()
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                # 先取消其他行的勾选
                for r in range(row_count):
                    if r != item.row():
                        chk = self.servicesTableWidget.item(r, 0)
                        if chk and chk.checkState() == QtCore.Qt.CheckState.Checked:
                            chk.setCheckState(QtCore.Qt.CheckState.Unchecked)
                # 记录当前选中的serviceID
                service_id_item = self.servicesTableWidget.item(item.row(), 1)
                if service_id_item:
                    self.selected_service_id = service_id_item.text()
            else:
                # 取消勾选时，如果就是当前行，则清空
                if self.selected_service_id:
                    service_id_item = self.servicesTableWidget.item(item.row(), 1)
                    if service_id_item and service_id_item.text() == self.selected_service_id:
                        self.selected_service_id = None

    # 发布套餐
    def publish_package(self):
        phone = self.main_window.current_user_phone
        if not phone:
            QtWidgets.QMessageBox.warning(self.main_window, "提示", "请先登录管理账号。")
            return

        package_id, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "请输入套餐ID:")
        if not ok or not package_id:
            return
        package_name, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "请输入套餐名称:")
        if not ok or not package_name:
            return
        price_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "请输入套餐价格(数字):")
        if not ok or not price_str:
            return
        contract_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "请输入合约期(整数,单位月):")
        if not ok or not contract_str:
            return
        voice_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "请输入语音额度(数字):")
        if not ok or not voice_str:
            return
        over_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "请输入超额标准(数字/分钟):")
        if not ok or not over_str:
            return

        try:
            price = float(price_str)
            contract_duration = int(contract_str)
            voice_quota = float(voice_str)
            over_quota_standard = float(over_str)
            self.system.add_package_for_admin(
                phone, package_id, package_name, price, 
                contract_duration, voice_quota, over_quota_standard
            )
            QtWidgets.QMessageBox.information(self.main_window, "发布成功", f"套餐[{package_id}]已发布。")
            self.display_all_packages()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

    # 下架套餐
    def remove_package(self):
        try:
            if not self.selected_package_id:
                QtWidgets.QMessageBox.warning(self.main_window, "提示", "请先勾选需要下架的套餐。")
                return
            phone = self.main_window.current_user_phone
            self.system.remove_package_for_admin(phone, self.selected_package_id)
            QtWidgets.QMessageBox.information(self.main_window, "下架成功", f"套餐[{self.selected_package_id}]已下架。")
            self.selected_package_id = None
            self.display_all_packages()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

    # 发布业务
    def publish_service(self):
        phone = self.main_window.current_user_phone
        if not phone:
            QtWidgets.QMessageBox.warning(self.main_window, "提示", "请先登录管理账号。")
            return

        service_id, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布业务", "请输入业务ID:")
        if not ok or not service_id:
            return
        service_name, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布业务", "请输入业务名称:")
        if not ok or not service_name:
            return
        price_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布业务", "请输入业务价格(数字):")
        if not ok or not price_str:
            return
        quota_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布业务", "请输入额度(数字):")
        if not ok or not quota_str:
            return
        activation_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布业务", "请输入生效方式ID(整数):")
        if not ok or not activation_str:
            return

        try:
            price = float(price_str)
            quota = float(quota_str)
            activation_method_id = int(activation_str)
            self.system.add_service_for_admin(phone, service_id, service_name, price, quota, activation_method_id)
            QtWidgets.QMessageBox.information(self.main_window, "发布成功", f"业务[{service_id}]已发布。")
            self.display_all_services()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

    # 下架业务
    def remove_service(self):
        try:
            if not self.selected_service_id:
                QtWidgets.QMessageBox.warning(self.main_window, "提示", "请先勾选需要下架的业务。")
                return
            phone = self.main_window.current_user_phone
            self.system.remove_service_for_admin(phone, self.selected_service_id)
            QtWidgets.QMessageBox.information(self.main_window, "下架成功", f"业务[{self.selected_service_id}]已下架。")
            self.selected_service_id = None
            self.display_all_services()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

    def logout(self):
        self.main_window.current_user_phone = None
        self.main_window.loginTeleNumberEdit.clear()
        self.main_window.loginSecretEdit.clear()
        self.main_window.tabWidget.setCurrentIndex(0)