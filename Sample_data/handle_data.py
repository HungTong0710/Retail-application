import csv
import random
from datetime import datetime

# add 2 column
with open("Retail_Transaction_Dataset_Cleaned.csv", "r", encoding="utf-8") as infile:
    reader = list(csv.reader(infile))  # Đọc toàn bộ dữ liệu vào danh sách

# Lấy dòng tiêu đề và dữ liệu
header = reader[0]
data = reader[1:]

# Tạo danh sách TransactionID ngẫu nhiên (số lượng bằng số giao dịch)
transaction_ids = [f"T{i:03d}" for i in range(1, len(data) + 1)]
random.shuffle(transaction_ids)  # Xáo trộn danh sách ID để tạo thứ tự ngẫu nhiên

# Thêm 2 cột mới vào header
header.insert(0, "TransactionID")  # Cột ID giao dịch
header.insert(2, "EmployeeID")  # Cột nhân viên

# Xử lý từng dòng dữ liệu
for i, row in enumerate(data):
    # Gán TransactionID từ danh sách đã trộn
    transaction_id = transaction_ids[i]

    # Lấy TransactionDate và xác định EmployeeID
    transaction_date = row[4]  # Cột thứ 4 là TransactionDate (0-based index)
    try:
        time_part = transaction_date.split(" ")[1]  # Lấy giờ phút: "12:26"
        hour = int(time_part.split(":")[0])  # Lấy giờ
    except:
        hour = 12  # Nếu lỗi, mặc định là giữa ngày

    # Gán EmployeeID dựa vào giờ giao dịch
    if 6 <= hour < 12:
        employee_id = "E1"
    elif 12 <= hour < 18:
        employee_id = "E2"
    elif 18 <= hour < 24:
        employee_id = "E3"
    elif 0 <= hour < 5:
        employee_id = "E4"

    # Chèn 2 giá trị mới vào danh sách dòng
    row.insert(0, transaction_id)
    row.insert(2, employee_id)

