"""
manufacturer_menu.py
Manufacturer operations menu
CSC540 Project - Deliverable 2
"""

from database import db, log_transaction

def manufacturer_menu():
    """Manufacturer role menu"""
    while True:
        print("\n" + "="*60)
        print(" "*20 + "MANUFACTURER MENU")
        print("="*60)
        print("1. View Products")
        print("2. View Product Batches")
        print("3. View Ingredient Batches")
        print("4. Create Product")
        print("5. Back to Main Menu")
        print("-"*60)
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            view_products()
        elif choice == '2':
            view_product_batches()
        elif choice == '3':
            view_ingredient_batches()
        elif choice == '4':
            create_product()   # UPDATED
        elif choice == '5':
            return
        else:
            print("\n✗ Invalid choice. Please enter 1-5.")

def view_products():
    """View all products"""
    print("\n--- Products List ---")
    
    products = db.fetch_all("""
        SELECT p.product_number, p.product_name, p.standard_batch_size,
               c.category_name, m.manufacturer_name
        FROM Product p
        JOIN Category c ON p.category_id = c.category_id
        JOIN Manufacturer m ON p.manufacturer_id = m.manufacturer_id
        ORDER BY p.product_name
    """)
    
    if not products:
        print("\n✗ No products found.")
        return
    
    print(f"\nTotal Products: {len(products)}\n")
    
    for p in products:
        print(f"{p['product_number']}: {p['product_name']}")
        print(f"  Manufacturer: {p['manufacturer_name']}")
        print(f"  Category: {p['category_name']}")
        print(f"  Batch Size: {p['standard_batch_size']}")
        print()

def view_product_batches():
    """View product batches"""
    print("\n--- Product Batches ---")
    
    product_number = input("Enter Product Number (or press Enter for all): ").strip()
    
    if product_number:
        query = """
            SELECT pb.lot_number, pb.batch_id, p.product_name,
                   pb.product_quantity, pb.expiration_date, pb.cost_per_unit
            FROM ProductBatch pb
            JOIN Product p ON pb.product_id = p.product_number
            WHERE pb.product_id = %s
            ORDER BY pb.expiration_date DESC
        """
        batches = db.fetch_all(query, (product_number,))
    else:
        query = """
            SELECT pb.lot_number, pb.batch_id, p.product_name,
                   pb.product_quantity, pb.expiration_date, pb.cost_per_unit
            FROM ProductBatch pb
            JOIN Product p ON pb.product_id = p.product_number
            ORDER BY pb.expiration_date DESC
            LIMIT 20
        """
        batches = db.fetch_all(query)
    
    if not batches:
        print("\n✗ No batches found.")
        return
    
    print(f"\nShowing {len(batches)} batch(es):\n")
    
    for b in batches:
        print(f"Lot: {b['lot_number']}")
        print(f"  Product: {b['product_name']}")
        print(f"  Batch ID: {b['batch_id']}")
        print(f"  Quantity: {b['product_quantity']}")
        print(f"  Expiration: {b['expiration_date']}")
        if b['cost_per_unit']:
            print(f"  Cost/Unit: ${b['cost_per_unit']:.2f}")
        print()

def view_ingredient_batches():
    """View ingredient batches"""
    print("\n--- Ingredient Batches ---")
    
    batches = db.fetch_all("""
        SELECT ib.lot_number, i.ingredient_name, s.supplier_name,
               ib.quantity, ib.on_hand_qty, ib.cost_per_unit,
               ib.intake_date, ib.expiration_date
        FROM IngredientBatch ib
        JOIN Ingredient i ON ib.ingredient_id = i.ingredient_id
        JOIN Supplier s ON ib.supplier_id = s.supplier_id
        ORDER BY ib.intake_date DESC
        LIMIT 20
    """)
    
    if not batches:
        print("\n✗ No ingredient batches found.")
        return
    
    print(f"\nShowing {len(batches)} recent batch(es):\n")
    
    for b in batches:
        print(f"Lot: {b['lot_number']}")
        print(f"  Ingredient: {b['ingredient_name']}")
        print(f"  Supplier: {b['supplier_name']}")
        print(f"  Quantity: {b['quantity']}")
        print(f"  On Hand: {b['on_hand_qty']}")
        print(f"  Cost/Unit: ${b['cost_per_unit']:.2f}")
        print(f"  Intake: {b['intake_date']}")
        print(f"  Expires: {b['expiration_date']}")
        print()

def create_product():
    """Create a new product from user input"""
    print("\n--- Create New Product ---")

    # Show existing categories to help the user
    categories = db.fetch_all("""
        SELECT category_id, category_name
        FROM Category
        ORDER BY category_id
    """)
    if not categories:
        print("\n✗ No categories found. Please insert categories first.")
        return

    print("\nAvailable Categories:")
    for c in categories:
        print(f"  {c['category_id']}: {c['category_name']}")

    # Show manufacturers as well
    manufacturers = db.fetch_all("""
        SELECT manufacturer_id, manufacturer_name
        FROM Manufacturer
        ORDER BY manufacturer_id
    """)
    if not manufacturers:
        print("\n✗ No manufacturers found. Please insert manufacturers first.")
        return

    print("\nAvailable Manufacturers:")
    for m in manufacturers:
        print(f"  {m['manufacturer_id']}: {m['manufacturer_name']}")

    # --- Collect input from user ---
    name = input("\nEnter product name: ").strip()
    if not name:
        print("\n✗ Product name cannot be empty.")
        return

    try:
        category_id = int(input("Enter category ID: ").strip())
        manufacturer_id = int(input("Enter manufacturer ID: ").strip())
        standard_batch_size = int(input("Enter standard batch size: ").strip())
    except ValueError:
        print("\n✗ Invalid numeric input.")
        return

    if standard_batch_size <= 0:
        print("\n✗ Standard batch size must be > 0.")
        return

    # Validate category and manufacturer exist
    cat = db.fetch_all(
        "SELECT 1 AS ok FROM Category WHERE category_id = %s",
        (category_id,)
    )
    if not cat:
        print("\n✗ Category ID does not exist.")
        return

    manu = db.fetch_all(
        "SELECT 1 AS ok FROM Manufacturer WHERE manufacturer_id = %s",
        (manufacturer_id,)
    )
    if not manu:
        print("\n✗ Manufacturer ID does not exist.")
        return

    # Generate next product_number automatically
    rows = db.fetch_all("SELECT COALESCE(MAX(product_number), 0) AS max_num FROM Product")
    max_num = rows[0]['max_num'] if rows else 0
    product_number = max_num + 1

    print("\nYou are about to create this product:")
    print(f"  Product Number: {product_number}")
    print(f"  Name: {name}")
    print(f"  Category ID: {category_id}")
    print(f"  Manufacturer ID: {manufacturer_id}")
    print(f"  Standard Batch Size: {standard_batch_size}")

    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("\n✗ Cancelled.")
        return

    try:
        query = """
            INSERT INTO Product
                (product_name, category_id, manufacturer_id, standard_batch_size)
            VALUES (%s, %s, %s, %s, %s)
        """
        db.execute_query(
            query,
            (product_number, name, category_id, manufacturer_id, standard_batch_size)
        )

        # Log transaction for undo
        log_transaction(
            'INSERT_PRODUCT',
            'Product',
            str(product_number),
            user_name='manufacturer'
        )

        print("\n✓ Product created successfully!")
        print(f"  Product Number: {product_number}")

    except Exception as e:
        print(f"\n✗ Error creating product: {e}")
