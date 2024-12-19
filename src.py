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

def create_new_phone_account(phone_number, name, id_card_number, password, package_id=None):
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
    default_package_id = "T1"

    # 如果没有提供套餐ID，使用默认套餐ID
    if package_id is None:
        package_id = default_package_id
    
    # 查询用户的用户类型（UserTypeID）
    cursor.execute("SELECT UserTypeID FROM Users WHERE IDCardNumber = %s", (id_card_number,))
    user_type_result = cursor.fetchone()

    # 检查目标手机号有没有注册过
    cursor.execute("SELECT PhoneNumber FROM PhoneAccounts WHERE PhoneNumber = %s", (phone_number,))
    phone_account = cursor.fetchone()
    if phone_account is not None:
        raise DatabaseError(f"Phone number {phone_number} already exists.")
    
    cursor.execute("SELECT Name FROM Users WHERE IDCardNumber = %s", (id_card_number,))
    user_name = cursor.fetchone()
    print(user_name)
    if user_name[0]!=name:
        raise InformationNotMatchError(f"User name {name} does not match the ID card number {id_card_number}.")

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
# try:
#     create_new_phone_account("13812345678","张三", "123456789012345678", "securepassword123")
# except UserNotFoundError as e:
#     print(f"User not found: {e}")
# except DatabaseError as e:
#     print(f"Database error: {e}")
# except InformationNotMatchError as e:
#     print(f"Information not match: {e}")

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
    if amount <= 0:
        # 充值额度不能为负数
        raise ValueError("Payment amount must be greater than zero.")

    # 获取当前时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 检查手机号是否存在
    cursor.execute("SELECT Balance FROM PhoneAccounts WHERE PhoneNumber = %s", (phone_number,))
    account = cursor.fetchone()

    if account is None:
        # 抛出手机号未找到异常
        raise PhoneNumberNotFoundError(f"Phone number {phone_number} not found.")

    # 更新余额
    new_balance = account[0] + Decimal("{:.2f}".format(amount))
    
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
# try:
#     make_payment("13812345678", 50.00, "credit card")
# except PhoneNumberNotFoundError as e:
#     print(f"Error: {e}")
# except PaymentProcessingError as e:
#     print(f"Error: {e}")
# except ValueError as e:
#     print(f"Error: {e}")


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
# try:
#     user_info = get_user_info_by_phone("13812345678")
#     print(user_info)
# except PhoneNumberNotFoundError as e:
#     print(f"Error: {e}")

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
# try:
#     register_user("123456789012345678", "张三", 28, "M", "普通用户")
# except UserTypeNotFoundError as e:
#     print(f"Error: {e}")
# except DatabaseError as e:
#     print(f"Database error: {e}")

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

# try:
#     package_info = get_package_details("13812345678")
#     print(package_info)
# except PhoneNumberNotFoundError as e:
#     print(f"Error: {e}")
# except DatabaseError as e:
#     print(f"Database error: {e}")

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
    
# try:
#     available_packages = get_available_packages()
#     for package in available_packages:
#         print(package)
# except DatabaseError as e:
#     print(f"Database error: {e}")
  
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

# try:
#     change_phone_package('13812345678', 'T1')
# except DatabaseError as e:
#     print(f"Database error: {e}")