# Ghi dữ liệu vào file mới
with open("Retail_Transaction_Dataset_Final.csv", "w", encoding="utf-8", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(header)  # Ghi tiêu đề mới
    writer.writerows(data)  # Ghi toàn bộ dữ liệu

print("✅ Đã thêm cột 'TransactionID' (random) và 'EmployeeID' vào file 'Retail_Transaction_Dataset_Final.csv'")


import csv
import random
from faker import Faker
from datetime import datetime, timedelta


fake = Faker()

# Danh sách Membership Level và Category
categories = ["Electronics", "Books", "Home Decor", "Clothing"]

# Danh sách lưu trữ dữ liệu
members_data = [
    ["CustomerID", "Name", "Email", "Phone Number", "Birthday", "MembershipStatus",
     "JoinDate", "MembershipLevel", "TotalSpend", "TotalTransactions",
     "MostPurchasedCategory", "LastPurchaseDate", "LoyaltyPoints"]
]

# Tạo 5 khách hàng giả lập
for i in range(1, 10 + 1):
    customer_id = f"C{i:03d}"  # ID dạng C001, C002...
    name = fake.name()  # Tên giả
    email = fake.email()  # Email giả
    phone = fake.phone_number()[:10]  # Số điện thoại hợp lệ
    birthday = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d")  # Ngày sinh

    # Ngày tham gia (5 năm trở lại, có giờ phút)
    join_date = fake.date_between(start_date="-5y", end_date="today")
    join_time = fake.time(pattern="%H:%M", end_datetime=None)  # Random giờ phút
    join_date_str = join_date.strftime(f"%Y-%m-%d {join_time}")  # Kết hợp ngày + giờ

    # Chọn Membership Level trước để đảm bảo tính hợp lý
    membership_level = random.choices(["Silver", "Gold", "Platinum"], weights=[50, 35, 15])[0]

    # Chọn Total Transactions hợp lý theo Membership Level
    if membership_level == "Silver":
        total_transactions = random.randint(0, 100)
    elif membership_level == "Gold":
        total_transactions = random.randint(100, 300)
    else:  # Platinum
        total_transactions = random.randint(300, 500)

    # Tính Loyalty Points (cứ 4 giao dịch mới được +1 điểm, nhưng có tuần không đạt)
    possible_loyalty = total_transactions // 4  # Số điểm tối đa có thể nhận
    loyalty_points = random.randint(int(possible_loyalty * 0.7), possible_loyalty)  # Giới hạn 70 - 100% số điểm tối đa

    # Cập nhật Membership Level theo Loyalty Points
    if loyalty_points >= 100:
        membership_level = "Platinum"
    elif loyalty_points >= 50:
        membership_level = "Gold"
    else:
        membership_level = "Silver"

    # Xác định Total Spend theo Membership Level
    if membership_level == "Silver":
        total_spend = round(random.uniform(100, 5000), 2)
    elif membership_level == "Gold":
        total_spend = round(random.uniform(5000, 12000), 2)
    else:  # Platinum
        total_spend = round(random.uniform(12000, 20000), 2)

    # Chọn danh mục mua nhiều nhất
    most_purchased_category = random.choice(categories)

    # **Xác định Last Purchase Date để đảm bảo tỷ lệ Active/Inactive/Expired hợp lý**
    current_date = datetime.today()
    status_category = random.choices(["Active", "Inactive", "Expired"], weights=[50, 30, 20])[0]  # 50% Active, 30% Inactive, 20% Expired

    if status_category == "Active":

        last_purchase_date = current_date - timedelta(days=random.randint(1,180))# Từ 1 đến 6 tháng trước
    elif status_category == "Inactive":
        last_purchase_date = current_date - timedelta(days=random.randint(181, 365))  # 6 - 12 tháng trước
    else:
        last_purchase_date = current_date - timedelta(days=random.randint(366, 1825))  # 1 - 5 năm trước

    last_purchase_time = fake.time(pattern="%H:%M", end_datetime=None)  # Random giờ phút
    last_purchase_date_str = last_purchase_date.strftime(f"%Y-%m-%d {last_purchase_time}")  # Kết hợp ngày + giờ

    # Cập nhật Membership Status từ `status_category`
    membership_status = status_category

    # Thêm dữ liệu vào danh sách
    members_data.append([
        customer_id, name, email, phone, birthday, membership_status, join_date_str,
        membership_level, total_spend, total_transactions, most_purchased_category,
        last_purchase_date_str, loyalty_points
    ])

# Ghi dữ liệu vào file CSV
with open("Members_Data.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(members_data)

print("✅ Đã tạo thành công file 'Members_Data.csv' với 1000 khách hàng!")

#test


# file transaction của members
import csv

# Đọc danh sách thành viên và số lượng giao dịch từ Members Data
members_info = {}  # Lưu CustomerID và số lượng giao dịch cần có

with open("Members_Data.csv", "r", encoding="utf-8") as members_file:
    reader = csv.reader(members_file)
    next(reader)  # Bỏ qua tiêu đề
    for row in reader:
        customer_id = row[0]  # CustomerID
        total_transactions = int(row[9])  # Cột TotalTransactions
        members_info[customer_id] = total_transactions  # Lưu vào dictionary

# Đọc Transaction Data và cập nhật CustomerID
updated_transactions = []  # Danh sách mới sau khi cập nhật
transaction_count = {cid: 0 for cid in members_info}  # Đếm số giao dịch của mỗi thành viên

with open("Retail_Transaction_Dataset_Final.csv", "r", encoding="utf-8") as transactions_file:
    reader = csv.reader(transactions_file)
    header = next(reader)  # Đọc tiêu đề
    updated_transactions.append(header)  # Giữ nguyên tiêu đề

    for row in reader:
        old_customer_id = row[1]  # CustomerID cũ
        for new_customer_id, max_transactions in members_info.items():
            if transaction_count[new_customer_id] < max_transactions:  # Kiểm tra số giao dịch
                row[1] = new_customer_id  # Cập nhật CustomerID
                updated_transactions.append(row)
                transaction_count[new_customer_id] += 1
                break  # Chỉ cập nhật một giao dịch, sau đó chuyển sang dòng tiếp theo

# Ghi dữ liệu mới vào file CSV
with open("Retail_Transaction_Dataset_Updated.csv", "w", encoding="utf-8", newline="") as output_file:
    writer = csv.writer(output_file)
    writer.writerows(updated_transactions)

print("✅ Đã cập nhật CustomerID trong Transaction Data và đảm bảo số lượng giao dịch khớp với Members Data!")

# gộp file tổng
import csv
import random

# Đọc dữ liệu khách vãng lai từ Transaction Data gốc
transactions_non_members = []
with open("Retail_Transaction_Dataset_Final.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    header = next(reader)  # Đọc tiêu đề
    transactions_non_members = list(reader)  # Đọc toàn bộ giao dịch khách vãng lai

# Đọc dữ liệu thành viên từ Transaction Data đã xử lý
transactions_members = []
with open("Retail_Transaction_Dataset_Updated.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)  # Bỏ qua tiêu đề (header không cần vì đã có từ file trên)
    transactions_members = list(reader)  # Đọc toàn bộ giao dịch thành viên

# Kết hợp danh sách khách vãng lai và thành viên
all_transactions = transactions_non_members + transactions_members
random.shuffle(all_transactions)  # Xáo trộn thứ tự

# Ghi dữ liệu mới vào file CSV
with open("Retail_Transaction_Dataset_With_Members.csv", "w", encoding="utf-8", newline="") as output_file:
    writer = csv.writer(output_file)
    writer.writerow(header)  # Ghi tiêu đề
    writer.writerows(all_transactions)  # Ghi tất cả giao dịch

print("✅ Đã thêm giao dịch thành viên vào Transaction Data và lưu vào 'Retail_Transaction_Dataset_With_Members.csv'")


#sắp xếp theo thời gian
import csv
from datetime import datetime

# Đọc dữ liệu từ file gốc
with open("Retail_Transaction_Dataset_With_Members.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    header = next(reader)  # Đọc tiêu đề
    transactions = list(reader)  # Đọc toàn bộ dữ liệu vào danh sách

# Chuyển TransactionDate thành datetime và sắp xếp theo thứ tự tăng dần
transactions.sort(key=lambda row: datetime.strptime(row[6], "%m/%d/%Y %H:%M"))  # Giả sử định dạng là MM/DD/YYYY HH:MM

# Ghi dữ liệu đã sắp xếp vào file mới
with open("Retail_Transaction_Dataset_Sorted.csv", "w", encoding="utf-8", newline="") as output_file:
    writer = csv.writer(output_file)
    writer.writerow(header)  # Ghi tiêu đề
    writer.writerows(transactions)  # Ghi dữ liệu đã sắp xếp

print("✅ Đã sắp xếp giao dịch theo ngày giờ và lưu vào 'Retail_Transaction_Dataset_Sorted.csv'")








