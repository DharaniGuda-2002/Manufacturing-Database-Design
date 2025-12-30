-- =====================================================
-- CSC540 Project - Strict Sample Data Load (FINAL APPROVED)
-- Based on "Sample Data - Public.pdf"
-- =====================================================
Use inventory_db;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Clear all existing data
-- DELETE FROM ConsumedIngredientLot;
-- DELETE FROM ProductBatch; 
-- DELETE FROM IngredientBatch;
-- DELETE FROM FormulationMaterial;
-- DELETE FROM SupplierIngredientFormulation;
-- DELETE FROM IngredientComposition;
-- DELETE FROM RecipeIngredient;
-- DELETE FROM Recipe;
-- DELETE FROM Product;
-- DELETE FROM DoNotCombine;
-- DELETE FROM User;
-- DELETE FROM Ingredient;
-- DELETE FROM Supplier;
-- DELETE FROM Manufacturer;
-- DELETE FROM Category;
-- DELETE FROM TransactionLog; 

-- Reset Auto-Increments
-- ALTER TABLE User AUTO_INCREMENT = 1;
-- ALTER TABLE DoNotCombine AUTO_INCREMENT = 1;
-- ALTER TABLE TransactionLog AUTO_INCREMENT = 1;
-- ALTER TABLE SupplierIngredientFormulation AUTO_INCREMENT = 1;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- 2. REFERENCE DATA
-- =====================================================

INSERT INTO Category (category_id, category_name) VALUES
(2, 'Dinners'),
(3, 'Sides');

INSERT INTO Manufacturer (manufacturer_id, manufacturer_name) VALUES
(1, 'MFG001'),
(2, 'MFG002');

INSERT INTO Supplier (supplier_id, supplier_name) VALUES
(20, 'Jane Doe'),
(21, 'James Miller');

-- =====================================================
-- 3. INGREDIENTS
-- =====================================================

INSERT INTO Ingredient (ingredient_id, ingredient_name, unit_of_measure, is_compound) VALUES
(101, 'Salt', 'unit', 0),
(102, 'Pepper', 'unit', 0),
(104, 'Sodium Phosphate', 'unit', 0),
(106, 'Beef Steak', 'unit', 0),
(108, 'Pasta', 'unit', 0),
(201, 'Seasoning Blend', 'unit', 1), 
(301, 'Super Seasoning', 'unit', 1); 

-- =====================================================
-- 4. FORMULATIONS & COMPOSITIONS
-- =====================================================

INSERT INTO SupplierIngredientFormulation 
(formulation_id, ingredient_id, supplier_id, version_id, valid_from, valid_to, unit_price, pack_size) 
VALUES
(1, 201, 20, 1, '2025-06-01', '2025-11-30', 20.0, 8.0);

INSERT INTO FormulationMaterial (formulation_id, materials_id, quantity_required) VALUES
(1, 101, 6.0),
(1, 102, 2.0);

INSERT INTO IngredientComposition (compound_id, material_id, quantity_required) VALUES
(201, 101, 6.0),
(201, 102, 2.0);

-- =====================================================
-- 5. PRODUCTS & RECIPES
-- =====================================================

INSERT INTO Product (product_number, product_name, category_id, manufacturer_id, standard_batch_size) VALUES
(100, 'Steak Dinner', 2, 1, 100),
(101, 'Mac & Cheese', 3, 2, 300);

INSERT INTO Recipe (recipe_id, product_id) VALUES
(1, 100),
(2, 101);

INSERT INTO RecipeIngredient (recipe_id, ingredient_id, quantity_required) VALUES
(1, 106, 6.0), 
(1, 201, 0.2), 
(2, 108, 7.0), 
(2, 101, 0.5), 
(2, 102, 2.0); 

