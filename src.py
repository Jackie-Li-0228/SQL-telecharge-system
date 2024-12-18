import mysql.connector
from datetime import datetime,timedelta
from decimal import Decimal
from Exception_Classes import *

# 数据库连接设置
db = mysql.connector.connect(
    host="localhost",        # 数据库主机
    user="root",    # 数据库用户名
    password="123123", # 数据库密码
    database="telecharge"  # 数据库名称
)

cursor = db.cursor()

def create_new_phone_account(phone_number, id_card_number, password, package_id=None):
    """
    Function to create a new phone account with the given phone number, ID card, and password.
    If package_id is not provided, it uses the default package ID.

    Parameters:
    - phone_number: The phone number for the new account.
    - id_card_number: The ID card number of the user.
    - password: The password for the phone account.
    - package_id: (Optional) The package ID for the phone account. If not provided, the default is used.
    
    Raises:
    - UserNotFoundError: If the user with the given ID card number does not exist.
    - DatabaseError: If any database operation fails.
    """

    # 获取当前时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 默认套餐ID
    default_package_id = 1

    # 如果没有提供套餐ID，使用默认套餐ID
    if package_id is None:
        package_id = default_package_id
    
    # 查询用户的用户类型（UserTypeID）
    cursor.execute("SELECT UserTypeID FROM Users WHERE IDCardNumber = %s", (id_card_number,))
    user_type_result = cursor.fetchone()
    
    if user_type_result is None:
        # 抛出用户不存在的异常
        raise UserNotFoundError(f"User with the given ID card number {id_card_number} does not exist.")
    
    user_type_id = user_type_result[0]

    # 插入新的电话号码记录
    try:
        cursor.execute("""
            INSERT INTO PhoneAccounts (PhoneNumber, Balance, IsSuspended, VoiceBalance, 
                                       PackageStartTime, PackageEndTime, IDCardNumber, 
                                       PackageID, Password, UserTypeID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (phone_number, 0.00, False, 0.00, current_time, None, id_card_number, 
              package_id, password, user_type_id))
        
        # 提交更改
        db.commit()
        print(f"Phone account {phone_number} created successfully.")
    
    except mysql.connector.Error as err:
        # 捕获数据库错误并抛出自定义异常
        db.rollback()
        raise DatabaseError(f"Database error occurred: {err}")


# 使用函数
try:
    create_new_phone_account("13812345678", "123456789012345678", "securepassword123")
except UserNotFoundError as e:
    print(f"User not found: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")

def make_payment(phone_number, amount, payment_method):
    """
    Function to process a payment for the given phone number and amount.
    It updates the balance in the PhoneAccounts table and inserts the payment record.

    Parameters:
    - phone_number: The phone number to process payment for.
    - amount: The payment amount to add to the balance.
    - payment_method: The payment method used for the transaction (e.g., 'credit card', 'cash').

    Raises:
    - PhoneNumberNotFoundError: If the phone number is not found in the database.
    - PaymentProcessingError: If there is an error during the payment processing (e.g., database issues).
    """

    # 获取当前时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 检查手机号是否存在
    cursor.execute("SELECT Balance FROM PhoneAccounts WHERE PhoneNumber = %s", (phone_number,))
    account = cursor.fetchone()

    if account is None:
        # 抛出手机号未找到异常
        raise PhoneNumberNotFoundError(f"Phone number {phone_number} not found.")

    # 更新余额
    new_balance = account[0] + Decimal(amount)
    
    try:
        # 更新电话号码的余额
        cursor.execute("""
            UPDATE PhoneAccounts 
            SET Balance = %s
            WHERE PhoneNumber = %s
        """, (new_balance, phone_number))

        # 插入缴费记录
        cursor.execute("""
            INSERT INTO PaymentRecords (PaymentTime, Amount, PaymentMethod, PhoneNumber)
            VALUES (%s, %s, %s, %s)
        """, (current_time, amount, payment_method, phone_number))

        # 提交更改
        db.commit()
        print(f"Payment of {amount} for phone number {phone_number} completed successfully using {payment_method}.")

    except mysql.connector.Error as err:
        # 捕获数据库操作错误并抛出支付处理错误异常
        db.rollback()
        raise PaymentProcessingError(f"Error processing payment for phone number {phone_number}: {err}")

# 使用函数
try:
    make_payment("13812345678", 50.00, "credit card")
except PhoneNumberNotFoundError as e:
    print(f"Error: {e}")
except PaymentProcessingError as e:
    print(f"Error: {e}")


def get_user_info_by_phone(phone_number):
    """
    Function to get the user information associated with the given phone number.

    Parameters:
    - phone_number: The phone number to query.

    Returns:
    - A dictionary containing user information (name, ID card number, age, gender, user type).
    
    Raises:
    - PhoneNumberNotFoundError: If the phone number is not found in the database.
    """

    # 查询手机号对应的用户的身份证号和用户类型ID
    cursor.execute("""
        SELECT u.Name, u.IDCardNumber, u.Age, u.Gender, ut.UserTypeName
        FROM PhoneAccounts p
        JOIN Users u ON p.IDCardNumber = u.IDCardNumber
        JOIN UserTypes ut ON u.UserTypeID = ut.UserTypeID
        WHERE p.PhoneNumber = %s
    """, (phone_number,))

    user_info = cursor.fetchone()

    if user_info is None:
        # 抛出手机号未找到异常
        raise PhoneNumberNotFoundError(f"Phone number {phone_number} not found.")

    # 返回查询到的用户信息
    user_data = {
        "PhoneNumber": phone_number,
        "Name": user_info[0],
        "IDCardNumber": user_info[1],
        "Age": user_info[2],
        "Gender": user_info[3],
        "UserType": user_info[4]
    }
    
    return user_data


# 使用函数获取用户信息
try:
    user_info = get_user_info_by_phone("13812345678")
    print(user_info)
except PhoneNumberNotFoundError as e:
    print(f"Error: {e}")

def register_user(id_card_number, name, age, gender, user_type_name="普通用户"):
    """
    Function to register a new user in the database.

    Parameters:
    - id_card_number: The ID card number of the user.
    - name: The name of the user.
    - age: The age of the user.
    - gender: The gender of the user ('M' or 'F').
    - user_type_name: The user type (default is "普通用户").
    
    Raises:
    - UserTypeNotFoundError: If the provided user type does not exist in the database.
    - DatabaseError: If there is any database-related error during registration.
    """
    
    # 查询用户类型的ID（默认是“普通用户”）
    cursor.execute("SELECT UserTypeID FROM UserTypes WHERE UserTypeName = %s", (user_type_name,))
    user_type_result = cursor.fetchone()

    if user_type_result is None:
        # 抛出用户类型未找到异常
        raise UserTypeNotFoundError(f"Invalid user type '{user_type_name}'. Defaulting to '普通用户'.")
    
    user_type_id = user_type_result[0]

    # 插入新用户记录
    try:
        cursor.execute("""
            INSERT INTO Users (IDCardNumber, Name, Age, Gender, UserTypeID)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_card_number, name, age, gender, user_type_id))

        # 提交事务
        db.commit()
        print(f"User '{name}' registered successfully.")
    except mysql.connector.Error as err:
        # 捕获数据库相关的异常，抛出自定义的DatabaseError
        raise DatabaseError(f"Error while registering user: {err}")