def change_package_for_all(phone_number):
    try:
        # 获取今天的日期，判断是否是每月的第一天
        current_date = datetime.now()
        if current_date.day != 1:
            raise InvalidDateError(message="You can only refresh the package on the first day of each month.")

        # 查询手机号对应的用户类型ID
        cursor.execute("""
            SELECT UserTypeID FROM PhoneAccounts WHERE PhoneNumber = %s
        """, (phone_number,))
        result = cursor.fetchone()

        if result is None:
            raise PhoneNumberNotFoundError(message=f"Phone number {phone_number} not found in the system.")

        user_type_id = result[0]

        # 如果用户不是管理员
        if user_type_id != 3:  # 假设3代表管理员
            raise UserNotAdminError(message=f"The user associated with phone number {phone_number} is not an admin.")

        # 获取上个月的信息
        last_month = (current_date.month - 1) if current_date.month > 1 else 12
        last_month_start = datetime(current_date.year, last_month, 1)

        # 查询电话账户-服务表中的上个月套餐服务信息
        cursor.execute("""
            SELECT PhoneNumber, ServiceID, ActivationTime
            FROM PhoneAccount_Services
            WHERE ServiceID LIKE 'T%' AND ActivationTime >= %s AND ActivationTime < %s
        """, (last_month_start, current_date))

        services = cursor.fetchall()

        # 如果没有找到上个月的套餐记录
        if not services:
            raise NoLastMonthPackagesError(message="No packages were found from the last month.")

        # 使用字典保存每个手机号的最新套餐信息
        package_updates = {}

        # 遍历服务信息，找到每个手机号对应的最后一条套餐
        for service in services:
            phone_number = service[0]
            if service[2] == datetime(current_date.year, current_date.month, 1):
                # 获取套餐ID
                new_package_id = service[1]
                
                # 保证只保存每个手机号的最新套餐
                package_updates[phone_number] = (new_package_id, current_date)

        # 如果没有找到有效的套餐
        if not package_updates:
            raise NoValidPackageFoundError(message="No valid packages found for updating any phone account.")

        # 查询套餐的详细信息（包括合约期和语音额度）
        cursor.execute("""
            SELECT PackageID, ContractDuration, VoiceQuota
            FROM Packages
            WHERE PackageID IN (%s)
        """, (",".join([package_updates[phone_number][0] for phone_number in package_updates]),))

        packages = cursor.fetchall()
        package_info_map = {pkg[0]: (pkg[1], pkg[2]) for pkg in packages}

        # 更新所有手机号的套餐信息
        for phone_number, (new_package_id, package_start_time) in package_updates.items():
            # 获取对应套餐的合约期和语音额度
            contract_duration, voice_quota = package_info_map.get(new_package_id, (None, None))

            if contract_duration is None or voice_quota is None:
                raise NoValidPackageFoundError(message=f"Package {new_package_id} is invalid or missing required details.")

            # 计算套餐结束时间
            package_end_time = package_start_time + timedelta(days=30 * contract_duration)  # 合约期按月计算

            # 更新套餐信息
            cursor.execute("""
                UPDATE PhoneAccounts
                SET PackageID = %s, PackageStartTime = %s, PackageEndTime = %s, VoiceBalance = %s
                WHERE PhoneNumber = %s
            """, (new_package_id, package_start_time, package_end_time, voice_quota, phone_number))

        # 提交所有更新事务
        db.commit()
        print(f"Successfully updated {len(package_updates)} phone accounts to their new packages.")

    except (PhoneNumberNotFoundError, UserNotAdminError, InvalidDateError, NoLastMonthPackagesError, NoValidPackageFoundError) as e:
        print(f"Error occurred: {e}")
        db.rollback()

# try:
#     change_package_for_all("13812345678")
# except (PhoneNumberNotFoundError, UserNotAdminError, InvalidDateError, NoLastMonthPackagesError, NoValidPackageFoundError) as e:
#     print(f"Error occurred: {e}")

def record_call(caller, receiver, call_duration_minutes):
    '''
        给定主叫号码、被叫号码和通话时长，记录通话记录到数据库中。
    '''
    try:
        # 检查号码是否有效
        cursor.execute("SELECT 1 FROM PhoneAccounts WHERE PhoneNumber = %s", (caller,))
        if cursor.fetchone() is None:
            raise PhoneNumberNotFoundError(message=f"Caller phone number {caller} not found.")

        cursor.execute("SELECT 1 FROM PhoneAccounts WHERE PhoneNumber = %s", (receiver,))
        if cursor.fetchone() is None:
            raise PhoneNumberNotFoundError(message=f"Receiver phone number {receiver} not found.")

        # 获取当前时间作为通话时间
        current_time = datetime.now()

        # 插入通话记录到数据库
        cursor.execute("""
            INSERT INTO CallRecords (Caller, CallTime, Receiver, CallDuration)
            VALUES (%s, %s, %s, %s)
        """, (caller, current_time, receiver, call_duration_minutes))

        # 提交事务
        db.commit()
        print(f"Call from {caller} to {receiver} recorded successfully.")
    
    except PhoneNumberNotFoundError as e:
        print(f"Error: {e}")
        db.rollback()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        db.rollback()

# 函数使用示例
# caller = "13800000001"
# receiver = "13800000002"
# call_duration_minutes = 5  # 通话时长为5分钟

