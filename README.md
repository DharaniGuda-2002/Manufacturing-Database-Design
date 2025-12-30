# Inventory Management System  
## Prepared & Frozen Meals Manufacturer Database  
**CSC 540 – Project Deliverable 2**

---

## Team Members
- Dharani Guda (dguda)  
- Ayush Gupta (agupta86)  
- Sasidhar Appalla (sappall)  
- Shanmukha Srinivas Sai Chatadi (schatad)

**Submission Date:** November 2024

---

## System Requirements

### Software
- MySQL 8.0 or MariaDB 10.5+
- Python 3.8 or higher

### Python Dependency
```bash
pip install mysql-connector-python
````

---

## Database Setup Instructions

### Step 1: Create Database

```sql
CREATE DATABASE inventory_db;
USE inventory_db;
```

### Step 2: Load Schema

```sql
SOURCE /path/to/COMPLETE_schema.sql;
```

**Expected Output**

* 15 tables
* 4 triggers
* 3 stored procedures
* 3 views

### Step 3: Load Sample Data

```sql
SOURCE /path/to/data.sql;
```

**Includes**

* 6 products with recipes
* 5 product batches
* 24 ingredient batches
* Multiple suppliers and manufacturers

### Step 4: Verify Installation

```sql
SHOW TABLES;
SELECT COUNT(*) FROM Product;       -- Expected: 6
SELECT COUNT(*) FROM ProductBatch;  -- Expected: 5
```

---

## Python Application Setup

### Configure Database Credentials

Edit `database.py`:

```python
self.password = 'YOUR_MYSQL_PASSWORD_HERE'
```

### Verify Python Version

```bash
python --version
```

### Install Dependency

```bash
pip install mysql-connector-python
```

### Test Connection

```bash
python main.py
```

**Expected Output**

```
✓ Connected to MySQL Server version X.X.X
✓ Connected to database: inventory_db
```

---

## Running the Application

```bash
python main.py
```

### Main Menu Options

1. Manufacturer operations
2. Supplier operations
3. General viewer
4. Required queries
5. Undo recent operations
6. Exit

---

## Required Queries

1. **Last Batch Ingredients**
   Lists ingredients and lot numbers used in the most recent batch of a product.

2. **Suppliers and Spending**
   Displays total spending per supplier for a given manufacturer.

3. **Unit Cost for Specific Lot**
   Calculates per-unit product cost with ingredient-level breakdown.

4. **Conflicting Ingredients**
   Identifies unsafe ingredient combinations using do-not-combine rules.

5. **Manufacturers Not Supplied by Supplier**
   Lists manufacturers that never purchased from a given supplier.

---

## UNDO Feature

Access via **Option 5** in the main menu.

**Demonstrates**

* Transaction logging
* Stored-procedure-based rollback
* Referential integrity handling

---

## Project Structure

```
CSC_Submission/
├── csc540_inventory/
│   ├── database.py
│   ├── main.py
│   ├── manufacturer_menu.py
│   ├── supplier_menu.py
│   ├── query_menu.py
│   ├── undo_menu.py
│   ├── viewer_menu.py
│   ├── Project_Report.pdf
│   └── README.md
├── SQL_Files/
│   ├── COMPLETE_schema.sql
│   └── data.sql
└── Updated_ER.pdf
```

---

## Database Features Implemented

### Tables (15)

Category, Manufacturer, Supplier, Ingredient, Product, Recipe, User,
DoNotCombine, SupplierIngredientFormulation, FormulationMaterial,
IngredientComposition, RecipeIngredient, IngredientBatch, ProductBatch,
ConsumedIngredientLot

### Triggers (4)

* Auto-generation of lot numbers
* Expiration validation
* Inventory maintenance
* Product batch ID generation

### Stored Procedures (3)

* `RecordProductionBatch`
* `TraceRecall` *(Graduate Requirement)*
* `CheckIngredientConflicts` *(Graduate Requirement)*

### Views (3)

* ActiveSupplierFormulations
* FlattenedProductBOM
* RecentConflictViolations

### Constraints

* CHECK (quantities, expiration rules)
* FOREIGN KEY
* UNIQUE
* NOT NULL

---

## Sample Data Overview

* Categories: 5
* Manufacturers: 3
* Suppliers: 5
* Products: 6
* Ingredients: 34
* Product Batches: 5
* Ingredient Batches: 24

---

## Testing Recommendations

* Verify tables, triggers, procedures, and views
* Test trigger behavior on insert/update
* Execute all stored procedures
* Validate UNDO functionality
* Test edge cases (invalid quantities, expiration violations)

---

## Known Notes

* Numeric lot number format for consistency
* Cost per unit derived from real ingredient usage
* UNDO supports INSERT operations only


