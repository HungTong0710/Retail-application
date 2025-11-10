import re
from PyQt5.QtCore import QDateTime, QTimer
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QLineEdit, QComboBox
from Frame.frame9 import Ui_MainWindow
from datetime import datetime

class MainWindow_fr9(QMainWindow):
    def __init__(self,mainwindow):
        super().__init__()
        self.resize(1320, 810)
        self.mainwindow = mainwindow
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Khởi tạo giao diện Frame 9
        self.ui_frame9 = Ui_MainWindow()
        self.frame9_window = QMainWindow()
        self.ui_frame9.setupUi(self.frame9_window)
        self.stacked_widget.addWidget(self.frame9_window)


        # Cập nhật thời gian thực
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_date_time)
        self.timer.start(1000)
        self.update_date_time()

        # Kết nối các sự kiện
        self.ui_frame9.add_data_button_9.clicked.connect(self.add_data)
        self.ui_frame9.delete_data_button_9.clicked.connect(self.clear_input_fields)

        # Kết nối sự kiện reset viền đỏ khi người dùng sửa
        self.ui_frame9.name_input_9.textChanged.connect(lambda: self.reset_error_style(self.ui_frame9.name_input_9))
        self.ui_frame9.email_input_9.textChanged.connect(lambda: self.reset_error_style(self.ui_frame9.email_input_9))
        self.ui_frame9.phone_number_input_9.textChanged.connect(lambda: self.reset_error_style(self.ui_frame9.phone_number_input_9))
        self.ui_frame9.date_of_birth_input_9.textChanged.connect(lambda: self.reset_error_style(self.ui_frame9.date_of_birth_input_9))
        self.ui_frame9.membership_status_select_9.currentIndexChanged.connect(lambda: self.reset_error_style(self.ui_frame9.membership_status_select_9))
        self.ui_frame9.membership_level_select_9.currentIndexChanged.connect(lambda: self.reset_error_style(self.ui_frame9.membership_level_select_9))

    def reset_error_style(self, widget):
        widget.setStyleSheet("")
        widget.setToolTip("")

    def update_date_time(self):
        now = QDateTime.currentDateTime()
        self.ui_frame9.real_date_label_9.setText(now.toString("MM-dd-yyyy"))
        self.ui_frame9.real_time_label_9.setText(now.toString("hh:mm"))

    def add_data(self):
        errors = {}

        name = self.ui_frame9.name_input_9.text().strip()
        email = self.ui_frame9.email_input_9.text().strip()
        birthday = self.ui_frame9.date_of_birth_input_9.text().strip()
        phone = self.ui_frame9.phone_number_input_9.text().strip()
        membership_status = self.ui_frame9.membership_status_select_9.currentText().strip()
        membership_level = self.ui_frame9.membership_level_select_9.currentText().strip()

        if not name:
            errors[self.ui_frame9.name_input_9] = "Vui lòng nhập tên"
        if not email or "@" not in email:
            errors[self.ui_frame9.email_input_9] = "Email phải chứa ký tự @"
        if not phone or not phone.isdigit():
            errors[self.ui_frame9.phone_number_input_9] = "Số điện thoại chỉ được chứa số"
        if not birthday:
            errors[self.ui_frame9.date_of_birth_input_9] = "Vui lòng nhập ngày sinh"
        elif not re.match(r"^\d{4}-\d{2}-\d{2}$", birthday):
            errors[self.ui_frame9.date_of_birth_input_9] = "Định dạng ngày sinh phải là YYYY-MM-DD"
        if self.ui_frame9.membership_status_select_9.currentIndex() == 0:
            errors[self.ui_frame9.membership_status_select_9] = "Vui lòng chọn trạng thái thành viên"
        if self.ui_frame9.membership_level_select_9.currentIndex() == 0:
            errors[self.ui_frame9.membership_level_select_9] = "Vui lòng chọn cấp độ thành viên"

        # Kiểm tra và chuyển đổi ngày sinh
        birthday_date = None
        if birthday and re.match(r"^\d{4}-\d{2}-\d{2}$", birthday):
            try:
                birthday_date = datetime.strptime(birthday, "%Y-%m-%d")
            except ValueError:
                errors[self.ui_frame9.date_of_birth_input_9] = "Ngày sinh không hợp lệ"

        if errors:
            self.highlight_errors(errors)
            error_messages = "\n".join(errors.values())
            self.show_message("Lỗi nhập liệu", error_messages, "error")
            return

        try:
            # Trong phương thức add_data():
            new_customer_id = self.mainwindow.db_manager.generate_new_customer_id(is_member=True)  # Thêm is_member=True
        except Exception as e:
            self.show_message("Lỗi", f"Không thể tạo CustomerID mới: {str(e)}", "error")
            return


        join_date = datetime.now()

        join_date = join_date.replace(microsecond=0)

        member_data = {
            "_id": new_customer_id,
            "CustomerID": new_customer_id,
            "Name": name,
            "Email": email,
            "Phone Number": phone,
            "Birthday": birthday_date,
            "MembershipStatus": membership_status,
            "JoinDate": join_date,
            "MembershipLevel": membership_level,
            "TotalSpend": 0.0,
            "TotalTransactions": 0,
            "MostPurchasedCategory": "None",
            "LastPurchaseDate": None,
            "LoyaltyPoints": 0
        }

        try:
            result = self.mainwindow.db_manager.insert_customer(member_data)
            self.show_message("Thành công", f"Thêm khách hàng thành công! ID: {new_customer_id}", "info")
        except Exception as e:
            self.show_message("Lỗi", f"Thêm khách hàng thất bại: {str(e)}", "error")

    def highlight_errors(self, errors):

        widgets = [
            self.ui_frame9.name_input_9,
            self.ui_frame9.email_input_9,
            self.ui_frame9.phone_number_input_9,
            self.ui_frame9.date_of_birth_input_9,
            self.ui_frame9.membership_status_select_9,
            self.ui_frame9.membership_level_select_9
        ]
        for widget in widgets:
            widget.setStyleSheet("")
            widget.setToolTip("")

        for widget, message in errors.items():
            widget.setStyleSheet("border: 2px solid red;")
            widget.setToolTip(message)

    def clear_input_fields(self):
        reply = self.show_message(
            "Xác nhận xóa dữ liệu",
            "Bạn có chắc chắn muốn xóa toàn bộ dữ liệu nhập?",
            "question",
            buttons=QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.ui_frame9.name_input_9.clear()
            self.ui_frame9.email_input_9.clear()
            self.ui_frame9.date_of_birth_input_9.clear()
            self.ui_frame9.phone_number_input_9.clear()
            self.ui_frame9.membership_status_select_9.setCurrentIndex(0)
            self.ui_frame9.membership_level_select_9.setCurrentIndex(0)
            self.ui_frame9.name_input_9.setFocus()

    def show_message(self, title, message, message_type="info", buttons=QMessageBox.Ok):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(
            "QMessageBox { background-color: rgb(40, 207, 107); color: white; }"
            "QLabel { color: white; font-size: 14px; }"
            "QPushButton { background-color: white; color: black; font-size: 12px; }"
        )
        if message_type == "info":
            msg_box.setIcon(QMessageBox.Information)
        elif message_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif message_type == "error":
            msg_box.setIcon(QMessageBox.Critical)
        elif message_type == "question":
            msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(buttons)
        return msg_box.exec_()

    def hide_fr9(self):
        self.ui_frame9.analyze_button_9.hide()