# try:
#     record_call(caller, receiver, call_duration_minutes)
# except Exception as e:
#     print(f"Error occurred: {e}")

def add_package_for_admin(phone_number,package_id, package_name, price, contract_duration, voice_quota, over_quota_standard, expiration_time=None, launch_time=None):
    """
    向套餐表中插入一条新套餐记录
    
    :param phone_number: 手机号，用来确认是否是管理员的操作
    :param package_id: 套餐ID
    :param package_name: 套餐名称
    :param price: 套餐价格
    :param contract_duration: 合约期（以月为单位）
    :param voice_quota: 语音额度
    :param over_quota_standard: 超套标准
    :param expiration_time: 下架时间（可选，默认为NULL）
    :param launch_time: 上架时间（可选，默认为当前时间）
    """
    # 确认手机号是否是管理员
    cursor.execute("""SELECT UserTypeID FROM PhoneAccounts WHERE PhoneNumber = %s""", (phone_number,))
    user_type_id = cursor.fetchone()[0]
    if user_type_id != 3:
        raise UserNotAdminError(f"Phone number {phone_number} does not have admin privileges.")

    if launch_time is None:
        launch_time = datetime.now()

    try:
        # 插入套餐数据
        cursor.execute("""
            INSERT INTO Packages (PackageID, PackageName, Price, LaunchTime, ExpirationTime, ContractDuration, VoiceQuota, OverQuotaStandard)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (package_id, package_name, price, launch_time, expiration_time, contract_duration, voice_quota, over_quota_standard))

        # 提交事务
        db.commit()
        print(f"Package '{package_name}' with ID {package_id} added successfully.")
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()

# 函数使用示例
# phone_number = "114514"  # 管理员手机号
# package_id = "T2"
# package_name = "超值套餐"
# price = 19.99
# contract_duration = 12  # 合约期为12个月
# voice_quota = 500.00  # 语音额度500分钟
# over_quota_standard = 0.15  # 超套标准0.15元/分钟
# 
# try:
#     add_package_for_admin(phone_number,package_id, package_name, price, contract_duration, voice_quota, over_quota_standard)
# except Exception as e:
#     print(f"An error occurred: {e}")

def remove_package_for_admin(phone_number, package_id):
    """
    下架指定套餐：如果手机号对应用户是管理员，则将套餐失效时间设置为当前时间
    
    :param phone_number: 用户手机号
    :param package_id: 套餐ID
    """
    try:
        # 查询该手机号对应的用户的 UserTypeID
        cursor.execute("""
            SELECT ut.UserTypeID 
            FROM PhoneAccounts pa
            JOIN UserTypes ut ON pa.UserTypeID = ut.UserTypeID
            WHERE pa.PhoneNumber = %s
        """, (phone_number,))
        
        result = cursor.fetchone()
        
        if result is None:
            raise PhoneNumberNotFoundError(f"Phone number {phone_number} not found.")
        
        user_type_id = result[0]
        
        # 检查用户是否为管理员（假设管理员的 UserTypeID 是 3）
        if user_type_id != 3:
            raise UserNotAdminError(f"Phone number {phone_number} does not have admin privileges.")
        
        # 如果是管理员，更新套餐的失效时间为当前时间
        current_time = datetime.now()

        # 更新套餐表中的 ExpirationTime
        cursor.execute("""
            UPDATE Packages
            SET ExpirationTime = %s
            WHERE PackageID = %s
            AND ExpirationTime IS NULL
        """, (current_time, package_id))
        
        # 提交事务
        db.commit()
        print(f"Package {package_id} has been successfully removed (expired) at {current_time}.")
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        db.rollback()
    
    except UserNotAdminError as e:
        print(f"Error: {e}")
    
    except PhoneNumberNotFoundError as e:
        print(f"Error: {e}")

# 示例：下架某个套餐
# phone_number = "13812345678"  # 管理员手机号
# package_id = "T2"  # 套餐ID

# try:
#     remove_package_for_admin(phone_number, package_id)
# except Exception as e:
#     print(f"An error occurred: {e}")

def get_call_records_by_phone(phone_number):
    """
    获取与手机号相关的所有通话记录，包括呼出和被呼出的记录
    
    :param phone_number: 用户手机号
    :return: 通话记录列表
    """
    try:
        # 查询与该手机号相关的所有通话记录
        cursor.execute("""
            SELECT CallID, CallTime, CallDuration, Caller, Receiver
            FROM CallRecords
            WHERE Caller = %s OR Receiver = %s
            ORDER BY CallTime DESC
        """, (phone_number, phone_number))
        
        # 获取所有结果
        call_records = cursor.fetchall()
        
        if not call_records:
            raise PhoneNumberNotFoundError(f"No call records found for phone number {phone_number}.")
        
        # 格式化通话记录并返回
        records = []
        for record in call_records:
            call_id, call_time, call_duration, caller, receiver = record
            records.append({
                "CallID": call_id,
                "CallTime": call_time,
                "CallDuration": call_duration,
                "Caller": caller,
                "Receiver": receiver
            })
        
        return records
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except PhoneNumberNotFoundError as e:
        print(f"Error: {e}")

# 示例：获取某个手机号的所有通话记录
# phone_number = "13800000001"  # 输入手机号

# try:
#     call_records = get_call_records_by_phone(phone_number)
    
#     # 输出通话记录
#     for record in call_records:
#         print(f"CallID: {record['CallID']}, Time: {record['CallTime']}, Duration: {record['CallDuration']}s, Caller: {record['Caller']}, Receiver: {record['Receiver']}")
# except Exception as e:
#     print(f"An error occurred: {e}")

def get_payment_records_by_phone(phone_number):
    """
    获取与手机号相关的所有缴费记录
    
    :param phone_number: 用户手机号
    :return: 缴费记录列表
    """
    try:
        # 查询与该手机号相关的所有缴费记录
        cursor.execute("""
            SELECT PaymentID, PaymentTime, Amount, PaymentMethod, PhoneNumber
            FROM PaymentRecords
            WHERE PhoneNumber = %s
            ORDER BY PaymentTime DESC
        """, (phone_number,))
        
        # 获取所有结果
        payment_records = cursor.fetchall()
        
        if not payment_records:
            raise PhoneNumberNotFoundError(f"No payment records found for phone number {phone_number}.")
        
        # 格式化缴费记录并返回
        records = []
        for record in payment_records:
            payment_id, payment_time, amount, payment_method, phone_number = record
            records.append({
                "PaymentID": payment_id,
                "PaymentTime": payment_time,
                "Amount": amount,
                "PaymentMethod": payment_method,
                "PhoneNumber": phone_number
            })
        
        return records
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except PhoneNumberNotFoundError as e:
        print(f"Error: {e}")
        return []

# 示例：获取某个手机号的所有缴费记录
# phone_number = "13412345678"  # 输入手机号

# try:
#     payment_records = get_payment_records_by_phone(phone_number)
    
#     # 输出缴费记录
#     for record in payment_records:
#         print(f"PaymentID: {record['PaymentID']}, Time: {record['PaymentTime']}, Amount: {record['Amount']}€, Method: {record['PaymentMethod']}, PhoneNumber: {record['PhoneNumber']}")
# except Exception as e:
#     print(f"An error occurred: {e}")

def get_transaction_records_by_phone(phone_number):
    """
    获取与手机号相关的所有交易记录
    
    :param phone_number: 用户手机号
    :return: 交易记录列表
    """
    try:
        # 查询与该手机号相关的所有交易记录
        cursor.execute("""
            SELECT TransactionID, TransactionTime, PurchasedItem, Amount, PhoneNumber
            FROM TransactionRecords
            WHERE PhoneNumber = %s
            ORDER BY TransactionTime DESC
        """, (phone_number,))
        
        # 获取所有结果
        transaction_records = cursor.fetchall()
        
        if not transaction_records:
            raise PhoneNumberNotFoundError(f"No transaction records found for phone number {phone_number}.")
        
        # 格式化交易记录并返回
        records = []
        for record in transaction_records:
            transaction_id, transaction_time, purchased_item, amount, phone_number = record
            records.append({
                "TransactionID": transaction_id,
                "TransactionTime": transaction_time,
                "PurchasedItem": purchased_item,
                "Amount": amount,
                "PhoneNumber": phone_number
            })
        
        return records
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except PhoneNumberNotFoundError as e:
        print(f"Error: {e}")
        return []

# 示例：获取某个手机号的所有交易记录
# phone_number = "13812345679"  # 输入手机号

# try:
#     transaction_records = get_transaction_records_by_phone(phone_number)
    
#     # 输出交易记录
#     for record in transaction_records:
#         print(f"TransactionID: {record['TransactionID']}, Time: {record['TransactionTime']}, Item: {record['PurchasedItem']}, Amount: {record['Amount']}€, PhoneNumber: {record['PhoneNumber']}")
# except Exception as e:
#     print(f"An error occurred: {e}")

def get_services_by_phone(phone_number):
    """
    获取与手机号相关的所有手机号-服务表记录
    
    :param phone_number: 用户手机号
    :return: 服务记录列表
    """
    try:
        # 查询与该手机号相关的所有手机号-服务表记录
        cursor.execute("""
            SELECT PhoneServiceID, PurchaseTime, ActivationTime, PhoneNumber, ServiceID
            FROM PhoneAccount_Services
            WHERE PhoneNumber = %s
            ORDER BY PurchaseTime DESC
        """, (phone_number,))
        
        # 获取所有结果
        service_records = cursor.fetchall()
        
        if not service_records:
            raise PhoneNumberNotFoundError(f"No service records found for phone number {phone_number}.")
        
        # 格式化服务记录并返回
        records = []
        for record in service_records:
            phone_service_id, purchase_time, activation_time, phone_number, service_id = record
            records.append({
                "PhoneServiceID": phone_service_id,
                "PurchaseTime": purchase_time,
                "ActivationTime": activation_time,
                "PhoneNumber": phone_number,
                "ServiceID": service_id
            })
        
        return records
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except PhoneNumberNotFoundError as e:
        print(f"Error: {e}")
        return []

# 示例：获取某个手机号的所有手机号-服务表记录
# phone_number = "13812345679"  # 输入手机号

# try:
#     service_records = get_services_by_phone(phone_number)
    
#     # 输出服务记录
#     for record in service_records:
#         print(f"PhoneServiceID: {record['PhoneServiceID']}, PurchaseTime: {record['PurchaseTime']}, ActivationTime: {record['ActivationTime']}, ServiceID: {record['ServiceID']}")
# except Exception as e:
#     print(f"An error occurred: {e}")

def add_service_for_admin(phone_number, service_id, service_name, price, quota, activation_method_id):
    """
    上架业务的函数
    
    :param phone_number: 用户手机号，用于检查是否为管理员
    :param service_id: 业务ID
    :param service_name: 业务名称
    :param price: 业务价格
    :param quota: 业务额度
    :param activation_method_id: 激活方式ID（1表示立即生效，2表示次月生效）
    :return: None
    """
    try:
        # 检查手机号是否为管理员
        cursor.execute("""
            SELECT UserTypeID
            FROM PhoneAccounts
            WHERE PhoneNumber = %s
        """, (phone_number,))
        
        result = cursor.fetchone()
        if not result or result[0] != 3:  # 3 代表管理员
            raise UserNotAdminError(f"Phone number {phone_number} is not an admin.")

        # 获取当前时间并设置激活时间
        current_time = datetime.now()
        if activation_method_id == 1:
            activation_time = current_time  # 立即生效
        elif activation_method_id == 2:
            # 次月生效
            activation_time = datetime(current_time.year, current_time.month + 1, 1)
        else:
            raise ValueError("Invalid activation method ID. Must be 1 or 2.")

        # 插入新的业务记录
        cursor.execute("""
            INSERT INTO Services (ServiceID, Name, Price, Quota, ActivationMethodID)
            VALUES (%s, %s, %s, %s, %s)
        """, (service_id, service_name, price, quota, activation_method_id))

        # 提交事务
        db.commit()
        print(f"Service {service_name} with ID {service_id} added successfully.")
    
    except UserNotAdminError as e:
        print(f"Error: {e}")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        db.rollback()
    except ValueError as e:
        print(f"Error: {e}")

# 示例：上架业务
# phone_number = "13834567890"  # 管理员手机号
# service_id = "S1"  # 业务ID
# service_name = "高级语音包"  # 业务名称
# price = 99.99  # 业务价格
# quota = 100  # 业务额度
# activation_method_id = 1  # 立即生效

# try:
#     add_service_for_admin(phone_number, service_id, service_name, price, quota, activation_method_id)
# except Exception as e:
#     print(f"An error occurred: {e}")

