import pymongo
from datetime import datetime

class DBManager:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="Data_Object"):
        try:
            self.client = pymongo.MongoClient(uri)
            self.db = self.client[db_name]
            self.customers = self.db["customers"]
            self.transactions = self.db["transactions"]
            self.employees = self.db["employees"]
            print("Connected to MongoDB successfully in DBManager!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.customers = None
            self.transactions = None

    # ----- Methods cho bảng Customers -----
    def get_all_customers(self):
        if self.customers is None:
            return []
        return list(self.customers.find({}).sort("JoinDate", pymongo.DESCENDING))

    def insert_customer(self, customer_data):
        if self.customers is None:
            raise Exception("No connection to MongoDB")
        # Đảm bảo JoinDate là datetime object
        if "JoinDate" not in customer_data:
            customer_data["JoinDate"] = datetime.now()
        elif isinstance(customer_data["JoinDate"], str):
            try:
                customer_data["JoinDate"] = datetime.strptime(
                    customer_data["JoinDate"],
                    "%Y-%m-%dT%H:%M:%S.000+00:00"
                )
            except ValueError:
                raise ValueError("Định dạng JoinDate không hợp lệ. Sử dụng yyyy-MM-ddTHH:mm:ss.000+00:00")
        # Đảm bảo Birthday là datetime object nếu có
        if "Birthday" in customer_data and isinstance(customer_data["Birthday"], str):
            try:
                customer_data["Birthday"] = datetime.strptime(
                    customer_data["Birthday"],
                    "%Y-%m-%d"
                )
            except ValueError:
                raise ValueError("Định dạng Birthday không hợp lệ. Sử dụng YYYY-MM-DD")
        return self.customers.insert_one(customer_data)

    def update_customer(self, customer_id, updated_data):
        if self.customers is None:
            raise Exception("No connection to MongoDB")
        return self.customers.update_one({"_id": customer_id}, {"$set": updated_data})

    def delete_customer(self, customer_id):
        if self.customers is None:
            raise Exception("No connection to MongoDB")
        return self.customers.delete_one({"_id": customer_id})

    def search_customers(self, query):
        if self.customers is None:
            return []
        return list(self.customers.find(query))

    def generate_new_customer_id(self, is_member=False):
        if is_member:
            # Logic tạo ID member
            if self.customers is None:
                raise Exception("No connection to MongoDB")
            pipeline = [
                {"$match": {"_id": {"$regex": r"^C\d+$"}}},
                {"$addFields": {"numeric_id": {"$toInt": {"$substrBytes": ["$_id", 1, {"$strLenBytes": "$_id"}]}}}},
                {"$group": {"_id": None, "max_id": {"$max": "$numeric_id"}}}
            ]
            result = list(self.customers.aggregate(pipeline))
            new_id = (result[0]["max_id"] + 1) if result and result[0].get("max_id") is not None else 1
            return f"C{new_id}"
        else:
            if self.transactions is None:
                raise Exception("No connection to MongoDB")
            try:
                # Tìm CustomerID lớn nhất kiểu số nguyên
                pipeline = [
                    {"$match": {"CustomerID": {"$type": "int"}}},
                    {"$group": {"_id": None, "max_id": {"$max": "$CustomerID"}}}
                ]
                result = list(self.transactions.aggregate(pipeline))
                if result and result[0].get("max_id") is not None:
                    new_id = result[0]["max_id"] + 1
                else:
                    new_id = 1  # Bắt đầu từ 1 nếu không có dữ liệu
                return new_id
            except Exception as e:
                print(f"Lỗi khi tạo ID vãng lai: {e}")
                return 1  # Fallback value

    def update_customer_info(self, customer_id):
        # Kiểm tra kết nối tới MongoDB
        if self.customers is None:
            raise Exception("No connection to MongoDB")

        # Tìm thông tin khách hàng
        customers = self.search_customers({"_id": customer_id})
        if not customers:
            return

        # Lấy tất cả giao dịch của khách hàng
        transactions = self.search_transactions({"CustomerID": customer_id})

        # Tính tổng chi tiêu và số lượng giao dịch
        total_spend = sum(float(tx.get("TotalAmount", 0)) for tx in transactions)
        total_transactions = len(transactions)

        # Tìm danh mục sản phẩm được mua nhiều nhất
        category_count = {}
        for tx in transactions:
            category = tx.get("ProductCategory", "None")
            category_count[category] = category_count.get(category, 0) + 1
        most_common_category = max(category_count, key=category_count.get) if category_count else "None"

        # Xử lý và chuyển đổi TransactionDate về datetime cho tất cả các giao dịch
        tx_dates = []
        for tx in transactions:
            dt = tx.get("TransactionDate")
            if dt:
                if isinstance(dt, str):
                    try:
                        dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.000+00:00")
                    except ValueError:
                        # Nếu định dạng không đúng, bỏ qua giao dịch này
                        continue
                tx_dates.append(dt)
        last_purchase_date = max(tx_dates) if tx_dates else None

        # Xác định trạng thái thành viên dựa trên ngày giao dịch gần nhất
        membership_status = "Active"
        if last_purchase_date:
            days_since_last_purchase = (datetime.now() - last_purchase_date).days
            if days_since_last_purchase > 365:
                membership_status = "Expired"
            elif days_since_last_purchase > 182:
                membership_status = "Inactive"

        # Tính điểm trung thành dựa trên số giao dịch hàng tháng
        monthly_tx_count = {}
        for tx in transactions:
            dt = tx.get("TransactionDate")
            if dt:
                if isinstance(dt, str):
                    try:
                        dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.000+00:00")
                    except ValueError:
                        continue
                year_month = (dt.year, dt.month)
                monthly_tx_count[year_month] = monthly_tx_count.get(year_month, 0) + 1
        loyalty_points = sum(1 for count in monthly_tx_count.values() if count >= 4)

        # Xác định cấp độ thành viên dựa trên điểm trung thành và tổng chi tiêu
        membership_level = "Silver"
        if loyalty_points > 50 and total_spend > 20000:
            membership_level = "Platinum"
        elif loyalty_points > 20 and total_spend > 10000:
            membership_level = "Gold"

        # Dữ liệu cập nhật
        updated_data = {
            "LoyaltyPoints": int(loyalty_points),
            "TotalSpend": float(total_spend),
            "TotalTransactions": int(total_transactions),
            "MostPurchasedCategory": str(most_common_category),
            "LastPurchaseDate": last_purchase_date,  # Đã là datetime nếu tồn tại
            "MembershipStatus": str(membership_status),
            "MembershipLevel": str(membership_level)
        }

        # Cập nhật thông tin khách hàng trong MongoDB
        self.update_customer(customer_id, updated_data)

    # ----- Methods cho bảng Transactions -----
    def get_all_transactions(self):
        if self.transactions is None:
            return []
        return list(self.transactions.find({}).sort("TransactionDate", pymongo.DESCENDING))

    def insert_transaction(self, transaction_data):
        if self.transactions is None:
            raise Exception("No connection to MongoDB")

        # Chuyển đổi TransactionDate thành datetime object
        if "TransactionDate" in transaction_data:
            try:
                transaction_data["TransactionDate"] = datetime.strptime(
                    transaction_data["TransactionDate"],
                    "%Y-%m-%dT%H:%M:%S.000+00:00"  # Định dạng ISO 8601
                )
            except Exception as e:
                raise ValueError(f"Invalid TransactionDate format: {str(e)}")
        else:
            transaction_data["TransactionDate"] = datetime.now()

        # Chuyển đổi kiểu dữ liệu
        transaction_data["Quantity"] = int(transaction_data["Quantity"])  # Int32
        transaction_data["Price"] = float(transaction_data["Price"])  # Double
        transaction_data["DiscountApplied(%)"] = float(transaction_data["DiscountApplied(%)"])  # Double
        transaction_data["TotalAmount"] = float(transaction_data["TotalAmount"])  # Double

        return self.transactions.insert_one(transaction_data)

    def update_transaction(self, transaction_id, updated_data):
        if self.transactions is None:
            raise Exception("No connection to MongoDB")

        # Chuyển đổi kiểu dữ liệu nếu cần
        if "Quantity" in updated_data:
            updated_data["Quantity"] = int(updated_data["Quantity"])  # Int32
        if "Price" in updated_data:
            updated_data["Price"] = float(updated_data["Price"])  # Double
        if "DiscountApplied(%)" in updated_data:
            updated_data["DiscountApplied(%)"] = float(updated_data["DiscountApplied(%)"])  # Double
        if "TotalAmount" in updated_data:
            updated_data["TotalAmount"] = float(updated_data["TotalAmount"])  # Double
        if "TransactionDate" in updated_data:
            try:
                updated_data["TransactionDate"] = datetime.strptime(
                    updated_data["TransactionDate"],
                    "%Y-%m-%dT%H:%M:%S.000+00:00"
                )
            except ValueError:
                raise ValueError("Invalid TransactionDate format")
        return self.transactions.update_one(
            {"_id": transaction_id},
            {"$set": updated_data}
        )

    def delete_transaction(self, transaction_id):
        if self.transactions is None:
            raise Exception("No connection to MongoDB")
        return self.transactions.delete_one({"_id": transaction_id})

    def search_transactions(self, query):
        if self.transactions is None:
            return []
        return list(self.transactions.find(query))

    def generate_new_transaction_id(self):
        if self.transactions is None:
            raise Exception("No connection to MongoDB")
        last_transaction = self.transactions.find_one(
            {"_id": {"$regex": "^T\\d{6}$"}},
            sort=[("_id", pymongo.DESCENDING)]
        )
        if last_transaction:
            last_id_number = int(last_transaction["_id"][1:])
            new_number = last_id_number + 1
        else:
            new_number = 1
        return f"T{new_number:06d}"

    # ----- Methods cho bảng Employees -----
    def check_login(self, username, password, role):
        try:
            if self.employees is None:
                return None
            user = self.employees.find_one({
                "username": username,
                "password": password,
                "role": {"$regex": f"^{role}$", "$options": "i"}
            })
            return user
        except Exception as e:
            print(f"Lỗi đăng nhập: {e}")
            return None
