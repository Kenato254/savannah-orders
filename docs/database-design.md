# Database Design Documentation

This document provides an overview of the database schema for managing **customers** and **orders**.

![Alt text](/docs/images/db-design.png)

---

## **1. Customers Table**

**Purpose**: Stores customer details.  
**Primary Key**: `customer_id`  
**Foreign Key**: `user_id` → `Users(user_id)` (One-to-One relationship)

| Column Name       | Data Type      | Constraints                                   | Description                                |
|-------------------|----------------|----------------------------------------------|--------------------------------------------|
| `customer_id`     | `int`          | `NOT NULL`, `PRIMARY KEY`                    | Unique identifier for each customer.       |
| `customer_name`   | `varchar(100)` | `NOT NULL`                                   | Name of the customer.                      |
| `user_id`         | `int`          | `NOT NULL`, `REFERENCES Users(user_id)`      | Links the customer to a specific user.     |
| `code`            | `varchar(50)`  | `NOT NULL`, `UNIQUE`                         | Unique customer code.                      |
| `phone_number`    | `varchar(15)`  | `NOT NULL`                                   | Customer's phone number.                   |
| `created_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`, `ON UPDATE CURRENT_TIMESTAMP` | Timestamp when the customer was created or last updated. |
| `updated_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`, `ON UPDATE CURRENT_TIMESTAMP` | Timestamp when the customer was last updated. |

---

## **2. Orders Table**

**Purpose**: Tracks orders placed by customers.  
**Primary Key**: `order_id`  
**Foreign Key**: `customer_id` → `Customers(customer_id)`

| Column Name       | Data Type      | Constraints                                    | Description                                |
|-------------------|----------------|-----------------------------------------------|--------------------------------------------|
| `order_id`        | `int`          | `NOT NULL`, `PRIMARY KEY`                     | Unique identifier for each order.          |
| `customer_id`     | `int`          | `NOT NULL`, `INDEX`, `REFERENCES Customers(customer_id)` | Links the order to a specific customer.   |
| `item`            | `varchar(100)` | `NOT NULL`                                    | Name of the item ordered.                  |
| `amount`          | `decimal(10,2)`| `NOT NULL`                                    | Total amount for the order.                |
| `created_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`, `ON UPDATE CURRENT_TIMESTAMP` | Timestamp when the order was placed or last updated. |
| `updated_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`, `ON UPDATE CURRENT_TIMESTAMP` | Timestamp when the order was last updated. |

---

## Relationships

1. **Users → Customers**:
   Each user is associated with exactly one customer (1:1 relationship). This is enforced by making `user_id` in the `Customers` table a foreign key referencing `Users(user_id)`.

2. **Customers → Orders**:
   A customer can place multiple orders (1:N relationship).

---

## Notes

- The one-to-one relationship between `Users` and `Customers` ensures that each user corresponds to one customer record.
- `created_at` and `updated_at` columns in both tables now use `ON UPDATE CURRENT_TIMESTAMP` to automatically update when records are modified.
- Foreign key constraints maintain referential integrity across tables.
- Indexed columns (`customer_id` in Orders) enhance query performance.

---

This schema ensures scalability, data integrity, and efficient querying for an application managing customers and their orders.