"""Deterministic seed data generator for All Points Agents.

Uses Faker + random.seed(42) to produce reproducible data across all 21 tables.
Dates are relative to today so the data always feels current.
"""

import random
import sqlite3
from datetime import datetime, timedelta, date

from faker import Faker

from ..constants import (
    CRITICAL_EXCEPTION_TYPES,
    EMAIL_CATEGORIES,
    EXCEPTION_TYPES,
    FREIGHT_CLASS_MULTIPLIERS,
    SERVICE_TYPES,
    VIOLATION_DESCRIPTIONS,
)

fake = Faker()
Faker.seed(42)
random.seed(42)

# ── Reference data ──────────────────────────────────────────────

CLIENTS = [
    ("TurtleBox", "TB", "Consumer Electronics"),
    ("NovaSkin Cosmetics", "NS", "Beauty & Skincare"),
    ("PeakGear Outdoors", "PG", "Outdoor Recreation"),
    ("RetroFit Athletics", "RA", "Athletic Apparel"),
    ("Coastal Living Co", "CL", "Home & Garden"),
    ("EcoWare Solutions", "EW", "Sustainable Goods"),
    ("BrightPath Tech", "BP", "Technology Accessories"),
    ("Nexus Home", "NH", "Home Furnishings"),
]

PARCEL_CARRIERS = [
    ("UPS", "UPS", "parcel", "A12345", "standard", 1.15, 3),
    ("UPS (New Contract)", "UPS2", "parcel", "B67890", "negotiated", 0.95, 3),
    ("FedEx", "FEDEX", "parcel", "987654321", "standard", 1.00, 3),
    ("USPS", "USPS", "parcel", "USPS123", "commercial_plus", 0.90, 3),
]

LTL_CARRIERS = [
    ("XPO Logistics", "XPO", "ltl", "XPO-5001", "negotiated", 0.95, 4),
    ("Estes Express", "ESTES", "ltl", "EST-3002", "standard", 0.98, 3),
    ("Old Dominion", "ODFL", "ltl", "OD-7003", "premium", 1.02, 2),
    ("ABF Freight", "ABF", "ltl", "ABF-4004", "standard", 1.00, 3),
    ("YRC Freight", "YRC", "ltl", "YRC-6005", "standard", 1.12, 4),
]

ALL_CARRIERS = PARCEL_CARRIERS + LTL_CARRIERS

# Products per client — matches existing SKU patterns from the demos
PRODUCT_CATALOG = {
    "TB": [
        ("TB-SPK-001", "TurtleBox Gen 2 Speaker", 320, 18, 14, 12, 299.99, "85"),
        ("TB-SPK-002", "TurtleBox Mini Speaker", 160, 12, 10, 8, 199.99, "85"),
        ("TB-ACC-010", "TurtleBox Carrying Case", 48, 20, 16, 4, 49.99, None),
        ("TB-ACC-011", "TurtleBox Wall Mount", 32, 10, 8, 4, 29.99, None),
        ("TB-CBL-020", "TurtleBox USB-C Cable 6ft", 4, 8, 4, 2, 14.99, None),
        ("TB-BAT-030", "TurtleBox Replacement Battery", 16, 6, 4, 3, 39.99, None),
    ],
    "NS": [
        ("NS-KIT-050", "NovaSkin Starter Kit", 32, 10, 8, 6, 89.99, None),
        ("NS-SER-025", "NovaSkin Vitamin C Serum", 8, 4, 3, 6, 45.99, None),
        ("NS-MSK-030", "NovaSkin Hydrating Mask (6pk)", 24, 8, 6, 4, 54.99, None),
        ("NS-CLN-015", "NovaSkin Gentle Cleanser", 12, 6, 4, 8, 28.99, None),
        ("NS-TNR-020", "NovaSkin Toning Mist", 10, 4, 3, 7, 32.99, None),
        ("NS-CRM-040", "NovaSkin Night Cream", 8, 4, 4, 4, 62.99, None),
    ],
    "PG": [
        ("PG-TENT-200", "PeakGear Summit 4-Person Tent", 960, 28, 12, 12, 349.99, "100"),
        ("PG-BAG-075", "PeakGear Summit Daypack", 48, 20, 14, 8, 89.99, None),
        ("PG-SLP-150", "PeakGear Sleeping Bag 20F", 80, 22, 12, 12, 129.99, "85"),
        ("PG-STK-030", "PeakGear Trekking Poles (Pair)", 32, 28, 6, 4, 64.99, None),
        ("PG-WAT-025", "PeakGear Hydration Bladder 3L", 16, 16, 10, 4, 34.99, None),
        ("PG-LNT-045", "PeakGear LED Headlamp", 6, 6, 4, 4, 29.99, None),
    ],
    "RA": [
        ("RA-SHOE-100", "RetroFit Running Shoes", 40, 14, 10, 6, 129.99, None),
        ("RA-APRL-050", "RetroFit Performance Jacket", 24, 16, 12, 4, 89.99, None),
        ("RA-SHRT-035", "RetroFit Training Tee", 12, 14, 10, 2, 34.99, None),
        ("RA-PANT-060", "RetroFit Compression Tights", 16, 14, 10, 2, 54.99, None),
        ("RA-SOCK-015", "RetroFit Performance Socks (3pk)", 8, 8, 6, 4, 24.99, None),
        ("RA-BAG-040", "RetroFit Gym Duffel", 32, 22, 12, 12, 59.99, None),
    ],
    "CL": [
        ("CL-CNDL-025", "Coastal Living Soy Candle", 16, 6, 6, 6, 28.99, None),
        ("CL-THRW-080", "Coastal Living Cotton Throw", 48, 16, 12, 4, 79.99, None),
        ("CL-VASE-045", "Coastal Living Ceramic Vase", 64, 10, 10, 14, 54.99, "85"),
        ("CL-FRME-030", "Coastal Living Photo Frame 8x10", 24, 12, 10, 2, 34.99, None),
        ("CL-PLLW-035", "Coastal Living Accent Pillow", 20, 18, 18, 6, 42.99, None),
        ("CL-DFSR-050", "Coastal Living Reed Diffuser", 12, 6, 6, 10, 38.99, None),
    ],
    "EW": [
        ("EW-BTL-020", "EcoWare Stainless Bottle 32oz", 16, 10, 4, 4, 29.99, None),
        ("EW-WRAP-015", "EcoWare Beeswax Wraps (3pk)", 4, 10, 8, 2, 18.99, None),
        ("EW-BAG-025", "EcoWare Produce Bags (5pk)", 6, 12, 8, 2, 14.99, None),
        ("EW-STRW-010", "EcoWare Bamboo Straws (8pk)", 4, 10, 4, 2, 12.99, None),
        ("EW-CONT-035", "EcoWare Glass Container Set", 80, 14, 10, 8, 44.99, "85"),
        ("EW-UTSL-018", "EcoWare Bamboo Utensil Set", 6, 10, 4, 2, 16.99, None),
    ],
    "BP": [
        ("BP-CHG-030", "BrightPath Wireless Charger", 12, 6, 6, 2, 34.99, None),
        ("BP-HUB-055", "BrightPath USB-C Hub 7-in-1", 8, 8, 4, 2, 59.99, None),
        ("BP-KBD-080", "BrightPath Ergonomic Keyboard", 32, 18, 8, 3, 79.99, None),
        ("BP-MSE-045", "BrightPath Vertical Mouse", 8, 6, 4, 6, 44.99, None),
        ("BP-CAM-100", "BrightPath 4K Webcam", 8, 6, 4, 3, 99.99, None),
        ("BP-MNT-070", "BrightPath Monitor Light Bar", 16, 20, 4, 4, 54.99, None),
    ],
    "NH": [
        ("NH-LAMP-065", "Nexus Home Table Lamp", 80, 12, 12, 18, 74.99, "85"),
        ("NH-CLCK-035", "Nexus Home Wall Clock", 32, 14, 14, 4, 44.99, None),
        ("NH-ORGZ-040", "Nexus Home Desk Organizer", 24, 12, 8, 6, 38.99, None),
        ("NH-MIRR-090", "Nexus Home Wall Mirror 24in", 96, 26, 2, 26, 89.99, "85"),
        ("NH-BKND-025", "Nexus Home Marble Bookends", 80, 8, 4, 6, 49.99, None),
        ("NH-TRAY-030", "Nexus Home Serving Tray", 24, 16, 12, 2, 34.99, None),
    ],
}

