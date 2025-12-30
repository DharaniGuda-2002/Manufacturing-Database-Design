"""
supplier_menu.py
Supplier operations menu
CSC540 Project - Deliverable 2
"""

from database import db


def supplier_menu():
    """Supplier role menu"""
    while True:
        print("\n" + "="*60)
        print(" " * 22 + "SUPPLIER MENU")
        print("="*60)
        print("1. View All Suppliers")
        print("2. View Supplier Formulations")
        print("3. View Ingredient Batches by Supplier")
        print("4. Manage Ingredients Supplied")
        print("5. Create/Update Ingredient (Atomic/Compound)")
        print("6. Maintain Do-Not-Combine List")
        print("7. Receive Ingredient Batch (Lot Intake)")
        print("8. Back to Main Menu")
        print("-" * 60)

        choice = input("Enter choice (1-8): ").strip()

        if choice == '1':
            view_suppliers()
        elif choice == '2':
            view_formulations()
        elif choice == '3':
            view_supplier_batches()
        elif choice == '4':
            manage_ingredients_supplied()
        elif choice == '5':
            create_or_update_ingredient()
        elif choice == '6':
            manage_do_not_combine()
        elif choice == '7':
            receive_ingredient_batch()
        elif choice == '8':
            return
        else:
            print("\n✗ Invalid choice. Please enter 1-8.")


# ------------------------------------------------------
# Existing functionality
# ------------------------------------------------------

def view_suppliers():
    """View all suppliers"""
    print("\n--- Suppliers List ---")

    suppliers = db.fetch_all("""
        SELECT supplier_id, supplier_name
        FROM Supplier
        ORDER BY supplier_name
    """)

    if not suppliers:
        print("\n✗ No suppliers found.")
        return

    print(f"\nTotal Suppliers: {len(suppliers)}\n")

    for s in suppliers:
        print(f"{s['supplier_id']}: {s['supplier_name']}")


def view_formulations():
    """View supplier formulations"""
    print("\n--- Supplier Ingredient Formulations ---")

    formulations = db.fetch_all("""
        SELECT sif.formulation_id, i.ingredient_name, s.supplier_name,
               sif.pack_size, sif.unit_price, sif.valid_from, sif.valid_to
        FROM SupplierIngredientFormulation sif
        JOIN Ingredient i ON sif.ingredient_id = i.ingredient_id
        JOIN Supplier s ON sif.supplier_id = s.supplier_id
        WHERE sif.valid_to IS NULL OR sif.valid_to >= CURDATE()
        ORDER BY s.supplier_name, i.ingredient_name
        LIMIT 30
    """)

    if not formulations:
        print("\n✗ No formulations found.")
        return

    print(f"\nShowing {len(formulations)} active formulation(s):\n")

    for f in formulations:
        print(f"Formulation ID: {f['formulation_id']}")
        print(f"  Ingredient: {f['ingredient_name']}")
        print(f"  Supplier: {f['supplier_name']}")
        print(f"  Pack Size: {f['pack_size']}")
        print(f"  Unit Price: ${f['unit_price']:.2f}")
        print(f"  Valid From: {f['valid_from']}")
        if f['valid_to']:
            print(f"  Valid To: {f['valid_to']}")
        print()


