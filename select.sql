-- ================================
-- BASIC LOOKUPS (Reference Tables)
-- ================================
use inventory_db;
SELECT * FROM Category;
SELECT * FROM Manufacturer;
SELECT * FROM Supplier;
SELECT * FROM Ingredient;

-- ================================
-- USER + RULES
-- ================================

SELECT * FROM User;
SELECT * FROM DoNotCombine;

-- ================================
-- PRODUCT & RECIPE STRUCTURE
-- ================================

SELECT * FROM Product;
SELECT * FROM Recipe;
SELECT * FROM RecipeIngredient;

-- ================================
-- COMPOUND INGREDIENT BOM
-- ================================

SELECT * FROM IngredientComposition;

-- ================================
-- SUPPLIER FORMULATIONS
-- ================================

SELECT * FROM SupplierIngredientFormulation;
SELECT * FROM FormulationMaterial;

-- ================================
-- INVENTORY (LOTS)
-- ================================

SELECT * FROM IngredientBatch;
SELECT * FROM ProductBatch;

-- ================================
-- CONSUMPTION (TRACING)
-- ================================

SELECT * FROM ConsumedIngredientLot;

-- ================================
-- VIEWS (Derived Data)
-- ================================

SELECT * FROM ActiveSupplierFormulations;
SELECT * FROM FlattenedProductBOM;
SELECT * FROM RecentConflictViolations;