RETAILERS = [
    ("Target", "target", "Partners Online", 30),
    ("Nordstrom", "nordstrom", "Nordstrom Partner Portal", 45),
    ("Best Buy", "best_buy", "Best Buy Vendor Portal", 30),
    ("Amazon", "amazon", "Vendor Central", 60),
    ("Walmart", "walmart", "Retail Link", 30),
]

RETAILER_VIOLATIONS = {
    "target": ["ASN_LATE", "LABEL_PLACEMENT", "CARTON_OVERAGE", "PALLET_HEIGHT", "PO_SHIP_WINDOW"],
    "nordstrom": ["PACKING_SLIP_MISSING", "LABEL_PLACEMENT", "ROUTING_VIOLATION", "CARTON_WEIGHT", "ASN_LATE"],
    "best_buy": ["ASN_LATE", "CARTON_LABEL_ERROR", "SHIP_WINDOW_EARLY", "PALLET_TI_HI", "EDI_856_MISSING"],
    "amazon": ["PO_ON_TIME", "ASN_ACCURACY", "PREP_VIOLATION", "LABEL_BARCODE_UNREADABLE", "CARTON_CONTENT_MISMATCH"],
    "walmart": ["MABD_VIOLATION", "ASN_LATE", "LABEL_PLACEMENT", "PALLET_HEIGHT", "ROUTING_VIOLATION"],
}

PARCEL_SERVICES = [
    "UPS Ground", "UPS Next Day Air", "UPS 2nd Day Air", "UPS 3 Day Select",
    "FedEx Ground", "FedEx Home Delivery", "FedEx 2Day",
    "USPS Priority Mail",
]

DESTINATIONS = [
    ("New York", "NY", "10001", 3),
    ("Los Angeles", "CA", "90001", 8),
    ("Chicago", "IL", "60601", 4),
    ("Houston", "TX", "77001", 5),
    ("Miami", "FL", "33101", 3),
    ("Seattle", "WA", "98101", 8),
    ("Boston", "MA", "02101", 3),
    ("Denver", "CO", "80201", 6),
    ("Nashville", "TN", "37201", 2),
    ("Phoenix", "AZ", "85001", 7),
    ("Charlotte", "NC", "28201", 2),
    ("Dallas", "TX", "75201", 5),
]

DEPARTMENTS = ["Warehouse", "Shipping", "Receiving", "Returns", "Kitting", "Special Projects"]

EMPLOYEE_ROLES = [
    ("Warehouse Associate", "Warehouse"),
    ("Warehouse Associate", "Warehouse"),
    ("Warehouse Associate", "Warehouse"),
    ("Shift Lead", "Warehouse"),
    ("Shipping Clerk", "Shipping"),
    ("Shipping Clerk", "Shipping"),
    ("Shipping Lead", "Shipping"),
    ("Receiving Clerk", "Receiving"),
    ("Receiving Clerk", "Receiving"),
    ("Returns Processor", "Returns"),
    ("Returns Processor", "Returns"),
    ("Kitting Specialist", "Kitting"),
    ("Kitting Specialist", "Kitting"),
    ("Special Projects Coordinator", "Special Projects"),
    ("Operations Manager", "Warehouse"),
]

# Map departments → most common service types
DEPT_SERVICE_MAP = {
    "Warehouse": ["pick_and_pack", "receiving", "shipping"],
    "Shipping": ["shipping", "pick_and_pack"],
    "Receiving": ["receiving"],
    "Returns": ["returns"],
    "Kitting": ["kitting"],
    "Special Projects": ["special_projects", "kitting"],
}


# ── Helpers ─────────────────────────────────────────────────────

def _ups_tracking() -> str:
    return "1Z" + "".join(str(random.randint(0, 9)) for _ in range(18))


def _fedex_tracking() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(14))


def _usps_tracking() -> str:
    return "9400" + "".join(str(random.randint(0, 9)) for _ in range(18))


def _calc_base_rate(weight_lbs: float) -> float:
    """Parcel base rate from weight tiers."""
    if weight_lbs <= 1:
        return 4.50
    if weight_lbs <= 5:
        return 6.00 + (weight_lbs - 1) * 0.80
    if weight_lbs <= 20:
        return 9.20 + (weight_lbs - 5) * 0.55
    if weight_lbs <= 50:
        return 17.45 + (weight_lbs - 20) * 0.45
    return 31.00 + (weight_lbs - 50) * 0.40


