from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QLineEdit, QComboBox
from Frame.frame11 import Ui_MainWindow  # File giao diện tạo bởi Qt Designer
from Ext.db_manager import DBManager
from datetime import datetime

class MainWindow_11_Ext(QMainWindow, Ui_MainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.selected_row = -1   # Lưu chỉ số hàng được chọn từ Frame 8 (nếu có)
        self.original_data = None  # Lưu dữ liệu gốc để reset
        self.table_widget = None  # Tham chiếu đến bảng dữ liệu của Frame 8

        # Kết nối các sự kiện nút
        self.insert_button_11.clicked.connect(self.insert_data)
        self.reset_button_11.clicked.connect(self.reset_data)
        self.update_button_11.clicked.connect(self.update_data)
        self.clear_button_11.clicked.connect(self.clear_data)
        self.transaction_button_11.hide()
        self.analyze_button_11.hide()

    def set_table_widget(self, table_widget):
        self.table_widget = table_widget

    def set_selected_row(self, row):
        self.selected_row = row

    def load_data_from_table(self, data):
        # Lưu dữ liệu gốc để dùng cho update (danh sách gồm các trường theo thứ tự):
        # [CustomerID, Name, Email, Phone Number, Birthday, MembershipStatus,
        #  JoinDate, MembershipLevel, TotalSpend, TotalTransactions,
        #  MostPurchasedCategory, LastPurchaseDate, LoyaltyPoints]
        self.original_data = data
        self.customer_id_input_11.setText(data[0])           # _id
        self.name_input_11.setText(data[1])                    # Name
        self.email_input_11.setText(data[2])                   # Email
        self.phone_number_input_11.setText(data[3])            # Phone Number
        self.date_of_birth_input_11.setText(data[4])           # Birthday
        self.join_date_input_11.setText(data[6])               # JoinDate
        self.total_spend_input_11.setText(data[8])             # TotalSpend
        self.total_transaction_input_11.setText(data[9])       # TotalTransactions
        self.most_pc_category_input_11.setText(data[10])       # MostPurchasedCategory
        self.last_pc_date_input_11.setText(data[11])           # LastPurchaseDate
        self.loyalty_points_input_11.setText(data[12])         # LoyaltyPoints

        # Cập nhật MembershipStatus (QComboBox)
        status_index = self.membership_status_select_11.findText(str(data[5]).title())
        self.membership_status_select_11.setCurrentIndex(status_index if status_index >= 0 else 0)

        # Cập nhật MembershipLevel (QComboBox)
        level_index = self.membership_level_select_11.findText(str(data[7]).title())
        self.membership_level_select_11.setCurrentIndex(level_index if level_index >= 0 else 0)

    def get_form_data(self):
        try:
            return {
                "_id": self.customer_id_input_11.text(),
                "Name": self.name_input_11.text(),
                "Email": self.email_input_11.text(),
                "Phone Number": self.phone_number_input_11.text(),
                "Birthday": self.date_of_birth_input_11.text(),
                "MembershipStatus": self.membership_status_select_11.currentText(),
                "JoinDate": self.join_date_input_11.text(),
                "MembershipLevel": self.membership_level_select_11.currentText(),
                "TotalSpend": self.total_spend_input_11.text(),
                "TotalTransactions": self.total_transaction_input_11.text(),
                "MostPurchasedCategory": self.most_pc_category_input_11.text(),
                "LastPurchaseDate": self.last_pc_date_input_11.text(),
                "LoyaltyPoints": self.loyalty_points_input_11.text()
            }
        except Exception as e:
            print(f"Lỗi lấy dữ liệu: {e}")
            return None

    def validate_inputs(self):
        # Trong frame 11, các trường bắt buộc cho update/insert là:
        # Name, Email, Phone Number, Birthday
        inputs = [
            self.name_input_11, self.email_input_11,
            self.phone_number_input_11, self.date_of_birth_input_11
        ]
        empty_fields = [field for field in inputs if not field.text().strip()]
        if empty_fields:
            for field in empty_fields:
                field.setStyleSheet("border: 2px solid red;")
            self.show_message("Lỗi", "Vui lòng điền đầy đủ các trường: Name, Email, Phone Number, Birthday!", "error")
            return False
        for field in inputs:
            field.setStyleSheet("")
        return True

    def insert_data(self):
        # Yêu cầu khi insert: trường CustomerID phải để trống để hệ thống tự generate ID member mới
        if self.customer_id_input_11.text().strip() != "":
            self.show_message("Lỗi", "Khi thêm mới, CustomerID phải để trống để hệ thống tự tạo ID member mới!", "error")
            return

        if not self.validate_inputs():
            return

        form_data = self.get_form_data()
        if not form_data:
            self.show_message("Lỗi", "Không có dữ liệu để thêm!", "error")
            return

        # Sinh ID member mới (theo định dạng Cxxx) từ DBManager
        new_customer_id = self.main_window.db_manager.generate_new_customer_id(is_member=True)
        # Chỉ lấy thông tin thay đổi từ form: Name, Email, Phone Number, Birthday
        join_date = datetime.now()  # JoinDate sẽ lấy thời gian hiện tại

        # Đảm bảo chỉ lưu thời gian và ngày mà không có phần milliseconds hay timezone
        join_date = join_date.replace(microsecond=0)
        new_customer = {
            "_id": new_customer_id,
            "Name": form_data["Name"],
            "Email": form_data["Email"],
            "Phone Number": form_data["Phone Number"],
            "Birthday": self.convert_to_datetime(form_data["Birthday"]),
            # Các trường còn lại được set mặc định
            "MembershipStatus": "Active",
            "JoinDate": self.convert_to_datetime(join_date),
            "MembershipLevel": "Silver",
            "TotalSpend": "0",
            "TotalTransactions": "0",
            "MostPurchasedCategory": "None",
            "LastPurchaseDate": "None",
            "LoyaltyPoints": "0"
        }
        try:
            result = self.main_window.db_manager.insert_customer(new_customer)
            self.show_message("Thành công", f"Đã thêm dữ liệu với ID: {result.inserted_id}", "info")
            if self.table_widget:
                row_count = self.table_widget.rowCount()
                self.table_widget.insertRow(row_count)
                # Hiển thị theo thứ tự các trường như hiển thị (theo load_data_from_table)
                for col, value in enumerate(new_customer.values()):
                    self.table_widget.setItem(row_count, col, QTableWidgetItem(str(value)))
        except Exception as e:
            self.show_message("Lỗi", f"Không thể thêm dữ liệu: {e}", "error")

    def update_data(self):
        # Khi update, chỉ cho phép thay đổi các trường: Name, Email, Phone Number, Birthday.
        # Các trường còn lại phải giữ nguyên dữ liệu gốc.
        if self.main_window.db_manager.customers is None or self.selected_row == -1:
            self.show_message("Cảnh báo", "Chưa chọn hàng hoặc không có kết nối MongoDB!", "warning")
            return

        if not self.validate_inputs():
            return

        new_data = self.get_form_data()
        if not new_data:
            self.show_message("Lỗi", "Không có dữ liệu để cập nhật!", "error")
            return

        if not self.original_data:
            self.show_message("Lỗi", "Không có dữ liệu gốc để so sánh!", "error")
            return

        # Lấy dữ liệu gốc (không thay đổi): _id, JoinDate, TotalSpend, TotalTransactions, MostPurchasedCategory, LastPurchaseDate, LoyaltyPoints, MembershipStatus, MembershipLevel
        updated_data = {
            "_id": self.original_data[0],  # Không thay đổi
            "Name": new_data["Name"],
            "Email": new_data["Email"],
            "Phone Number": new_data["Phone Number"],

            # Chuyển đổi Birthday sang datetime nếu cần
            "Birthday": self.convert_to_datetime(self.original_data[4]),  # Assuming it's the 5th item in original_data

            # MembershipStatus, JoinDate, MembershipLevel giữ nguyên
            "MembershipStatus": self.original_data[5],
            "JoinDate": self.convert_to_datetime(self.original_data[6]),  # Assuming it's the 7th item in original_data

            # Chuyển đổi LastPurchaseDate sang datetime nếu cần
            "LastPurchaseDate": self.convert_to_datetime(self.original_data[11]),
            # Assuming it's the 12th item in original_data

            # Chuyển LoyaltyPoints sang int và TotalSpend sang float
            "LoyaltyPoints": int(self.original_data[12]),  # Assuming it's the 13th item in original_data
            "TotalSpend": float(self.original_data[8]),  # Assuming it's the 9th item in original_data
            "TotalTransactions": int(self.original_data[9]),
            "MostPurchasedCategory": self.original_data[10]
        }
        try:
            customer_id = updated_data["_id"]
            result = self.main_window.db_manager.update_customer(customer_id, updated_data)
            if result.modified_count > 0:
                self.show_message("Thành công", "Đã cập nhật dữ liệu!", "info")
                if self.table_widget:
                    for col, value in enumerate(updated_data.values()):
                        self.table_widget.setItem(self.selected_row, col, QTableWidgetItem(str(value)))
            else:
                self.show_message("Thông báo", "Không có dữ liệu nào được cập nhật!", "info")
        except Exception as e:
            self.show_message("Lỗi", f"Không thể cập nhật dữ liệu: {e}", "error")

    def reset_data(self):
        if self.original_data is None:
            self.show_message("Cảnh báo", "Không có dữ liệu gốc để khôi phục!", "warning")
            return
        self.load_data_from_table(self.original_data)
        self.show_message("Thông tin", "Đã khôi phục dữ liệu gốc!", "info")

    def clear_data(self):
        self.customer_id_input_11.clear()
        self.name_input_11.clear()
        self.email_input_11.clear()
        self.phone_number_input_11.clear()
        self.date_of_birth_input_11.clear()
        self.join_date_input_11.clear()
        self.total_spend_input_11.clear()
        self.total_transaction_input_11.clear()
        self.most_pc_category_input_11.clear()
        self.last_pc_date_input_11.clear()
        self.loyalty_points_input_11.clear()
        self.membership_status_select_11.setCurrentIndex(0)
        self.membership_level_select_11.setCurrentIndex(0)
        self.customer_id_input_11.setFocus()
        self.show_message("Thông tin", "Đã xóa toàn bộ trường!", "info")

    def show_message(self, title, message, message_type="info"):
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
        msg_box.exec_()

    from datetime import datetime

    def convert_to_datetime(self,date_value):
        try:
            # If it's already a datetime object, just return it
            if isinstance(date_value, datetime):
                return date_value

            # If it's a string, try to convert it using multiple formats
            if isinstance(date_value, str):
                try:
                    # Try ISO format with timezone (the format you were using initially)
                    return datetime.strptime(date_value, "%Y-%m-%dT%H:%M:%S.000+00:00")
                except ValueError:
                    pass  # If it fails, try the next format

                try:
                    # Try the format with space between date and time, without timezone
                    return datetime.strptime(date_value, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass  # If it fails, try the next format

                try:
                    # Try the format with just the date (no time, no timezone)
                    return datetime.strptime(date_value, "%Y-%m-%d")
                except ValueError:
                    pass  # If it fails, return None

            # Return None if it's not a string or datetime object
            return None
        except Exception as e:
            print(f"Error converting date: {e}")
            return None  # Return None in case of an error
