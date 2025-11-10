from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from Frame.frame8 import Ui_MainWindow  # File giao diện tạo bởi Qt Designer

class MainWindow_fr8(QMainWindow, Ui_MainWindow):
    def __init__(self,mainWindow):
        super().__init__()
        self.setupUi(self)
        self.mainWindow = mainWindow
        self.selected_row_data = []
        self.selected_row = -1
        self.load_data()

        # Kết nối các sự kiện giao diện
        self.search_pushButton_8.clicked.connect(self.search_data)
        self.showall_pushButton_8.clicked.connect(self.show_all_data)
        self.search_lineEdit_8.returnPressed.connect(self.search_data)
        self.deletedata_pushButton_8.clicked.connect(self.delete_data_frame8)
        self.reset_btn.clicked.connect(self.show_all_data)
        self.tableWidget_8.cellClicked.connect(self.select_row)

    def load_data(self):
        data = self.mainWindow.db_manager.get_all_customers()
        self.display_data(data)
        return data

    def display_data(self, data):
        self.tableWidget_8.setRowCount(len(data))
        keys = ["_id", "Name", "Email", "Phone Number", "Birthday",
                "MembershipStatus", "JoinDate", "MembershipLevel",
                "TotalSpend", "TotalTransactions", "MostPurchasedCategory",
                "LastPurchaseDate", "LoyaltyPoints"]
        for row, doc in enumerate(data):
            for col, key in enumerate(keys):
                value = doc.get(key, "N/A")
                if key == "Birthday":
                    try:
                        if isinstance(value, datetime):
                            value = value.strftime("%Y-%m-%d")
                        else:
                            dt = datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
                            value = dt.strftime("%Y-%m-%d")
                    except Exception:
                        value = str(value)
                item = QTableWidgetItem(str(value))
                self.tableWidget_8.setItem(row, col, item)

    def search_data(self):
        search_by = self.comboBox_8.currentText()
        search_value = self.search_lineEdit_8.text().strip()
        field_mapping = {
            "CustomerID": "_id",
            "Name": "Name",
            "Email": "Email",
            "Phone Number": "Phone Number",
            "Birthday": "Birthday",
            "MembershipStatus": "MembershipStatus",
            "JoinDate": "JoinDate",
            "MembershipLevel": "MembershipLevel",
            "TotalSpend": "TotalSpend",
            "TotalTransactions": "TotalTransactions",
            "MostPurchasedCategory": "MostPurchasedCategory",
            "LastPurchaseDate": "LastPurchaseDate",
            "LoyaltyPoints": "LoyaltyPoints"
        }
        query_field = field_mapping.get(search_by)
        query = {}
        if not query_field:
            self.show_message("Lỗi!", "Trường tìm kiếm không hợp lệ.", "error")
            return


        try:
            if search_by in ["TotalSpend", "TotalTransactions", "LoyaltyPoints"]:
                if "-" in search_value:
                    lower, upper = map(float, search_value.split("-"))
                    query[query_field] = {"$gte": lower, "$lte": upper}
                else:
                    query[query_field] = float(search_value)
            elif search_by in ["JoinDate", "LastPurchaseDate", "Birthday"]:
                search_value = search_value.strip()
                if "to" in search_value:
                    start_str, end_str = search_value.split("to", 1)
                    start_str = start_str.strip()
                    end_str = end_str.strip()
                else:
                    if " " not in search_value:
                        start_str = f"{search_value} 00:00"
                        end_str = f"{search_value} 23:59"
                    else:
                        start_str = search_value
                        end_str = search_value
                try:
                    start_date = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
                    end_date = datetime.strptime(end_str, "%Y-%m-%d %H:%M").replace(second=59)
                except ValueError:
                    self.show_message("Lỗi",
                                      "Định dạng ngày không hợp lệ! Vui lòng nhập theo định dạng YYYY-MM-DD hoặc YYYY-MM-DD HH:MM",
                                      "error")
                    return

                query[query_field] = {"$gte": start_date, "$lte": end_date}

            else:
                if search_by == "MembershipStatus":
                    query[query_field] = {"$regex": f"^{search_value}$", "$options": "i"}
                else:
                    query[query_field] = {"$regex": search_value, "$options": "i"}

            filtered_data = self.mainWindow.db_manager.search_customers(query)
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
        data = self.mainWindow.db_manager.get_all_customers()
        self.display_data(data)
        self.search_lineEdit_8.clear()
        self.search_lineEdit_8.setFocus()

    def delete_data_frame8(self):
        select_row = self.tableWidget_8.currentRow()
        if select_row == -1:
            self.show_message("Lỗi!", "Vui lòng chọn một hàng để xóa.", "warning")
            return
        reply = self.show_message("Xác nhận", "Bạn có muốn xóa hàng này không?", "question",buttons=QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            customer_id = self.tableWidget_8.item(select_row, 0).text()
            try:
                result = self.mainWindow.db_manager.delete_customer(customer_id)
                if result.deleted_count > 0:
                    self.tableWidget_8.removeRow(select_row)
                    self.display_data(self.load_data())
                    self.show_message("Thành công", "Dữ liệu đã được xóa!", "info")
                else:
                    self.show_message("Lỗi!", "Xóa không thành công!", "error")
            except Exception as e:
                self.show_message("Lỗi!", f"ID không hợp lệ hoặc xóa thất bại: {str(e)}", "error")

    def select_row(self, row, column):
        self.selected_row = row
        self.selected_row_data = [
            self.tableWidget_8.item(row, col).text() if self.tableWidget_8.item(row, col) else ""
            for col in range(self.tableWidget_8.columnCount())
        ]
        print(f"Hàng được chọn: {self.selected_row_data}")

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

    def hide_fr8(self):
        self.deletedata_pushButton_8.hide()
        self.detail_pushButton_8.hide()
        self.analyze_pushButton_8.hide()
        self.transaction_pushButton_8.hide()
