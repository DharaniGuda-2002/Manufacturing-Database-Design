"""
query_menu.py
Required queries menu (4 queries as per assignment)
CSC540 Project - Deliverable 2
"""

from database import db

def query_menu():
    """Required queries menu"""
    while True:
        print("\n" + "="*60)
        print(" "*18 + "REQUIRED QUERIES MENU")
        print("="*60)
        print("1. Query 1: Last Batch Ingredients")
        print("2. Query 2: Suppliers and Spending")
        print("3. Query 3: Unit Cost for Specific Lot")
        print("4. Query 4: Conflicting Ingredients in Batch")
        print("5. Query 5: Manufacturers NOT Supplied by Supplier")
        print("6. Back to Main Menu")
        print("-"*60)
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == '1':
            query1_last_batch_ingredients()
        elif choice == '2':
            query2_suppliers_spending()
        elif choice == '3':
            query3_unit_cost()
        elif choice == '4':
            query4_conflicting_ingredients()
        elif choice == '5':
            query5_manufacturers_not_supplied()
        elif choice == '6':
            return
        else:
            print("\n✗ Invalid choice. Please enter 1-6.")

def query1_last_batch_ingredients():
    """
    Query 1: For a specific product, list all ingredient lots 
    used in the most recent batch
    """
    print("\n" + "="*60)
    print("QUERY 1: Last Batch Ingredients for Product")
    print("="*60)
    
    # Get products
    products = db.fetch_all("SELECT product_number, product_name FROM Product ORDER BY product_name")
    print("\nAvailable Products:")
    for p in products:
        print(f"  {p['product_number']}: {p['product_name']}")
    
    product_number = input("\nEnter Product Number (or press Enter for default): ").strip()
    
    # Use first product as default
    if not product_number and products:
        product_number = products[0]['product_number']
        print(f"Using default: {product_number}")
    
    # Get most recent batch
    recent_batch = db.fetch_one("""
        SELECT lot_number, expiration_date, product_quantity
        FROM ProductBatch
        WHERE product_id = %s
        ORDER BY expiration_date DESC
        LIMIT 1
    """, (product_number,))
    
    if not recent_batch:
        print(f"\n✗ No batches found for product '{product_number}'.")
        return
    
    # Get ingredients used in this batch
    ingredients = db.fetch_all("""
        SELECT 
            cil.ingredient_lot_id,
            i.ingredient_name,
            cil.quantity_used,
            s.supplier_name,
            ib.cost_per_unit,
            (cil.quantity_used * ib.cost_per_unit) as total_cost
        FROM ConsumedIngredientLot cil
        JOIN IngredientBatch ib ON cil.ingredient_lot_id = ib.lot_number
        JOIN Ingredient i ON ib.ingredient_id = i.ingredient_id
        JOIN Supplier s ON ib.supplier_id = s.supplier_id
        WHERE cil.product_batch_id = %s
        ORDER BY cil.quantity_used DESC
    """, (recent_batch['lot_number'],))
    
    print(f"\n{'='*60}")
    print(f"Most Recent Batch: {recent_batch['lot_number']}")
    print(f"Expiration Date: {recent_batch['expiration_date']}")
    print(f"Quantity Produced: {recent_batch['product_quantity']}")
    print(f"{'='*60}")
    
    if not ingredients:
        print("\n✗ No ingredient consumption records found for this batch.")
        return
    
    print(f"\nIngredients Used ({len(ingredients)} total):\n")
    total_cost = 0
    
    for ing in ingredients:
        print(f"Lot: {ing['ingredient_lot_id']}")
        print(f"  Ingredient: {ing['ingredient_name']}")
        print(f"  Supplier: {ing['supplier_name']}")
        print(f"  Quantity Used: {ing['quantity_used']}")
        print(f"  Unit Cost: ${ing['cost_per_unit']:.2f}")
        print(f"  Total Cost: ${ing['total_cost']:.2f}\n")
        total_cost += ing['total_cost']
    
    print(f"{'='*60}")
    print(f"Total Ingredient Cost: ${total_cost:.2f}")
    print(f"{'='*60}")

