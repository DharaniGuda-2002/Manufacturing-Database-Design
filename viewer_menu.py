"""
viewer_menu.py
General viewer operations menu
CSC540 Project - Deliverable 2
"""

from database import db

def viewer_menu():
    """General viewer role menu"""
    while True:
        print("\n" + "="*60)
        print(" "*19 + "GENERAL VIEWER MENU")
        print("="*60)
        print("1. Browse Products")
        print("2. View Product Recipe (BOM)")
        print("3. View Active Formulations View")
        print("4. Search Products")
        print("5. Back to Main Menu")
        print("-"*60)
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            browse_products()
        elif choice == '2':
            view_product_recipe()
        elif choice == '3':
            view_active_formulations_view()
        elif choice == '4':
            search_products()
        elif choice == '5':
            return
        else:
            print("\n✗ Invalid choice. Please enter 1-5.")

def browse_products():
    """Browse all products"""
    print("\n--- Browse Products ---")
    
    products = db.fetch_all("""
        SELECT p.product_number, p.product_name, p.standard_batch_size,
               c.category_name, m.manufacturer_name
        FROM Product p
        JOIN Category c ON p.category_id = c.category_id
        JOIN Manufacturer m ON p.manufacturer_id = m.manufacturer_id
        ORDER BY c.category_name, p.product_name
    """)
    
    if not products:
        print("\n✗ No products found.")
        return
    
    current_category = None
    for p in products:
        if p['category_name'] != current_category:
            current_category = p['category_name']
            print(f"\n{'='*60}")
            print(f"Category: {current_category}")
            print(f"{'='*60}")
        
        print(f"\n{p['product_number']}: {p['product_name']}")
        print(f"  Manufacturer: {p['manufacturer_name']}")
        print(f"  Batch Size: {p['standard_batch_size']}")

def view_product_recipe():
    """View recipe (Bill of Materials) for a product"""
    print("\n--- Product Recipe (Bill of Materials) ---")
    
    # Show products first
    products = db.fetch_all("SELECT product_number, product_name FROM Product ORDER BY product_name")
    print("\nAvailable Products:")
    for p in products[:10]:
        print(f"  {p['product_number']}: {p['product_name']}")
    if len(products) > 10:
        print(f"  ... and {len(products) - 10} more")
    
    product_number = input("\nEnter Product Number: ").strip()
    
    if not product_number:
        print("\n✗ Product number required.")
        return
    
    # Get product info
    product = db.fetch_one("""
        SELECT p.product_name, p.standard_batch_size, m.manufacturer_name
        FROM Product p
        JOIN Manufacturer m ON p.manufacturer_id = m.manufacturer_id
        WHERE p.product_number = %s
    """, (product_number,))
    
    if not product:
        print(f"\n✗ Product '{product_number}' not found.")
        return
    
    # Get recipe
    recipe = db.fetch_one("""
        SELECT recipe_id, product_id
        FROM Recipe
        WHERE product_id = %s
    """, (product_number,))
    
    if not recipe:
        print(f"\n✗ No recipe found for this product.")
        return
    
    # Get ingredients
    ingredients = db.fetch_all("""
        SELECT i.ingredient_name, ri.quantity_required, i.unit_of_measure
        FROM RecipeIngredient ri
        JOIN Ingredient i ON ri.ingredient_id = i.ingredient_id
        WHERE ri.recipe_id = %s
        ORDER BY ri.quantity_required DESC
    """, (recipe['recipe_id'],))
    
    print(f"\n{'='*60}")
    print(f"Product: {product['product_name']}")
    print(f"Manufacturer: {product['manufacturer_name']}")
    print(f"Batch Size: {product['standard_batch_size']}")
    print(f"{'='*60}")
    
    if not ingredients:
        print("\n✗ No ingredients found in recipe.")
        return
    
    print(f"\nRecipe Ingredients ({len(ingredients)} total):")
    
    for ing in ingredients:
        print(f"\n  • {ing['ingredient_name']}")
        print(f"    Quantity: {ing['quantity_required']} {ing['unit_of_measure']}")

def view_active_formulations_view():
    """View the ActiveSupplierFormulations view"""
    print("\n--- Active Supplier Formulations (View) ---")
    
    formulations = db.fetch_all("""
        SELECT formulation_id, ingredient_name, supplier_name,
               pack_size, unit_price, valid_from, valid_to
        FROM ActiveSupplierFormulations
        ORDER BY supplier_name, ingredient_name
        LIMIT 30
    """)
    
    if not formulations:
        print("\n✗ No active formulations found.")
        return
    
    print(f"\nShowing {len(formulations)} active formulation(s):\n")
    
    for f in formulations:
        print(f"{f['formulation_id']}: {f['ingredient_name']}")
        print(f"  Supplier: {f['supplier_name']}")
        print(f"  Pack: {f['pack_size']}, Price: ${f['unit_price']:.2f}")
        print(f"  Valid: {f['valid_from']} to {f['valid_to'] if f['valid_to'] else 'Ongoing'}")
        print()

def search_products():
    """Search products by keyword"""
    print("\n--- Search Products ---")
    
    keyword = input("Enter search keyword: ").strip()
    
    if not keyword:
        print("\n✗ Please enter a keyword.")
        return
    
    products = db.fetch_all("""
        SELECT p.product_number, p.product_name,
               c.category_name, m.manufacturer_name
        FROM Product p
        JOIN Category c ON p.category_id = c.category_id
        JOIN Manufacturer m ON p.manufacturer_id = m.manufacturer_id
        WHERE p.product_name LIKE %s 
           OR c.category_name LIKE %s
           OR m.manufacturer_name LIKE %s
        ORDER BY p.product_name
    """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    
    if not products:
        print(f"\n✗ No products found matching '{keyword}'.")
        return
    
    print(f"\nFound {len(products)} product(s):\n")
    for p in products:
        print(f"{p['product_number']}: {p['product_name']}")
        print(f"  Manufacturer: {p['manufacturer_name']}")
        print(f"  Category: {p['category_name']}")
        print()
