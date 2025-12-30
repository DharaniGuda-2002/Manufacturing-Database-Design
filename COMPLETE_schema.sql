-- =====================================================
-- CSC540 Project - Deliverable 2
-- Complete Schema: Tables + Triggers + Procedures + Views
-- =====================================================

-- Disable foreign key checks temporarily to allow clean drop
DROP SCHEMA IF EXISTS inventory_db;
CREATE SCHEMA inventory_db;
use inventory_db;

SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS TransactionLog; -- Added this
DROP TABLE IF EXISTS ConsumedIngredientLot;
DROP TABLE IF EXISTS ProductBatch;
DROP TABLE IF EXISTS IngredientBatch;
DROP TABLE IF EXISTS FormulationMaterial;
DROP TABLE IF EXISTS SupplierIngredientFormulation;
DROP TABLE IF EXISTS IngredientComposition;
DROP TABLE IF EXISTS RecipeIngredient;
DROP TABLE IF EXISTS Recipe;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS DoNotCombine;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Ingredient;
DROP TABLE IF EXISTS Supplier;
DROP TABLE IF EXISTS Manufacturer;
DROP TABLE IF EXISTS Category;

-- Drop views if they exist
DROP VIEW IF EXISTS ActiveSupplierFormulations;
DROP VIEW IF EXISTS FlattenedProductBOM;
DROP VIEW IF EXISTS RecentConflictViolations;

-- Drop procedure if exists
DROP PROCEDURE IF EXISTS UndoLastOperation; -- Added this

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- TABLES
-- =====================================================

CREATE TABLE Category (
  category_id   BIGINT PRIMARY KEY,
  category_name VARCHAR(100) NOT NULL
);

CREATE TABLE Manufacturer (
  manufacturer_id   BIGINT PRIMARY KEY,
  manufacturer_name VARCHAR(200) NOT NULL
);

CREATE TABLE Supplier (
  supplier_id   BIGINT PRIMARY KEY,
  supplier_name VARCHAR(200) NOT NULL
);

CREATE TABLE Ingredient (
  ingredient_id   BIGINT PRIMARY KEY,
  ingredient_name VARCHAR(200) NOT NULL,
  unit_of_measure VARCHAR(32) NOT NULL,
  is_compound     BOOLEAN NOT NULL DEFAULT 0
);

-- NEW: User table for role management
CREATE TABLE User (
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('MANUFACTURER', 'SUPPLIER', 'VIEWER') NOT NULL,
    manufacturer_id BIGINT,
    supplier_id BIGINT,
    FOREIGN KEY (manufacturer_id) REFERENCES Manufacturer(manufacturer_id),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
);

-- NEW: TransactionLog table for UNDO feature
CREATE TABLE TransactionLog (
    transaction_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    operation_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(255),
    old_values TEXT,
    new_values TEXT,
    user_name VARCHAR(100),
    transaction_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_undone BOOLEAN DEFAULT FALSE,
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_is_undone (is_undone)
);

-- NEW: Do-Not-Combine conflicts (GRAD requirement)
CREATE TABLE DoNotCombine (
    conflict_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    ingredient_a_id BIGINT NOT NULL,
    ingredient_b_id BIGINT NOT NULL,
    reason VARCHAR(255),
    FOREIGN KEY (ingredient_a_id) REFERENCES Ingredient(ingredient_id),
    FOREIGN KEY (ingredient_b_id) REFERENCES Ingredient(ingredient_id),
    UNIQUE (ingredient_a_id, ingredient_b_id),
    CHECK (ingredient_a_id < ingredient_b_id)
);

CREATE TABLE Product (
  product_number      BIGINT PRIMARY KEY,
  product_name        VARCHAR(200) NOT NULL,
  category_id         BIGINT NOT NULL,
  manufacturer_id     BIGINT NOT NULL,
  standard_batch_size INT NOT NULL,
  FOREIGN KEY (category_id) REFERENCES Category(category_id),
  FOREIGN KEY (manufacturer_id) REFERENCES Manufacturer(manufacturer_id),
  UNIQUE (product_name),
  CHECK (standard_batch_size > 0)
);

