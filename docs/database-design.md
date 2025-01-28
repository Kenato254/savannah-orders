# Database Design Documentation

This document provides an overview of the database schema for managing **users**, **customers**, **orders**, and **tokens**.

![Alt text](/docs/images/db-design.png)

---

## **1. Users Table**

**Purpose**: Stores information about the users of the system.  
**Primary Key**: `user_id`

| Column Name    | Data Type        | Constraints                                       | Description                              |
|----------------|------------------|--------------------------------------------------|------------------------------------------|
| `user_id`      | `int`            | `NOT NULL`, `PRIMARY KEY`                        | Unique identifier for each user.         |
| `email`        | `varchar(100)`   | `NOT NULL`, `INDEX`                              | Email address of the user.               |
| `username`     | `varchar(50)`    | `NOT NULL`                                       | Username chosen by the user.             |
| `password`     | `varchar(255)`   | `NOT NULL`                                       | Encrypted password for the user.         |
| `role`         | `varchar(50)`    | `NOT NULL`, `DEFAULT 'Customer'`                | Role of the user (e.g., Customer).       |
| `created_at`   | `datetime`       | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`          | Timestamp when the user was created.     |
| `updated_at`   | `datetime`       | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | Timestamp when the user was last updated.|

---

## **2. Tokens Table**

**Purpose**: Manages authentication tokens for users.  
**Primary Key**: `token_id`  
**Foreign Key**: `user_id` → `Users(user_id)`

| Column Name      | Data Type      | Constraints                                    | Description                                    |
|------------------|----------------|-----------------------------------------------|------------------------------------------------|
| `token_id`       | `int`          | `NOT NULL`, `PRIMARY KEY`                     | Unique identifier for each token.             |
| `refresh_token`  | `varchar(255)` | `NOT NULL`                                    | Refresh token value for session management.   |
| `user_id`        | `int`          | `NOT NULL`, `INDEX`, `REFERENCES Users(user_id)` | Links the token to a specific user.           |
| `is_revoked`     | `bool`         | `NOT NULL`, `DEFAULT FALSE`                   | Indicates if the token has been revoked.      |
| `expires_at`     | `datetime`     | `NOT NULL`                                    | Expiration timestamp for the token.           |

---

## **3. Customers Table**

**Purpose**: Stores customer details.  
**Primary Key**: `customer_id`  
**Foreign Key**: `user_id` → `Users(user_id)` (One-to-One relationship)

| Column Name       | Data Type      | Constraints                                   | Description                                |
|-------------------|----------------|----------------------------------------------|--------------------------------------------|
| `customer_id`     | `int`          | `NOT NULL`, `PRIMARY KEY`                    | Unique identifier for each customer.       |
| `customer_name`   | `varchar(100)` | `NOT NULL`                                   | Name of the customer.                      |
| `user_id`         | `int`          | `NOT NULL`, `INDEX`, `REFERENCES Users(user_id)` | Links the customer to a specific user.    |
| `code`            | `varchar(50)`  | `NOT NULL`, `UNIQUE`                         | Unique customer code.                      |
| `phone_number`    | `varchar(15)`  | `NOT NULL`                                   | Customer's phone number.                   |
| `created_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`      | Timestamp when the customer was created.   |
| `updated_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | Timestamp when the customer was last updated. |

---

## **4. Orders Table**

**Purpose**: Tracks orders placed by customers.  
**Primary Key**: `order_id`  
**Foreign Key**: `customer_id` → `Customers(customer_id)`

| Column Name       | Data Type      | Constraints                                    | Description                                |
|-------------------|----------------|-----------------------------------------------|--------------------------------------------|
| `order_id`        | `int`          | `NOT NULL`, `PRIMARY KEY`                     | Unique identifier for each order.          |
| `customer_id`     | `int`          | `NOT NULL`, `INDEX`, `REFERENCES Customers(customer_id)` | Links the order to a specific customer.   |
| `item`            | `varchar(100)` | `NOT NULL`                                    | Name of the item ordered.                  |
| `amount`          | `decimal(10,2)`| `NOT NULL`                                    | Total amount for the order.                |
| `created_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`       | Timestamp when the order was placed.       |
| `updated_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | Timestamp when the order was last updated. |

---

## Relationships

1. **Users → Customers**:
   Each user is associated with exactly one customer (1:1 relationship). This is enforced by making user_id in the Customers table both a foreign key and a unique constraint.

2. **Customers → Orders**:
   A customer can place multiple orders (1:N relationship).

3. **Users → Tokens**:  
   Each user can have multiple tokens for authentication purposes (1:N relationship).

---

## Notes

- The one-to-one relationship between `Users` and `Customers` ensures that each user corresponds to one customer record.
- `created_at` and `updated_at` columns in all tables ensure proper tracking of record creation and modification.
- Foreign key constraints maintain referential integrity across tables.
- Indexed columns (`user_id`, `email`, `customer_id`.) enhance query performance.

---

This schema ensures scalability, data integrity, and efficient querying for an application managing users, customers, orders, and authentication tokens.
