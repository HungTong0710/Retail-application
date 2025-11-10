from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from Frame.frame1 import Ui_MainWindow
class MainWindow_fr1(QMainWindow, Ui_MainWindow):
    def __init__(self,mainwindow):
        super().__init__()
        self.setupUi(self)
        self.selected_row = -1
        self.mainwindow = mainwindow

        self.data = self.mainwindow.db_manager.get_all_transactions()
        self.selected_row_data =[]

        self.load_data()


        self.search_pushButton_1.clicked.connect(self.search_data)
        self.showall_pushButton_1.clicked.connect(self.show_all_data)
        self.search_lineEdit_1.returnPressed.connect(self.search_data)
        self.deletedata_pushButton_1.clicked.connect(self.delete_selected_row)
        self.tableWidget.cellClicked.connect(self.select_row)
        self.refresh_btn_1.clicked.connect(self.show_all_data)

    def load_data(self):
        data = self.data
        self.display_data(data)
        return data

    def display_data(self, data):
        self.tableWidget.setRowCount(len(data))

        keys = ["_id", "CustomerID", "EmployeeID", "ProductID", "Quantity",
                "Price", "TransactionDate", "PaymentMethod", "ProductCategory",
                "DiscountApplied(%)", "TotalAmount"]
        for row, doc in enumerate(data):
            for col, key in enumerate(keys):
                value = doc.get(key, "0")
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row, col, item)

    def search_data(self):
        search_by = self.comboBox.currentText()
        search_value = self.search_lineEdit_1.text().strip()
        field_mapping = {
            "TransactionID": "_id",
            "CustomerID": "CustomerID",
            "EmployeeID": "EmployeeID",
            "ProductID": "ProductID",
            "Quantity": "Quantity",
            "Price": "Price",
            "TransactionDate": "TransactionDate",
            "PaymentMethod": "PaymentMethod",
            "ProductCategory": "ProductCategory",
            "DiscountApplied(%)": "DiscountApplied(%)",
            "TotalAmount": "TotalAmount"
        }
        query_field = field_mapping.get(search_by)
        query = {}
        if not query_field:
            self.show_message("Lỗi!", "Trường tìm kiếm không hợp lệ.", "error")
            return


        try:

            if search_by in ["Quantity", "Price", "DiscountApplied(%)", "TotalAmount"]:
                if "-" in search_value:
                    lower, upper = search_value.split("-")
                    query[query_field] = {
                        "$gte": float(lower.strip()),
                        "$lte": float(upper.strip())
                    }
                else:
                    query[query_field] = float(search_value.strip())
            elif search_by == "TransactionDate":
                search_value = search_value.strip()

                if "to" in search_value:
                    start_str, end_str = search_value.split("to", 1)
                else:
                    if " " in search_value:
                        start_str = end_str = search_value
                    else:
                        start_str = f"{search_value} 00:00"
                        end_str = f"{search_value} 23:59"

                start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d %H:%M")
                end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d %H:%M").replace(second=59)

                query[query_field] = {"$gte": start_date, "$lte": end_date}

            elif search_by == "CustomerID":
                if search_value.startswith("C"):
                    query[query_field] = search_value.upper()
                else:
                    try:
                        customer_id = int(search_value)
                        query[query_field] = customer_id
                    except ValueError:
                        self.show_message("Lỗi", "ID không hợp lệ!", "error")
                        return
            # Xử lý trường văn bản (CustomerID, ProductCategory, ...)
            else:
                query[query_field] = {"$regex": search_value, "$options": "i"}

            # Thực hiện truy vấn
            filtered_data = self.mainwindow.db_manager.search_transactions(query)
            if not filtered_data:
                self.show_message("Thông báo", "Không tìm thấy kết quả phù hợp!", "info")
            else:
                self.display_data(filtered_data)

        except ValueError as ve:
            error_msg = (
                "Định dạng không hợp lệ! Ví dụ:\n"
                "- Tìm theo ngày: 2021-07-04 hoặc 2021-07-04 09:52\n"
                "- Khoảng ngày: 2021-07-04 00:00 to 2021-07-04 23:59"
            )
            self.show_message("Lỗi", error_msg, "error")
        except Exception as e:
            self.show_message("Lỗi", f"Lỗi khi tìm kiếm: {str(e)}", "error")

    def show_all_data(self):
        data = self.mainwindow.db_manager.get_all_transactions()
        self.display_data(data)
        self.search_lineEdit_1.clear()
        self.search_lineEdit_1.setFocus()
        self.show_message("Cập nhật", "Dữ liệu đã được tải lại!")

    def select_row(self, row, column):
        self.selected_row = row
        self.selected_row_data = [
            self.tableWidget.item(row, col).text() if self.tableWidget.item(row, col) else ""
            for col in range(self.tableWidget.columnCount())
        ]
        print(f"Row selected: {self.selected_row_data}")

    def delete_selected_row(self):
        select_row = self.tableWidget.currentRow()
        if select_row == -1:
            self.show_message("Lỗi!", "Vui lòng chọn một hàng để xóa.", "warning")
            return
        reply = self.show_message("Xác nhận", "Bạn có muốn xóa hàng này không?", "question", buttons=QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            transaction_id = self.tableWidget.item(select_row, 0).text()
            try:
                result = self.mainwindow.db_manager.delete_transaction(transaction_id)
                if result.deleted_count > 0:
                    self.tableWidget.removeRow(select_row)
                    # self.display_data(self.load_data())
                    self.show_message("Thành công", "Dữ liệu đã được xóa!", "info")
                else:
                    self.show_message("Lỗi!", "Xóa không thành công!", "error")
            except Exception as e:
                self.show_message("Lỗi!", f"ID không hợp lệ hoặc xóa thất bại: {str(e)}", "error")

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

    def hide_fr1(self):
        self.analyze_pushButton_1.hide()
        self.detail_pushButton_1.hide()
        self.deletedata_pushButton_1.hide()
        self.member_pushButton_1.hide()
