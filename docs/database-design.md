# Database Design Documentation

This document provides an overview of the database schema for managing **customers** and **orders**.

![Entity Relationships](/docs/images/db-design.png)

---

## **1. Customers Table**

**Purpose**: Stores customer details.  
**Primary Key**: `customer_id`  

| Column Name       | Data Type      | Constraints                                   | Description                                |
|-------------------|----------------|----------------------------------------------|--------------------------------------------|
| `customer_id`     | `int`          | `NOT NULL`, `PRIMARY KEY`                    | Unique identifier for each customer.       |
| `customer_name`   | `varchar(100)` | `NOT NULL`                                   | Name of the customer.                      |
| `code`            | `varchar(50)`  | `UNIQUE`                                     | Unique customer code.                      |
| `phone_number`    | `varchar(15)`  | `NOT NULL`                                   | Customer's phone number.                   |
| `created_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`      | Timestamp when the customer was created    |
| `updated_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`, `ON UPDATE CURRENT_TIMESTAMP` | Timestamp when the customer was last updated. |

---

## **2. Orders Table**

**Purpose**: Tracks orders placed by customers.  
**Primary Key**: `order_id`  
**Foreign Key**: `customer_id` → `Customers(customer_id)`

| Column Name       | Data Type      | Constraints                                    | Description                                 |
|-------------------|----------------|-----------------------------------------------|---------------------------------------------|
| `order_id`        | `int`          | `NOT NULL`, `PRIMARY KEY`                     | Unique identifier for each order.           |
| `customer_id`     | `int`          | `NOT NULL`, `INDEX`, `REFERENCES Customers(customer_id)` | Links the order to a specific customer.    |
| `item`            | `varchar(100)` | `NOT NULL`                                    | Name of the item ordered.                   |
| `amount`          | `decimal(10,2)`| `NOT NULL`                                    | Total amount for the order.                 |
| `status`          | `varchar(20)`  | `NOT NULL`, `DEFAULT 'Active'`                | Status of the order (e.g., Active, Cancelled, Delivered). |
| `created_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`       | Timestamp when the order was placed.        |
| `updated_at`      | `datetime`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`, `ON UPDATE CURRENT_TIMESTAMP` | Timestamp when the order was placed or last updated. |

---

## Relationships

1. **Customers → Orders**:
   A customer can place multiple orders (1:N relationship).

---

## Notes

- `created_at` and `updated_at` columns in both tables now use `ON UPDATE CURRENT_TIMESTAMP` to automatically update when records are modified.
- Foreign key constraints maintain referential integrity across tables.
- Indexed columns (`customer_id` in Orders) enhance query performance.

---

This schema ensures scalability, data integrity, and efficient querying for an application managing customers and their orders.