-- =====================================================
-- 6. USERS
-- =====================================================
-- NOTE: Matching PDF usernames (MFG001) but adding passwords for App functionality
INSERT INTO User (username, password, role, manufacturer_id, supplier_id) VALUES
('MFG001', 'password123', 'MANUFACTURER', 1, NULL),
('MFG002', 'password123', 'MANUFACTURER', 2, NULL),
('SUP020', 'password123', 'SUPPLIER', NULL, 20),
('SUP021', 'password123', 'SUPPLIER', NULL, 21),
('VIEW001', 'password123', 'VIEWER', NULL, NULL);

-- =====================================================
-- 7. INGREDIENT BATCHES
-- =====================================================

INSERT INTO IngredientBatch (lot_number, ingredient_id, supplier_id, supplier_batch_id, quantity, cost_per_unit, expiration_date, intake_date, on_hand_qty) VALUES
('101-20-B0001', 101, 20, 'B0001', 1000, 0.1, '2025-11-15', '2025-01-01', 1000),
('101-21-B0001', 101, 21, 'B0001', 800, 0.08, '2025-10-30', '2025-01-01', 800),
-- FIX: Changed expiration from 2025-11-01 to 2025-12-01 so it is not expired today (Nov 19)
('101-20-B0002', 101, 20, 'B0002', 500, 0.1, '2025-12-01', '2025-01-01', 500), 
('101-20-B0003', 101, 20, 'B0003', 500, 0.1, '2025-12-15', '2025-01-01', 500),
('102-20-B0001', 102, 20, 'B0001', 1200, 0.3, '2025-12-15', '2025-01-01', 1200), 
('106-20-B0005', 106, 20, 'B0005', 3000, 0.5, '2025-12-15', '2025-01-01', 3000),
('106-20-B0006', 106, 20, 'B0006', 600, 0.5, '2025-12-20', '2025-01-01', 600),    
('108-20-B0001', 108, 20, 'B0001', 1000, 0.25, '2025-09-28', '2025-01-01', 1000),
('108-20-B0003', 108, 20, 'B0003', 6300, 0.25, '2025-12-31', '2025-01-01', 6300), 
('201-20-B0001', 201, 20, 'B0001', 100, 2.5, '2025-11-30', '2025-01-01', 100),
('201-20-B0002', 201, 20, 'B0002', 20, 2.5, '2025-12-30', '2025-01-01', 20);     

-- =====================================================
-- 8. PRODUCT BATCHES & CONSUMPTION
-- =====================================================

INSERT INTO ProductBatch (lot_number, product_id, manufacturer_id, batch_id, product_quantity, expiration_date) VALUES
('100-MFG001-B0901', 100, 1, 901, 100, '2025-11-15'),
('101-MFG002-B0101', 101, 2, 101, 300, '2025-11-15'); 

-- Triggers will handle inventory reduction here
INSERT INTO ConsumedIngredientLot (product_batch_id, ingredient_lot_id, quantity_used) VALUES
('100-MFG001-B0901', '106-20-B0006', 600),
('100-MFG001-B0901', '201-20-B0002', 20),
('101-MFG002-B0101', '101-20-B0002', 150),
('101-MFG002-B0101', '108-20-B0003', 2100),
('101-MFG002-B0101', '102-20-B0001', 600);

-- Update product costs
UPDATE ProductBatch pb
SET cost_per_unit = (
    SELECT COALESCE(SUM(c.quantity_used * ib.cost_per_unit), 0) / pb.product_quantity
    FROM ConsumedIngredientLot c
    JOIN IngredientBatch ib ON c.ingredient_lot_id = ib.lot_number
    WHERE c.product_batch_id = pb.lot_number
)
WHERE pb.lot_number IN ('100-MFG001-B0901', '101-MFG002-B0101');

-- =====================================================
-- 9. CONFLICTS
-- =====================================================

-- Fixed ID order (104 < 106)
INSERT INTO DoNotCombine (ingredient_a_id, ingredient_b_id, reason) VALUES
(104, 106, 'Do not combine Beef Steak and Sodium Phosphate');

SELECT 'Strict Sample Data Loaded Successfully!' AS Status;