# 使用示例
try:
    register_user("123456789012345678", "张三", 28, "M", "普通用户")
except UserTypeNotFoundError as e:
    print(f"Error: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")

def get_package_details(phone_number):
    """
    Function to get the package details of the current phone number, including package information 
    from the Packages table and account-related information from the PhoneAccounts table.

    Parameters:
    - phone_number: The phone number to retrieve package details for.

    Returns:
    - A dictionary containing package details and account information.

    Raises:
    - PhoneNumberNotFoundError: If the phone number is not found in the PhoneAccounts table.
    - DatabaseError: If there is any database-related error during the query.
    """
    try:
        # 查询手机号对应的套餐和账户信息
        cursor.execute("""
            SELECT p.PackageID, pkg.PackageName, pkg.Price, pkg.LaunchTime, pkg.ExpirationTime, 
                   pkg.ContractDuration, pkg.VoiceQuota, pkg.OverQuotaStandard, 
                   p.Balance, p.IsSuspended, p.VoiceBalance, p.PackageStartTime, p.PackageEndTime
            FROM PhoneAccounts p
            JOIN Packages pkg ON p.PackageID = pkg.PackageID
            WHERE p.PhoneNumber = %s
        """, (phone_number,))

        package_details = cursor.fetchone()

        if package_details is None:
            raise PhoneNumberNotFoundError(f"Phone number {phone_number} not found.")

        # 提取查询到的字段并组织为字典
        package_data = {
            "PhoneNumber": phone_number,
            "PackageID": package_details[0],
            "PackageName": package_details[1],
            "PackagePrice": package_details[2],
            "LaunchTime": package_details[3],
            "ExpirationTime": package_details[4],
            "ContractDuration": package_details[5],
            "VoiceQuota": package_details[6],
            "OverQuotaStandard": package_details[7],
            "AccountBalance": package_details[8],
            "IsSuspended": package_details[9],
            "VoiceBalance": package_details[10],
            "PackageStartTime": package_details[11],
            "PackageEndTime": package_details[12]
        }

        return package_data

    except mysql.connector.Error as err:
        # 捕获数据库错误并抛出异常
        raise DatabaseError(f"Error while fetching package details: {err}")

