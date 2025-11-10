
from datetime import datetime
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from Frame.frame7 import Ui_MainWindow

class MainWindow_fr7(QMainWindow, Ui_MainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setupUi(self)
        self.resize(1320, 810)
        self.total_amount_input_7.setReadOnly(True)
        self.customer_id_input_7.setFocus()

        self.add_data_button_7.clicked.connect(self.on_add_data_button_clicked)
        self.delete_data_button_7.clicked.connect(self.clear_inputs)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_frame7)
        self.timer.start(1000)
        self.update_time_frame7()

        self.customer_id_input_7.textChanged.connect(lambda: self.customer_id_input_7.setStyleSheet(""))
        self.product_id_input_7.currentIndexChanged.connect(lambda: self.product_id_input_7.setStyleSheet(""))
        self.quantity_input_7.textChanged.connect(lambda: self.quantity_input_7.setStyleSheet(""))
        self.price_input_7.textChanged.connect(lambda: self.price_input_7.setStyleSheet(""))
        self.discount_applied_input_7.textChanged.connect(lambda: self.discount_applied_input_7.setStyleSheet(""))
        self.payment_method_select_7.currentIndexChanged.connect(lambda: self.payment_method_select_7.setStyleSheet(""))
        self.product_category_select_7.currentIndexChanged.connect(lambda: self.product_category_select_7.setStyleSheet(""))

    def update_time_frame7(self):
        current_datetime = QDateTime.currentDateTime()
        self.real_date_label_7.setText(current_datetime.toString("yyyy-MM-dd"))
        self.real_time_label_7.setText(current_datetime.toString("HH:mm"))

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

    def validate_transaction_inputs(self):
        errors = {}
        if self.product_id_input_7.currentText() in ("0", ""):
            errors[self.product_id_input_7] = "Vui lòng chọn mã sản phẩm"
        if not self.quantity_input_7.text():
            errors[self.quantity_input_7] = "Vui lòng nhập số lượng"
        if not self.price_input_7.text():
            errors[self.price_input_7] = "Vui lòng nhập giá sản phẩm"
        if self.payment_method_select_7.currentIndex() == 0:
            errors[self.payment_method_select_7] = "Vui lòng chọn phương thức thanh toán"
        if self.product_category_select_7.currentIndex() == 0:
            errors[self.product_category_select_7] = "Vui lòng chọn danh mục sản phẩm"

        if self.quantity_input_7.text() and not self.quantity_input_7.text().isdigit():
            errors[self.quantity_input_7] = "Số lượng phải là số nguyên dương"
        if self.price_input_7.text() and not self.price_input_7.text().replace('.', '', 1).isdigit():
            errors[self.price_input_7] = "Giá sản phẩm phải là số hợp lệ"
        if self.discount_applied_input_7.text():
            if not self.discount_applied_input_7.text().replace('.', '', 1).isdigit():
                errors[self.discount_applied_input_7] = "Chiết khấu phải là số"
            elif float(self.discount_applied_input_7.text()) >= 20:
                errors[self.discount_applied_input_7] = "Chiết khấu không được lớn hơn 20%"
        return errors

    def prepare_transaction_data(self):
        try:
            discount_applied = self.discount_applied_input_7.text() or "0"
            self.discount_applied_input_7.setText(discount_applied)
            customer_id = str(self.customer_id_input_7.text().strip().upper())
            update_existing_customer = False

            if customer_id:
                if not customer_id.startswith("C"):
                    self.show_message("Lỗi nhập liệu", "Customer ID phải bắt đầu bằng 'C'", "warning")
                    return None, None
                existing_customers = self.main_window.db_manager.search_customers({"_id": customer_id})
                if not existing_customers:
                    self.show_message("Lỗi", f"Customer ID '{customer_id}' không tồn tại!", "warning")
                    return None, None
                update_existing_customer = True
            else:
                customer_id = self.main_window.db_manager.generate_new_customer_id(is_member=False)

            product_id = self.product_id_input_7.currentText()
            quantity = int(self.quantity_input_7.text())
            price = float(self.price_input_7.text())
            payment_method = self.payment_method_select_7.currentText()
            product_category = self.product_category_select_7.currentText()

            discount = (float(discount_applied) / 100) * price * quantity
            total_amount = price * quantity - discount
            self.total_amount_input_7.setText(f"{total_amount:.2f}")

            current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-ddTHH:mm:ss.000+00:00")
            transaction_id = self.main_window.db_manager.generate_new_transaction_id()
            employee_id = self.main_window.current_employee_id

            transaction_data = {
                "_id": transaction_id,
                "CustomerID": customer_id,
                "EmployeeID": employee_id,
                "ProductID": product_id,
                "Quantity": quantity,
                "Price": price,
                "TransactionDate": current_datetime,
                "PaymentMethod": payment_method,
                "ProductCategory": product_category,
                "DiscountApplied(%)": discount,
                "TotalAmount": total_amount
            }
            return transaction_data, update_existing_customer

        except Exception as e:
            self.show_message("Lỗi", f"Lỗi khi chuẩn bị dữ liệu: {e}", "error")
            return None, None

    def add_transaction(self):
        transaction_data, update_existing_customer = self.prepare_transaction_data()
        if transaction_data is None:
            return
        try:
            self.main_window.db_manager.insert_transaction(transaction_data)
            self.show_message("Thành công", f"Giao dịch {transaction_data['_id']} đã được lưu thành công.", "info")
            if update_existing_customer:
                self.update_customer_data(transaction_data)
        except Exception as e:
            self.show_message("Lỗi", f"Không thể lưu giao dịch: {e}", "error")

    def on_add_data_button_clicked(self):
        errors = self.validate_transaction_inputs()
        if errors:
            self.show_errors(errors)
            self.show_message("Lỗi nhập liệu", "\n".join(errors.values()), "warning")
            return
        self.show_errors({})
        self.add_transaction()

    def update_customer_data(self, transaction_data):
        try:
            # Lấy CustomerID từ transaction_data
            customer_id = transaction_data.get("CustomerID")
            if not customer_id:
                self.show_message("Lỗi", "Không xác định được CustomerID!", "error")
                return

            customers = self.main_window.db_manager.search_customers({"_id": customer_id})
            if not customers:
                return
            customer = customers[0]
            transactions = self.main_window.db_manager.search_transactions(
                {"CustomerID": customer_id})  # List chứa giao dịch của Customer
            current_month = datetime.now().month
            current_year = datetime.now().year

            # Khởi tạo biến
            loyalty_points = int(customer.get("LoyaltyPoints", 0))
            total_spend = 0
            total_transactions = len(transactions)
            most_common_category = "None"
            closest_purchase_date = None

            # Tính loyalty_points cho tháng hiện tại
            tx_current_month = []
            for tx in transactions:
                try:
                    tx_date_val = tx.get("TransactionDate")
                    if isinstance(tx_date_val, str):
                        tx_date = datetime.strptime(tx_date_val, "%Y-%m-%dT%H:%M:%S.000+00:00")
                    else:
                        tx_date = tx_date_val
                    if tx_date.month == current_month and tx_date.year == current_year:
                        tx_current_month.append(tx)
                except Exception as e:
                    print(f"Lỗi xử lý ngày giao dịch: {e}")
                    continue

            if len(tx_current_month) >= 4:
                if "loyalty_points_updated_this_month" not in customer or not customer[
                    "loyalty_points_updated_this_month"]:
                    loyalty_points += 1
                    updated_data = {"loyalty_points_updated_this_month": True}
                    self.main_window.db_manager.update_customer(customer_id, updated_data)

            category_count = {}
            for tx in transactions:
                total_spend += float(tx.get("TotalAmount", 0))
                category = tx.get("ProductCategory", "None")
                category_count[category] = category_count.get(category, 0) + 1

            if category_count:
                most_common_category = max(category_count, key=category_count.get)

            tx_dates = [tx.get("TransactionDate") for tx in transactions if tx.get("TransactionDate")]
            if tx_dates:
                closest_purchase_date = min(tx_dates, key=lambda x: abs(datetime.now() - (
                    x if isinstance(x, datetime) else datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.000+00:00"))))

            membership_status = "Active"
            if closest_purchase_date:
                days_since_last_purchase = (datetime.now() - closest_purchase_date).days
                if days_since_last_purchase > 182:
                    membership_status = "Inactive"
                elif days_since_last_purchase > 365:
                    membership_status = "Expired"

            membership_level = "Silver"
            if loyalty_points > 50 and total_spend > 20000:
                membership_level = "Platinum"
            elif loyalty_points > 20 and total_spend > 10000:
                membership_level = "Gold"

            updated_data = {
                "LoyaltyPoints": loyalty_points,
                "TotalSpend": total_spend,
                "TotalTransactions": total_transactions,
                "MostPurchasedCategory": most_common_category,
                "LastPurchaseDate": closest_purchase_date if isinstance(closest_purchase_date, datetime) else None,
                "MembershipStatus": membership_status,
                "MembershipLevel": membership_level
            }

            # Cập nhật thông tin khách hàng
            self.main_window.db_manager.update_customer(customer_id, updated_data)
            print(f"✅ Đã cập nhật thông tin thành viên cho {customer_id}")

        except Exception as e:
            self.show_message("Lỗi", f"Không thể cập nhật thông tin thành viên: {e}", "error")

    def clear_inputs(self):
        reply = self.show_message("Xác nhận", "Bạn có chắc chắn muốn xóa dữ liệu không?", "question", buttons=QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.customer_id_input_7.clear()
            self.product_id_input_7.setCurrentIndex(0)
            self.quantity_input_7.clear()
            self.price_input_7.clear()
            self.payment_method_select_7.setCurrentIndex(0)
            self.product_category_select_7.setCurrentIndex(0)
            self.discount_applied_input_7.clear()
            self.total_amount_input_7.clear()
            self.customer_id_input_7.setFocus()

    def show_errors(self, errors):
        widgets = [
            self.customer_id_input_7, self.product_id_input_7, self.quantity_input_7,
            self.price_input_7, self.discount_applied_input_7, self.total_amount_input_7
        ]
        for widget in widgets:
            widget.setStyleSheet("")
            widget.setToolTip("")
        for widget, message in errors.items():
            widget.setStyleSheet("border: 2px solid red; background-color: #ffeeee; color: black;")
            widget.setToolTip(message)

    def hide_fr7(self):
        self.analyze_button_7.hide()