CREATE TABLE Recipe (
  recipe_id  BIGINT PRIMARY KEY,
  product_id BIGINT NOT NULL,
  FOREIGN KEY (product_id) REFERENCES Product(product_number)
);

CREATE TABLE RecipeIngredient (
  recipe_id         BIGINT NOT NULL,
  ingredient_id     BIGINT NOT NULL,
  quantity_required DECIMAL(18,6) NOT NULL,
  PRIMARY KEY (recipe_id, ingredient_id),
  FOREIGN KEY (recipe_id) REFERENCES Recipe(recipe_id),
  FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id),
  CHECK (quantity_required > 0)
);

CREATE TABLE IngredientComposition (
  compound_id       BIGINT NOT NULL,
  material_id       BIGINT NOT NULL,
  quantity_required DECIMAL(18,6) NOT NULL,
  PRIMARY KEY (compound_id, material_id),
  FOREIGN KEY (compound_id) REFERENCES Ingredient(ingredient_id),
  FOREIGN KEY (material_id) REFERENCES Ingredient(ingredient_id),
  CHECK (compound_id <> material_id),
  CHECK (quantity_required > 0)
);

CREATE TABLE SupplierIngredientFormulation (
  formulation_id BIGINT PRIMARY KEY,
  ingredient_id  BIGINT NOT NULL,
  supplier_id    BIGINT NOT NULL,
  pack_size      DECIMAL(18,6) NOT NULL,
  unit_price     DECIMAL(18,6) NOT NULL,
  valid_from     DATE NOT NULL,
  valid_to       DATE,
  version_id     BIGINT NOT NULL,
  FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id),
  FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
  CHECK (pack_size > 0),
  CHECK (unit_price >= 0),
  CHECK (valid_to IS NULL OR valid_to >= valid_from)
);

CREATE TABLE FormulationMaterial (
  formulation_id    BIGINT NOT NULL,
  materials_id      BIGINT NOT NULL,
  quantity_required DECIMAL(18,6) NOT NULL,
  PRIMARY KEY (formulation_id, materials_id),
  FOREIGN KEY (formulation_id) REFERENCES SupplierIngredientFormulation(formulation_id),
  FOREIGN KEY (materials_id) REFERENCES Ingredient(ingredient_id),
  CHECK (quantity_required > 0)
);

CREATE TABLE ProductBatch (
  lot_number       VARCHAR(190) PRIMARY KEY,
  product_id       BIGINT NOT NULL,
  manufacturer_id  BIGINT NOT NULL,
  batch_id         BIGINT NOT NULL,
  expiration_date  DATE NOT NULL,
  product_quantity INT NOT NULL,
  cost_per_unit    DECIMAL(18,6),
  FOREIGN KEY (product_id) REFERENCES Product(product_number),
  FOREIGN KEY (manufacturer_id) REFERENCES Manufacturer(manufacturer_id),
  UNIQUE (product_id, manufacturer_id, batch_id),
  CHECK (product_quantity > 0)
);

CREATE TABLE IngredientBatch (
  lot_number        VARCHAR(255) PRIMARY KEY,
  ingredient_id     BIGINT NOT NULL,
  supplier_id       BIGINT NOT NULL,
  supplier_batch_id VARCHAR(80) NOT NULL,
  quantity          DECIMAL(18,6) NOT NULL,
  cost_per_unit     DECIMAL(18,6) NOT NULL,
  expiration_date   DATE NOT NULL,
  intake_date       DATE NOT NULL,
  on_hand_qty       DECIMAL(18,6) NOT NULL,
  FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id),
  FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
  UNIQUE (ingredient_id, supplier_id, supplier_batch_id),
  CHECK (quantity >= 0),
  CHECK (on_hand_qty >= 0),
  CHECK (expiration_date >= DATE_ADD(intake_date, INTERVAL 90 DAY))
);

