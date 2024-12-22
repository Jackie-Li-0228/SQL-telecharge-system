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
        # 确保以下名称与 .ui 文件中的 objectName 一致
        self.userComboBox = self.main_window.findChild(QtWidgets.QComboBox, 'userComboBox')
        self.businessComboBox = self.main_window.findChild(QtWidgets.QComboBox, 'businessComboBox')
        self.packageComboBox = self.main_window.findChild(QtWidgets.QComboBox, 'packageComboBox')
        self.phoneLineEdit = self.main_window.findChild(QtWidgets.QLineEdit, 'phoneLineEdit')
        self.displayListView = self.main_window.findChild(QtWidgets.QListView, 'displayListView')  # 修改为 QListView

        # 确保 logoutButton_admin 名称一致可连上
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
        else:
            print("displayListView 未找到，无法清空。")

    def handle_user_actions(self):
        self.clear_display()
        idx = self.userComboBox.currentIndex()
        phone = self.phoneLineEdit.text().strip()

        # 新增：检查电话号码是否为空
        if not phone:
            QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "电话号码不能为空。")
            # 阻塞信号，防止重置信号触发
            self.userComboBox.blockSignals(True)
            self.userComboBox.setCurrentIndex(0)
            self.userComboBox.blockSignals(False)
            return

        if idx == 1:  # 查看详细信息
            try:
                user_info = self.system.get_user_info_by_phone(phone)
                info_text = "\n".join([f"{k}: {v}" for k, v in user_info.items()])
                QtWidgets.QMessageBox.information(self.main_window, "用户详细信息", info_text)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))

        elif idx == 2:  # 查看交易记录
            try:
                records = self.system.get_transaction_records_by_phone(phone)
                list_items = [f"TransactionID: {rec.get('TransactionID', '')}, Time: {rec.get('TransactionTime', '')}, Item: {rec.get('PurchasedItem', '')}, Amount: {rec.get('Amount', '')}" for rec in records]
                model = QStringListModel(list_items)
                self.displayListView.setModel(model)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))

        elif idx == 3:  # 模拟通话
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
        self.clear_display()
        idx = self.businessComboBox.currentIndex()

        if idx == 1:  # 展示所有业务
            try:
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
                    1  # 一个示例激活方式
                )
                QtWidgets.QMessageBox.information(self.main_window, "成功", "业务已发布。")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self.main_window, "错误", str(e))

        # 阻塞信号，防止重置信号触发
        self.businessComboBox.blockSignals(True)
        self.businessComboBox.setCurrentIndex(0)
        self.businessComboBox.blockSignals(False)

    def handle_package_actions(self):
        self.clear_display()
        idx = self.packageComboBox.currentIndex()

        if idx == 1:  # 展示所有套餐
            try:
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

        elif idx == 3:  # 发布新套餐
            pkg_id, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "套餐ID:")
            if not ok or not pkg_id:
                return
            pkg_name, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "套餐名称:")
            if not ok or not pkg_name:
                return
            price_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "价格:")
            if not ok or not price_str:
                return
            contract_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "合约期:")
            if not ok or not contract_str:
                return
            voice_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "语音额度:")
            if not ok or not voice_str:
                return
            over_str, ok = QtWidgets.QInputDialog.getText(self.main_window, "发布套餐", "超额标准:")
            if not ok or not over_str:
                return

            try:
                phone = self.main_window.current_user_phone
                if not phone:
                    QtWidgets.QMessageBox.warning(self.main_window, "输入错误", "管理员电话号码未设置。")
                    return
                self.system.add_package_for_admin(
                    phone,
                    pkg_id,
                    pkg_name,
                    float(price_str),
                    int(contract_str),
                    float(voice_str),
                    float(over_str)
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