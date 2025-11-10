from PyQt5.QtWidgets import QMainWindow, QMessageBox, QLineEdit
from Frame.frame4_fixed import Ui_MainWindow

class MainWindow_fr4(QMainWindow, Ui_MainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        # Kết nối sự kiện đăng nhập
        self.login_pushButton_4.clicked.connect(self.handle_login)
        self.asswordlineEdit_4.setEchoMode(QLineEdit.Password)

        self.comboBox.setCurrentIndex(0)

    def handle_login(self):
        username = str(self.username_lineEdit_4.text().strip())
        password = str(self.asswordlineEdit_4.text().strip())
        role = str(self.comboBox.currentText().strip())

        # Kiểm tra nếu chưa nhập hoặc role không hợp lệ
        if username == "" or password == "" or role == "" or role.lower() == "role":
            self.show_message("Lỗi", "Vui lòng điền đủ thông tin và chọn role!", "error")
            return

        try:
            user = self.main_window.db_manager.check_login(username, password, role)
            if user is not None:
                # Lưu _id của nhân viên vào GUI chính
                self.main_window.current_employee_id = user["_id"]
                self.main_window.set_user_role(role)
                # Chuyển sang một frame chính, ví dụ index 1 (frame7)
                self.main_window.stacked_widget.setCurrentIndex(1)
                self.main_window.show()
                self.close()
            else:
                self.show_message("Lỗi", "Sai tài khoản, mật khẩu hoặc role!", "error")
        except Exception as e:
            self.show_message("Lỗi", f"Lỗi hệ thống: {str(e)}", "error")

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
