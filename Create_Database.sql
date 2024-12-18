-- 创建用户表
CREATE TABLE Users (
    IDCardNumber CHAR(18) PRIMARY KEY,   -- 身份证号作为主键
    Name VARCHAR(100) NOT NULL,           -- 姓名
    Age INT NOT NULL,                     -- 年龄
    Gender CHAR(1) CHECK (Gender IN ('M', 'F'))  -- 性别（M代表男性，F代表女性）
);

-- 创建套餐表
CREATE TABLE Packages (
    PackageID INT PRIMARY KEY,            -- 套餐ID作为主键
    PackageName VARCHAR(100) NOT NULL,     -- 套餐名称
    Price DECIMAL(10, 2) NOT NULL,         -- 套餐价格
    StartTime DATETIME NOT NULL,           -- 上架时间
    EndTime DATETIME,                      -- 下架时间
    ContractDuration INT,                  -- 合约期（单位：月）
    VoiceQuota DECIMAL(10, 2),             -- 语音额度
    OverQuotaStandard DECIMAL(10, 2)      -- 超套标准
);

-- 创建电话账户表
CREATE TABLE PhoneAccounts (
    PhoneNumber CHAR(11) PRIMARY KEY,      -- 电话号码作为主键
    Balance DECIMAL(10, 2) NOT NULL,       -- 账户余额
    IsSuspended BOOLEAN NOT NULL,          -- 是否停机
    VoiceBalance DECIMAL(10, 2) NOT NULL,  -- 语音余额
    PackageStartTime DATETIME NOT NULL,    -- 套餐生效时间
    PackageEndTime DATETIME,               -- 套餐失效时间
    IDCardNumber CHAR(18),                 -- 外键，关联到用户表的身份证号
    PackageID INT,                         -- 外键，关联到套餐表的套餐ID
    FOREIGN KEY (IDCardNumber) REFERENCES Users(IDCardNumber),
    FOREIGN KEY (PackageID) REFERENCES Packages(PackageID)
);

-- 创建通话记录表
CREATE TABLE CallRecords (
    CallID INT PRIMARY KEY,                -- 通话ID作为主键
    Caller CHAR(11) NOT NULL,              -- 呼出方电话号码
    CallTime DATETIME NOT NULL,            -- 通话时间
    Receiver CHAR(11) NOT NULL,            -- 接收方电话号码
    CallDuration INT NOT NULL,             -- 通话时长（单位：秒）
    FOREIGN KEY (Caller) REFERENCES PhoneAccounts(PhoneNumber),
    FOREIGN KEY (Receiver) REFERENCES PhoneAccounts(PhoneNumber)
);

-- 创建缴费记录表
CREATE TABLE PaymentRecords (
    PaymentID INT PRIMARY KEY,             -- 缴费ID作为主键
    PaymentTime DATETIME NOT NULL,         -- 缴费时间
    Amount DECIMAL(10, 2) NOT NULL,        -- 缴费金额
    PaymentMethod VARCHAR(50) NOT NULL,    -- 支付方式
    PhoneNumber CHAR(11),                  -- 外键，关联到电话账户表的电话号码
    FOREIGN KEY (PhoneNumber) REFERENCES PhoneAccounts(PhoneNumber)
);

-- 创建业务表
CREATE TABLE Services (
    ServiceID INT PRIMARY KEY,             -- 业务ID作为主键
    Name VARCHAR(100) NOT NULL,             -- 业务名称
    Price DECIMAL(10, 2) NOT NULL,         -- 业务价格
    Quota DECIMAL(10, 2) NOT NULL,         -- 业务额度
    ActivationMethod VARCHAR(50) NOT NULL  -- 生效方式
);

-- 创建交易记录表
CREATE TABLE TransactionRecords (
    TransactionID INT PRIMARY KEY,         -- 交易ID作为主键
    TransactionTime DATETIME NOT NULL,     -- 交易时间
    PurchasedItem VARCHAR(100) NOT NULL,   -- 购买项目
    Amount DECIMAL(10, 2) NOT NULL,        -- 交易金额
    PhoneNumber CHAR(11),                  -- 外键，关联到电话账户表的电话号码
    FOREIGN KEY (PhoneNumber) REFERENCES PhoneAccounts(PhoneNumber)
);

-- 创建电话账户-服务表
CREATE TABLE PhoneAccount_Services (
    PhoneServiceID INT PRIMARY KEY,        -- 电话-服务ID作为主键
    PurchaseTime DATETIME NOT NULL,        -- 服务购买时间
    ActivationTime DATETIME NOT NULL,      -- 服务生效时间
    PhoneNumber CHAR(11),                  -- 外键，关联到电话账户表的电话号码
    ServiceID INT,                         -- 外键，关联到业务表或套餐表的服务ID
    FOREIGN KEY (PhoneNumber) REFERENCES PhoneAccounts(PhoneNumber),
    FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID)
);
