from datetime import datetime
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from Frame.frame10 import Ui_MainWindow

class MainWindow_fr10(QMainWindow, Ui_MainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.selected_row = -1
        self.original_data = None
        self.table_widget = None
        self.resize(1320, 810)

        # Cập nhật tổng tiền khi thay đổi số lượng, giá, giảm giá
        self.quantity_input_10.textChanged.connect(self.update_total_amount)
        self.price_input_10.textChanged.connect(self.update_total_amount)
        self.discount_applied_input_10.textChanged.connect(self.update_total_amount)

        # Kết nối các nút chức năng
        self.insert_button_10.clicked.connect(self.insert_data)
        self.reset_button_10.clicked.connect(self.reset_data)
        self.clear_button_10.clicked.connect(self.clear_data)
        self.update_button_10.clicked.connect(self.update_data)
        self.member_button_10.hide()
        self.analyze_button_10.hide()

    def set_table_widget(self, table_widget):
        self.table_widget = table_widget

    def set_selected_row(self, row):
        self.selected_row = row

    def validate_inputs(self):
        inputs = [
            self.employee_lineEdit_10,
            self.product_id_input_10,
            self.quantity_input_10, self.price_input_10,
            self.discount_applied_input_10,
            self.time_input_10
        ]
        empty_fields = [field for field in inputs if not field.text().strip()]
        if empty_fields:
            for field in empty_fields:
                field.setStyleSheet("border: 2px solid red;")
            self.show_message("Lỗi", "Vui lòng điền đầy đủ các trường bắt buộc!", "error")
            return False

        transaction_id = self.transactionid_lineEdit_10.text().strip().upper()
        if transaction_id and not transaction_id.startswith("T"):
            self.transactionid_lineEdit_10.setStyleSheet("border: 2px solid red;")
            self.show_message("Lỗi", "Transaction ID phải bắt đầu bằng 'T'.", "error")
            return False

        for field in inputs:
            field.setStyleSheet("")
        return True

    def update_total_amount(self):
        quantity = self.quantity_input_10.text()
        price = self.price_input_10.text()
        discount = self.discount_applied_input_10.text()
        if not quantity or not price:
            self.total_amount_input_10.clear()
            return
        try:
            total = float(price) * int(quantity)
            if discount:
                total -= total * (float(discount) / 100)
            self.total_amount_input_10.setText(f"{round(total, 2)}")
        except ValueError:
            self.total_amount_input_10.clear()

    def load_data_from_table(self, row_data):
        self.original_data = row_data

        # Các giá trị khác
        self.transactionid_lineEdit_10.setText(row_data[0])
        self.customer_id_input_10.setText(row_data[1])
        self.employee_lineEdit_10.setText(row_data[2])
        self.product_id_input_10.setText(row_data[3])
        self.quantity_input_10.setText(row_data[4])
        self.price_input_10.setText(row_data[5])
        self.discount_applied_input_10.setText(row_data[9])
        self.total_amount_input_10.setText(row_data[10])

        # Chuyển đổi TransactionDate từ MongoDB (YYYY-MM-DD HH:MM:SS) sang MM/DD/YYYY HH:MM
        try:
            transaction_date_str = row_data[6]  # Giả sử là chuỗi 'YYYY-MM-DD HH:MM:SS' từ MongoDB
            transaction_date_obj = datetime.strptime(transaction_date_str,
                                                     "%Y-%m-%d %H:%M:%S")  # Chuyển thành đối tượng datetime
            formatted_date = transaction_date_obj.strftime("%m/%d/%Y %H:%M")  # Định dạng lại thành MM/DD/YYYY HH:MM
            self.time_input_10.setText(formatted_date)  # Hiển thị đúng định dạng cho người dùng
        except Exception as e:
            print(f"Lỗi khi chuyển đổi TransactionDate: {e}")
            self.time_input_10.setText("")  # Nếu có lỗi thì để trống

        # Cập nhật QComboBox
        self.payment_method_select_10.setCurrentText(row_data[7].title())
        self.product_category_select_10.setCurrentText(row_data[8].title())

    def get_form_data(self):
        try:
            # Lấy dữ liệu TransactionDate từ giao diện (MM/DD/YYYY HH:MM)
            transaction_date = self.time_input_10.text().strip()

            # Kiểm tra và chuyển định dạng TransactionDate sang "YYYY-MM-DD HH:mm:ss"
            try:
                # Chuyển đổi từ "MM/DD/YYYY HH:MM" sang "YYYY-MM-DD HH:mm:ss"
                transaction_date_obj = datetime.strptime(transaction_date, "%m/%d/%Y %H:%M")
                transaction_date = transaction_date_obj.strftime("%Y-%m-%dT%H:%M:%S.000+00:00")
            except ValueError:
                self.show_message("Lỗi",
                                  "Định dạng Transaction Date không hợp lệ! Vui lòng nhập đúng định dạng 'MM/DD/YYYY HH:MM'.",
                                  "error")
                return None  # Trả về None nếu không hợp lệ

            # Lấy dữ liệu từ các trường khác
            return {
                "_id": self.transactionid_lineEdit_10.text(),
                "CustomerID": self.customer_id_input_10.text(),
                "EmployeeID": self.employee_lineEdit_10.text(),
                "ProductID": self.product_id_input_10.text(),
                "Quantity": self.quantity_input_10.text(),
                "Price": self.price_input_10.text(),
                "TransactionDate": transaction_date,  # Sử dụng TransactionDate đã được kiểm tra và chuyển đổi
                "PaymentMethod": self.payment_method_select_10.currentText(),
                "ProductCategory": self.product_category_select_10.currentText(),
                "DiscountApplied(%)": self.discount_applied_input_10.text(),
                "TotalAmount": self.total_amount_input_10.text()
            }
        except Exception as e:
            print(f"Lỗi lấy dữ liệu: {e}")
            return None


    def insert_data(self):
        if not self.validate_inputs():
            return

        new_data = self.get_form_data()
        if not new_data:
            self.show_message("Lỗi", "Không có dữ liệu để thêm!", "error")
            return

        tx_id_input = new_data["_id"].strip().upper()
        if tx_id_input:
            self.show_message("Lỗi", "Khi thêm mới, Transaction ID phải để trống để tự động tạo!", "error")
            return
        else:
            new_data["_id"] = self.main_window.db_manager.generate_new_transaction_id()

        # Xử lý CustomerID
        customer_id = new_data["CustomerID"].strip().upper()
        if customer_id == "":
            try:
                new_customer_id = self.main_window.db_manager.generate_new_customer_id(is_member=False)
                new_data["CustomerID"] = int(new_customer_id)  # Ép kiểu sang Int32
            except Exception as e:
                self.show_message("Lỗi", f"Không thể tạo ID vãng lai: {e}", "error")
                return
        else:
            # Kiểm tra ID member
            if not customer_id.startswith("C"):
                self.show_message("Lỗi", "ID member phải bắt đầu bằng 'C'!", "error")
                return
            if len(customer_id) < 2 or not customer_id[1:].isdigit():
                self.show_message("Lỗi", "ID member phải có dạng 'C' theo sau là số!", "error")
                return
            # Kiểm tra tồn tại trong collection customers
            existing_customer = self.main_window.db_manager.search_customers({"_id": customer_id})
            if not existing_customer:
                self.show_message("Lỗi", f"Không tìm thấy member {customer_id} trong hệ thống!", "error")
                return

        new_data["TransactionDate"] = QDateTime.currentDateTime().toString("yyyy-MM-ddTHH:mm:ss.000+00:00")

        try:
            self.main_window.db_manager.insert_transaction(new_data)
            self.show_message("Thành công", f"Đã thêm giao dịch với ID: {new_data['_id']}", "info")

            if self.table_widget:
                row_count = self.table_widget.rowCount()
                self.table_widget.insertRow(row_count)
                for col, value in enumerate(new_data.values()):
                    self.table_widget.setItem(row_count, col, QTableWidgetItem(str(value)))

            if customer_id.startswith("C"):
                self.main_window.db_manager.update_customer_info(customer_id)
        except Exception as e:
            self.show_message("Lỗi", f"Không thể thêm dữ liệu: {e}", "error")

    def update_data(self):
        if self.main_window.db_manager.transactions is None or self.selected_row == -1:
            self.show_message("Cảnh báo", "Chưa chọn hàng hoặc không có kết nối MongoDB!", "warning")
            return

        if not self.validate_inputs():
            return

        updated_data = self.get_form_data()
        if not updated_data:
            self.show_message("Lỗi", "Không có dữ liệu để cập nhật!", "error")
            return

        if not self.original_data:
            self.show_message("Lỗi", "Không có dữ liệu gốc để so sánh!", "error")
            return

        original_tx_id = self.original_data[0]
        original_customer_id = self.original_data[1]

        if updated_data["_id"] != original_tx_id:
            self.show_message("Lỗi", "Không được thay đổi Transaction ID!", "error")
            return

        is_original_member = str(original_customer_id).startswith("C")
        new_customer_id = updated_data["CustomerID"]
        is_new_member = new_customer_id.startswith("C")

        if not is_original_member:
            if new_customer_id == "" or new_customer_id == original_customer_id:
                updated_data["CustomerID"] = original_customer_id
            elif is_new_member:
                if len(new_customer_id) < 2 or not new_customer_id[1:].isdigit():
                    self.show_message("Lỗi", "ID member phải có dạng C + số (ví dụ: C1, C2)!", "error")
                    return
                if not self.main_window.db_manager.search_customers({"_id": new_customer_id}):
                    self.show_message("Lỗi", f"Không tìm thấy member {new_customer_id}!", "error")
                    return
            else:
                if not new_customer_id.isdigit():
                    self.show_message("Lỗi", "ID vãng lai phải là số!", "error")
                    return
        else:
            if new_customer_id == "" or new_customer_id == original_customer_id:
                updated_data["CustomerID"] = original_customer_id
            else:
                if not is_new_member:
                    self.show_message("Lỗi", "Không thể chuyển member thành vãng lai!", "error")
                    return
                if len(new_customer_id) < 2 or not new_customer_id[1:].isdigit():
                    self.show_message("Lỗi", "ID member phải có dạng C + số (ví dụ: C1, C2)!", "error")
                    return
                if new_customer_id != original_customer_id:
                    if not self.main_window.db_manager.search_customers({"_id": new_customer_id}):
                        self.show_message("Lỗi", f"Không tìm thấy member {new_customer_id}!", "error")
                        return

        try:
            result = self.main_window.db_manager.update_transaction(original_tx_id, updated_data)
            if result.modified_count > 0:
                self.show_message("Thành công", "Đã cập nhật giao dịch!", "info")
                if self.table_widget:
                    for col, value in enumerate(updated_data.values()):
                        self.table_widget.setItem(self.selected_row, col, QTableWidgetItem(str(value)))

                if is_original_member and original_customer_id != new_customer_id:
                    self.main_window.db_manager.update_customer_info(original_customer_id)
                if is_new_member:
                    self.main_window.db_manager.update_customer_info(new_customer_id)
            else:
                self.show_message("Thông báo", "Không có dữ liệu nào được cập nhật!", "info")
        except Exception as e:
            self.show_message("Lỗi", f"Không thể cập nhật giao dịch: {e}", "error")

    def clear_data(self):
        for widget in [
            self.transactionid_lineEdit_10, self.customer_id_input_10,
            self.employee_lineEdit_10, self.product_id_input_10, self.quantity_input_10,
            self.price_input_10, self.discount_applied_input_10,
            self.total_amount_input_10
        ]:
            widget.clear()
        self.payment_method_select_10.setCurrentIndex(0)
        self.product_category_select_10.setCurrentIndex(0)
        self.transactionid_lineEdit_10.setFocus()
        self.show_message("Thông tin", "Đã xóa toàn bộ trường!", "info")

    def reset_data(self):
        if self.original_data:
            self.load_data_from_table(self.original_data)
            self.show_message("Thông tin", "Đã khôi phục dữ liệu gốc!", "info")
        else:
            self.show_message("Cảnh báo", "Không có dữ liệu gốc để reset!", "warning")

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


