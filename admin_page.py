from PyQt6 import QtWidgets, QtGui
from Exception_Classes import *
from src import TelechargeSystem
from PyQt6.QtCore import QStringListModel

class AdminInterface:
    def __init__(self, main_window):
        self.main_window = main_window
        self.system = TelechargeSystem()

        # 下拉框
        self.userComboBox = None
        self.businessComboBox = None
        self.packageComboBox = None
        self.phoneLineEdit = None
        self.displayListView = None 

        self.setup_ui()

    def setup_ui(self):
        self.userComboBox = self.main_window.findChild(QtWidgets.QComboBox, 'userComboBox')
        self.businessComboBox = self.main_window.findChild(QtWidgets.QComboBox, 'businessComboBox')
        self.packageComboBox = self.main_window.findChild(QtWidgets.QComboBox, 'packageComboBox')
        self.phoneLineEdit = self.main_window.findChild(QtWidgets.QLineEdit, 'phoneLineEdit')
        self.displayListView = self.main_window.findChild(QtWidgets.QListView, 'displayListView')  

        self.main_window.refreshButton_admin.clicked.connect(self.refresh_admin_page)
        logout_button = self.main_window.findChild(QtWidgets.QPushButton, 'logoutButton_admin')
        if logout_button:
            logout_button.clicked.connect(self.logout)
        else:
            print("logoutButton_admin 未找到。")

        self.userComboBox.clear()
        self.userComboBox.addItem("选择功能")
        self.userComboBox.addItem("查看详细信息")
        self.userComboBox.addItem("查看交易记录")
        self.userComboBox.addItem("模拟通话")
        self.userComboBox.currentIndexChanged.connect(self.handle_user_actions)

        self.businessComboBox.clear()
        self.businessComboBox.addItem("选择功能")
        self.businessComboBox.addItem("展示所有业务")
        self.businessComboBox.addItem("发布新业务")
        self.businessComboBox.currentIndexChanged.connect(self.handle_business_actions)

        self.packageComboBox.clear()
        self.packageComboBox.addItem("选择功能")
        self.packageComboBox.addItem("展示所有套餐")
        self.packageComboBox.addItem("下架套餐")
        self.packageComboBox.addItem("发布新套餐")
        self.packageComboBox.currentIndexChanged.connect(self.handle_package_actions)

    def clear_display(self):
        if self.displayListView:
            model = QStringListModel()
            self.displayListView.setModel(model)
            print("displayListView 已清空。")
            self.refresh_admin_page()
        else:
            print("displayListView 未找到，无法清空。")

    def refresh_admin_page(self):
        self.system.close_connection()
        self.system.connect_db()
    
    def handle_user_actions(self):
        idx = self.userComboBox.currentIndex()
        phone = self.phoneLineEdit.text().strip()

        if not phone:
            QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "电话号码不能为空。")
            self.userComboBox.blockSignals(True)
            self.userComboBox.setCurrentIndex(0)
            self.userComboBox.blockSignals(False)
            return

        if idx == 1:  
            try:
                user_info = self.system.get_user_info_by_phone(phone)
                info_text = "\n".join([f"{k}: {v}" for k, v in user_info.items()])
                QtWidgets.QMessageBox.information(self.main_window, "用户详细信息", info_text)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))

        elif idx == 2: 
            try:
                self.clear_display()
                records = self.system.get_transaction_records_by_phone(phone)
                list_items = [f"TransactionID: {rec.get('TransactionID', '')}, Time: {rec.get('TransactionTime', '')}, Item: {rec.get('PurchasedItem', '')}, Amount: {rec.get('Amount', '')}" for rec in records]
                model = QStringListModel(list_items)
                self.displayListView.setModel(model)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))

        elif idx == 3: 
            self.clear_display()
            caller = phone
            receiver, ok = QtWidgets.QInputDialog.getText(self.main_window, "模拟通话", "被叫号码:")
            if ok and receiver:
                duration_str, ok2 = QtWidgets.QInputDialog.getText(self.main_window, "通话时长", "请输入分钟:")
                if ok2 and duration_str:
                    try:
                        duration = int(duration_str)
                        self.system.simulate_call(caller, receiver, duration)
                        QtWidgets.QMessageBox.information(self.main_window, "成功", "模拟通话完成。")
                    except Exception as e:
                        QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))

        # 阻塞信号，防止重置信号触发
        self.userComboBox.blockSignals(True)
        self.userComboBox.setCurrentIndex(0)
        self.userComboBox.blockSignals(False)

    def handle_business_actions(self):
        idx = self.businessComboBox.currentIndex()

        if idx == 1:  # 展示所有业务
            try:
                self.clear_display()
                services = self.system.get_available_services()
                list_items = [f"ServiceID: {srv.get('ServiceID', '')}, ServiceName: {srv.get('ServiceName', '')}, Price: {srv.get('Price', '')}, Quota: {srv.get('Quota', '')}, ActivationMethodID: {srv.get('ActivationMethodID', '')}, Status: {srv.get('Status', '')}" for srv in services]
                model = QStringListModel(list_items)
                self.displayListView.setModel(model)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))

        elif idx == 2:  # 发布新业务
            service_id, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布业务", "业务ID:")

            if not ok or not service_id:
                return
            try:
                if self.system.service_id_exists(service_id.strip()):
                    QtWidgets.QMessageBox.warning(self.main_window, "错误", f"业务ID {service_id.strip()} 已存在，请更换其他ID。")
                    return
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))
                return
            service_name, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布业务", "业务名称:")
            if not ok or not service_name:
                return
            price_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布业务", "价格(数字):")
            if not ok or not price_str:
                return
            quota_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布业务", "额度(数字):")
            if not ok or not quota_str:
                return

            try:
                phone = self.main_window.current_user_phone
                if not phone:
                    QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "管理员电话号码未设置。")
                    return
                self.system.add_service_for_admin(
                    phone,
                    service_id,
                    service_name,
                    float(price_str),
                    float(quota_str),
                    1 # 默认激活方式为1
                )
                QtWidgets.QMessageBox.information(self.main_window, "成功", "业务已发布。")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))

        # 阻塞信号，防止重置信号触发
        self.businessComboBox.blockSignals(True)
        self.businessComboBox.setCurrentIndex(0)
        self.businessComboBox.blockSignals(False)

    def handle_package_actions(self):
        idx = self.packageComboBox.currentIndex()

        if idx == 1:  # 展示所有套餐
            try:
                self.clear_display()
                packages = self.system.get_available_packages()
                list_items = [f"PackageID: {pkg.get('PackageID', '')}, PackageName: {pkg.get('PackageName', '')}, Price: {pkg.get('PackagePrice', '')}, LaunchTime: {pkg.get('LaunchTime', '')}, ExpirationTime: {pkg.get('ExpirationTime', '')}, ContractDuration: {pkg.get('ContractDuration', '')}, VoiceQuota: {pkg.get('VoiceQuota', '')}, OverQuotaStandard: {pkg.get('OverQuotaStandard', '')}, Status: {pkg.get('Status', '')}" for pkg in packages]
                model = QStringListModel(list_items)
                self.displayListView.setModel(model)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))

        elif idx == 2:  # 下架套餐
            package_id, ok = QtWidgets.QInputDialog.getText(self.main_window, "下架套餐", "输入要下架的套餐ID:")
            if ok and package_id:
                confirm = QtWidgets.QMessageBox.question(
                    self.main_window, 
                    "确认", 
                    f"确定下架 {package_id}？", 
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
                )
                if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
                    try:
                        phone = self.main_window.current_user_phone
                        if not phone:
                            QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "管理员电话号码未设置。")
                            return
                        self.system.remove_package_for_admin(phone, package_id)
                        QtWidgets.QMessageBox.information(self.main_window, "成功", "已下架套餐。")
                    except Exception as e:
                        QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))


        if idx == 3:  # 发布新套餐
            pkg_id, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "套餐ID:")
            if not ok or not pkg_id.strip():
                return
            # 发布前先检查是否重复
            try:
                if self.system.package_id_exists(pkg_id.strip()):
                    QtWidgets.QMessageBox.warning(self.main_window, "错误", f"套餐ID {pkg_id.strip()} 已存在，请更换其他ID。")
                    return
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))
                return

            pkg_name, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "套餐名称:")
            if not ok or not pkg_name.strip():
                return
            price_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "价格:")
            if not ok or not price_str.strip():
                return
            contract_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "合约期:")
            if not ok or not contract_str.strip():
                return
            voice_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "语音额度:")
            if not ok or not voice_str.strip():
                return
            over_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "超额标准:")
            if not ok or not over_str.strip():
                return

            try:
                price = float(price_str)
                contract = int(contract_str)
                voice_quota = float(voice_str)
                over_quota = float(over_str)
            except ValueError:
                QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "价格、合约期、语音额度和超额标准必须是数字。")
                return

            try:
                phone = self.main_window.current_user_phone
                if not phone:
                    QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "管理员电话号码未设置。")
                    return
                self.system.add_package_for_admin(
                    phone,
                    pkg_id.strip(),
                    pkg_name.strip(),
                    price,
                    contract,
                    voice_quota,
                    over_quota
                )
                QtWidgets.QMessageBox.information(self.main_window, "成功", "已发布新套餐。")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))

        # 阻塞信号，防止重置信号触发
        self.packageComboBox.blockSignals(True)
        self.packageComboBox.setCurrentIndex(0)
        self.packageComboBox.blockSignals(False)
    
    def show(self):
        self.main_window.tabWidget.setCurrentIndex(5)
        # 可根据需要刷新页面

    def logout(self):
        self.main_window.tabWidget.setCurrentIndex(0)
        self.main_window.current_user_phone = None
        self.main_window.is_suspended = None