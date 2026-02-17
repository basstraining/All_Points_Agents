"""Shared constants for All Points Agents."""

# ---------- Violation codes (Chargeback Defense) ----------
VIOLATION_DESCRIPTIONS = {
    "ASN_LATE": "Advanced Shipping Notice (ASN/EDI 856) received after shipment delivery",
    "LABEL_PLACEMENT": "GS1-128 shipping label not placed in correct position on carton",
    "CARTON_OVERAGE": "Shipped more cartons than specified on purchase order",
    "PALLET_HEIGHT": "Pallet height exceeds retailer maximum specification",
    "PO_SHIP_WINDOW": "Shipment fell outside the PO must-ship-by / cancel date window",
    "PACKING_SLIP_MISSING": "Packing slip not included or not visible in carton",
    "ROUTING_VIOLATION": "Did not use retailer-specified carrier or routing guide",
    "CARTON_WEIGHT": "Carton weight exceeds retailer maximum per-carton limit",
    "CARTON_LABEL_ERROR": "Carton label contains incorrect or unreadable information",
    "SHIP_WINDOW_EARLY": "Shipment arrived before the earliest acceptable delivery date",
    "PALLET_TI_HI": "Pallet configuration does not match required TI/HI spec",
    "EDI_856_MISSING": "EDI 856 (ASN) not transmitted within required timeframe",
    "PO_ON_TIME": "Purchase order not delivered within the on-time delivery window",
    "ASN_ACCURACY": "ASN content does not match actual shipment contents",
    "PREP_VIOLATION": "Items not prepped per Amazon packaging requirements (poly bag, bubble wrap, etc.)",
    "LABEL_BARCODE_UNREADABLE": "Barcode on shipping label cannot be scanned at receiving",
    "CARTON_CONTENT_MISMATCH": "Carton contents do not match what was declared on ASN",
    "MABD_VIOLATION": "Shipment did not meet Must Arrive By Date",
}

# ---------- Exception types (Carrier Exception Monitor) ----------
CRITICAL_EXCEPTION_TYPES = {"address_issue", "customs_delay", "damaged", "lost"}

EXCEPTION_TYPES = [
    "weather_delay",
    "address_issue",
    "customs_delay",
    "damaged",
    "lost",
    "delivery_attempted",
    "held_at_facility",
]

SHIPMENT_STATUSES = ["on_time", "in_transit", "delayed", "exception", "delivered"]

# ---------- Email categories (Email Triage) ----------
EMAIL_CATEGORIES = [
    "tracking_request",
    "delivery_confirmation",
    "inventory_question",
    "billing_question",
    "shipping_issue",
    "complex_issue",
]

AUTO_RESOLVE_CATEGORIES = {"tracking_request", "delivery_confirmation"}
AUTO_RESOLVE_CONFIDENCE_THRESHOLD = 0.7

# ---------- Labor service types (Profitability / 3PL) ----------
SERVICE_TYPES = [
    "pick_and_pack",
    "receiving",
    "kitting",
    "returns",
    "shipping",
    "special_projects",
]

# ---------- Freight classes (LTL Automation) ----------
FREIGHT_CLASSES = [
    "50", "55", "60", "65", "70", "77.5", "85", "92.5",
    "100", "110", "125", "150", "175", "200", "250", "300", "400", "500",
]

FREIGHT_CLASS_MULTIPLIERS = {
    "50": 0.70, "55": 0.75, "60": 0.80, "65": 0.85,
    "70": 0.90, "77.5": 0.95, "85": 1.00, "92.5": 1.10,
    "100": 1.20, "110": 1.30, "125": 1.40, "150": 1.60,
    "175": 1.80, "200": 2.00, "250": 2.50, "300": 3.00,
    "400": 4.00, "500": 5.00,
}

# ---------- Carrier service codes (Rate Shopping) ----------
PARCEL_SERVICE_CODES = {
    "ups_ground": "UPS Ground",
    "ups_ground_legacy": "UPS Ground (Account 1)",
    "ups_ground_new": "UPS Ground (Account 2)",
    "fedex_ground": "FedEx Ground",
    "fedex_home": "FedEx Home Delivery",
    "usps_priority": "USPS Priority Mail",
}

# ---------- Zone multipliers (from Atlanta hub) ----------
ZONE_MULTIPLIER_BASE = 0.08  # Each zone above 2 adds 8%

# ---------- Retailer portals (Chargeback Defense) ----------
RETAILER_PORTALS = {
    "target": "Partners Online",
    "nordstrom": "Nordstrom Partner Portal",
    "best_buy": "Best Buy Vendor Portal",
    "amazon": "Vendor Central",
    "walmart": "Retail Link",
}

# ---------- All Points ATL info ----------
COMPANY_NAME = "All Points ATL"
COMPANY_PHONE = "(404) 555-0100"
COMPANY_EMAIL = "info@allpointsatl.com"
COMPLIANCE_EMAIL = "compliance@allpointsatl.com"
WAREHOUSE_ZIP = "30318"  # Atlanta warehouse origin
