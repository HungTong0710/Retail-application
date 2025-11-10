from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QTableWidgetItem
from Ext.frame_1_Ext import MainWindow_fr1
from Ext.frame_8_Ext import MainWindow_fr8
from Ext.frame_7_Ext import MainWindow_fr7
from Ext.frame10_ext import MainWindow_fr10
from Ext.frame9_Ext import MainWindow_fr9
from Ext.MainWindow_11_Ext import MainWindow_11_Ext
from Ext.frame4_Ext import MainWindow_fr4
from Ext.frame_cuoi_ext import FrameCuoiExt
from Ext.db_manager import DBManager
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1320, 810)

        # Biến lưu role của user
        self.current_role = None
        self.current_employee_id = None
        self.db_manager = DBManager()

        # Khởi tạo các frame
        self.frame4_window = MainWindow_fr4(self)
        self.frame1_window = MainWindow_fr1(self)
        self.frame8_window = MainWindow_fr8(self)
        self.frame7_window = MainWindow_fr7(self)
        self.frame10_window = MainWindow_fr10(self)
        self.frame9_window = MainWindow_fr9(self)
        self.frame11_window = MainWindow_11_Ext(self)

        #khởi tạo các StackWidget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.stacked_widget.addWidget(self.frame4_window)  # index 0
        self.stacked_widget.addWidget(self.frame7_window)  # index 1
        self.stacked_widget.addWidget(self.frame1_window)  # index 2
        self.stacked_widget.addWidget(self.frame8_window)  # index 3
        self.stacked_widget.addWidget(self.frame10_window) # index 4
        self.stacked_widget.addWidget(self.frame9_window)  # index 5
        self.stacked_widget.addWidget(self.frame11_window) # index 6


        # Kết nối chuyển tab Frame 7
        self.frame7_window.table_view_button_7.clicked.connect(self.switch_to_frame1)
        self.frame7_window.log_out_button_7.clicked.connect(self.end_app)
        self.frame7_window.member_button_7.clicked.connect(self.switch_to_frame9)

        # Kết nối chuyển tab Frame 1
        self.frame1_window.member_pushButton_1.clicked.connect(self.switch_to_frame8)
        self.frame1_window.logout_button_1.clicked.connect(self.end_app)
        self.frame1_window.back_pushButton_1.clicked.connect(self.switch_to_frame7)
        self.frame1_window.detail_pushButton_1.clicked.connect(self.switch_to_frame10)
        self.frame1_window.analyze_pushButton_1.clicked.connect(self.switch_to_frame_cuoi)

        # Kết nối chuyển tab Frame 8
        self.frame8_window.transaction_pushButton_8.clicked.connect(self.switch_to_frame1)
        self.frame8_window.logout_button_8.clicked.connect(self.end_app)
        self.frame8_window.back_pushButton_8.clicked.connect(self.switch_to_frame9)
        self.frame8_window.detail_pushButton_8.clicked.connect(self.switch_to_frame11)
        self.frame8_window.analyze_pushButton_8.clicked.connect(self.switch_to_frame_cuoi)

        # Kết nối chuyển tab Frame 9
        self.frame9_window.ui_frame9.logout_button_9.clicked.connect(self.end_app)
        self.frame9_window.ui_frame9.table_view_button_9.clicked.connect(self.switch_to_frame8)
        self.frame9_window.ui_frame9.transaction_button_9.clicked.connect(self.switch_to_frame7)

        # Kết nối chuyển tab Frame 10
        self.frame10_window.back_button_10.clicked.connect(self.switch_to_frame1)
        self.frame10_window.log_out_button_10.clicked.connect(self.end_app)

        # Kết nối chuyển tab Frame 11
        self.frame11_window.log_out_button_11.clicked.connect(self.end_app)
        self.frame11_window.back_button_11.clicked.connect(self.switch_to_frame8)


    def set_user_role(self, role):
        # Nhận role từ màn hình đăng nhập và cập nhật phân quyền giao diện Frame4
        self.current_role = role
        self.update_ui_permissions()

    def update_ui_permissions(self):
        """
        Cập nhật giao diện dựa trên role của người dùng:
        - Nếu là 'staff': ẩn đi các nút chức năng chuyển tab không cần thiết.
        - Nếu là 'manager': hiển thị đầy đủ các nút.
        """
        if self.current_role == "Staff":
            self.frame7_window.hide_fr7()
            self.frame9_window.hide_fr9()
            self.frame8_window.hide_fr8()
            self.frame1_window.hide_fr1()
        if self.current_role == "Manager":
            self.frame7_window.hide_fr7()
            self.frame9_window.hide_fr9()


    def switch_to_frame7(self):
        self.stacked_widget.setCurrentIndex(1)

    def switch_to_frame1(self):
        self.stacked_widget.setCurrentIndex(2)

    def switch_to_frame8(self):
        self.stacked_widget.setCurrentIndex(3)

    def switch_to_frame9(self):
        self.stacked_widget.setCurrentIndex(5)

    def end_app(self):
        QApplication.quit()

    def switch_to_frame10(self):
        selected_row = self.frame1_window.tableWidget.currentRow()
        if selected_row >= 0:
            data = [
                self.frame1_window.tableWidget.item(selected_row, col).text()
                if self.frame1_window.tableWidget.item(selected_row, col) else ""
                for col in range(self.frame1_window.tableWidget.columnCount())
            ]
            self.frame10_window.load_data_from_table(data)
            self.frame10_window.set_table_widget(self.frame1_window.tableWidget)
            self.frame10_window.set_selected_row(selected_row)
            self.stacked_widget.setCurrentIndex(4)
        else:
            self.frame1_window.show_message("Error!", "Please select a row to view details.", "warning")

    def switch_to_frame11(self):
        selected_row = self.frame8_window.tableWidget_8.currentRow()
        if selected_row >= 0:
            data = [
                self.frame8_window.tableWidget_8.item(selected_row, col).text()
                if self.frame8_window.tableWidget_8.item(selected_row, col) else ""
                for col in range(self.frame8_window.tableWidget_8.columnCount())
            ]
            self.frame11_window.load_data_from_table(data)
            self.frame11_window.set_table_widget(self.frame8_window.tableWidget_8)
            self.frame11_window.set_selected_row(selected_row)
            self.stacked_widget.setCurrentIndex(6)
        else:
            self.frame8_window.show_message("Error!", "Please select a row to view details.", "warning")

    def switch_to_frame_cuoi(self):
        self.frame_cuoi = FrameCuoiExt(self)
        self.stacked_widget.addWidget(self.frame_cuoi)
        self.stacked_widget.setCurrentWidget(self.frame_cuoi)
        self.frame_cuoi.pushButton_6.clicked.connect(self.switch_to_frame1)
        self.frame_cuoi.pushButton_5.clicked.connect(self.switch_to_frame8)
        self.frame_cuoi.pushButton_7.clicked.connect(self.end_app)

