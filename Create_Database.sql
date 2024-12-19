drop database if exists telecharge;
create database telecharge;
use telecharge;

-- 创建用户类型表
CREATE TABLE UserTypes (
    UserTypeID INT PRIMARY KEY AUTO_INCREMENT,  -- 用户类型ID
    UserTypeName VARCHAR(50) NOT NULL           -- 用户类型名称
);

-- 插入三种用户类型
INSERT INTO UserTypes (UserTypeName)
VALUES ('普通用户'), ('客服'), ('超级管理员');

-- 创建用户表
CREATE TABLE Users (
    IDCardNumber CHAR(18) PRIMARY KEY,    -- 用户身份证号，作为主键
    Name VARCHAR(100) NOT NULL,            -- 用户姓名
    Age INT NOT NULL,                      -- 用户年龄
    Gender CHAR(1) CHECK (Gender IN ('M', 'F')),  -- 用户性别（M代表男性，F代表女性）
    UserTypeID INT,                        -- 用户类型ID，外键引用UserTypes表
    FOREIGN KEY (UserTypeID) REFERENCES UserTypes(UserTypeID)
);

-- 插入一些示例用户数据
INSERT INTO Users (IDCardNumber, Name, Age, Gender, UserTypeID)
VALUES
    ('123456789012345678', '张三', 28, 'M', 1),  -- 普通用户
    ('234567890123456789', '李四', 34, 'F', 2),  -- 客服
    ('345678901234567890', '王五', 40, 'M', 3);  -- 超级管理员


-- 创建套餐表
CREATE TABLE Packages (
    PackageID VARCHAR(5) PRIMARY KEY,            -- 套餐ID作为主键
    PackageName VARCHAR(100) NOT NULL,     -- 套餐名称
    Price DECIMAL(10, 2) NOT NULL,         -- 套餐价格
    LaunchTime DATETIME NOT NULL,           -- 上架时间
    ExpirationTime DATETIME,                -- 下架时间
    ContractDuration INT,                  -- 合约期（单位：月）
    VoiceQuota DECIMAL(10, 2),             -- 语音额度
    OverQuotaStandard DECIMAL(10, 2)      -- 超套标准
);

-- 向套餐表中插入默认套餐数据
INSERT INTO Packages (PackageID, PackageName, Price, LaunchTime, ExpirationTime, ContractDuration, VoiceQuota, OverQuotaStandard)
VALUES 
    ("T1", '默认套餐', 8.00, '1999-01-01 00:00:00', NULL, 1, 0.00, 0.10);

-- 修改电话号码表，增加密码和用户类型字段
CREATE TABLE PhoneAccounts (
    PhoneNumber CHAR(11) PRIMARY KEY,      -- 电话号码作为主键
    Balance DECIMAL(10, 2) NOT NULL,       -- 账户余额
    IsSuspended BOOLEAN NOT NULL,          -- 是否停机
    VoiceBalance DECIMAL(10, 2) NOT NULL,  -- 语音余额
    PackageStartTime DATETIME NOT NULL,    -- 套餐生效时间
    PackageEndTime DATETIME,               -- 套餐失效时间
    IDCardNumber CHAR(18),                 -- 外键，关联到用户表的身份证号
    PackageID VARCHAR(5),                         -- 外键，关联到套餐表的套餐ID
    Password VARCHAR(255) NOT NULL,         -- 密码字段
    UserTypeID INT,                        -- 用户类型ID，外键关联到UserTypes表
    FOREIGN KEY (PackageID) REFERENCES Packages(PackageID),
    FOREIGN KEY (UserTypeID) REFERENCES UserTypes(UserTypeID)  -- 用户类型字段
);

-- 创建通话记录表
CREATE TABLE CallRecords (
    CallID INT PRIMARY KEY AUTO_INCREMENT,                -- 通话ID作为主键
    Caller CHAR(11) NOT NULL,              -- 呼出方电话号码
    CallTime DATETIME NOT NULL,            -- 通话时间
    Receiver CHAR(11) NOT NULL,            -- 接收方电话号码
    CallDuration INT NOT NULL,             -- 通话时长（单位：分钟）
    FOREIGN KEY (Caller) REFERENCES PhoneAccounts(PhoneNumber),
    FOREIGN KEY (Receiver) REFERENCES PhoneAccounts(PhoneNumber)
);

-- 创建缴费记录表
CREATE TABLE PaymentRecords (
    PaymentID INT PRIMARY KEY AUTO_INCREMENT,             -- 缴费ID作为主键
    PaymentTime DATETIME NOT NULL,         -- 缴费时间
    Amount DECIMAL(10, 2) NOT NULL,        -- 缴费金额
    PaymentMethod VARCHAR(50) NOT NULL,    -- 支付方式
    PhoneNumber CHAR(11),                  -- 外键，关联到电话账户表的电话号码
    FOREIGN KEY (PhoneNumber) REFERENCES PhoneAccounts(PhoneNumber)
);

CREATE TABLE ActivationMethods (
    ActivationMethodID INT PRIMARY KEY AUTO_INCREMENT,  -- 生效方式ID
    ActivationMethodName VARCHAR(50) NOT NULL           -- 生效方式名称
);

INSERT INTO ActivationMethods (ActivationMethodID, ActivationMethodName) VALUES (1, "立即生效"), (2, "次月生效");

-- 创建业务表
CREATE TABLE Services (
    ServiceID VARCHAR(5) PRIMARY KEY,             -- 业务ID作为主键
    Name VARCHAR(100) NOT NULL,             -- 业务名称
    Price DECIMAL(10, 2) NOT NULL,         -- 业务价格
    Quota DECIMAL(10, 2) NOT NULL,         -- 业务额度
    ActivationMethodID INT NOT NULL,  -- 生效方式
    FOREIGN KEY (ActivationMethodID) REFERENCES ActivationMethods(ActivationMethodID)
);

-- 创建交易记录表
CREATE TABLE TransactionRecords (
    TransactionID INT PRIMARY KEY AUTO_INCREMENT,         -- 交易ID作为主键
    TransactionTime DATETIME NOT NULL,     -- 交易时间
    PurchasedItem VARCHAR(100) NOT NULL,   -- 购买项目
    Amount DECIMAL(10, 2) NOT NULL,        -- 交易金额
    PhoneNumber CHAR(11),                  -- 外键，关联到电话账户表的电话号码
    FOREIGN KEY (PhoneNumber) REFERENCES PhoneAccounts(PhoneNumber)
);

-- 创建电话账户-服务表
CREATE TABLE PhoneAccount_Services (
    PhoneServiceID INT PRIMARY KEY AUTO_INCREMENT,        -- 电话-服务ID作为主键
    PurchaseTime DATETIME NOT NULL,        -- 服务购买时间
    ActivationTime DATETIME NOT NULL,      -- 服务生效时间
    PhoneNumber CHAR(11),                  -- 外键，关联到电话账户表的电话号码
    ServiceID VARCHAR(5),                         -- 外键，关联到业务表或套餐表的服务ID
    FOREIGN KEY (PhoneNumber) REFERENCES PhoneAccounts(PhoneNumber)
);