def view_supplier_batches():
    """View ingredient batches by supplier"""
    print("\n--- Ingredient Batches by Supplier ---")

    suppliers = db.fetch_all("SELECT supplier_id, supplier_name FROM Supplier ORDER BY supplier_name")
    if not suppliers:
        print("\n✗ No suppliers found.")
        return

    print("\nAvailable Suppliers:")
    for s in suppliers:
        print(f"  {s['supplier_id']}: {s['supplier_name']}")

    supplier_id = input("\nEnter Supplier ID: ").strip()

    if not supplier_id:
        print("\n✗ Supplier ID required.")
        return

    batches = db.fetch_all("""
        SELECT ib.lot_number, i.ingredient_name, ib.supplier_batch_id,
               ib.quantity, ib.cost_per_unit, ib.intake_date,
               (ib.quantity * ib.cost_per_unit) as total_cost
        FROM IngredientBatch ib
        JOIN Ingredient i ON ib.ingredient_id = i.ingredient_id
        WHERE ib.supplier_id = %s
        ORDER BY ib.intake_date DESC
        LIMIT 20
    """, (supplier_id,))

    if not batches:
        print(f"\n✗ No batches found for supplier {supplier_id}.")
        return

    print(f"\nShowing {len(batches)} recent batch(es):\n")

    total_revenue = 0
    for b in batches:
        print(f"Lot: {b['lot_number']}")
        print(f"  Ingredient: {b['ingredient_name']}")
        print(f"  Batch ID: {b['supplier_batch_id']}")
        print(f"  Quantity: {b['quantity']}")
        print(f"  Unit Cost: ${b['cost_per_unit']:.2f}")
        print(f"  Total: ${b['total_cost']:.2f}")
        print(f"  Date: {b['intake_date']}")
        print()
        total_revenue += b['total_cost']

    print(f"{'=' * 60}")
    print(f"Total Revenue (Last 20): ${total_revenue:.2f}")


# ------------------------------------------------------
# 4. Manage Ingredients Supplied
# (SupplierIngredientFormulation)
# ------------------------------------------------------

