from Frame.frame_final import Ui_MainWindow
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib
from PyQt5.QtWidgets import QMessageBox
matplotlib.use("Agg")
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from collections import defaultdict
from PyQt5.QtWidgets import *
class FrameCuoiExt(QMainWindow, Ui_MainWindow):
    def __init__(self, mainwindow):
        super().__init__()
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.select_day_dateEdit_13.setDate(QDate.currentDate())

        # Biến lưu trữ dữ liệu đã lọc
        self.filtered_transactions = []
        self.filtered_members = []


        # Khởi tạo dữ liệu giao dịch và thành viên từ MongoDB
        self.transactions_data = self.mainwindow.db_manager.get_all_transactions()
        self.members_data = self.mainwindow.db_manager.get_all_customers()

        # Kết nối sự kiện: bất cứ thay đổi nào trong bộ lọc đều gọi hàm update_data
        self.Enter_button_13.clicked.connect(self.update_data)
        self.category_select_13.currentIndexChanged.connect(self.update_data)
        self.Member_select_13.currentIndexChanged.connect(self.update_data)
        self.select_day_dateEdit_13.dateChanged.connect(self.update_data)



        # Đặt placeholder ban đầu
        self.day1_LineEdit_2.setPlaceholderText("MM/DD/YYYY")
        self.day2_LineEdit_2.setPlaceholderText("MM/DD/YYYY")
        self.set_default_dates()
        # Bấm vào thì xóa placeholder
        self.day1_LineEdit_2.mousePressEvent = self.clear_placeholder_day1
        self.day2_LineEdit_2.mousePressEvent = self.clear_placeholder_day2

        self.Enter_day_button_2.clicked.connect(self.process_data)
        self.Enter_xy_button_2.clicked.connect(self.plot_bar_chart)
        self.Enter_factor_button_2.clicked.connect(self.handle_factor_selection)

        # Cập nhật bảng sau khi điền dữ liệu
        self.Top5_table_2.resizeColumnsToContents()
        self.Top5_table_2.resizeRowsToContents()

        # Đặt bảng để vừa khít ô vuông
        self.Top5_table_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Top5_table_2.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Top_table_13.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Top_table_13.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Quantity_revenue_table_13.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Quantity_revenue_table_13.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.update_data()

        self.load_data()

    def load_data(self):
        try:
            data = self.members_data
        except Exception as e:
            print(f"Lỗi khi đọc từ MongoDB: {e}")
            data = []
        self.total_member(data)
        self.status_member(data)
        self.top_5_transaction(data)
        self.top_5_spend(data)
        self.membership_status_chart(data)
        self.membership_level_chart(data)
        self.top_5_point(data)
    def total_member(self, data):
        if not data:
            self.label_4.setText(self.label_4.text().replace("000", "0"))
            return

        total_customers = len(data)
        self.label_4.setText(self.label_4.text().replace("000", str(total_customers)))

    def status_member(self, data):
            counts = {"active": 0, "inactive": 0, "expired": 0}

            for row in data:
                status = row.get("MembershipStatus", "").strip().lower()
                if status in counts:
                    counts[status] += 1

            self.label_5.setText(self.label_5.text().replace("000", str(counts["active"])))
            self.label_9.setText(self.label_9.text().replace("000", str(counts["inactive"])))
            self.label_11.setText(self.label_11.text().replace("000", str(counts["expired"])))

    def top_5_transaction(self, data):
        try:

            sorted_data_transaction = sorted(data, key=lambda x: int(x.get("TotalTransactions", 0)), reverse=True)[:5]


            labels_top_5_transaction = [self.transaction1_label_12, self.transaction2_label_12,
                                        self.transaction3_label_12, self.transaction4_label_12,
                                        self.transaction5_label_12]

            for i in range(len(sorted_data_transaction)):

                transaction_name = sorted_data_transaction[i].get("Name", "Unknown")
                transaction_amount = sorted_data_transaction[i].get("TotalTransactions", 0)
                labels_top_5_transaction[i].setText(f"{i + 1}. {transaction_name}: {transaction_amount}")

        except Exception as e:
            print(f"Lỗi: {e}")
    def top_5_spend(self, data):
        try:
            sorted_data_spend = sorted(data, key=lambda x: float(x.get("TotalSpend", 0)), reverse=True)[:5]


            labels_top_5_spend = [self.spend1_label_12, self.spend2_label_12, self.spend3_label_12,
                                  self.spend4_label_12, self.spend5_label_12]

            for i in range(len(sorted_data_spend)):
                member_name = sorted_data_spend[i].get("Name", "Unknown")
                spend_amount = sorted_data_spend[i].get("TotalSpend", 0)


                labels_top_5_spend[i].setText(f"{i + 1}. {member_name}: {spend_amount}")

        except Exception as e:
            print(f"Lỗi: {e}")
    def top_5_point(self, data):
        try:
            sorted_data_point = sorted(data, key=lambda x: float(x.get("LoyaltyPoints", 0)), reverse=True)[:5]

            labels_top_5_point = [self.point1_label_12, self.point2_label_12, self.point3_label_12,
                                  self.point4_label_12, self.point5_label_12]

            for i in range(len(sorted_data_point)):
                member_name = sorted_data_point[i].get("Name", "Unknown")
                loyalty_points = sorted_data_point[i].get("LoyaltyPoints", 0)

                labels_top_5_point[i].setText(f"{i + 1}. {member_name}: {loyalty_points}")

        except Exception as e:
            print(f"Lỗi: {e}")
    def membership_status_chart(self, data):
        membership_status = {"Active": 0, "Inactive": 0, "Expired": 0}
        for row in data:
            try:
                status = row.get("MembershipStatus", "").strip()
                if status in membership_status:
                    membership_status[status] += 1
            except KeyError:
                continue

        if sum(membership_status.values()) == 0:
            print("Không có dữ liệu hợp lệ")
            return

        # Dữ liệu cho biểu đồ
        labels = list(membership_status.keys())
        sizes = list(membership_status.values())
        colors = ["green", "red", "gray"]

        # Vẽ biểu đồ tròn
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90, textprops={"fontsize": 10})

        # Cập nhật biểu đồ vào giao diện
        self.canvas = FigureCanvasQTAgg(fig)
        scene = QGraphicsScene()
        scene.addWidget(self.canvas)
        self.membership_status_graphics_12.setScene(scene)
        plt.close(fig)
    def membership_level_chart(self, data):
        membership_spend = {"Silver": 0, "Gold": 0, "Platinum": 0}

        for row in data:
            try:
                level = row.get("MembershipLevel", "")
                spend = float(row.get("TotalSpend", 0))
                if level in membership_spend:
                    membership_spend[level] += spend
            except ValueError:
                continue

        if sum(membership_spend.values()) == 0:
            print("Không có dữ liệu hợp lệ")
            return

        labels = list(membership_spend.keys())
        values = list(membership_spend.values())

        # Vẽ biểu đồ cột
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(labels, values, color=["gray", "gold", "purple"])
        ax.set_xlabel("Membership Level")
        ax.set_ylabel("Total Spend")

        # Cập nhật biểu đồ vào giao diện
        self.canvas = FigureCanvasQTAgg(fig)
        scene = QGraphicsScene()
        scene.addWidget(self.canvas)
        self.level_members_graphics_12.setScene(scene)
        plt.close(fig)
    def update_data(self):
        try:
            # Lọc theo MembershipLevel
            membership_filter = self.Member_select_13.currentText()
            if membership_filter != "Select":
                self.filtered_members = [member for member in self.members_data if
                                         member.get("MembershipLevel") == membership_filter]
                valid_customers = [member["_id"] for member in self.filtered_members]
                self.filtered_transactions = [txn for txn in self.transactions_data if
                                              txn["CustomerID"] in valid_customers]
            else:
                self.filtered_members = self.members_data
                self.filtered_transactions = self.transactions_data

            # Lọc theo ngày
            selected_date = self.select_day_dateEdit_13.date().toPyDate()
            self.filtered_transactions = [txn for txn in self.filtered_transactions if
                                          txn["TransactionDate"].date() <= selected_date]

            # Lọc theo ProductCategory
            category_filter = self.category_select_13.currentText()
            if category_filter != "Select":
                self.filtered_transactions = [txn for txn in self.filtered_transactions if
                                              txn.get("ProductCategory") == category_filter]

            # Cập nhật giao diện sau khi lọc
            self.update_statistics_frame13()
            self.update_monthly_avg_chart()
            self.update_top_table_13()
            self.update_quantity_revenue_table_13()

            print(
                f"Filtered transactions: {len(self.filtered_transactions)} records, Filtered members: {len(self.filtered_members)} records.")

        except Exception as e:
            print(f"Error updating data: {e}")
            QMessageBox.critical(self, "Error", f"Error updating data: {e}")
    def update_monthly_avg_chart(self, df_chart=None):
        try:
            if not self.filtered_transactions:
                QMessageBox.warning(self, "Data Error", "No filtered transaction data available.")
                return

            transactions_filtered = self.filtered_transactions

            date_column = "TransactionDate"
            selected_value = self.select_x_select_13.currentText()

            if selected_value and selected_value != "Select":
                transactions_filtered = [txn for txn in transactions_filtered if
                                         txn.get("ProductID") == selected_value and txn.get(date_column)]


            for txn in transactions_filtered:
                txn["YearMonth"] = txn[date_column].strftime('%Y-%m')  # Chuyển đổi thành chuỗi 'YYYY-MM'


            monthly_avg = defaultdict(list)

            for txn in transactions_filtered:
                year_month = txn["YearMonth"]
                quantity = txn.get("Quantity", 0)
                monthly_avg[year_month].append(quantity)

            monthly_avg_values = {}
            for year_month, quantities in monthly_avg.items():
                monthly_avg_values[year_month] = sum(quantities) / len(quantities)

            if not monthly_avg_values:
                scene = QGraphicsScene()
                self.segment_graphics_13.setScene(scene)
                return

            months = list(monthly_avg_values.keys())
            avg_quantities = list(monthly_avg_values.values())

            # Vẽ biểu đồ
            plt.clf()
            fig, ax = plt.subplots(figsize=(12, 6), dpi=120)

            ax.plot(months, avg_quantities, marker="o", linestyle="-", color="green")

            ax.set_title("Monthly Average Quantity", fontsize=20, fontweight="bold")
            ax.set_xlabel("Month", fontsize=18)
            ax.set_ylabel("Average Quantity", fontsize=18)
            ax.tick_params(axis="both", labelsize=16)

            plt.tight_layout()

            self.canvas = FigureCanvasQTAgg(fig)
            scene = QGraphicsScene()
            scene.addWidget(self.canvas)
            self.segment_graphics_13.setScene(scene)
            self.segment_graphics_13.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
            plt.close(fig)

        except Exception as e:
            print(f"Chart update error: {e}")
            QMessageBox.warning(self, "Chart Error", f"Error updating chart: {e}")
    def update_top_table_13(self):
        try:
            if not self.filtered_members:
                QMessageBox.warning(self, "Data Error", "No filtered member data available.")
                return

            self.Top_table_13.setRowCount(0)

            # Chuẩn bị dữ liệu để thêm vào bảng
            rows = []
            for member in self.filtered_members:
                name = str(member.get("Name", "Unknown"))
                total_spend = str(member.get("TotalSpend", 0))
                membership_level = str(member.get("MembershipLevel", "Unknown"))

                # Thêm các giá trị vào hàng
                rows.append([name, total_spend, membership_level])

            # Thêm dữ liệu vào bảng
            self.Top_table_13.setRowCount(len(rows))  # Đặt số hàng trong bảng
            for row_position, row_data in enumerate(rows):
                for column_position, data in enumerate(row_data):
                    self.Top_table_13.setItem(row_position, column_position, QTableWidgetItem(data))


        except Exception as e:
            print(f" Lỗi khi cập nhật Top_table_13: {e}")
            QMessageBox.critical(self, "Error", f"Lỗi khi hiển thị dữ liệu: {e}")
    def update_quantity_revenue_table_13(self):
        try:
            # Kiểm tra dữ liệu đã lọc từ MongoDB
            if not self.filtered_transactions:
                QMessageBox.warning(self, "Data Error", "No filtered transaction data available.")
                return


            transactions_filtered = self.filtered_transactions


            categories = ["A", "B", "C", "D"]
            data_summary = []

            for category in categories:
                filtered_category = [txn for txn in transactions_filtered if txn.get("ProductID") == category]

                total_quantity = sum(txn.get("Quantity", 0) for txn in filtered_category)
                total_revenue = sum(
                    txn.get("TotalAmount", 0) for txn in filtered_category)

                data_summary.append([total_quantity, total_revenue])

            self.Quantity_revenue_table_13.setRowCount(4)
            self.Quantity_revenue_table_13.setColumnCount(2)

            # Gán dữ liệu vào bảng
            for i, category in enumerate(categories):
                self.Quantity_revenue_table_13.setItem(i, 0, QTableWidgetItem(
                    f"{data_summary[i][0]}"))
                self.Quantity_revenue_table_13.setItem(i, 1, QTableWidgetItem(
                    f"{data_summary[i][1]:.2f}"))


        except Exception as e:
            print(f" Lỗi khi cập nhật Quantity_revenue_table_13: {e}")
            QMessageBox.critical(self, "Error", f"Lỗi khi hiển thị dữ liệu: {e}")
    def update_statistics_frame13(self):


        try:
            # Kiểm tra dữ liệu đã lọc từ MongoDB
            if not self.filtered_transactions or not self.filtered_members:
                QMessageBox.warning(self, "Data Error", "No filtered transaction or member data available.")
                return

            transactions_filtered = self.filtered_transactions
            members_filtered = self.filtered_members


            total_col_5 = sum(txn.get("Quantity", 0) for txn in transactions_filtered)

            total_col_11 = sum(txn.get("TotalAmount", 0) for txn in transactions_filtered)

            avg_col_10 = sum(txn.get("DiscountApplied(%)", 0) for txn in transactions_filtered) / len(
                transactions_filtered) if transactions_filtered else 0

            total_rows_filtered_transactions = len(transactions_filtered)

            category_filter = self.category_select_13.currentText()

            if members_filtered:

                if category_filter != "Select":
                    filtered_category_members = [member for member in members_filtered if
                                                 member.get("MostPurchasedCategory") == category_filter]

                    total_rows_filtered_members = len(members_filtered)
                    total_rows_filtered_members_col_11 = len(filtered_category_members)
                    percentage_members = (
                                                     total_rows_filtered_members_col_11 / total_rows_filtered_members) * 100 if total_rows_filtered_members > 0 else 0
                else:
                    percentage_members = 0
            else:
                percentage_members = 0

            total_rows_all_transactions = len(
                self.transactions_data) if self.transactions_data else 1  # Tránh chia cho 0
            percentage_transactions = (total_rows_filtered_transactions / total_rows_all_transactions) * 100


            self.label_18.setText(f"{total_col_5:.2f}")
            self.label_30.setText(f"{total_col_11:.2f}")
            self.label_31.setText(f"{avg_col_10:.2f}")
            self.label_32.setText(str(total_rows_filtered_transactions))
            self.label_33.setText(f"{percentage_members:.2f}%")
            self.label_34.setText(f"{percentage_transactions:.2f}%")



        except Exception as e:
            print(f" Lỗi khi cập nhật số liệu thống kê Frame 13: {e}")
            QMessageBox.critical(self, "Error", f"Lỗi khi cập nhật dữ liệu: {e}")



    def set_default_dates(self):
        try:
            transactions = self.transactions_data
            if not transactions:
                QMessageBox.warning(self, "Data Error", "No transactions found in MongoDB.")
                return

            valid_transactions = [txn for txn in transactions if txn.get("TransactionDate")]
            sorted_transactions = sorted(valid_transactions, key=lambda txn: txn["TransactionDate"])
            first_date = sorted_transactions[0].get("TransactionDate")
            first_date = first_date.strftime("%m/%d/%Y")
            self.day1_LineEdit_2.setText(first_date)

            today_date = datetime.today().strftime("%m/%d/%Y")
            self.day2_LineEdit_2.setText(today_date)

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi khi lấy ngày từ dataset: {e}")
        self.run_calculations()

    def run_calculations(self):

        start_date, end_date = self.validate_dates()
        if start_date and end_date:
            total_orders, total_revenue = self.calculate_total_data_revenue(start_date, end_date)
            if total_orders is not None and total_revenue is not None:
                self.calculate_average_data(start_date, end_date, total_orders, total_revenue)
                self.calculate_top5_products(start_date, end_date)

    def handle_factor_selection(self):
        selected_index  = self.select_factor_select_2.currentIndex()
        if selected_index == 0:
            pass  # Không làm gì nếu chọn index 0
        elif selected_index == 1:  # Nếu chọn "Looping line chart"
            self.plot_revenue_trend()
        elif selected_index == 2:  # Nếu chọn "Pie chart"
            self.plot_pie_chart()

    def process_data(self):
        date_range = self.validate_dates()
        if date_range:
            start_date, end_date = date_range
            total_orders, total_revenue = self.calculate_total_data_revenue(start_date, end_date)
            if total_orders is not None and total_revenue is not None:
                self.calculate_average_data(start_date, end_date, total_orders, total_revenue)
                self.calculate_top5_products(start_date, end_date)  # Hiển thị Top 5 sản phẩm

    def clear_placeholder_day1(self, event):
        if self.day1_LineEdit_2.text() == "MM/DD/YYYY":
            self.day1_LineEdit_2.clear()
        QLineEdit.mousePressEvent(self.day1_LineEdit_2, event)

    def clear_placeholder_day2(self, event):
        if self.day2_LineEdit_2.text() == "MM/DD/YYYY":
            self.day2_LineEdit_2.clear()
        QLineEdit.mousePressEvent(self.day2_LineEdit_2, event)

    def convert_date_to_int(self, date_str):
        try:
            parts = date_str.split("-")  # Tách theo dấu '-'

            if len(parts) != 3:
                raise ValueError("Ngày không hợp lệ. Định dạng yêu cầu: YYYY-MM-DD")

            # YYYYMMDD: Ghép các phần lại rồi chuyển thành int
            return int(parts[0] + parts[1] + parts[2])

        except ValueError as ve:
            print(f"Lỗi chuyển ngày: {ve}")
            return None
        except Exception as e:
            print(f"Lỗi không xác định khi chuyển ngày: {e}")
            return None

    def convert_date_to_int_2(self,date_str):
        try:
            date_obj = datetime.strptime(date_str, "%m/%d/%Y")
            return int(date_obj.strftime("%Y%m%d"))
        except ValueError as e:
            QMessageBox.warning(None, "Lỗi xử lý ngày", f"Lỗi: {e}")
            return None  # Trả về None nếu lỗi

    def validate_dates(self):
        start_date = self.day1_LineEdit_2.text().strip()
        end_date = self.day2_LineEdit_2.text().strip()

        try:
            start_parts = start_date.split("/")
            end_parts = end_date.split("/")

            if len(start_parts) != 3 or len(end_parts) != 3:
                raise ValueError("Ngày không hợp lệ! Vui lòng nhập theo định dạng MM/DD/YYYY")

            # Chuyển ngày về dạng số để so sánh
            start_value = int(start_parts[2] + start_parts[0] + start_parts[1])
            end_value = int(end_parts[2] + end_parts[0] + end_parts[1])

            if start_value > end_value:
                raise ValueError("Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc")

            return start_value, end_value

        except ValueError as e:
            QMessageBox.warning(self, "Lỗi nhập liệu", str(e))
            return None

    def calculate_total_data_revenue(self, start_date, end_date):
        try:
            # Lấy dữ liệu giao dịch từ MongoDB
            transactions = self.transactions_data

            total_orders = 0
            total_revenue = 0.0


            for txn in transactions:
                transaction_date = txn.get("TransactionDate")


                if transaction_date:
                    if isinstance(transaction_date, datetime):  # Kiểm tra kiểu dữ liệu là datetime
                        txn_date_value = self.convert_date_to_int(transaction_date.strftime("%Y-%m-%d"))
                    else:
                        txn_date_value = self.convert_date_to_int(transaction_date.split()[0])  # Nếu là chuỗi

                    # Kiểm tra nếu ngày giao dịch nằm trong khoảng thời gian yêu cầu
                    if start_date <= txn_date_value <= end_date:
                        total_orders += 1
                        total_revenue += txn.get("TotalAmount", 0.0)  # Giả sử "Revenue" là trường doanh thu trong MongoDB

            # Cập nhật các giá trị lên giao diện
            self.TotalData_LineEdit_2.setText(str(total_orders))
            self.Revence_LineEdit_2.setText(f"{total_revenue:.2f}")

            return total_orders, total_revenue

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi khi xử lý dữ liệu: {e}")
            return None, None

    def calculate_average_data(self, start_date, end_date, total_orders, total_revenue):
        try:
            # Lấy dữ liệu giao dịch từ MongoDB thông qua DBManager
            transactions = self.transactions_data  # Thay vì self.filtered_transactions

            if not transactions:
                QMessageBox.warning(self, "Data Error", "No transaction data available.")
                return

            total_discount = 0.0
            unique_days = set()

            # Duyệt qua dữ liệu giao dịch lấy từ MongoDB
            for txn in transactions:
                transaction_date = txn.get("TransactionDate")

                # Kiểm tra nếu có ngày giao dịch và chuyển thành giá trị số
                if transaction_date:
                    if isinstance(transaction_date, datetime):  # Kiểm tra kiểu datetime
                        txn_date_value = self.convert_date_to_int(
                            transaction_date.strftime("%Y-%m-%d"))  # Sử dụng strftime để chuyển datetime thành chuỗi
                    else:
                        txn_date_value = self.convert_date_to_int(transaction_date.split()[0])  # Nếu là chuỗi

                    if start_date <= txn_date_value <= end_date:
                        total_discount += txn.get("DiscountApplied(%)",
                                                  0.0)  # Giả sử "Discount" là trường giảm giá trong MongoDB
                        # Lưu số ngày duy nhất
                        if isinstance(transaction_date, datetime):
                            unique_days.add(
                                transaction_date.strftime("%Y-%m-%d"))  # Chuyển datetime thành chuỗi nếu cần
                        else:
                            unique_days.add(transaction_date.split()[0])  # Đối với chuỗi

            # Tính số ngày trong khoảng thời gian (tránh lỗi chia 0)
            num_days = len(unique_days) if len(unique_days) > 0 else 1

            # Tính toán trung bình
            avg_orders_per_day = total_orders / num_days
            avg_revenue_per_day = total_revenue / num_days
            avg_discount_rate = (total_discount / total_revenue) * 100 if total_revenue > 0 else 0

            # Hiển thị dữ liệu lên các LineEdit
            self.AveTrans_LineEdit_2.setText(f"{avg_orders_per_day:.2f}")
            self.AveRevenue_LineEdit_2.setText(f"{avg_revenue_per_day:.2f}")
            self.AppDiscountRate_LineEdit_2.setText(f"{avg_discount_rate:.2f}%")

        except ZeroDivisionError:
            QMessageBox.warning(self, "Lỗi", "Không có giao dịch nào trong khoảng thời gian này!")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi khi tính toán dữ liệu trung bình: {e}")

    def calculate_top5_products(self, start_date, end_date):
        """Cập nhật bảng Top 5 sản phẩm bán chạy nhất dựa trên số lượng từ MongoDB."""

        product_sales = {}  # Dictionary lưu thông tin sản phẩm { (Category, ProductID): [Quantity, Revenue] }

        try:
            transactions = self.transactions_data
            if not transactions:
                QMessageBox.warning(self, "Dữ liệu trống", "Không có dữ liệu giao dịch từ MongoDB.")
                return

            for txn in transactions:
                transaction_date = txn.get("TransactionDate")
                if not transaction_date:
                    continue

                if isinstance(transaction_date, datetime):  # Kiểm tra kiểu dữ liệu là datetime
                    txn_date_value = self.convert_date_to_int(transaction_date.strftime("%Y-%m-%d"))
                else:
                    txn_date_value = self.convert_date_to_int(transaction_date.split()[0])  # Nếu là chuỗi  # YYYY-MM-DD

                if start_date <= txn_date_value <= end_date:
                    category = txn.get("ProductCategory", "Unknown")
                    product_id = txn.get("ProductID", "Unknown")
                    quantity = int(txn.get("Quantity", 0))
                    price = float(txn.get("Price", 0))
                    revenue = quantity * price

                    key = (category, product_id)

                    if key in product_sales:
                        product_sales[key][0] += quantity
                        product_sales[key][1] += revenue
                    else:
                        product_sales[key] = [quantity, revenue]

            # Sắp xếp theo số lượng bán giảm dần và lấy Top 5 sản phẩm
            sorted_products = sorted(product_sales.items(), key=lambda x: x[1][0], reverse=True)[:5]

            # Cập nhật dữ liệu lên bảng `Top5_table_2`
            self.Top5_table_2.setRowCount(len(sorted_products))

            for row_idx, ((category, product_id), (quantity, revenue)) in enumerate(sorted_products):
                self.Top5_table_2.setItem(row_idx, 0, QTableWidgetItem(category))
                self.Top5_table_2.setItem(row_idx, 1, QTableWidgetItem(product_id))
                self.Top5_table_2.setItem(row_idx, 2, QTableWidgetItem(str(quantity)))
                self.Top5_table_2.setItem(row_idx, 3, QTableWidgetItem(f"{revenue:.2f}"))

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi khi xử lý dữ liệu top sản phẩm: {e}")

    def plot_bar_chart(self):
        """Vẽ biểu đồ cột: X là ProductID trong ProductCategory được chọn, Y là tổng doanh thu"""
        start_date, end_date = self.validate_dates()
        if not start_date or not end_date:
            return  # Dừng lại nếu ngày không hợp lệ

        selected_category = self.select_x_select_2.currentText()  # Lấy danh mục sản phẩm từ combobox
        revenue_data = {}  # Dictionary để lưu tổng doanh thu theo ProductID

        try:
            # Lấy tất cả các giao dịch từ MongoDB
            transactions = self.transactions_data
            if not transactions:
                QMessageBox.warning(self, "Dữ liệu trống", "Không có dữ liệu giao dịch từ MongoDB.")
                return

            # Duyệt qua các giao dịch và tính tổng doanh thu cho mỗi ProductID trong selected_category
            for txn in transactions:
                transaction_date = txn.get("TransactionDate")
                if not transaction_date:
                    continue

                if isinstance(transaction_date, datetime):  # Kiểm tra kiểu dữ liệu là datetime
                    txn_date_value = self.convert_date_to_int(transaction_date.strftime("%Y-%m-%d"))
                else:
                    txn_date_value = self.convert_date_to_int(transaction_date.split()[0])  # Nếu là chuỗi  # YYYY-MM-DD

                if start_date <= txn_date_value <= end_date:
                    product_category = txn.get("ProductCategory", "Unknown")
                    product_id = txn.get("ProductID", "Unknown")
                    quantity = int(txn.get("Quantity", 0))
                    price = float(txn.get("Price", 0))
                    revenue = quantity * price

                    # Chỉ lấy dữ liệu của ProductCategory được chọn
                    if product_category == selected_category:
                        if product_id in revenue_data:
                            revenue_data[product_id] += revenue
                        else:
                            revenue_data[product_id] = revenue

            # Kiểm tra nếu không có dữ liệu
            if not revenue_data:
                QMessageBox.warning(self, "Thông báo", f"Không có dữ liệu cho danh mục '{selected_category}'!")
                return

            # Chuyển dữ liệu thành danh sách
            product_ids = list(revenue_data.keys())
            revenues = list(revenue_data.values())

            # Sắp xếp ProductID theo thứ tự mong muốn (A, B, C, ... hoặc 1, 2, 3...)
            sorted_items = sorted(revenue_data.items(), key=lambda x: x[0])
            product_ids = [item[0] for item in sorted_items]
            revenues = [item[1] for item in sorted_items]

            # Vẽ biểu đồ cột
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.bar(product_ids, revenues, color='blue')

            # Gắn tiêu đề & nhãn
            ax.set_title(f"Doanh thu của từng ProductID trong {selected_category}")
            ax.set_xlabel("ProductID")
            ax.set_ylabel("Doanh thu (VND)")
            ax.set_xticks(range(len(product_ids)))
            ax.set_xticklabels(product_ids, rotation=45, ha="right")  # Xoay nhãn X để dễ nhìn
            ax.grid(axis='y', linestyle="--", alpha=0.7)

            # Tạo FigureCanvas và hiển thị trong xy_graphicsView_2
            canvas = FigureCanvasQTAgg(fig)
            scene = QGraphicsScene()
            scene.addWidget(canvas)
            self.xy_graphicsView_2.setScene(scene)
            self.xy_graphicsView_2.show()

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi khi xử lý dữ liệu: {e}")

    def plot_revenue_trend(self):
        """Vẽ biểu đồ đường thể hiện xu hướng doanh thu theo tháng trong khoảng thời gian được chọn"""
        start_date, end_date = self.validate_dates()
        if not start_date or not end_date:
            return  # Dừng nếu ngày không hợp lệ

        revenue_by_month = {}

        try:
            # Lấy tất cả các giao dịch từ MongoDB
            transactions = self.transactions_data
            if not transactions:
                QMessageBox.warning(self, "Dữ liệu trống", "Không có dữ liệu giao dịch từ MongoDB.")
                return

            # Duyệt qua các giao dịch và tính tổng doanh thu theo tháng
            for txn in transactions:
                transaction_date = txn.get("TransactionDate")
                if not transaction_date:
                    continue

                # Kiểm tra nếu transaction_date là datetime, nếu có thì sử dụng strftime
                if isinstance(transaction_date, datetime):  # Kiểm tra kiểu dữ liệu là datetime
                    txn_month = transaction_date.strftime("%Y-%m")  # Lấy tháng và năm (YYYY-MM)
                else:
                    txn_month = transaction_date.split()[0][:7]  # Nếu là chuỗi, lấy phần "YYYY-MM"

                if start_date <= self.convert_date_to_int(txn_month + "-01") <= end_date:
                    try:
                        revenue = float(txn.get("TotalAmount", 0))  # Giả sử trường "Revenue" lưu doanh thu
                        # Cộng dồn doanh thu theo tháng
                        revenue_by_month[txn_month] = revenue_by_month.get(txn_month, 0) + revenue
                    except ValueError:
                        continue  # Bỏ qua nếu giá trị doanh thu không hợp lệ

            # Kiểm tra nếu không có dữ liệu
            if not revenue_by_month:
                QMessageBox.warning(self, "Thông báo", "Không có dữ liệu doanh thu trong khoảng thời gian này!")
                return

            # Sắp xếp dữ liệu theo tháng
            sorted_months = sorted(revenue_by_month.keys())
            sorted_revenues = [revenue_by_month[month] for month in sorted_months]

            # Vẽ biểu đồ
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(sorted_months, sorted_revenues, marker='o', linestyle='-', color='b', label="Doanh thu")

            # Cấu hình biểu đồ
            ax.set_title("Xu hướng doanh thu theo tháng")
            ax.set_xlabel("Tháng")
            ax.set_ylabel("Tổng doanh thu (VND)")
            ax.tick_params(axis='x', rotation=45)  # Xoay nhãn tháng
            ax.grid(True, linestyle="--", alpha=0.7)
            ax.legend()

            # Hiển thị trên Factor_graphicsView_2
            canvas = FigureCanvasQTAgg(fig)
            scene = QGraphicsScene()
            scene.addWidget(canvas)
            self.Factor_graphicsView_2.setScene(scene)
            self.Factor_graphicsView_2.show()

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi khi xử lý dữ liệu: {e}")

    def plot_pie_chart(self):
        """Vẽ biểu đồ tròn: Mỗi phần là số lượng bán của một ProductCategory"""
        start_date, end_date = self.validate_dates()
        if not start_date or not end_date:
            return  # Dừng nếu ngày không hợp lệ

        category_sales = {}  # Dictionary lưu tổng số lượng bán theo ProductCategory

        try:
            # Lấy tất cả các giao dịch từ MongoDB
            transactions = self.transactions_data
            if not transactions:
                QMessageBox.warning(self, "Dữ liệu trống", "Không có dữ liệu giao dịch từ MongoDB.")
                return

            # Duyệt qua các giao dịch và tính tổng số lượng bán theo ProductCategory
            for txn in transactions:
                transaction_date = txn.get("TransactionDate")
                if not transaction_date:
                    continue

                if isinstance(transaction_date, datetime):  # Kiểm tra kiểu dữ liệu là datetime
                    txn_date_value = self.convert_date_to_int(transaction_date.strftime("%Y-%m-%d"))
                else:
                    txn_date_value = self.convert_date_to_int(transaction_date.split()[0])  # Nếu là chuỗi  # YYYY-MM-DD

                if start_date <= txn_date_value <= end_date:
                    product_category = txn.get("ProductCategory", "Unknown")
                    quantity = int(txn.get("Quantity", 0))

                    # Cộng dồn số lượng bán theo ProductCategory
                    category_sales[product_category] = category_sales.get(product_category, 0) + quantity

            # Kiểm tra nếu không có dữ liệu
            if not category_sales:
                QMessageBox.warning(self, "Thông báo", "Không có dữ liệu số lượng bán!")
                return

            # Chuyển dữ liệu thành danh sách
            categories = list(category_sales.keys())
            quantities = list(category_sales.values())

            # Vẽ biểu đồ tròn
            fig, ax = plt.subplots(figsize=(7, 7))
            ax.pie(quantities, labels=categories, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
            ax.set_title("Tỷ lệ số lượng bán")

            # Hiển thị trong Factor_graphicsView_2
            canvas = FigureCanvasQTAgg(fig)
            scene = QGraphicsScene()
            scene.addWidget(canvas)
            self.Factor_graphicsView_2.setScene(scene)
            self.Factor_graphicsView_2.show()

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi khi xử lý dữ liệu: {e}")

