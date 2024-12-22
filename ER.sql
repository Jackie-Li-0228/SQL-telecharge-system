-- 用户类型表
CREATE TABLE `UserTypes` (
    `UserTypeID` INT AUTO_INCREMENT COMMENT '用户类型',
    `UserTypeName` VARCHAR(50) NOT NULL COMMENT '用户类型名称',
    PRIMARY KEY (`UserTypeID`)
) COMMENT = '用户类型';

-- 用户表
CREATE TABLE `Users` (
    `IDCardNumber` CHAR(18) COMMENT '用户身份证号(主键)',
    `Name` VARCHAR(100) NOT NULL COMMENT '用户姓名',
    `Age` INT NOT NULL COMMENT '用户年龄',
    `Gender` CHAR(1) CHECK (`Gender` IN ('M', 'F')) COMMENT '用户性别',
    `UserTypeID` INT COMMENT '用户类型',
    PRIMARY KEY (`IDCardNumber`),
    FOREIGN KEY (`UserTypeID`) REFERENCES `UserTypes`(`UserTypeID`)
) COMMENT = '用户';

-- 套餐表
CREATE TABLE `Packages` (
    `PackageID` VARCHAR(5) COMMENT '套餐ID作为主键',
    `PackageName` VARCHAR(100) NOT NULL COMMENT '套餐名称',
    `Price` DECIMAL(10, 2) NOT NULL COMMENT '套餐价格',
    `LaunchTime` DATETIME NOT NULL COMMENT '上架时间',
    `ExpirationTime` DATETIME COMMENT '下架时间',
    `ContractDuration` INT COMMENT '合约期（单位：月）',
    `VoiceQuota` DECIMAL(10, 2) COMMENT '语音额度',
    `OverQuotaStandard` DECIMAL(10, 2) COMMENT '超套标准',
    PRIMARY KEY (`PackageID`)
) COMMENT = '套餐';

-- 电话号码表（已修改，增加密码和用户类型字段）
CREATE TABLE `PhoneAccounts` (
    `PhoneNumber` CHAR(11) COMMENT '电话号码作为主键',
    `Balance` DECIMAL(10, 2) NOT NULL COMMENT '账户余额',
    `IsSuspended` BOOLEAN NOT NULL COMMENT '是否停机',
    `VoiceBalance` DECIMAL(10, 2) NOT NULL COMMENT '语音余额',
    `PackageStartTime` DATETIME NOT NULL COMMENT '套餐生效时间',
    `PackageEndTime` DATETIME COMMENT '套餐失效时间',
    `IDCardNumber` CHAR(18) COMMENT '外键，关联到用户表的身份证号',
    `PackageID` VARCHAR(5) COMMENT '外键，关联到套餐表的套餐ID',
    `Password` VARCHAR(255) NOT NULL COMMENT '密码字段',
    `UserTypeID` INT COMMENT '用户类型ID，外键关联到UserTypes表',
    PRIMARY KEY (`PhoneNumber`),
    FOREIGN KEY (`PackageID`) REFERENCES `Packages`(`PackageID`),
    FOREIGN KEY (`UserTypeID`) REFERENCES `UserTypes`(`UserTypeID`)
) COMMENT = '电话号码';

-- 通话记录表
CREATE TABLE `CallRecords` (
    `CallID` INT AUTO_INCREMENT COMMENT '通话ID作为主键',
    `Caller` CHAR(11) NOT NULL COMMENT '呼出方电话号码',
    `CallTime` DATETIME NOT NULL COMMENT '通话时间',
    `Receiver` CHAR(11) NOT NULL COMMENT '接收方电话号码',
    `CallDuration` INT NOT NULL COMMENT '通话时长（单位：分钟）',
    PRIMARY KEY (`CallID`),
    FOREIGN KEY (`Caller`) REFERENCES `PhoneAccounts`(`PhoneNumber`),
    FOREIGN KEY (`Receiver`) REFERENCES `PhoneAccounts`(`PhoneNumber`)
) COMMENT = '通话记录';

-- 缴费记录表
CREATE TABLE `PaymentRecords` (
    `PaymentID` INT AUTO_INCREMENT COMMENT '缴费ID作为主键',
    `PaymentTime` DATETIME NOT NULL COMMENT '缴费时间',
    `Amount` DECIMAL(10, 2) NOT NULL COMMENT '缴费金额',
    `PaymentMethod` VARCHAR(50) NOT NULL COMMENT '支付方式',
    `PhoneNumber` CHAR(11) COMMENT '外键，关联到电话账户表的电话号码',
    PRIMARY KEY (`PaymentID`),
    FOREIGN KEY (`PhoneNumber`) REFERENCES `PhoneAccounts`(`PhoneNumber`)
) COMMENT = '缴费记录';

-- 生效方式表
CREATE TABLE `ActivationMethods` (
    `ActivationMethodID` INT AUTO_INCREMENT COMMENT '生效方式ID',
    `ActivationMethodName` VARCHAR(50) NOT NULL COMMENT '生效方式名称',
    PRIMARY KEY (`ActivationMethodID`)
) COMMENT = '生效方式';

-- 业务表
CREATE TABLE `Services` (
    `ServiceID` VARCHAR(5) COMMENT '业务ID作为主键',
    `Name` VARCHAR(100) NOT NULL COMMENT '业务名称',
    `Price` DECIMAL(10, 2) NOT NULL COMMENT '业务价格',
    `Quota` DECIMAL(10, 2) NOT NULL COMMENT '业务额度',
    `ActivationMethodID` INT NOT NULL COMMENT '生效方式',
    PRIMARY KEY (`ServiceID`),
    FOREIGN KEY (`ActivationMethodID`) REFERENCES `ActivationMethods`(`ActivationMethodID`)
) COMMENT = '业务';

-- 交易记录表
CREATE TABLE `TransactionRecords` (
    `TransactionID` INT AUTO_INCREMENT COMMENT '交易ID作为主键',
    `TransactionTime` DATETIME NOT NULL COMMENT '交易时间',
    `PurchasedItem` VARCHAR(100) NOT NULL COMMENT '购买项目',
    `Amount` DECIMAL(10, 2) NOT NULL COMMENT '交易金额',
    `PhoneNumber` CHAR(11) COMMENT '外键，关联到电话账户表的电话号码',
    PRIMARY KEY (`TransactionID`),
    FOREIGN KEY (`PhoneNumber`) REFERENCES `PhoneAccounts`(`PhoneNumber`)
) COMMENT = '交易记录';

-- 电话账户-服务表
CREATE TABLE `PhoneAccount_Services` (
    `PhoneServiceID` INT AUTO_INCREMENT COMMENT '电话-服务ID作为主键',
    `PurchaseTime` DATETIME NOT NULL COMMENT '服务购买时间',
    `ActivationTime` DATETIME NOT NULL COMMENT '服务生效时间',
    `PhoneNumber` CHAR(11) COMMENT '外键，关联到电话账户表的电话号码',
    `ServiceID` VARCHAR(5) COMMENT '外键，关联到业务表或套餐表的服务ID',
    PRIMARY KEY (`PhoneServiceID`),
    FOREIGN KEY (`PhoneNumber`) REFERENCES `PhoneAccounts`(`PhoneNumber`)
) COMMENT = '电话账户-服务';