def query2_suppliers_spending():
    """
    Query 2: For a given manufacturer, list all suppliers they purchase from
    and the total amount spent with each supplier.
    """
    print("\n" + "="*60)
    print("QUERY 2: Suppliers and Spending for Manufacturer")
    print("="*60)

    manufacturers = db.fetch_all("""
        SELECT manufacturer_id, manufacturer_name
        FROM Manufacturer
        ORDER BY manufacturer_id
    """)

    print("\nAvailable Manufacturers:")
    for m in manufacturers:
        print(f"  {m['manufacturer_id']}: {m['manufacturer_name']}")

    # User input
    mfg_id = input("\nEnter Manufacturer ID (or press Enter for default): ").strip()

    if not mfg_id:
        if manufacturers:
            mfg_id = str(manufacturers[0]['manufacturer_id'])
            print(f"Using default manufacturer: {mfg_id}")
        else:
            print("\n✗ No manufacturers found.")
            return

    suppliers = db.fetch_all("""
        SELECT
            s.supplier_id,
            s.supplier_name,
            COUNT(DISTINCT ib.lot_number) AS batches_purchased,
            SUM(c.quantity_used * ib.cost_per_unit) AS total_spent
        FROM ProductBatch pb
        JOIN ConsumedIngredientLot c
            ON c.product_batch_id = pb.lot_number
        JOIN IngredientBatch ib
            ON ib.lot_number = c.ingredient_lot_id
        JOIN Supplier s
            ON s.supplier_id = ib.supplier_id
        WHERE pb.manufacturer_id = %s
        GROUP BY s.supplier_id, s.supplier_name
        ORDER BY s.supplier_id;
    """, (mfg_id,))

    if not suppliers:
        print(f"\n✗ No supplier data found for manufacturer {mfg_id}.")
        return

    mfg_name = db.fetch_one("""
        SELECT manufacturer_name
        FROM Manufacturer
        WHERE manufacturer_id = %s
    """, (mfg_id,))

    print(f"\n{'='*60}")
    print(f"Manufacturer: {mfg_name['manufacturer_name'] if mfg_name else mfg_id}")
    print(f"{'='*60}\n")

    print(f"Suppliers ({len(suppliers)} total):\n")

    grand_total = 0
    for sup in suppliers:
        print(f"{sup['supplier_id']}: {sup['supplier_name']}")
        print(f"  Batches Purchased: {sup['batches_purchased']}")
        print(f"  Total Spent: ${sup['total_spent']:.2f}\n")
        grand_total += sup['total_spent']

    print(f"{'='*60}")
    print(f"Total Spending: ${grand_total:.2f}")
    print(f"{'='*60}")