CREATE TABLE ConsumedIngredientLot (
  product_batch_id  VARCHAR(190) NOT NULL,
  ingredient_lot_id VARCHAR(255) NOT NULL,
  quantity_used     DECIMAL(18,6) NOT NULL,
  PRIMARY KEY (product_batch_id, ingredient_lot_id),
  FOREIGN KEY (product_batch_id) REFERENCES ProductBatch(lot_number),
  FOREIGN KEY (ingredient_lot_id) REFERENCES IngredientBatch(lot_number),
  CHECK (quantity_used > 0)
);

-- =====================================================
-- TRIGGERS (Required)
-- =====================================================

-- TRIGGER 1: Auto-generate ingredient lot number
DELIMITER $$
CREATE TRIGGER before_ingredient_batch_insert
BEFORE INSERT ON IngredientBatch
FOR EACH ROW
BEGIN
    SET NEW.lot_number = CONCAT(NEW.ingredient_id, '-', NEW.supplier_id, '-', NEW.supplier_batch_id);
    
    IF NEW.on_hand_qty IS NULL THEN
        SET NEW.on_hand_qty = NEW.quantity;
    END IF;
    
    IF NEW.intake_date IS NULL THEN
        SET NEW.intake_date = CURDATE();
    END IF;
END$$
DELIMITER ;

-- TRIGGER 2: Prevent expired consumption
DELIMITER $$
CREATE TRIGGER before_consume_ingredient
BEFORE INSERT ON ConsumedIngredientLot
FOR EACH ROW
BEGIN
    DECLARE lot_expiration DATE;
    
    SELECT expiration_date INTO lot_expiration
    FROM IngredientBatch
    WHERE lot_number = NEW.ingredient_lot_id;
    
    IF lot_expiration < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot consume expired ingredient lot';
    END IF;
END$$
DELIMITER ;

