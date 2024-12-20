from PyQt6 import QtWidgets
from Exception_Classes import *
from src import TelechargeSystem

class AdminInterface:
    def __init__(self, main_window):
        self.main_window = main_window
        self.system = TelechargeSystem()
        self.setup_ui()
        
    def setup_ui(self):
        pass