def _calc_dim_weight(l: float, w: float, h: float) -> float:
    return (l * w * h) / 139.0


# ── Seed functions ──────────────────────────────────────────────

def seed_all(conn: sqlite3.Connection) -> dict[str, int]:
    """Seed every table. Returns a dict of table→record_count."""
    counts: dict[str, int] = {}
    cur = conn.cursor()

    # ── 1. Clients ──
    client_ids = {}
    for name, code, industry in CLIENTS:
        email = f"info@{code.lower()}brand.com"
        phone = fake.phone_number()
        website = f"https://www.{code.lower()}brand.com"
        cur.execute(
            "INSERT INTO clients (name, code, industry, contact_email, contact_phone, website) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, code, industry, email, phone, website),
        )
        client_ids[code] = cur.lastrowid
    counts["clients"] = len(CLIENTS)

    # ── 2. Contacts ──
    contact_count = 0
    contact_ids: list[int] = []
    # Client contacts (5-6 per client)
    for code, cid in client_ids.items():
        for _ in range(random.randint(5, 6)):
            fn, ln = fake.first_name(), fake.last_name()
            role = random.choice(["Logistics Manager", "Account Manager", "Shipping Coordinator", "Operations Director", "Warehouse Manager", "VP Supply Chain"])
            cur.execute(
                "INSERT INTO contacts (client_id, first_name, last_name, email, phone, role, contact_type) "
                "VALUES (?, ?, ?, ?, ?, ?, 'client')",
                (cid, fn, ln, f"{fn.lower()}.{ln.lower()}@{code.lower()}brand.com", fake.phone_number(), role),
            )
            contact_ids.append(cur.lastrowid)
            contact_count += 1
    # End-customer contacts (~10 extra)
    for _ in range(10):
        fn, ln = fake.first_name(), fake.last_name()
        cur.execute(
            "INSERT INTO contacts (client_id, first_name, last_name, email, phone, role, contact_type) "
            "VALUES (?, ?, ?, ?, ?, 'Customer', 'end_customer')",
            (random.choice(list(client_ids.values())), fn, ln, fake.email(), fake.phone_number()),
        )
        contact_ids.append(cur.lastrowid)
        contact_count += 1
    counts["contacts"] = contact_count

    # ── 3. Addresses ──
    addr_count = 0
    warehouse_addr_ids: list[int] = []
    dest_addr_ids: list[int] = []

    # All Points warehouse (origin)
    cur.execute(
        "INSERT INTO addresses (client_id, label, street1, city, state, zip_code, is_residential, address_type) "
        "VALUES (NULL, 'warehouse', '1000 Logistics Parkway', 'Atlanta', 'GA', '30318', 0, 'warehouse')",
    )
    warehouse_addr_ids.append(cur.lastrowid)
    addr_count += 1

    # Second warehouse dock
    cur.execute(
        "INSERT INTO addresses (client_id, label, street1, city, state, zip_code, is_residential, address_type) "
        "VALUES (NULL, 'warehouse', '1002 Logistics Parkway, Dock B', 'Atlanta', 'GA', '30318', 0, 'origin')",
    )
    warehouse_addr_ids.append(cur.lastrowid)
    addr_count += 1

    # Client HQ addresses
    client_addr_ids = {}
    for code, cid in client_ids.items():
        city, state, zipcode = fake.city(), fake.state_abbr(), fake.zipcode()
        cur.execute(
            "INSERT INTO addresses (client_id, label, street1, city, state, zip_code, is_residential, address_type) "
            "VALUES (?, 'primary', ?, ?, ?, ?, 0, 'billing')",
            (cid, fake.street_address(), city, state, zipcode),
        )
        client_addr_ids[code] = cur.lastrowid
        addr_count += 1

    # Customer destination addresses (~65)
    for _ in range(65):
        dest = random.choice(DESTINATIONS)
        is_res = random.choice([0, 0, 1])  # ~33% residential
        cid = random.choice(list(client_ids.values()))
        cur.execute(
            "INSERT INTO addresses (client_id, label, street1, city, state, zip_code, is_residential, address_type) "
            "VALUES (?, 'shipping', ?, ?, ?, ?, ?, 'destination')",
            (cid, fake.street_address(), dest[0], dest[1], dest[2], is_res),
        )
        dest_addr_ids.append(cur.lastrowid)
        addr_count += 1
    counts["addresses"] = addr_count

    # ── 4. Products ──
    product_ids: dict[str, list[int]] = {}  # client_code → list of product IDs
    prod_count = 0
    for code, items in PRODUCT_CATALOG.items():
        cid = client_ids[code]
        product_ids[code] = []
        for sku, name, weight_oz, l, w, h, value, fclass in items:
            cur.execute(
                "INSERT INTO products (client_id, sku, name, weight_oz, length_in, width_in, height_in, unit_value, freight_class) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (cid, sku, name, weight_oz, l, w, h, value, fclass),
            )
            product_ids[code].append(cur.lastrowid)
            prod_count += 1
    counts["products"] = prod_count

    # ── 5. Carriers ──
    carrier_ids: dict[str, int] = {}
    for name, code, ctype, acct, tier, factor, days in ALL_CARRIERS:
        cur.execute(
            "INSERT INTO carriers (name, code, carrier_type, account_number, contract_tier, pricing_factor, transit_days) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, code, ctype, acct, tier, factor, days),
        )
        carrier_ids[code] = cur.lastrowid
    counts["carriers"] = len(ALL_CARRIERS)

    # ── 6. Employees ──
    employee_ids: list[tuple[int, str]] = []  # (id, department)
    for role, dept in EMPLOYEE_ROLES:
        fn, ln = fake.first_name(), fake.last_name()
        hire = fake.date_between(start_date="-3y", end_date="-3m").isoformat()
        rate = round(random.uniform(15.0, 28.0), 2)
        if "Lead" in role or "Manager" in role or "Coordinator" in role:
            rate = round(random.uniform(22.0, 35.0), 2)
        cur.execute(
            "INSERT INTO employees (first_name, last_name, email, role, department, hourly_rate, hire_date) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (fn, ln, f"{fn.lower()}.{ln.lower()}@allpointsatl.com", role, dept, rate, hire),
        )
        employee_ids.append((cur.lastrowid, dept))
    counts["employees"] = len(EMPLOYEE_ROLES)

    # ── 7. Retailers ──
    retailer_ids: dict[str, int] = {}
    for name, code, portal, window in RETAILERS:
        cur.execute(
            "INSERT INTO retailers (name, code, portal_name, dispute_window_days) VALUES (?, ?, ?, ?)",
            (name, code, portal, window),
        )
        retailer_ids[code] = cur.lastrowid
    counts["retailers"] = len(RETAILERS)

    # ── 8. Shipments + shipment_items + exceptions ──
    shipment_count = 0
    shipment_item_count = 0
    exception_count = 0
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    base_date = today - timedelta(days=14)  # Data spans last 2 weeks to today
    parcel_carrier_codes = ["UPS", "UPS2", "FEDEX", "USPS"]

    for i in range(220):
        client_code = random.choice(list(client_ids.keys()))
        cid = client_ids[client_code]
        carrier_code = random.choice(parcel_carrier_codes)
        crid = carrier_ids[carrier_code]

        ship_date = base_date + timedelta(days=random.randint(0, 14))
        transit = random.randint(2, 7)
        expected = ship_date + timedelta(days=transit)

        # Determine status
        roll = random.random()
        if roll < 0.30:
            status = "delivered"
            actual = expected + timedelta(days=random.randint(-1, 1))
        elif roll < 0.55:
            status = "in_transit"
            actual = None
        elif roll < 0.70:
            status = "on_time"
            actual = None
        elif roll < 0.85:
            status = "delayed"
            actual = None
        else:
            status = "exception"
            actual = None

        # Service
        if carrier_code in ("UPS", "UPS2"):
            service = random.choice(["UPS Ground", "UPS 2nd Day Air", "UPS 3 Day Select"])
        elif carrier_code == "FEDEX":
            service = random.choice(["FedEx Ground", "FedEx Home Delivery", "FedEx 2Day"])
        else:
            service = "USPS Priority Mail"

        # Tracking
        if carrier_code in ("UPS", "UPS2"):
            tracking = _ups_tracking()
        elif carrier_code == "FEDEX":
            tracking = _fedex_tracking()
        else:
            tracking = _usps_tracking()

        shipment_num = f"SH-{40000 + i}"
        order_num = f"{client_code}-2026-{3000 + i}"

        # Pick a destination address and contact
        dest_id = random.choice(dest_addr_ids) if dest_addr_ids else None
        contact_id = random.choice(contact_ids) if contact_ids else None
        origin_id = random.choice(warehouse_addr_ids)

        # Pick products and calc weight
        prods = product_ids[client_code]
        n_items = random.randint(1, 3)
        selected_prods = random.choices(prods, k=n_items)
        weight_lbs = 0.0

        # Retrieve product weights
        prod_weights = {}
        for pid in set(selected_prods):
            row = cur.execute("SELECT weight_oz FROM products WHERE id = ?", (pid,)).fetchone()
            prod_weights[pid] = row[0] if row else 16.0

        for pid in selected_prods:
            qty = random.randint(1, 2)
            weight_lbs += (prod_weights[pid] * qty) / 16.0

        dest_row = cur.execute("SELECT zip_code FROM addresses WHERE id = ?", (dest_id,)).fetchone() if dest_id else None
        dest_zip = dest_row[0] if dest_row else "10001"
        zone = next((d[3] for d in DESTINATIONS if d[2] == dest_zip), random.randint(2, 8))

        cur.execute(
            "INSERT INTO shipments (shipment_number, order_number, client_id, contact_id, carrier_id, "
            "tracking_number, service, status, ship_date, expected_delivery, actual_delivery, "
            "origin_address_id, dest_address_id, weight_lbs, zone) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                shipment_num, order_num, cid, contact_id, crid,
                tracking, service, status,
                ship_date.strftime("%Y-%m-%d"), expected.strftime("%Y-%m-%d"),
                actual.strftime("%Y-%m-%d") if actual else None,
                origin_id, dest_id, round(weight_lbs, 2), zone,
            ),
        )
        ship_id = cur.lastrowid
        shipment_count += 1

        # Shipment items
        for pid in selected_prods:
            qty = random.randint(1, 2)
            cur.execute(
                "INSERT INTO shipment_items (shipment_id, product_id, quantity) VALUES (?, ?, ?)",
                (ship_id, pid, qty),
            )
            shipment_item_count += 1

        # Exceptions (~30% of shipments)
        if status in ("delayed", "exception") or (status == "in_transit" and random.random() < 0.1):
            etype = random.choice(EXCEPTION_TYPES)
            is_crit = 1 if etype in CRITICAL_EXCEPTION_TYPES else 0
            days_over = random.randint(0, 4) if status in ("delayed", "exception") else 0
            if days_over > 1:
                is_crit = 1
            messages = {
                "weather_delay": f"Weather delay affecting deliveries in the {fake.city()} area",
                "address_issue": f"Unable to deliver: address incomplete or incorrect at {fake.street_address()}",
                "customs_delay": "Package held at customs for documentation review",
                "damaged": "Package reported damaged during transit — inspection required",
                "lost": "Package scan gap — last scanned at sorting facility, location unknown",
                "delivery_attempted": f"Delivery attempted — no one available at {fake.street_address()}",
                "held_at_facility": "Customer requested hold at local facility for pickup",
            }
            cur.execute(
                "INSERT INTO exceptions (shipment_id, exception_type, exception_message, is_critical, days_overdue) "
                "VALUES (?, ?, ?, ?, ?)",
                (ship_id, etype, messages[etype], is_crit, days_over),
            )
            exception_count += 1

    counts["shipments"] = shipment_count
    counts["shipment_items"] = shipment_item_count
    counts["exceptions"] = exception_count

    # ── 9. Emails ──
    email_count = 0
    email_subjects = {
        "tracking_request": [
            "Where is my order?", "Tracking update request", "Order status inquiry",
            "Haven't received tracking info", "When will my package arrive?",
        ],
        "delivery_confirmation": [
            "Was my order delivered?", "Delivery confirmation needed",
            "Package shows delivered but not received", "Confirm delivery status",
        ],
        "inventory_question": [
            "Stock availability inquiry", "When will {sku} be back in stock?",
            "Bulk order availability", "Inventory levels for upcoming order",
        ],
        "billing_question": [
            "Invoice discrepancy", "Question about recent charge",
            "Payment terms inquiry", "Need updated invoice",
        ],
        "shipping_issue": [
            "Damaged package received", "Wrong items shipped",
            "Missing items in shipment", "Package arrived open/tampered",
        ],
        "complex_issue": [
            "Ongoing delivery problems with multiple orders",
            "Escalation: repeated shipping errors",
            "Request for account review and rate adjustment",
            "Complaint: service quality degradation",
        ],
    }

    for i in range(160):
        cat = random.choice(EMAIL_CATEGORIES)
        subjects = email_subjects[cat]
        subject = random.choice(subjects)
        sender_name = fake.name()
        sender_email = fake.email()
        body = fake.paragraph(nb_sentences=random.randint(3, 8))
        received = (base_date + timedelta(
            days=random.randint(0, 14),
            hours=random.randint(6, 20),
            minutes=random.randint(0, 59),
        )).isoformat()
        is_read = random.choice([0, 0, 1])
        confidence = round(random.uniform(0.6, 0.99), 2) if random.random() > 0.3 else None
        action = None
        if confidence and confidence > 0.7 and cat in ("tracking_request", "delivery_confirmation"):
            action = "auto_resolved"
        elif confidence:
            action = "escalated"

        cid = random.choice(list(client_ids.values())) if random.random() > 0.3 else None
        msg_id = f"MSG-{10000 + i}"

        cur.execute(
            "INSERT INTO emails (message_id, sender_name, sender_email, subject, body_preview, body_text, "
            "received_at, is_read, category, confidence, action_taken, client_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (msg_id, sender_name, sender_email, subject, body[:200], body, received, is_read, cat, confidence, action, cid),
        )
        email_count += 1
    counts["emails"] = email_count

    # ── 10. Email templates ──
    templates = [
        ("tracking_request", "Tracking Auto-Reply", "Re: {subject}",
         "Hi {sender_name},\n\nThank you for reaching out! Your order {order_number} is currently {status}. "
         "Track your package here: {tracking_url}\n\nBest,\nAll Points ATL Customer Service"),
        ("delivery_confirmation", "Delivery Confirmation Reply", "Re: {subject}",
         "Hi {sender_name},\n\nYour order {order_number} was delivered on {delivery_date}. "
         "If you have not received it, please reply to this email.\n\nBest,\nAll Points ATL Customer Service"),
        ("shipping_issue", "Shipping Issue Acknowledgement", "Re: {subject} - We're on it",
         "Hi {sender_name},\n\nWe're sorry to hear about the issue with your shipment. "
         "A team member will investigate and follow up within 24 hours.\n\nAll Points ATL Customer Service"),
        ("billing_question", "Billing Inquiry Received", "Re: {subject}",
         "Hi {sender_name},\n\nWe've received your billing inquiry and our accounts team will respond within 1-2 business days.\n\nAll Points ATL"),
        ("inventory_question", "Inventory Inquiry", "Re: {subject}",
         "Hi {sender_name},\n\nThank you for your interest. We're checking current stock levels and will get back to you shortly.\n\nAll Points ATL"),
        ("complex_issue", "Escalation Received", "Re: {subject} - Escalated",
         "Hi {sender_name},\n\nYour request has been escalated to our operations team. "
         "You'll hear from a dedicated representative within 4 business hours.\n\nAll Points ATL"),
    ]
    for cat, tname, subj, body in templates:
        cur.execute(
            "INSERT INTO email_templates (category, template_name, subject_template, body_template) VALUES (?, ?, ?, ?)",
            (cat, tname, subj, body),
        )
    counts["email_templates"] = len(templates)

    # ── 11. Labor entries ──
    labor_count = 0
    labor_start = today - timedelta(days=59)  # Last ~2 months of labor data
    for day_offset in range(59):
        work_date = labor_start + timedelta(days=day_offset)
        if work_date.weekday() >= 5:  # skip weekends (mostly)
            if random.random() > 0.15:
                continue
        # Each day, ~7-10 employees log hours across various clients
        day_workers = random.sample(employee_ids, k=min(random.randint(7, 10), len(employee_ids)))
        for emp_id, dept in day_workers:
            cid = random.choice(list(client_ids.values()))
            svcs = DEPT_SERVICE_MAP.get(dept, ["pick_and_pack"])
            svc = random.choice(svcs)
            hours = round(random.uniform(2.0, 8.0), 1)
            cur.execute(
                "INSERT INTO labor_entries (client_id, employee_id, work_date, hours, service_type) "
                "VALUES (?, ?, ?, ?, ?)",
                (cid, emp_id, work_date.strftime("%Y-%m-%d"), hours, svc),
            )
            labor_count += 1
    counts["labor_entries"] = labor_count

    # ── 12. Invoices + line items ──
    invoice_count = 0
    line_item_count = 0
    inv_num = 1
    # Two invoice periods: last month and current month
    last_month = (today.replace(day=1) - timedelta(days=1))
    invoice_months = [
        (last_month.strftime("%Y-%m"), last_month.replace(day=28)),
        (today.strftime("%Y-%m"), today - timedelta(days=1)),
    ]
    for month_prefix, inv_date in invoice_months:
        for code, cid in client_ids.items():
            due_date = inv_date + timedelta(days=30)

            # Calculate labor cost for this client/month
            rows = cur.execute(
                "SELECT SUM(le.hours * e.hourly_rate) as total, SUM(le.hours) as hrs "
                "FROM labor_entries le JOIN employees e ON le.employee_id = e.id "
                "WHERE le.client_id = ? AND le.work_date LIKE ?",
                (cid, f"{month_prefix}%"),
            ).fetchone()
            labor_total = rows[0] if rows[0] else 0
            labor_hrs = rows[1] if rows[1] else 0

            if labor_total == 0:
                continue

            # Invoice amount = labor cost + margin (15-40%)
            margin = random.uniform(1.15, 1.40)
            total_amount = round(labor_total * margin, 2)

            # Status: older invoices mostly paid, newer ones mostly pending
            is_older = (inv_date < today - timedelta(days=20))
            if is_older:
                status = random.choice(["paid", "paid", "paid", "paid", "overdue"])
                payment_date = (inv_date + timedelta(days=random.randint(10, 25))).strftime("%Y-%m-%d") if status == "paid" else None
            else:
                status = random.choice(["pending", "pending", "paid"])
                payment_date = (inv_date + timedelta(days=random.randint(5, 15))).strftime("%Y-%m-%d") if status == "paid" else None

            inv_number = f"INV-2026-{inv_num:03d}"
            cur.execute(
                "INSERT INTO invoices (client_id, invoice_number, invoice_date, due_date, total_amount, status, payment_date) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cid, inv_number, inv_date.strftime("%Y-%m-%d"), due_date.strftime("%Y-%m-%d"), total_amount, status, payment_date),
            )
            inv_id = cur.lastrowid
            invoice_count += 1
            inv_num += 1

            # Line items by service type
            svc_rows = cur.execute(
                "SELECT le.service_type, SUM(le.hours) as hrs, SUM(le.hours * e.hourly_rate) as cost "
                "FROM labor_entries le JOIN employees e ON le.employee_id = e.id "
                "WHERE le.client_id = ? AND le.work_date LIKE ? "
                "GROUP BY le.service_type",
                (cid, f"{month_prefix}%"),
            ).fetchall()
            for svc_row in svc_rows:
                svc_type = svc_row[0]
                svc_hrs = svc_row[1]
                svc_cost = svc_row[2]
                line_amount = round(svc_cost * margin, 2)
                desc = svc_type.replace("_", " ").title()
                cur.execute(
                    "INSERT INTO invoice_line_items (invoice_id, description, service_type, quantity, unit_price, amount) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (inv_id, f"{desc} Services", svc_type, round(svc_hrs, 1), round(line_amount / svc_hrs, 2) if svc_hrs else 0, line_amount),
                )
                line_item_count += 1

    counts["invoices"] = invoice_count
    counts["invoice_line_items"] = line_item_count

    # ── 13. Orders + order_items + rates + labels ──
    order_count = 0
    order_item_count = 0
    rate_count = 0
    label_count = 0

    for i in range(120):
        client_code = random.choice(list(client_ids.keys()))
        cid = client_ids[client_code]
        prods = product_ids[client_code]
        prod_id = random.choice(prods)
        qty = random.choices([1, 1, 1, 2, 3], k=1)[0]

        prod_row = cur.execute(
            "SELECT weight_oz, length_in, width_in, height_in, unit_value FROM products WHERE id = ?",
            (prod_id,),
        ).fetchone()
        w_oz, p_l, p_w, p_h, p_val = prod_row

        total_weight_oz = w_oz * qty
        height = p_h * qty  # stack vertically
        declared = round(p_val * qty, 2)

        dest = random.choice(DESTINATIONS)
        dest_addr = random.choice(dest_addr_ids) if dest_addr_ids else None
        is_res = random.choice([0, 0, 1])
        zone = dest[3]

        order_date = (base_date + timedelta(days=random.randint(0, 14), hours=random.randint(6, 18))).isoformat()
        order_num = f"APO-{2000 + i}"

        status = "awaiting_shipment" if random.random() < 0.7 else "shipped"

        cur.execute(
            "INSERT INTO orders (order_number, client_id, order_date, status, ship_to_address_id, "
            "is_residential, declared_value, total_weight_oz, length_in, width_in, height_in, zone, service_requested) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ground')",
            (order_num, cid, order_date, status, dest_addr, is_res, declared, total_weight_oz, p_l, p_w, height, zone),
        )
        ord_id = cur.lastrowid
        order_count += 1

        # Order items
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
            (ord_id, prod_id, qty, p_val),
        )
        order_item_count += 1

        # Generate 4 rates per order (one per parcel carrier)
        weight_lbs = total_weight_oz / 16.0
        dim_weight = _calc_dim_weight(p_l, p_w, height)
        billable = max(weight_lbs, dim_weight)
        base = _calc_base_rate(billable)
        zone_mult = 1.0 + (zone - 2) * 0.08
        base *= zone_mult

        cheapest_rate_id = None
        cheapest_total = float("inf")

        for carr_name, carr_code, _, _, _, factor, days in PARCEL_CARRIERS:
            crid = carrier_ids[carr_code]

            # Carrier-specific adjustments
            if carr_code == "USPS" and weight_lbs > 15:
                rate = base * factor * 1.12
            elif carr_code == "USPS" and weight_lbs <= 4:
                rate = base * factor * 0.82
            elif carr_code == "FEDEX" and zone > 4:
                rate = base * factor * 1.06
            elif carr_code == "FEDEX":
                rate = base * factor * 0.93
            else:
                rate = base * factor

            rate *= random.uniform(0.97, 1.03)
            rate = round(rate, 2)
            fuel = round(rate * 0.095, 2)
            res_surcharge = 4.35 if is_res else 0.0
            total = round(rate + fuel + res_surcharge, 2)

            transit = max(2, 1 + zone // 2) + random.choice([0, 0, 0, 1])
            del_date = (base_date + timedelta(days=transit + 1)).strftime("%Y-%m-%d")

            svc_code = f"{carr_code.lower()}_ground"
            svc_name = f"{carr_name} Ground" if "USPS" not in carr_name else "USPS Priority Mail"

            cur.execute(
                "INSERT INTO rates (order_id, carrier_id, service_code, service_name, base_rate, "
                "fuel_surcharge, residential_surcharge, total_amount, billable_weight_lbs, "
                "delivery_days, delivery_date, zone, is_cheapest) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)",
                (ord_id, crid, svc_code, svc_name, rate, fuel, res_surcharge, total, round(billable, 2), transit, del_date, zone),
            )
            if total < cheapest_total:
                cheapest_total = total
                cheapest_rate_id = cur.lastrowid
            rate_count += 1

        # Mark cheapest
        if cheapest_rate_id:
            cur.execute("UPDATE rates SET is_cheapest = 1 WHERE id = ?", (cheapest_rate_id,))

        # Create label for shipped orders
        if status == "shipped" and cheapest_rate_id:
            rate_row = cur.execute(
                "SELECT carrier_id, service_name, total_amount FROM rates WHERE id = ?",
                (cheapest_rate_id,),
            ).fetchone()
            tracking = _ups_tracking()  # simplified
            cur.execute(
                "INSERT INTO labels (order_id, rate_id, tracking_number, carrier_id, service_name, cost) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (ord_id, cheapest_rate_id, tracking, rate_row[0], rate_row[1], rate_row[2]),
            )
            label_count += 1

    counts["orders"] = order_count
    counts["order_items"] = order_item_count
    counts["rates"] = rate_count
    counts["labels"] = label_count

    # ── 14. Chargebacks + evidence_files + disputes ──
    cb_count = 0
    ev_count = 0
    disp_count = 0

    for i in range(35):
        ret_code = random.choice(list(RETAILER_VIOLATIONS.keys()))
        ret_id = retailer_ids[ret_code]
        ret_row = cur.execute("SELECT dispute_window_days FROM retailers WHERE id = ?", (ret_id,)).fetchone()
        window = ret_row[0]

        client_code = random.choice(list(client_ids.keys()))
        cid = client_ids[client_code]
        violation = random.choice(RETAILER_VIOLATIONS[ret_code])

        carrier_code = random.choice(["UPS", "FEDEX", "XPO", "ESTES", "ODFL"])
        crid = carrier_ids[carrier_code]

        amount = round(random.uniform(200, 15000), 2)
        cb_date = base_date + timedelta(days=random.randint(-10, 10))
        deadline = cb_date + timedelta(days=window)
        ship_date = cb_date - timedelta(days=random.randint(5, 15))
        del_date = ship_date + timedelta(days=random.randint(3, 8))

        # Status distribution
        roll = random.random()
        if roll < 0.35:
            cb_status = "new"
        elif roll < 0.50:
            cb_status = "reviewing"
        elif roll < 0.70:
            cb_status = "disputed"
        elif roll < 0.82:
            cb_status = "won"
        elif roll < 0.94:
            cb_status = "lost"
        else:
            cb_status = "expired"

        cb_num = f"CB-{10000 + i}"
        po_num = f"PO-{400000 + i}"
        sh_num = f"SH-{50000 + i}"
        bol_num = f"BOL-{100000 + i}"

        if carrier_code in ("UPS", "UPS2"):
            tracking = _ups_tracking()
        elif carrier_code == "FEDEX":
            tracking = _fedex_tracking()
        else:
            tracking = f"PRO-{random.randint(100000, 999999)}"

        cur.execute(
            "INSERT INTO chargebacks (chargeback_number, retailer_id, client_id, carrier_id, po_number, "
            "shipment_id, bol_number, violation_code, chargeback_amount, chargeback_date, dispute_deadline, "
            "ship_date, delivery_date, tracking_number, units_shipped, cartons, pallets, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                cb_num, ret_id, cid, crid, po_num, sh_num, bol_num, violation,
                amount, cb_date.strftime("%Y-%m-%d"), deadline.strftime("%Y-%m-%d"),
                ship_date.strftime("%Y-%m-%d"), del_date.strftime("%Y-%m-%d"),
                tracking, random.randint(24, 5000), random.randint(2, 120), random.randint(1, 12),
                cb_status,
            ),
        )
        cb_id = cur.lastrowid
        cb_count += 1

        # Evidence files (2-4 per chargeback)
        evidence_types = [
            ("bol", f"BOL_{bol_num}.pdf", "Bill of Lading", "ShipStation"),
            ("tracking_summary", f"Tracking_{tracking[:10]}.pdf", "Carrier tracking history", "ShipStation"),
            ("pod", f"POD_{sh_num}.pdf", "Proof of Delivery", "Carrier Portal"),
            ("asn_confirmation", f"ASN_{po_num}.pdf", "EDI 856 transmission log", "EDI System"),
            ("label_sample", f"Label_{sh_num}.pdf", "GS1-128 label sample", "WMS"),
            ("pick_ticket", f"Pick_{po_num}.pdf", "Pick ticket showing carton counts", "WMS"),
            ("weight_log", f"Weight_{sh_num}.csv", "Scale weight log", "Packing Station"),
            ("pallet_config", f"Pallet_{sh_num}.pdf", "Pallet build specification", "WMS"),
        ]
        n_evidence = random.randint(2, 4)
        selected_evidence = random.sample(evidence_types, k=min(n_evidence, len(evidence_types)))
        for etype, fname, desc, source in selected_evidence:
            auto = 1 if random.random() > 0.2 else 0
            cur.execute(
                "INSERT INTO evidence_files (chargeback_id, evidence_type, file_name, description, source, url, is_auto_compiled) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cb_id, etype, fname, desc, source, f"https://files.allpointsatl.com/evidence/{fname}", auto),
            )
            ev_count += 1

        # Disputes (for disputed/won/lost chargebacks)
        if cb_status in ("disputed", "won", "lost"):
            d_ref = f"DSP-{random.randint(100000, 999999)}" if cb_status != "disputed" or random.random() > 0.5 else None
            d_status = "submitted" if cb_status == "disputed" else cb_status
            submitted = (cb_date + timedelta(days=random.randint(3, 10))).isoformat() if d_status != "draft" else None
            subject = f"Chargeback Dispute: {cb_num} | {po_num}"
            body = (
                f"To Whom It May Concern,\n\n"
                f"We are writing to formally dispute chargeback {cb_num} for violation {violation} "
                f"({VIOLATION_DESCRIPTIONS.get(violation, 'Unknown violation')}).\n\n"
                f"PO: {po_num}\nShipment: {sh_num}\nBOL: {bol_num}\nAmount: ${amount:,.2f}\n\n"
                f"We have attached supporting evidence demonstrating compliance with the stated requirements.\n\n"
                f"Regards,\nAll Points ATL Compliance Department"
            )
            cur.execute(
                "INSERT INTO disputes (chargeback_id, dispute_reference, letter_subject, letter_body, "
                "evidence_count, submitted_at, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cb_id, d_ref, subject, body, n_evidence, submitted, d_status),
            )
            disp_count += 1

    counts["chargebacks"] = cb_count
    counts["evidence_files"] = ev_count
    counts["disputes"] = disp_count

    # ── 15. LTL quotes + bookings ──
    ltl_quote_count = 0
    ltl_booking_count = 0
    ltl_carrier_codes = ["XPO", "ESTES", "ODFL", "ABF", "YRC"]

    for i in range(55):
        client_code = random.choice(list(client_ids.keys()))
        cid = client_ids[client_code]
        dest = random.choice(DESTINATIONS)
        weight = random.randint(300, 12000)
        fclass = random.choice(["50", "65", "70", "85", "100", "125", "150"])
        pieces = random.randint(1, 8)
        origin_zip = "30318"
        dest_zip = dest[2]

        class_mult = FREIGHT_CLASS_MULTIPLIERS.get(fclass, 1.0)

        # Generate a quote from each LTL carrier
        cheapest_qid = None
        cheapest_cost = float("inf")
        group_quotes = []

        for carr_name, carr_code, _, _, _, factor, days in LTL_CARRIERS:
            crid = carrier_ids[carr_code]
            base = weight * 0.35 * class_mult * factor
            base *= random.uniform(0.96, 1.04)
            fuel = base * 0.22
            accessorials = 75.0 if random.random() < 0.25 else 0.0
            total = round(base + fuel + accessorials, 2)

            transit = days + random.choice([0, 0, 1])
            est_del = (base_date + timedelta(days=transit + 1)).strftime("%Y-%m-%d")
            valid = (base_date + timedelta(days=7)).strftime("%Y-%m-%d")
            q_num = f"QT-{carr_code}-{20260200 + i:08d}{random.randint(100,999)}"

            cur.execute(
                "INSERT INTO ltl_quotes (quote_number, client_id, carrier_id, origin_zip, destination_zip, "
                "weight_lbs, freight_class, pieces, base_rate, fuel_surcharge, accessorials, total_cost, "
                "transit_days, estimated_delivery, valid_until, is_cheapest) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)",
                (q_num, cid, crid, origin_zip, dest_zip, weight, fclass, pieces,
                 round(base, 2), round(fuel, 2), accessorials, total, transit, est_del, valid),
            )
            qid = cur.lastrowid
            group_quotes.append(qid)
            ltl_quote_count += 1

            if total < cheapest_cost:
                cheapest_cost = total
                cheapest_qid = qid

        # Mark cheapest
        if cheapest_qid:
            cur.execute("UPDATE ltl_quotes SET is_cheapest = 1 WHERE id = ?", (cheapest_qid,))

        # Book ~40% of quote groups
        if random.random() < 0.40 and cheapest_qid:
            pickup = (base_date + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d")
            bol = f"BOL-{20260200 + i}{random.randint(10,99)}"
            pro = f"PRO-{100000 + i}"
            conf = f"CONF-{20260200 + i}{random.randint(10,99)}"

            shipper_name = "All Points ATL"
            consignee = fake.company()

            bk_status = random.choice(["confirmed", "confirmed", "picked_up", "in_transit", "delivered"])

            cur.execute(
                "INSERT INTO ltl_bookings (quote_id, bol_number, pro_number, confirmation_number, "
                "pickup_date, shipper_name, shipper_phone, shipper_email, shipper_address, "
                "consignee_name, consignee_phone, consignee_email, consignee_address, status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    cheapest_qid, bol, pro, conf, pickup,
                    shipper_name, "(404) 555-0100", "shipping@allpointsatl.com",
                    "1000 Logistics Parkway, Atlanta, GA 30318",
                    consignee, fake.phone_number(), fake.company_email(),
                    f"{fake.street_address()}, {dest[0]}, {dest[1]} {dest[2]}",
                    bk_status,
                ),
            )
            ltl_booking_count += 1

    counts["ltl_quotes"] = ltl_quote_count
    counts["ltl_bookings"] = ltl_booking_count

    # ── 16. Inventory + receiving records ──
    inv_count = 0
    recv_count = 0
    recv_item_count = 0

    # Inventory levels for every product
    bin_aisles = ["A", "B", "C", "D", "E"]
    for code, pids in product_ids.items():
        cid = client_ids[code]
        for idx, pid in enumerate(pids):
            on_hand = random.randint(20, 800)
            allocated = random.randint(0, min(on_hand, on_hand // 3))
            aisle = random.choice(bin_aisles)
            rack = random.randint(1, 12)
            shelf = random.randint(1, 4)
            bin_loc = f"{aisle}-{rack:02d}-{shelf:02d}"
            last_counted = (today - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            last_recv = (today - timedelta(days=random.randint(1, 21))).strftime("%Y-%m-%d")
            cur.execute(
                "INSERT INTO inventory (product_id, client_id, quantity_on_hand, quantity_allocated, "
                "bin_location, last_counted, last_received) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (pid, cid, on_hand, allocated, bin_loc, last_counted, last_recv),
            )
            inv_count += 1
    counts["inventory"] = inv_count

    # Receiving records — some with discrepancies (Michael's go-to example)
    DISCREPANCY_NOTES = [
        "2 units crushed in transit",
        "Outer carton damaged, contents intact — count verified short",
        "Pallet wrap torn, 5 units missing from top layer",
        "Vendor confirmed short-ship — replacement PO issued",
        "Water damage to bottom carton — 3 units unsalvageable",
        "Miscount by vendor — actual quantity verified by receiving team",
        None,  # No issue
        None,
        None,
    ]

    for i in range(40):
        client_code = random.choice(list(client_ids.keys()))
        cid = client_ids[client_code]
        recv_date = (today - timedelta(days=random.randint(0, 28))).strftime("%Y-%m-%d")
        po = f"IPO-{600000 + i}"
        carrier = random.choice(["UPS Freight", "FedEx Freight", "XPO Logistics", "Estes Express", "FedEx Ground"])
        tracking = _ups_tracking() if "UPS" in carrier else _fedex_tracking()

        # ~30% have a discrepancy
        has_disc = random.random() < 0.30
        rec_status = "discrepancy" if has_disc else "completed"

        cur.execute(
            "INSERT INTO receiving_records (client_id, po_number, received_date, carrier, tracking_number, status) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (cid, po, recv_date, carrier, tracking, rec_status),
        )
        recv_id = cur.lastrowid
        recv_count += 1

        # 1-4 line items per receiving record
        prods = product_ids[client_code]
        n_items = random.randint(1, 4)
        for _ in range(n_items):
            pid = random.choice(prods)
            expected = random.randint(50, 2000)
            if has_disc and random.random() < 0.6:
                # Short receipt — received less than expected
                short = random.randint(1, max(1, expected // 20))
                received = expected - short
                damaged = random.randint(0, min(3, short))
                note = random.choice([n for n in DISCREPANCY_NOTES if n is not None])
            else:
                received = expected
                damaged = 0
                note = None
            cur.execute(
                "INSERT INTO receiving_items (receiving_id, product_id, quantity_expected, "
                "quantity_received, quantity_damaged, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (recv_id, pid, expected, received, damaged, note),
            )
            recv_item_count += 1

    counts["receiving_records"] = recv_count
    counts["receiving_items"] = recv_item_count

    conn.commit()
    return counts
