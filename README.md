# Telecharge - 手机号管理与服务平台

Telecharge 是一个用于管理和提供手机服务的平台，旨在简化电话账户、套餐、业务和支付记录的管理。该平台支持对手机号进行多种操作，包括套餐变更、通话记录、缴费记录、服务订购等。它集成了完整的用户管理、套餐管理、业务管理和支付管理功能，并提供强大的数据库安全性和完整性保障。

## 功能概述

- **用户管理**：支持用户信息的查询、注册以及修改用户类型（普通用户、客服、超级管理员等）。
- **套餐管理**：可以查询、上架、下架套餐，支持根据当前时间显示可用的套餐。
- **服务管理**：支持查询所有可以订阅的业务服务，并根据业务ID进行订购操作。
- **通话记录与交易记录管理**：管理通话记录、缴费记录以及交易记录。
- **账户余额与停机管理**：可以查看手机号的账户余额、停机状态，并进行余额的扣除和更新。
- **数据安全与完整性保障**：数据加密、权限控制、SQL注入防护等安全措施保障数据的安全和完整性。

## 安装与运行

### 前提条件

1. Python 3.11.9 版本
2. MySQL 数据库（或兼容数据库）

### 安装步骤

1. 克隆本项目到本地：

   ```bash
   git clone https://github.com/Jackie-Li-0228/SQL-telecharge-system.git
   cd telecharge
    ```

2. 安装依赖：

   ```bash
   pip install mysql-connector-python==8.4.0 pymysql==1.1.1 pyqt6==6.4.2 qt6-tools==6.4.3.1.3
    ```

3. 配置数据库连接：

    在项目的 src.py 中设置数据库连接配置：

    ```python
    # 请修改此部分为您的数据库连接信息
    if not self.db:
        self.db = pymysql.connect(
            host='localhost',
            user='root',
            password='123123', 
            database='telecharge',
            autocommit=True
        )
        self.cursor = self.db.cursor()
    ```

4. 初始化数据库：

    ```bash
    mysql -u root -p < Create_Database.sql
    ```

5. 运行UI

    python main_page.py

## 项目地址
https://github.com/Jackie-Li-0228/SQL-telecharge-system.git