try:
    package_info = get_package_details("13812345678")
    print(package_info)
except PhoneNumberNotFoundError as e:
    print(f"Error: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")

def get_available_packages():
    """
    Function to get all available packages where the current time is between the launch time and expiration time.

    Returns:
    - A list of dictionaries, each containing details of an available package.

    Raises:
    - DatabaseError: If there is any database-related error during the query.
    """
    try:
        # 获取当前时间
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 查询当前时间在套餐的上架时间和下架时间之间的所有套餐
        cursor.execute("""
            SELECT PackageID, PackageName, Price, LaunchTime, ExpirationTime, 
                   ContractDuration, VoiceQuota, OverQuotaStandard
            FROM Packages
            WHERE LaunchTime <= %s AND (ExpirationTime IS NULL OR ExpirationTime >= %s)
        """, (current_time, current_time))

        available_packages = cursor.fetchall()

        # 如果没有可用的套餐
        if not available_packages:
            print("No available packages found.")
            return []

        # 将查询到的套餐信息组织为字典并返回
        package_list = []
        for package in available_packages:
            package_data = {
                "PackageID": package[0],
                "PackageName": package[1],
                "PackagePrice": package[2],
                "LaunchTime": package[3],
                "ExpirationTime": package[4],
                "ContractDuration": package[5],
                "VoiceQuota": package[6],
                "OverQuotaStandard": package[7]
            }
            package_list.append(package_data)

        return package_list

    except mysql.connector.Error as err:
        # 捕获数据库错误并抛出异常
        raise DatabaseError(f"Error while fetching available packages: {err}")
    
try:
    available_packages = get_available_packages()
    for package in available_packages:
        print(package)
except DatabaseError as e:
    print(f"Database error: {e}")
  
def change_phone_package(phone_number, new_package_id):
    """
    Function to change the package of a given phone number and insert a new record in the PhoneAccount_Services table.

    Parameters:
    - phone_number: The phone number whose package needs to be changed.
    - new_package_id: The ID of the new package to be applied to the phone number.

    Raises:
    - DatabaseError: If there is any database-related error during the query or insertion.
    """
    try:
        # 获取当前时间
        current_time = datetime.now()

        # 计算下个月的第一天作为生效时间
        next_month = current_time.replace(day=1) + timedelta(days=32)
        activation_time = next_month.replace(day=1)

        # 查询用户是否已经存在该手机号
        cursor.execute("SELECT PhoneNumber FROM PhoneAccounts WHERE PhoneNumber = %s", (phone_number,))
        phone_account = cursor.fetchone()

        if phone_account is None:
            raise ValueError(f"Error: Phone number {phone_number} not found.")

        # 查询套餐信息
        cursor.execute("SELECT PackageID FROM Packages WHERE PackageID = %s", (new_package_id,))
        package_info = cursor.fetchone()

        if package_info is None:
            raise ValueError(f"Error: Package with ID {new_package_id} not found.")

        # 获取当前时间作为购买时间
        purchase_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

        # 插入到PhoneAccount_Services表
        cursor.execute("""
            INSERT INTO PhoneAccount_Services (PhoneServiceID, PurchaseTime, ActivationTime, PhoneNumber, ServiceID)
            VALUES (NULL, %s, %s, %s, %s)
        """, (purchase_time, activation_time, phone_number, new_package_id))

        # 提交事务
        db.commit()

        print(f"Package {new_package_id} successfully applied to phone number {phone_number}.")
    
    except ValueError as e:
        # 捕获无效手机号或套餐ID
        print(f"Error: {e}")
    except mysql.connector.Error as err:
        # 捕获数据库错误
        db.rollback()
        raise DatabaseError(f"Error while changing package for phone number {phone_number}: {err}")

try:
    change_phone_package('13812345678', 2)
except DatabaseError as e:
    print(f"Database error: {e}")