def query3_unit_cost():
    """
    Query 3: Given a specific product batch lot number, calculate the 
    per-unit cost based on ingredient costs
    """
    print("\n" + "="*60)
    print("QUERY 3: Unit Cost for Product Batch")
    print("="*60)
    
    # Show recent batches
    batches = db.fetch_all("""
        SELECT pb.lot_number, p.product_name, pb.product_quantity, pb.expiration_date
        FROM ProductBatch pb
        JOIN Product p ON pb.product_id = p.product_number
        ORDER BY pb.expiration_date DESC
        LIMIT 10
    """)
    
    print("\nRecent Product Batches:")
    for b in batches:
        print(f"  {b['lot_number']}: {b['product_name']} (Qty: {b['product_quantity']}, Exp: {b['expiration_date']})")
    
    lot_number = input("\nEnter Product Batch Lot Number: ").strip()
    
    if not lot_number:
        print("\n✗ Lot number required.")
        return
    
    # Get batch info
    batch = db.fetch_one("""
        SELECT pb.lot_number, p.product_name, pb.product_quantity, pb.expiration_date
        FROM ProductBatch pb
        JOIN Product p ON pb.product_id = p.product_number
        WHERE pb.lot_number = %s
    """, (lot_number,))
    
    if not batch:
        print(f"\n✗ Batch '{lot_number}' not found.")
        return
    
    # Calculate total cost
    cost_breakdown = db.fetch_all("""
        SELECT 
            i.ingredient_name,
            cil.quantity_used,
            ib.cost_per_unit,
            (cil.quantity_used * ib.cost_per_unit) as ingredient_cost
        FROM ConsumedIngredientLot cil
        JOIN IngredientBatch ib ON cil.ingredient_lot_id = ib.lot_number
        JOIN Ingredient i ON ib.ingredient_id = i.ingredient_id
        WHERE cil.product_batch_id = %s
    """, (lot_number,))
    
    print(f"\n{'='*60}")
    print(f"Batch: {batch['lot_number']}")
    print(f"Product: {batch['product_name']}")
    print(f"Quantity Produced: {batch['product_quantity']} units")
    print(f"Expiration Date: {batch['expiration_date']}")
    print(f"{'='*60}")
    
    if not cost_breakdown:
        print("\n✗ No cost data available for this batch.")
        return
    
    print("\nCost Breakdown:\n")
    total_cost = 0
    
    for item in cost_breakdown:
        print(f"{item['ingredient_name']}")
        print(f"  Quantity: {item['quantity_used']} @ ${item['cost_per_unit']:.2f}/unit")
        print(f"  Cost: ${item['ingredient_cost']:.2f}\n")
        total_cost += item['ingredient_cost']
    
    unit_cost = total_cost / batch['product_quantity'] if batch['product_quantity'] > 0 else 0
    
    print(f"{'='*60}")
    print(f"Total Cost: ${total_cost:.2f}")
    print(f"Cost Per Unit: ${unit_cost:.2f}")
    print(f"{'='*60}")

def query4_conflicting_ingredients():
    """
    Query 4: For a given product batch, check if any ingredient lots used
    contain ingredients that should not be combined (do-not-combine rules)
    """
    print("\n" + "="*60)
    print("QUERY 4: Check for Conflicting Ingredients")
    print("="*60)
    
    # Show recent batches
    batches = db.fetch_all("""
        SELECT pb.lot_number, p.product_name, pb.expiration_date
        FROM ProductBatch pb
        JOIN Product p ON pb.product_id = p.product_number
        ORDER BY pb.expiration_date DESC
        LIMIT 10
    """)
    
    print("\nRecent Product Batches:")
    for b in batches:
        print(f"  {b['lot_number']}: {b['product_name']} ({b['expiration_date']})")
    
    lot_number = input("\nEnter Product Batch Lot Number: ").strip()
    
    if not lot_number:
        print("\n✗ Lot number required.")
        return
    
    # Get batch info
    batch = db.fetch_one("""
        SELECT pb.lot_number, p.product_name, pb.expiration_date
        FROM ProductBatch pb
        JOIN Product p ON pb.product_id = p.product_number
        WHERE pb.lot_number = %s
    """, (lot_number,))
    
    if not batch:
        print(f"\n✗ Batch '{lot_number}' not found.")
        return
    
    # Check for conflicts
    conflicts = db.fetch_all("""
        SELECT DISTINCT
            ia.ingredient_name as ingredient_a,
            ib.ingredient_name as ingredient_b,
            dnc.reason,
            iba.lot_number as lot_a,
            ibb.lot_number as lot_b
        FROM ConsumedIngredientLot cil1
        JOIN ConsumedIngredientLot cil2 ON cil1.product_batch_id = cil2.product_batch_id
        JOIN IngredientBatch iba ON cil1.ingredient_lot_id = iba.lot_number
        JOIN IngredientBatch ibb ON cil2.ingredient_lot_id = ibb.lot_number
        JOIN DoNotCombine dnc ON (
            (iba.ingredient_id = dnc.ingredient_a_id AND ibb.ingredient_id = dnc.ingredient_b_id)
            OR
            (iba.ingredient_id = dnc.ingredient_b_id AND ibb.ingredient_id = dnc.ingredient_a_id)
        )
        JOIN Ingredient ia ON iba.ingredient_id = ia.ingredient_id
        JOIN Ingredient ib ON ibb.ingredient_id = ib.ingredient_id
        WHERE cil1.product_batch_id = %s
        AND cil1.ingredient_lot_id < cil2.ingredient_lot_id
    """, (lot_number,))
    
    print(f"\n{'='*60}")
    print(f"Batch: {batch['lot_number']}")
    print(f"Product: {batch['product_name']}")
    print(f"Expiration Date: {batch['expiration_date']}")
    print(f"{'='*60}")
    
    if not conflicts:
        print("\n✓ No conflicting ingredients found!")
        print("  This batch is SAFE - all ingredients are compatible.")
    else:
        print(f"\n⚠️  WARNING: {len(conflicts)} CONFLICT(S) DETECTED!\n")
        for i, conf in enumerate(conflicts, 1):
            print(f"Conflict {i}:")
            print(f"  Ingredients: {conf['ingredient_a']} + {conf['ingredient_b']}")
            print(f"  Lots: {conf['lot_a']} + {conf['lot_b']}")
            if conf['reason']:
                print(f"  Reason: {conf['reason']}")
            print()
        print("⚠️  This batch may be UNSAFE for consumption!")
    
    print(f"{'='*60}")