-- TRIGGER 3: Maintain on-hand inventory
DELIMITER $$
CREATE TRIGGER after_consume_ingredient
AFTER INSERT ON ConsumedIngredientLot
FOR EACH ROW
BEGIN
    UPDATE IngredientBatch
    SET on_hand_qty = on_hand_qty - NEW.quantity_used
    WHERE lot_number = NEW.ingredient_lot_id;
    
    -- Check if on_hand goes negative (shouldn't happen with proper validation)
    IF (SELECT on_hand_qty FROM IngredientBatch WHERE lot_number = NEW.ingredient_lot_id) < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Insufficient inventory for consumption';
    END IF;
END$$
DELIMITER ;

-- TRIGGER 4: Auto-generate product lot number (optional but helpful)
DELIMITER $$
CREATE TRIGGER before_product_batch_insert
BEFORE INSERT ON ProductBatch
FOR EACH ROW
BEGIN
    IF NEW.lot_number IS NULL OR NEW.lot_number = '' THEN
        SET NEW.lot_number = CONCAT(NEW.product_id, '-', NEW.manufacturer_id, '-', NEW.batch_id);
    END IF;
END$$
DELIMITER ;

-- =====================================================
-- STORED PROCEDURES (Required)
-- =====================================================

-- PROCEDURE 1: Record Production Batch
DELIMITER $$
CREATE PROCEDURE RecordProductionBatch(
    IN p_product_id BIGINT,
    IN p_manufacturer_id BIGINT,
    IN p_batch_id BIGINT,
    IN p_produced_qty INT,
    IN p_expiration_date DATE,
    OUT p_lot_number VARCHAR(190),
    OUT p_total_cost DECIMAL(18,6)
)
BEGIN
    DECLARE v_standard_batch_size INT;
    DECLARE v_total_cost DECIMAL(18,6) DEFAULT 0;
    DECLARE v_lot_number VARCHAR(190);
    DECLARE v_cost_per_unit DECIMAL(18,6);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Production batch creation failed';
    END;
    
    START TRANSACTION;
    
    -- Validate product and get standard batch size
    SELECT standard_batch_size INTO v_standard_batch_size
    FROM Product
    WHERE product_number = p_product_id AND manufacturer_id = p_manufacturer_id;
    
    IF v_standard_batch_size IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid product or manufacturer';
    END IF;
    
    -- Validate produced quantity is multiple of standard batch size
    IF p_produced_qty % v_standard_batch_size != 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Produced quantity must be multiple of standard batch size';
    END IF;
    
    -- Generate lot number
    SET v_lot_number = CONCAT(p_product_id, '-', p_manufacturer_id, '-', p_batch_id);
    
    -- Create product batch record
    INSERT INTO ProductBatch (
        lot_number, product_id, manufacturer_id, batch_id,
        expiration_date, product_quantity, cost_per_unit
    ) VALUES (
        v_lot_number, p_product_id, p_manufacturer_id, p_batch_id,
        p_expiration_date, p_produced_qty, NULL
    );
    
    -- Compute total cost from consumed ingredients (if any already recorded)
    SELECT COALESCE(SUM(c.quantity_used * i.cost_per_unit), 0) INTO v_total_cost
    FROM ConsumedIngredientLot c
    JOIN IngredientBatch i ON c.ingredient_lot_id = i.lot_number
    WHERE c.product_batch_id = v_lot_number;
    
    -- Calculate cost per unit
    IF p_produced_qty > 0 THEN
        SET v_cost_per_unit = v_total_cost / p_produced_qty;
    ELSE
        SET v_cost_per_unit = 0;
    END IF;
    
    -- Update product batch with computed cost
    UPDATE ProductBatch
    SET cost_per_unit = v_cost_per_unit
    WHERE lot_number = v_lot_number;
    
    -- Set output parameters
    SET p_lot_number = v_lot_number;
    SET p_total_cost = v_total_cost;
    
    COMMIT;
END$$
DELIMITER ;

-- PROCEDURE 2: Trace Recall (GRAD requirement)
DELIMITER $$
CREATE PROCEDURE TraceRecall(
    IN p_ingredient_id BIGINT,
    IN p_lot_number VARCHAR(255),
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    IF p_lot_number IS NOT NULL THEN
        -- Specific lot recall
        SELECT DISTINCT
            pb.lot_number AS product_lot,
            pb.product_id,
            p.product_name,
            pb.manufacturer_id,
            m.manufacturer_name,
            pb.expiration_date,
            pb.product_quantity,
            c.ingredient_lot_id,
            ib.ingredient_id
        FROM ConsumedIngredientLot c
        JOIN ProductBatch pb ON c.product_batch_id = pb.lot_number
        JOIN Product p ON pb.product_id = p.product_number
        JOIN Manufacturer m ON pb.manufacturer_id = m.manufacturer_id
        JOIN IngredientBatch ib ON c.ingredient_lot_id = ib.lot_number
        WHERE c.ingredient_lot_id = p_lot_number
          AND ib.intake_date BETWEEN p_start_date AND p_end_date;
    ELSE
        -- All lots of an ingredient
        SELECT DISTINCT
            pb.lot_number AS product_lot,
            pb.product_id,
            p.product_name,
            pb.manufacturer_id,
            m.manufacturer_name,
            pb.expiration_date,
            pb.product_quantity,
            c.ingredient_lot_id,
            ib.ingredient_id
        FROM ConsumedIngredientLot c
        JOIN ProductBatch pb ON c.product_batch_id = pb.lot_number
        JOIN Product p ON pb.product_id = p.product_number
        JOIN Manufacturer m ON pb.manufacturer_id = m.manufacturer_id
        JOIN IngredientBatch ib ON c.ingredient_lot_id = ib.lot_number
        WHERE ib.ingredient_id = p_ingredient_id
          AND ib.intake_date BETWEEN p_start_date AND p_end_date;
    END IF;
END$$
DELIMITER ;

-- PROCEDURE 3: Check Ingredient Conflicts (GRAD requirement)
DELIMITER $$
CREATE PROCEDURE CheckIngredientConflicts(
    IN p_product_batch_id VARCHAR(190),
    OUT p_has_conflicts BOOLEAN,
    OUT p_conflict_count INT
)
BEGIN
    DECLARE v_conflict_count INT DEFAULT 0;
    
    -- Create temp table for batch ingredients
    DROP TEMPORARY TABLE IF EXISTS TempBatchIngredients;
    CREATE TEMPORARY TABLE TempBatchIngredients AS
    SELECT DISTINCT ib.ingredient_id
    FROM ConsumedIngredientLot c
    JOIN IngredientBatch ib ON c.ingredient_lot_id = ib.lot_number
    WHERE c.product_batch_id = p_product_batch_id
    
    UNION
    
    -- Include materials from compound ingredients (one level deep)
    SELECT DISTINCT ic.material_id AS ingredient_id
    FROM ConsumedIngredientLot c
    JOIN IngredientBatch ib ON c.ingredient_lot_id = ib.lot_number
    JOIN IngredientComposition ic ON ib.ingredient_id = ic.compound_id
    WHERE c.product_batch_id = p_product_batch_id;
    
    -- Check for conflicts
    SELECT COUNT(*) INTO v_conflict_count
    FROM DoNotCombine dnc
    WHERE EXISTS (
        SELECT 1 FROM TempBatchIngredients WHERE ingredient_id = dnc.ingredient_a_id
    )
    AND EXISTS (
        SELECT 1 FROM TempBatchIngredients WHERE ingredient_id = dnc.ingredient_b_id
    );
    
    -- Set output
    SET p_has_conflicts = (v_conflict_count > 0);
    SET p_conflict_count = v_conflict_count;
    
    DROP TEMPORARY TABLE IF EXISTS TempBatchIngredients;
END$$
DELIMITER ;

-- PROCEDURE 4: Undo Last Operation (For UNDO Feature)
DELIMITER $$
CREATE PROCEDURE UndoLastOperation(
    IN p_transaction_id BIGINT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_operation_type VARCHAR(50);
    DECLARE v_table_name VARCHAR(100);
    DECLARE v_record_id VARCHAR(255);
    DECLARE v_is_undone BOOLEAN;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = 'Undo operation failed - database error';
    END;
    
    START TRANSACTION;
    
    -- Get transaction details
    SELECT operation_type, table_name, record_id, is_undone
    INTO v_operation_type, v_table_name, v_record_id, v_is_undone
    FROM TransactionLog
    WHERE transaction_id = p_transaction_id;
    
    -- Check if already undone
    IF v_is_undone THEN
        SET p_success = FALSE;
        SET p_message = 'Transaction already undone';
        ROLLBACK;
    ELSE
        -- Undo based on operation type
        CASE v_operation_type
            WHEN 'INSERT_PRODUCT' THEN
                -- Delete recipe ingredients first
                DELETE ri FROM RecipeIngredient ri
                JOIN Recipe r ON ri.recipe_id = r.recipe_id
                WHERE r.product_id = v_record_id;
                
                -- Delete recipe
                DELETE FROM Recipe WHERE product_id = v_record_id;
                
                -- Delete product batches and consumed ingredients
                DELETE cil FROM ConsumedIngredientLot cil
                JOIN ProductBatch pb ON cil.product_batch_id = pb.lot_number
                WHERE pb.product_id = v_record_id;
                
                DELETE FROM ProductBatch WHERE product_id = v_record_id;
                
                -- Finally delete the product
                DELETE FROM Product WHERE product_number = v_record_id;
                
            WHEN 'INSERT_PRODUCT_BATCH' THEN
                DELETE FROM ConsumedIngredientLot WHERE product_batch_id = v_record_id;
                DELETE FROM ProductBatch WHERE lot_number = v_record_id;
                
            WHEN 'INSERT_INGREDIENT_BATCH' THEN
                DELETE FROM ConsumedIngredientLot WHERE ingredient_lot_id = v_record_id;
                DELETE FROM IngredientBatch WHERE lot_number = v_record_id;
                
            ELSE
                SET p_message = 'Undo not supported for this operation type';
                ROLLBACK;
        END CASE;
        
        -- Mark as undone
        UPDATE TransactionLog
        SET is_undone = TRUE
        WHERE transaction_id = p_transaction_id;
        
        SET p_success = TRUE;
        SET p_message = 'Operation undone successfully';
        COMMIT;
    END IF;
END$$
DELIMITER ;

-- =====================================================
-- VIEWS (Required)
-- =====================================================

-- VIEW 1: Current Active Supplier Formulations
DROP VIEW IF EXISTS ActiveSupplierFormulations;
CREATE VIEW ActiveSupplierFormulations AS
SELECT 
    sif.formulation_id,
    sif.ingredient_id,
    i.ingredient_name,
    sif.supplier_id,
    s.supplier_name,
    sif.pack_size,
    sif.unit_price,
    sif.valid_from,
    sif.valid_to,
    sif.version_id
FROM SupplierIngredientFormulation sif
JOIN Ingredient i ON sif.ingredient_id = i.ingredient_id
JOIN Supplier s ON sif.supplier_id = s.supplier_id
WHERE CURDATE() BETWEEN sif.valid_from AND COALESCE(sif.valid_to, '9999-12-31');

-- VIEW 2: Flattened Product BOM for Labeling
DROP VIEW IF EXISTS FlattenedProductBOM;
CREATE VIEW FlattenedProductBOM AS
SELECT 
    r.recipe_id,
    r.product_id,
    p.product_name,
    ri.ingredient_id,
    i.ingredient_name,
    ri.quantity_required AS direct_quantity,
    CASE 
        WHEN i.is_compound = 1 THEN (
            SELECT SUM(ic.quantity_required * ri.quantity_required)
            FROM IngredientComposition ic
            WHERE ic.compound_id = ri.ingredient_id
        )
        ELSE ri.quantity_required
    END AS total_quantity
FROM Recipe r
JOIN Product p ON r.product_id = p.product_number
JOIN RecipeIngredient ri ON r.recipe_id = ri.recipe_id
JOIN Ingredient i ON ri.ingredient_id = i.ingredient_id

UNION

-- Materials from compound ingredients
SELECT 
    r.recipe_id,
    r.product_id,
    p.product_name,
    ic.material_id AS ingredient_id,
    im.ingredient_name,
    ic.quantity_required * ri.quantity_required AS direct_quantity,
    ic.quantity_required * ri.quantity_required AS total_quantity
FROM Recipe r
JOIN Product p ON r.product_id = p.product_number
JOIN RecipeIngredient ri ON r.recipe_id = ri.recipe_id
JOIN Ingredient i ON ri.ingredient_id = i.ingredient_id
JOIN IngredientComposition ic ON i.ingredient_id = ic.compound_id
JOIN Ingredient im ON ic.material_id = im.ingredient_id
WHERE i.is_compound = 1;

-- VIEW 3: Health Risk Rule Violations (Last 30 Days)
DROP VIEW IF EXISTS RecentConflictViolations;
CREATE VIEW RecentConflictViolations AS
SELECT 
    pb.lot_number AS product_batch,
    pb.product_id,
    p.product_name,
    dnc.ingredient_a_id,
    ia.ingredient_name AS ingredient_a_name,
    dnc.ingredient_b_id,
    ib.ingredient_name AS ingredient_b_name,
    pb.expiration_date
FROM ProductBatch pb
JOIN Product p ON pb.product_id = p.product_number
JOIN ConsumedIngredientLot c1 ON pb.lot_number = c1.product_batch_id
JOIN IngredientBatch ib1 ON c1.ingredient_lot_id = ib1.lot_number
JOIN ConsumedIngredientLot c2 ON pb.lot_number = c2.product_batch_id
JOIN IngredientBatch ib2 ON c2.ingredient_lot_id = ib2.lot_number
JOIN DoNotCombine dnc ON (
    (ib1.ingredient_id = dnc.ingredient_a_id AND ib2.ingredient_id = dnc.ingredient_b_id)
    OR
    (ib1.ingredient_id = dnc.ingredient_b_id AND ib2.ingredient_id = dnc.ingredient_a_id)
)
JOIN Ingredient ia ON dnc.ingredient_a_id = ia.ingredient_id
JOIN Ingredient ib ON dnc.ingredient_b_id = ib.ingredient_id
WHERE pb.expiration_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY);

-- =====================================================
-- SHOW TABLES
-- =====================================================
SHOW TABLES;
SELECT 'TransactionLog table created successfully!' AS Status;