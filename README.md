Inventory Management System
A Django-based Inventory Management System designed for internal use in industries to manage inventory items, stock transactions, locations, and equipment.
The system supports multiple roles with role-based access control, detailed dashboards, and modern UI design.

Features
User Roles & Permissions
Inventory Manager / Admin: Full access to create, update, delete, and view inventory items, locations, stock transactions, and equipment
Technician: View-only access to inventory items and equipment.

Inventory Management

Add, edit, delete, and view inventory items.
Categorize items by Category, Brand, and Location.
Track quantity, minimum stock levels, and SKU.
Visualize stock levels with progress bars and status badges:
In Stock
Low Stock
Out of Stock

Locations

Manage warehouse locations where items are stored.
Assign items to specific locations.
Stock Transactions
Track item movements with stock in/out transactions.
Update quantity automatically after transactions.

Equipment Management

Add, edit, delete, and view equipment.
Track equipment assigned to locations or projects.

Dashboard & Alerts

Modern dashboard with:
Total items
In-stock items
Low-stock items
Out-of-stock items

Alert cards for low-stock and out-of-stock items with modals to view all affected items.

Filters & Search

Search items by name.
Filter by category, brand, and stock status.

Modern UI
Bootstrap 5 responsive design.
Hover effects, badges, cards, and progress bars for a clean, user-friendly interface.

Tech Stack

| Layer          | Technology                         |
| -------------- | ---------------------------------- |
| Backend        | Django 4.2, Python 3.11            |
| Database       | SQLite / PostgreSQL (configurable) |
| Frontend       | Bootstrap 5, HTML5, CSS3, JS       |
| Authentication | Django auth with role-based access |


Tooltips and modals for user actions.