def manage_ingredients_supplied():
    """Maintain the set of ingredient types a supplier can provide"""
    print("\n--- Manage Ingredients Supplied ---")

    # List suppliers
    suppliers = db.fetch_all("SELECT supplier_id, supplier_name FROM Supplier ORDER BY supplier_name")
    if not suppliers:
        print("\n✗ No suppliers found.")
        return

    print("\nAvailable Suppliers:")
    for s in suppliers:
        print(f"  {s['supplier_id']}: {s['supplier_name']}")

    supplier_id = input("\nEnter Supplier ID: ").strip()
    if not supplier_id:
        print("\n✗ Supplier ID is required.")
        return

    # Show current ingredients supplied
    supplied = db.fetch_all("""
        SELECT DISTINCT sif.ingredient_id, i.ingredient_name
        FROM SupplierIngredientFormulation sif
        JOIN Ingredient i ON sif.ingredient_id = i.ingredient_id
        WHERE sif.supplier_id = %s
        ORDER BY i.ingredient_name
    """, (supplier_id,))

    print("\nCurrent Ingredients Supplied:")
    if not supplied:
        print("  (none yet)")
    else:
        for row in supplied:
            print(f"  {row['ingredient_id']}: {row['ingredient_name']}")

    print("\nOptions:")
    print("  1. Add ingredient supplied (create formulation)")
    print("  2. Back")
    sub_choice = input("Enter choice (1-2): ").strip()

    if sub_choice != '1':
        return

    # Show all ingredients to choose from
    ingredients = db.fetch_all("""
        SELECT ingredient_id, ingredient_name, is_compound
        FROM Ingredient
        ORDER BY ingredient_id
    """)
    if not ingredients:
        print("\n✗ No ingredients defined yet.")
        return

    print("\nAvailable Ingredients:")
    for ing in ingredients:
        kind = "COMPOUND" if ing['is_compound'] else "ATOMIC"
        print(f"  {ing['ingredient_id']}: {ing['ingredient_name']} ({kind})")

    ing_id_raw = input("\nEnter Ingredient ID to add for this supplier: ").strip()
    try:
        ingredient_id = int(ing_id_raw)
    except ValueError:
        print("\n✗ Invalid ingredient ID.")
        return

    # basic validation
    existing_ing = db.fetch_all(
        "SELECT 1 AS ok FROM Ingredient WHERE ingredient_id = %s",
        (ingredient_id,)
    )
    if not existing_ing:
        print("\n✗ Ingredient ID does not exist.")
        return

    # Get pricing info
    try:
        pack_size = float(input("Enter pack size (e.g., 50.0): ").strip())
        unit_price = float(input("Enter unit price (per pack): ").strip())
    except ValueError:
        print("\n✗ Invalid numeric value for pack size or unit price.")
        return

    valid_from = input("Enter valid-from date (YYYY-MM-DD): ").strip()
    valid_to = input("Enter valid-to date (YYYY-MM-DD or blank for open-ended): ").strip()
    valid_to_val = valid_to if valid_to else None

    # Generate new formulation_id and version_id
    row = db.fetch_all("SELECT COALESCE(MAX(formulation_id), 0) AS max_id FROM SupplierIngredientFormulation")
    next_formulation_id = row[0]['max_id'] + 1 if row else 1

    row2 = db.fetch_all("""
        SELECT COALESCE(MAX(version_id), 0) AS max_ver
        FROM SupplierIngredientFormulation
        WHERE supplier_id = %s AND ingredient_id = %s
    """, (supplier_id, ingredient_id))
    next_version_id = row2[0]['max_ver'] + 1 if row2 else 1

    try:
        db.execute_query("""
            INSERT INTO SupplierIngredientFormulation
                (formulation_id, ingredient_id, supplier_id,
                 pack_size, unit_price, valid_from, valid_to, version_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (next_formulation_id, ingredient_id, supplier_id,
              pack_size, unit_price, valid_from, valid_to_val, next_version_id))

        print("\n✓ Ingredient added to supplier offerings.")
        print(f"  Formulation ID: {next_formulation_id}")
        print(f"  Version: {next_version_id}")
    except Exception as e:
        print(f"\n✗ Error adding ingredient to supplier: {e}")


# ------------------------------------------------------
# 5. Create / Update Ingredient (Atomic or Compound)
# ------------------------------------------------------

def create_or_update_ingredient():
    """Create or update an Ingredient and its composition if compound"""
    print("\n--- Create/Update Ingredient ---")
    print("1. Create new ingredient")
    print("2. Update existing ingredient")
    print("3. Back")
    choice = input("Enter choice (1-3): ").strip()

    if choice == '1':
        create_ingredient()
    elif choice == '2':
        update_ingredient()
    else:
        return


def create_ingredient():
    """Create a new ingredient (atomic or compound)"""
    print("\n--- Create New Ingredient ---")

    try:
        ingredient_id = int(input("Enter new Ingredient ID (e.g., 800): ").strip())
    except ValueError:
        print("\n✗ Invalid ingredient ID.")
        return

    # Check uniqueness
    existing = db.fetch_all(
        "SELECT 1 AS ok FROM Ingredient WHERE ingredient_id = %s",
        (ingredient_id,)
    )
    if existing:
        print("\n✗ Ingredient ID already exists.")
        return

    name = input("Enter ingredient name: ").strip()
    if not name:
        print("\n✗ Ingredient name cannot be empty.")
        return

    uom = input("Enter unit of measure (e.g., 'unit', 'oz'): ").strip()
    if not uom:
        print("\n✗ Unit of measure cannot be empty.")
        return

    is_compound_input = input("Is this ingredient COMPOUND? (yes/no): ").strip().lower()
    is_compound = 1 if is_compound_input in ("yes", "y") else 0

    try:
        db.execute_query("""
            INSERT INTO Ingredient (ingredient_id, ingredient_name, unit_of_measure, is_compound)
            VALUES (%s, %s, %s, %s)
        """, (ingredient_id, name, uom, is_compound))
    except Exception as e:
        print(f"\n✗ Error creating ingredient: {e}")
        return

    print(f"\n✓ Ingredient {ingredient_id} - {name} created.")

    if is_compound:
        print("\nNow define its composition (materials):")
        define_compound_composition(ingredient_id)


def update_ingredient():
    """Update an existing ingredient (and optionally its composition)"""
    print("\n--- Update Existing Ingredient ---")
    ing_id_raw = input("Enter Ingredient ID to update: ").strip()
    try:
        ingredient_id = int(ing_id_raw)
    except ValueError:
        print("\n✗ Invalid ingredient ID.")
        return

    rows = db.fetch_all("""
        SELECT ingredient_id, ingredient_name, unit_of_measure, is_compound
        FROM Ingredient
        WHERE ingredient_id = %s
    """, (ingredient_id,))
    if not rows:
        print("\n✗ Ingredient not found.")
        return

    row = rows[0]
    print(f"\nCurrent values for {ingredient_id}:")
    print(f"  Name: {row['ingredient_name']}")
    print(f"  UoM: {row['unit_of_measure']}")
    print(f"  Type: {'COMPOUND' if row['is_compound'] else 'ATOMIC'}")

    new_name = input("New name (press Enter to keep current): ").strip()
    if not new_name:
        new_name = row['ingredient_name']

    new_uom = input("New unit of measure (press Enter to keep current): ").strip()
    if not new_uom:
        new_uom = row['unit_of_measure']

    is_compound_input = input("Is COMPOUND? (yes/no, Enter to keep current): ").strip().lower()
    if is_compound_input in ("yes", "y"):
        new_is_compound = 1
    elif is_compound_input in ("no", "n"):
        new_is_compound = 0
    else:
        new_is_compound = row['is_compound']

    try:
        db.execute_query("""
            UPDATE Ingredient
            SET ingredient_name = %s,
                unit_of_measure = %s,
                is_compound = %s
            WHERE ingredient_id = %s
        """, (new_name, new_uom, new_is_compound, ingredient_id))
        print("\n✓ Ingredient updated.")
    except Exception as e:
        print(f"\n✗ Error updating ingredient: {e}")
        return

    # If compound, manage composition
    if new_is_compound:
        manage_comp = input("Update composition for this compound? (yes/no): ").strip().lower()
        if manage_comp in ("yes", "y"):
            define_compound_composition(ingredient_id)


def define_compound_composition(compound_id: int):
    """Define or re-define composition for a compound ingredient"""
    print(f"\n--- Define Composition for Compound {compound_id} ---")

    # Clear existing composition entries
    db.execute_query("DELETE FROM IngredientComposition WHERE compound_id = %s", (compound_id,))

    try:
        count = int(input("How many materials (children) does this compound have? ").strip())
    except ValueError:
        print("\n✗ Invalid number.")
        return

    if count <= 0:
        print("\nNo materials added.")
        return

    # Show simple ingredient list
    ingredients = db.fetch_all("""
        SELECT ingredient_id, ingredient_name, is_compound
        FROM Ingredient
        WHERE ingredient_id <> %s
        ORDER BY ingredient_id
    """, (compound_id,))

    print("\nAvailable Ingredients (to use as materials):")
    for ing in ingredients:
        kind = "COMPOUND" if ing['is_compound'] else "ATOMIC"
        print(f"  {ing['ingredient_id']}: {ing['ingredient_name']} ({kind})")

    for i in range(count):
        print(f"\nMaterial #{i+1}:")
        mat_raw = input("  Enter material ingredient ID: ").strip()
        try:
            mat_id = int(mat_raw)
        except ValueError:
            print("  ✗ Skipping invalid ID.")
            continue

        qty_raw = input("  Enter quantity required: ").strip()
        try:
            qty = float(qty_raw)
        except ValueError:
            print("  ✗ Skipping invalid quantity.")
            continue

        try:
            db.execute_query("""
                INSERT INTO IngredientComposition (compound_id, material_id, quantity_required)
                VALUES (%s, %s, %s)
            """, (compound_id, mat_id, qty))
        except Exception as e:
            print(f"  ✗ Error inserting composition row: {e}")

    print("\n✓ Composition updated.")


# ------------------------------------------------------
# 6. Maintain Do-Not-Combine List
# ------------------------------------------------------

def manage_do_not_combine():
    """Maintain the global Do-Not-Combine ingredient list"""
    while True:
        print("\n--- Do-Not-Combine List ---")
        print("1. View existing conflicts")
        print("2. Add conflict pair")
        print("3. Delete conflict pair")
        print("4. Back")
        choice = input("Enter choice (1-4): ").strip()

        if choice == '1':
            view_do_not_combine()
        elif choice == '2':
            add_do_not_combine()
        elif choice == '3':
            delete_do_not_combine()
        else:
            return


def view_do_not_combine():
    """View all Do-Not-Combine pairs"""
    rows = db.fetch_all("""
        SELECT d.conflict_id,
               d.ingredient_a_id, ia.ingredient_name AS a_name,
               d.ingredient_b_id, ib.ingredient_name AS b_name,
               d.reason
        FROM DoNotCombine d
        JOIN Ingredient ia ON d.ingredient_a_id = ia.ingredient_id
        JOIN Ingredient ib ON d.ingredient_b_id = ib.ingredient_id
        ORDER BY d.conflict_id
    """)
    if not rows:
        print("\n(no conflicts defined)")
        return

    for r in rows:
        print(f"\nConflict ID: {r['conflict_id']}")
        print(f"  A: {r['ingredient_a_id']} - {r['a_name']}")
        print(f"  B: {r['ingredient_b_id']} - {r['b_name']}")
        print(f"  Reason: {r['reason']}")


def add_do_not_combine():
    """Add a new Do-Not-Combine pair"""
    print("\n--- Add Do-Not-Combine Pair ---")

    # list ingredients (simple)
    ingredients = db.fetch_all("""
        SELECT ingredient_id, ingredient_name
        FROM Ingredient
        ORDER BY ingredient_id
    """)
    if not ingredients:
        print("\n✗ No ingredients available.")
        return

    print("\nAvailable Ingredients:")
    for ing in ingredients:
        print(f"  {ing['ingredient_id']}: {ing['ingredient_name']}")

    try:
        a_id = int(input("\nEnter first ingredient ID: ").strip())
        b_id = int(input("Enter second ingredient ID: ").strip())
    except ValueError:
        print("\n✗ Invalid ingredient ID.")
        return

    if a_id == b_id:
        print("\n✗ Cannot create conflict with itself.")
        return

    # Check they exist
    for _id in (a_id, b_id):
        rows = db.fetch_all("SELECT 1 AS ok FROM Ingredient WHERE ingredient_id = %s", (_id,))
        if not rows:
            print(f"\n✗ Ingredient {_id} does not exist.")
            return

    # enforce a < b for CHECK constraint
    ing_a = min(a_id, b_id)
    ing_b = max(a_id, b_id)

    reason = input("Enter reason (optional): ").strip()
    if not reason:
        reason = None

    try:
        db.execute_query("""
            INSERT INTO DoNotCombine (ingredient_a_id, ingredient_b_id, reason)
            VALUES (%s, %s, %s)
        """, (ing_a, ing_b, reason))
        print("\n✓ Conflict pair added.")
    except Exception as e:
        print(f"\n✗ Error adding conflict pair: {e}")


def delete_do_not_combine():
    """Delete a Do-Not-Combine pair by ingredient IDs"""
    print("\n--- Delete Do-Not-Combine Pair ---")
    try:
        a_id = int(input("Enter first ingredient ID: ").strip())
        b_id = int(input("Enter second ingredient ID: ").strip())
    except ValueError:
        print("\n✗ Invalid ingredient ID.")
        return

    ing_a = min(a_id, b_id)
    ing_b = max(a_id, b_id)

    try:
        db.execute_query("""
            DELETE FROM DoNotCombine
            WHERE ingredient_a_id = %s AND ingredient_b_id = %s
        """, (ing_a, ing_b))
        print("\n✓ If the pair existed, it has been deleted.")
    except Exception as e:
        print(f"\n✗ Error deleting conflict pair: {e}")


# ------------------------------------------------------
# 7. Receive Ingredient Batch (Lot Intake)
# ------------------------------------------------------

def receive_ingredient_batch():
    """
    Record a new ingredient batch (lot intake) for a supplier.
    Enforces:
      - ingredient must be supplied by that supplier (via formulation)
      - lot_number autogenerated as <ingredientId>-<supplierId>-<batchId> by trigger
      - expiration_date >= intake_date + 90 days (DB CHECK)
      - on_hand_qty initialized to quantity
    """
    print("\n--- Receive Ingredient Batch ---")

    # choose supplier
    suppliers = db.fetch_all("SELECT supplier_id, supplier_name FROM Supplier ORDER BY supplier_name")
    if not suppliers:
        print("\n✗ No suppliers found.")
        return

    print("\nAvailable Suppliers:")
    for s in suppliers:
        print(f"  {s['supplier_id']}: {s['supplier_name']}")

    supplier_raw = input("\nEnter Supplier ID: ").strip()
    try:
        supplier_id = int(supplier_raw)
    except ValueError:
        print("\n✗ Invalid Supplier ID.")
        return

    # show ingredients this supplier can provide
    offerings = db.fetch_all("""
        SELECT DISTINCT sif.ingredient_id, i.ingredient_name
        FROM SupplierIngredientFormulation sif
        JOIN Ingredient i ON sif.ingredient_id = i.ingredient_id
        WHERE sif.supplier_id = %s
          AND sif.valid_from <= CURDATE()
          AND (sif.valid_to IS NULL OR sif.valid_to >= CURDATE())
        ORDER BY i.ingredient_name
    """, (supplier_id,))

    if not offerings:
        print("\n✗ This supplier has no active ingredient formulations. Use 'Manage Ingredients Supplied' first.")
        return

    print("\nIngredients this supplier can provide:")
    for row in offerings:
        print(f"  {row['ingredient_id']}: {row['ingredient_name']}")

    ing_raw = input("\nEnter Ingredient ID for this batch: ").strip()
    try:
        ingredient_id = int(ing_raw)
    except ValueError:
        print("\n✗ Invalid Ingredient ID.")
        return

    # validate ingredient is in offerings
    ok = db.fetch_all("""
        SELECT 1 AS ok
        FROM SupplierIngredientFormulation
        WHERE supplier_id = %s
          AND ingredient_id = %s
          AND valid_from <= CURDATE()
          AND (valid_to IS NULL OR valid_to >= CURDATE())
    """, (supplier_id, ingredient_id))
    if not ok:
        print("\n✗ This supplier does not currently supply that ingredient.")
        return

    supplier_batch_id = input("Enter Supplier Batch ID (e.g., B0001): ").strip()
    if not supplier_batch_id:
        print("\n✗ Supplier batch ID is required.")
        return

    try:
        quantity = float(input("Enter quantity (oz): ").strip())
        cost_per_unit = float(input("Enter cost per unit: ").strip())
    except ValueError:
        print("\n✗ Invalid numeric value for quantity or cost.")
        return

    exp_date = input("Enter expiration date (YYYY-MM-DD): ").strip()
    if not exp_date:
        print("\n✗ Expiration date is required.")
        return

    # INSERT; trigger will:
    #  - set lot_number = concat(ingredient_id, '-', supplier_id, '-', supplier_batch_id)
    #  - set intake_date = CURDATE() if NULL
    #  - set on_hand_qty = quantity if NULL
    try:
        db.execute_query("""
            INSERT INTO IngredientBatch
                (ingredient_id, supplier_id, supplier_batch_id,
                 quantity, cost_per_unit, expiration_date,
                 intake_date, on_hand_qty)
            VALUES (%s, %s, %s, %s, %s, %s, NULL, NULL)
        """, (ingredient_id, supplier_id, supplier_batch_id,
              quantity, cost_per_unit, exp_date))

        print("\n✓ Ingredient batch received successfully.")
        print("  Lot number will follow rule <ingredientId>-<supplierId>-<batchId>.")
    except Exception as e:
        print(f"\n✗ Error receiving ingredient batch: {e}")