def query5_manufacturers_not_supplied():
    """
    Query 5: For a given supplier, list all manufacturers that they have NOT supplied to
    """
    print("\n" + "="*60)
    print("QUERY 5: Manufacturers NOT Supplied by Supplier")
    print("="*60)
    
    # Get suppliers
    suppliers = db.fetch_all("SELECT supplier_id, supplier_name FROM Supplier ORDER BY supplier_name")
    print("\nAvailable Suppliers:")
    for s in suppliers:
        print(f"  {s['supplier_id']}: {s['supplier_name']}")
    
    supplier_id = input("\nEnter Supplier ID (or press Enter for default): ").strip()
    
    # Use first supplier as default
    if not supplier_id and suppliers:
        supplier_id = str(suppliers[0]['supplier_id'])
        print(f"Using default: {supplier_id}")
    
    # Get supplier name
    supplier = db.fetch_one(
        "SELECT supplier_id, supplier_name FROM Supplier WHERE supplier_id = %s",
        (supplier_id,)
    )
    
    if not supplier:
        print(f"\n✗ Supplier {supplier_id} not found.")
        return
    
    # Find manufacturers NOT supplied by this supplier
    manufacturers_not_supplied = db.fetch_all("""
        SELECT 
            m.manufacturer_id,
            m.manufacturer_name,
            COUNT(DISTINCT p.product_number) as product_count
        FROM Manufacturer m
        LEFT JOIN Product p ON m.manufacturer_id = p.manufacturer_id
        WHERE NOT EXISTS (
            SELECT 1
            FROM ProductBatch pb
            JOIN ConsumedIngredientLot cil ON pb.lot_number = cil.product_batch_id
            JOIN IngredientBatch ib ON cil.ingredient_lot_id = ib.lot_number
            WHERE pb.manufacturer_id = m.manufacturer_id
            AND ib.supplier_id = %s
        )
        GROUP BY m.manufacturer_id, m.manufacturer_name
        ORDER BY m.manufacturer_name
    """, (supplier_id,))
    
    print(f"\n{'='*60}")
    print(f"Supplier: {supplier['supplier_name']} (ID: {supplier['supplier_id']})")
    print(f"{'='*60}")
    
    if not manufacturers_not_supplied:
        print("\n✓ This supplier has supplied to ALL manufacturers!")
    else:
        print(f"\nManufacturers NOT Supplied ({len(manufacturers_not_supplied)} total):\n")
        
        for mfg in manufacturers_not_supplied:
            print(f"{mfg['manufacturer_id']}: {mfg['manufacturer_name']}")
            print(f"  Products: {mfg['product_count']}")
            print(f"  Status: Has NEVER purchased from {supplier['supplier_name']}\n")
    
    print(f"{'='*60}")
