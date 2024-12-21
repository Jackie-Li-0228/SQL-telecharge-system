from PyQt6 import QtWidgets, QtCore
from decimal import Decimal, InvalidOperation
from Exception_Classes import *
from src import TelechargeSystem

class UserInterface:
    def __init__(self, main_window):
        self.main_window = main_window
        self.system = TelechargeSystem()
        self.setup_ui()

    def setup_ui(self):
        # 仅连接一次信号
        self.main_window.myPackageButton.clicked.connect(self.show_my_package)
        self.main_window.balanceButton.clicked.connect(self.show_balance)
        self.main_window.callBalanceButton.clicked.connect(self.show_call_balance)
        self.main_window.rechargeButton.clicked.connect(self.switch_to_recharge)
        self.main_window.billInquiryButton.clicked.connect(self.switch_to_bill_inquiry)
        self.main_window.businessHandlingButton.clicked.connect(self.switch_to_business_handling)
        self.main_window.callRecordsButton.clicked.connect(self.show_call_records)
        self.main_window.logoutButton_user.clicked.connect(self.logout)
        
        # 账号停机判定
        self.accountStatusLabel = self.main_window.findChild(QtWidgets.QLabel, 'accountStatusLabel_user')

        # 充值界面元素
        self.main_window.confirmRechargeButton.clicked.connect(self.confirm_recharge)
        self.main_window.backToUserButton_recharge.clicked.connect(self.back_to_user)
        self.rechargePhoneEdit=self.main_window.findChild(QtWidgets.QLineEdit, 'rechargePhoneEdit')
        self.rechargeAmountEdit=self.main_window.findChild(QtWidgets.QLineEdit, 'rechargeAmountEdit')
        self.rechargeMethodEdit=self.main_window.findChild(QtWidgets.QLineEdit, 'rechargeMethodEdit')

        # 账单查询界面按钮
        self.main_window.backToUserButton_billInquiry.clicked.connect(self.back_to_user)

        # 业务办理界面按钮
        self.main_window.handleBusinessButton.clicked.connect(self.handle_business)
        self.main_window.backToUserButton_businessHandling.clicked.connect(self.back_to_user)

    def back_to_user(self):
        self.main_window.tabWidget.setCurrentWidget(self.main_window.tab_user)
        self.refresh_user_page()
    
    def show(self):
        self.main_window.tabWidget.setCurrentIndex(3)
        self.refresh_user_page()

    def refresh_user_page(self):
        if self.accountStatusLabel:
            result = self.system.get_phoneaccount_by_phone(self.main_window.current_user_phone)
            self.main_window.is_suspended = result['IsSuspended']
            user_status = self.main_window.is_suspended
            if user_status == 0:
                self.accountStatusLabel.setText("状态: 正常")
            else:
                self.accountStatusLabel.setText("状态: 停机")

    def show_call_records(self):
        phone = self.main_window.current_user_phone
        try:
            # 调用 src.py 中的方法获取通话记录
            call_records = self.system.get_call_records_by_phone(phone)
        
            # 格式化通话记录
            record_strings = [
                f"时间: {record['CallTime']}, 时长: {record['CallDuration']} 分钟, 呼叫方: {record['Caller']}, 接收方: {record['Receiver']}"
                for record in call_records
            ]
        
            # 获取 ListView
            call_records_list_view = self.main_window.findChild(QtWidgets.QListView, 'callRecordsListView')
            if not call_records_list_view:
                # 如果 ListView 不存在，创建一个并添加到布局
                call_records_list_view = QtWidgets.QListView()
                call_records_list_view.setObjectName('callRecordsListView')
                bill_inquiry_layout = self.main_window.findChild(QtWidgets.QVBoxLayout, 'billInquiryLayout')  # 确认布局名称
                if bill_inquiry_layout:
                    bill_inquiry_layout.addWidget(call_records_list_view)
                else:
                    QtWidgets.QMessageBox.critical(self.main_window, "错误", "找到账单查询界面的布局 billInquiryLayout")
                    return
        
            # 设置 ListView 的模型
            model = QtCore.QStringListModel()
            model.setStringList(record_strings)
            call_records_list_view.setModel(model)
        
            # 切换到账单查询界面
            self.switch_to_bill_inquiry()
        
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self.main_window, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

    def show_my_package(self):
        phone = self.main_window.current_user_phone
        try:
            package_info = self.system.get_package_details(phone)
            info = "\n".join([f"{key}: {value}" for key, value in package_info.items()])
            QtWidgets.QMessageBox.information(self.main_window, "我的套餐", info)
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self.main_window, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

    # 话费余额
    def show_balance(self):
        phone = self.main_window.current_user_phone
        try:
            balance_info = self.system.get_package_details(phone)
            info = f"话费余额: {balance_info['AccountBalance']}元\n"
            QtWidgets.QMessageBox.information(self.main_window, "话费余额", info)
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self.main_window, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

    # 通话余额
    def show_call_balance(self):
        phone = self.main_window.current_user_phone
        try:
            call_balance_info = self.system.get_package_details(phone)
            info = f"本月剩余语音配额: {call_balance_info['VoiceBalance']}分钟\n"
            QtWidgets.QMessageBox.information(self.main_window, "通话余额", info)
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self.main_window, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

    # 切换到充值界面
    def switch_to_recharge(self):
        self.main_window.tabWidget.setCurrentWidget(self.main_window.findChild(QtWidgets.QWidget, 'tab_recharge'))
        
    # 充值
    def confirm_recharge(self):
        phone = self.main_window.rechargePhoneEdit.text().strip()
        self.system.check_input_format(phone, 'I')
        amount_text = self.main_window.rechargeAmountEdit.text().strip()
        payment_method = self.main_window.rechargeMethodEdit.text().strip()
        self.system.check_input_format(payment_method, 'S')
        if not phone or not amount_text or not payment_method:
            QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "请填写所有必填项。")
            return
        
        try:
            amount = Decimal(amount_text)
        except InvalidOperation:
            QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "请输入有效的金额。")
            return

        try:
            if amount <= 0 or amount > 1000:
                QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "充值金额必须大于0且小于等于1000。")
                return
        except InvalidOperation:
            QtWidgets.QMessageBox.warning(self.main_window, "数值异常", "请输入有效的金额。")
            return

        # 检查小数位数
        if amount.as_tuple().exponent < -2:
            QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "充值金额最多有两位小数。")
            return

        confirmation = QtWidgets.QMessageBox.question(
            self.main_window, "确认充值", f"确定要充值{amount}元到号码{phone}吗？",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if confirmation == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                self.system.make_payment(phone, float(amount),  payment_method)
                QtWidgets.QMessageBox.information(self.main_window, "充值成功", "话费充值成功！")
                self.back_to_user()
            except PhoneNumberNotFoundError as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))
            except PaymentProcessingError as e:
                QtWidgets.QMessageBox.critical(self.main_window, "支付错误", str(e))
            except ValueError as e:
                QtWidgets.QMessageBox.warning(self.main_window, "输入错误", str(e))
            except DatabaseError as e:
                QtWidgets.QMessageBox.critical(self.main_window, "数据库错误", str(e))
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

    # 切换到账单查询界面
    def switch_to_bill_inquiry(self):
        phone = self.main_window.current_user_phone
        try:
            transaction_records = self.system.get_transaction_records_by_phone(phone)
            self.billTableWidget = self.main_window.findChild(QtWidgets.QTableWidget, 'billTableWidget')
            if self.billTableWidget is None:
                self.billTableWidget = QtWidgets.QTableWidget()
                self.billTableWidget.setObjectName('billTableWidget')
                self.billTableLayout = self.main_window.findChild(QtWidgets.QVBoxLayout, 'billTableLayout')
                if self.billTableLayout:
                    self.billTableLayout.addWidget(self.billTableWidget)
                else:
                    QtWidgets.QMessageBox.critical(self.main_window, "错误", "找不到账单表格布局billTableLayout")
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
            self.main_window.tabWidget.setCurrentWidget(self.main_window.findChild(QtWidgets.QWidget, 'tab_billInquiry'))
        except PhoneNumberNotFoundError as e:
            QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))
        except DatabaseError as e:
            QtWidgets.QMessageBox.critical(self.main_window, "数据库错误", str(e))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", str(e))

    # 切换到业务办理界面
    def switch_to_business_handling(self):
        try:
            services = self.system.get_available_services()
            packages = self.system.get_available_packages()

            self.selected_service = None
            self.selected_package = None

            # 服务表格
            self.servicesTableWidget = self.main_window.findChild(QtWidgets.QTableWidget, 'servicesTableWidget')
            if self.servicesTableWidget is None:
                self.servicesTableWidget = QtWidgets.QTableWidget()
                self.servicesTableWidget.setObjectName('servicesTableWidget')
                self.servicesTableLayout = self.main_window.findChild(QtWidgets.QVBoxLayout, 'servicesTableLayout')
                if self.servicesTableLayout:
                    self.servicesTableLayout.addWidget(self.servicesTableWidget)
                else:
                    QtWidgets.QMessageBox.critical(self.main_window, "错误", "找不到服务表格布局servicesTableLayout")
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
            self.packagesTableWidget = self.main_window.findChild(QtWidgets.QTableWidget, 'packagesTableWidget')
            if self.packagesTableWidget is None:
                self.packagesTableWidget = QtWidgets.QTableWidget()
                self.packagesTableWidget.setObjectName('packagesTableWidget')
                self.packagesTableLayout = self.main_window.findChild(QtWidgets.QVBoxLayout, 'packagesTableLayout')
                if self.packagesTableLayout:
                    self.packagesTableLayout.addWidget(self.packagesTableWidget)
                else:
                    QtWidgets.QMessageBox.critical(self.main_window, "错误", "找不到套餐表格布局packagesTableLayout")
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

            self.main_window.tabWidget.setCurrentWidget(self.main_window.findChild(QtWidgets.QWidget, 'tab_businessHandling'))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, "错误", f"加载业务办理界面失败：{str(e)}")

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
                self.main_window, "确认办理", f"确定要办理以下业务吗？\n\n{details}",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            if confirmation == QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    self.system.subscribe_service(self.main_window.current_user_phone, service['ServiceID'])
                    QtWidgets.QMessageBox.information(self.main_window, "办理成功", "业务办理成功！")
                    self.switch_to_business_handling()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self.main_window, "办理失败", str(e))
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
                self.main_window, "确认办理", f"确定要办理以下套餐吗？\n\n{details}",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            if confirmation == QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    self.system.change_phone_package(self.main_window.current_user_phone, package['PackageID'])
                    QtWidgets.QMessageBox.information(self.main_window, "办理成功", "套餐办理成功！")
                    self.switch_to_business_handling()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self.main_window, "办理失败", str(e))
        else:
            QtWidgets.QMessageBox.warning(self.main_window, "提示", "请选择要办理的业务或套餐！")
            
    # 限制表格只选一项,需要分别处理        
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
                    'PackagePrice': self.packagesTableWidget.item(item.row(), 3).text(),
                    'ContractDuration': self.packagesTableWidget.item(item.row(), 4).text(),
                    'VoiceQuota': self.packagesTableWidget.item(item.row(), 5).text(),
                    'OverQuotaStandard': self.packagesTableWidget.item(item.row(), 6).text()
                }
                self.selected_service = None
            else:
                self.selected_package = None

    def logout(self):
        self.main_window.current_user_phone = None
        self.main_window.loginTeleNumberEdit.clear()
        self.main_window.loginSecretEdit.clear()
        self.main_window.tabWidget.setCurrentIndex(0)