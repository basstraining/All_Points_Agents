-- All Points Agents - Centralized Database Schema
-- 21 tables: 6 core + 15 domain-specific
-- All domain tables reference core tables via foreign keys

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ============================================================
-- CORE TABLES (shared across all agents)
-- ============================================================

CREATE TABLE IF NOT EXISTS clients (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    code            TEXT    NOT NULL UNIQUE,       -- Short code (e.g., "TB", "NS")
    industry        TEXT    NOT NULL,
    contact_email   TEXT,
    contact_phone   TEXT,
    website         TEXT,
    status          TEXT    NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'inactive', 'onboarding')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS contacts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id       INTEGER,
    first_name      TEXT    NOT NULL,
    last_name       TEXT    NOT NULL,
    email           TEXT    NOT NULL,
    phone           TEXT,
    role            TEXT,                           -- e.g., "Logistics Manager", "Customer"
    contact_type    TEXT    NOT NULL DEFAULT 'client'
                            CHECK (contact_type IN ('client', 'end_customer', 'vendor')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS addresses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id       INTEGER,
    contact_id      INTEGER,
    label           TEXT    NOT NULL DEFAULT 'primary',  -- primary, shipping, billing, warehouse
    street1         TEXT    NOT NULL,
    street2         TEXT,
    city            TEXT    NOT NULL,
    state           TEXT    NOT NULL,
    zip_code        TEXT    NOT NULL,
    country         TEXT    NOT NULL DEFAULT 'US',
    is_residential  INTEGER NOT NULL DEFAULT 0,     -- 0=commercial, 1=residential
    address_type    TEXT    NOT NULL DEFAULT 'destination'
                            CHECK (address_type IN ('origin', 'destination', 'billing', 'warehouse')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);

CREATE TABLE IF NOT EXISTS products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id       INTEGER NOT NULL,
    sku             TEXT    NOT NULL UNIQUE,
    name            TEXT    NOT NULL,
    description     TEXT,
    weight_oz       REAL    NOT NULL,               -- Weight in ounces
    length_in       REAL,                           -- Dimensions in inches
    width_in        REAL,
    height_in       REAL,
    unit_value      REAL    NOT NULL,               -- Dollar value per unit
    freight_class   TEXT,                           -- NMFC freight class for LTL
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS carriers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    code            TEXT    NOT NULL UNIQUE,         -- Short code (e.g., "UPS", "FEDEX")
    carrier_type    TEXT    NOT NULL
                            CHECK (carrier_type IN ('parcel', 'ltl', 'both')),
    account_number  TEXT,
    contract_tier   TEXT    NOT NULL DEFAULT 'standard'
                            CHECK (contract_tier IN ('standard', 'negotiated', 'commercial_plus', 'premium')),
    pricing_factor  REAL    NOT NULL DEFAULT 1.0,   -- Multiplier vs baseline
    transit_days    INTEGER NOT NULL DEFAULT 3,      -- Default transit time
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS employees (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT    NOT NULL,
    last_name       TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    role            TEXT    NOT NULL,                -- e.g., "Warehouse Associate", "Shift Lead"
    department      TEXT    NOT NULL,                -- e.g., "Warehouse", "Shipping", "Receiving"
    hourly_rate     REAL    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'inactive')),
    hire_date       TEXT    NOT NULL,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ============================================================
-- DOMAIN TABLES: Carrier Exception Monitor
-- ============================================================

CREATE TABLE IF NOT EXISTS shipments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_number TEXT    NOT NULL UNIQUE,         -- e.g., "SH-40221"
    order_number    TEXT    NOT NULL,                -- e.g., "TB-2026-3341"
    client_id       INTEGER NOT NULL,
    contact_id      INTEGER,                        -- End customer
    carrier_id      INTEGER NOT NULL,
    tracking_number TEXT    NOT NULL,
    service         TEXT    NOT NULL,                -- e.g., "UPS Ground", "FedEx 2Day"
    status          TEXT    NOT NULL DEFAULT 'in_transit'
                            CHECK (status IN ('on_time', 'in_transit', 'delayed', 'exception', 'delivered')),
    ship_date       TEXT    NOT NULL,
    expected_delivery TEXT  NOT NULL,
    actual_delivery TEXT,
    origin_address_id   INTEGER,
    dest_address_id     INTEGER,
    weight_lbs      REAL    NOT NULL,
    declared_value  REAL,
    zone            INTEGER,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (carrier_id) REFERENCES carriers(id),
    FOREIGN KEY (origin_address_id) REFERENCES addresses(id),
    FOREIGN KEY (dest_address_id) REFERENCES addresses(id)
);

CREATE TABLE IF NOT EXISTS shipment_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id     INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (shipment_id) REFERENCES shipments(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS exceptions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id     INTEGER NOT NULL,
    exception_type  TEXT    NOT NULL
                            CHECK (exception_type IN (
                                'weather_delay', 'address_issue', 'customs_delay',
                                'damaged', 'lost', 'delivery_attempted',
                                'held_at_facility'
                            )),
    exception_message TEXT  NOT NULL,
    is_critical     INTEGER NOT NULL DEFAULT 0,     -- 0=standard, 1=critical
    days_overdue    INTEGER NOT NULL DEFAULT 0,
    detected_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    resolved_at     TEXT,
    resolution_note TEXT,
    FOREIGN KEY (shipment_id) REFERENCES shipments(id)
);


-- ============================================================
-- DOMAIN TABLES: Email Triage
-- ============================================================

CREATE TABLE IF NOT EXISTS emails (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id      TEXT    NOT NULL UNIQUE,         -- External message ID
    sender_name     TEXT    NOT NULL,
    sender_email    TEXT    NOT NULL,
    subject         TEXT    NOT NULL,
    body_preview    TEXT    NOT NULL,
    body_text       TEXT,
    received_at     TEXT    NOT NULL,
    is_read         INTEGER NOT NULL DEFAULT 0,
    category        TEXT
                            CHECK (category IN (
                                'tracking_request', 'delivery_confirmation',
                                'inventory_question', 'billing_question',
                                'shipping_issue', 'complex_issue'
                            )),
    confidence      REAL,
    action_taken    TEXT
                            CHECK (action_taken IS NULL OR action_taken IN (
                                'auto_resolved', 'escalated', 'pending'
                            )),
    client_id       INTEGER,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS email_templates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    category        TEXT    NOT NULL,
    template_name   TEXT    NOT NULL,
    subject_template TEXT   NOT NULL,
    body_template   TEXT    NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);


-- ============================================================
-- DOMAIN TABLES: Profitability
-- ============================================================

CREATE TABLE IF NOT EXISTS labor_entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id       INTEGER NOT NULL,
    employee_id     INTEGER NOT NULL,
    work_date       TEXT    NOT NULL,
    hours           REAL    NOT NULL,
    service_type    TEXT    NOT NULL
                            CHECK (service_type IN (
                                'pick_and_pack', 'receiving', 'kitting',
                                'returns', 'shipping', 'special_projects'
                            )),
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS invoices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id       INTEGER NOT NULL,
    invoice_number  TEXT    NOT NULL UNIQUE,         -- e.g., "INV-2026-001"
    invoice_date    TEXT    NOT NULL,
    due_date        TEXT    NOT NULL,
    total_amount    REAL    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('paid', 'pending', 'overdue')),
    payment_date    TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS invoice_line_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id      INTEGER NOT NULL,
    description     TEXT    NOT NULL,
    service_type    TEXT    NOT NULL,
    quantity        REAL    NOT NULL DEFAULT 1,
    unit_price      REAL    NOT NULL,
    amount          REAL    NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
);


-- ============================================================
-- DOMAIN TABLES: Rate Shopping
-- ============================================================

CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number    TEXT    NOT NULL UNIQUE,         -- e.g., "APO-2000"
    client_id       INTEGER NOT NULL,
    contact_id      INTEGER,                        -- Customer contact
    order_date      TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'awaiting_shipment'
                            CHECK (status IN ('awaiting_shipment', 'shipped', 'cancelled')),
    ship_to_address_id INTEGER,
    is_residential  INTEGER NOT NULL DEFAULT 0,
    declared_value  REAL,
    total_weight_oz REAL    NOT NULL,
    length_in       REAL,
    width_in        REAL,
    height_in       REAL,
    zone            INTEGER,
    service_requested TEXT  NOT NULL DEFAULT 'ground',
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (ship_to_address_id) REFERENCES addresses(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        INTEGER NOT NULL DEFAULT 1,
    unit_price      REAL    NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS rates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,
    carrier_id      INTEGER NOT NULL,
    service_code    TEXT    NOT NULL,                -- e.g., "ups_ground", "fedex_ground"
    service_name    TEXT    NOT NULL,                -- e.g., "UPS Ground (Account 2)"
    base_rate       REAL    NOT NULL,
    fuel_surcharge  REAL    NOT NULL DEFAULT 0,
    residential_surcharge REAL NOT NULL DEFAULT 0,
    total_amount    REAL    NOT NULL,
    billable_weight_lbs REAL NOT NULL,
    delivery_days   INTEGER NOT NULL,
    delivery_date   TEXT    NOT NULL,
    zone            INTEGER,
    is_cheapest     INTEGER NOT NULL DEFAULT 0,     -- 1 if this was the best rate
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (carrier_id) REFERENCES carriers(id)
);

CREATE TABLE IF NOT EXISTS labels (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,
    rate_id         INTEGER NOT NULL,
    tracking_number TEXT    NOT NULL,
    carrier_id      INTEGER NOT NULL,
    service_name    TEXT    NOT NULL,
    cost            REAL    NOT NULL,
    label_url       TEXT,
    tracking_url    TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (rate_id) REFERENCES rates(id),
    FOREIGN KEY (carrier_id) REFERENCES carriers(id)
);


-- ============================================================
-- DOMAIN TABLES: Chargeback Defense
-- ============================================================

CREATE TABLE IF NOT EXISTS retailers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    code            TEXT    NOT NULL UNIQUE,         -- e.g., "target", "amazon"
    portal_name     TEXT    NOT NULL,                -- e.g., "Partners Online"
    dispute_window_days INTEGER NOT NULL DEFAULT 30,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS chargebacks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chargeback_number TEXT  NOT NULL UNIQUE,         -- e.g., "CB-10000"
    retailer_id     INTEGER NOT NULL,
    client_id       INTEGER NOT NULL,
    carrier_id      INTEGER,
    po_number       TEXT    NOT NULL,
    shipment_id     TEXT,                           -- Reference to external shipment
    bol_number      TEXT,
    violation_code  TEXT    NOT NULL,                -- e.g., "ASN_LATE"
    chargeback_amount REAL  NOT NULL,
    chargeback_date TEXT    NOT NULL,
    dispute_deadline TEXT   NOT NULL,
    ship_date       TEXT,
    delivery_date   TEXT,
    tracking_number TEXT,
    units_shipped   INTEGER,
    cartons         INTEGER,
    pallets         INTEGER,
    status          TEXT    NOT NULL DEFAULT 'new'
                            CHECK (status IN ('new', 'reviewing', 'disputed', 'won', 'lost', 'expired')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (retailer_id) REFERENCES retailers(id),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (carrier_id) REFERENCES carriers(id)
);

CREATE TABLE IF NOT EXISTS evidence_files (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chargeback_id   INTEGER NOT NULL,
    evidence_type   TEXT    NOT NULL,                -- e.g., "bol", "tracking_summary", "pod"
    file_name       TEXT    NOT NULL,
    description     TEXT    NOT NULL,
    source          TEXT    NOT NULL,                -- e.g., "ShipStation", "OneDrive", "WMS"
    url             TEXT,
    is_auto_compiled INTEGER NOT NULL DEFAULT 1,     -- 1=auto, 0=manual upload needed
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (chargeback_id) REFERENCES chargebacks(id)
);

CREATE TABLE IF NOT EXISTS disputes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chargeback_id   INTEGER NOT NULL,
    dispute_reference TEXT,                          -- e.g., "DSP-123456"
    letter_subject  TEXT    NOT NULL,
    letter_body     TEXT    NOT NULL,
    evidence_count  INTEGER NOT NULL DEFAULT 0,
    submitted_at    TEXT,
    status          TEXT    NOT NULL DEFAULT 'draft'
                            CHECK (status IN ('draft', 'submitted', 'won', 'lost')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (chargeback_id) REFERENCES chargebacks(id)
);


-- ============================================================
-- DOMAIN TABLES: Inventory & Receiving
-- ============================================================

CREATE TABLE IF NOT EXISTS inventory (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL,
    client_id       INTEGER NOT NULL,
    quantity_on_hand INTEGER NOT NULL DEFAULT 0,
    quantity_allocated INTEGER NOT NULL DEFAULT 0,    -- Reserved for open orders
    quantity_available INTEGER GENERATED ALWAYS AS (quantity_on_hand - quantity_allocated) STORED,
    bin_location    TEXT,                             -- e.g., "A-03-02" (aisle-rack-shelf)
    last_counted    TEXT,
    last_received   TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    UNIQUE(product_id, client_id)
);

CREATE TABLE IF NOT EXISTS receiving_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id       INTEGER NOT NULL,
    po_number       TEXT    NOT NULL,                -- Inbound PO from client
    received_date   TEXT    NOT NULL,
    carrier         TEXT,                            -- Inbound carrier
    tracking_number TEXT,
    status          TEXT    NOT NULL DEFAULT 'completed'
                            CHECK (status IN ('pending', 'in_progress', 'completed', 'discrepancy')),
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS receiving_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    receiving_id    INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity_expected INTEGER NOT NULL,
    quantity_received INTEGER NOT NULL,
    quantity_damaged  INTEGER NOT NULL DEFAULT 0,
    discrepancy     INTEGER GENERATED ALWAYS AS (quantity_received - quantity_expected) STORED,
    notes           TEXT,                            -- e.g., "2 units crushed in transit"
    FOREIGN KEY (receiving_id) REFERENCES receiving_records(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);


-- ============================================================
-- DOMAIN TABLES: LTL Automation
-- ============================================================

CREATE TABLE IF NOT EXISTS ltl_quotes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_number    TEXT    NOT NULL UNIQUE,         -- e.g., "QT-XPO-20260216101234"
    client_id       INTEGER NOT NULL,
    carrier_id      INTEGER NOT NULL,
    origin_zip      TEXT    NOT NULL,
    destination_zip TEXT    NOT NULL,
    weight_lbs      INTEGER NOT NULL,
    freight_class   TEXT    NOT NULL,
    pieces          INTEGER NOT NULL DEFAULT 1,
    base_rate       REAL    NOT NULL,
    fuel_surcharge  REAL    NOT NULL,
    accessorials    REAL    NOT NULL DEFAULT 0,
    total_cost      REAL    NOT NULL,
    transit_days    INTEGER NOT NULL,
    estimated_delivery TEXT NOT NULL,
    service_level   TEXT    NOT NULL DEFAULT 'Standard LTL',
    valid_until     TEXT    NOT NULL,
    is_cheapest     INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (carrier_id) REFERENCES carriers(id)
);

CREATE TABLE IF NOT EXISTS ltl_bookings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id        INTEGER NOT NULL,
    bol_number      TEXT    NOT NULL UNIQUE,         -- e.g., "BOL-20260216101234"
    pro_number      TEXT    NOT NULL UNIQUE,         -- e.g., "PRO-101234"
    confirmation_number TEXT NOT NULL,
    pickup_date     TEXT    NOT NULL,
    pickup_window   TEXT    NOT NULL DEFAULT '08:00 - 17:00',
    shipper_name    TEXT    NOT NULL,
    shipper_phone   TEXT,
    shipper_email   TEXT,
    shipper_address TEXT,
    consignee_name  TEXT    NOT NULL,
    consignee_phone TEXT,
    consignee_email TEXT,
    consignee_address TEXT,
    special_instructions TEXT,
    status          TEXT    NOT NULL DEFAULT 'confirmed'
                            CHECK (status IN ('confirmed', 'picked_up', 'in_transit', 'delivered', 'cancelled')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (quote_id) REFERENCES ltl_quotes(id)
);


-- ============================================================
-- INDEXES
-- ============================================================

-- Core table indexes
CREATE INDEX IF NOT EXISTS idx_contacts_client_id ON contacts(client_id);
CREATE INDEX IF NOT EXISTS idx_addresses_client_id ON addresses(client_id);
CREATE INDEX IF NOT EXISTS idx_addresses_contact_id ON addresses(contact_id);
CREATE INDEX IF NOT EXISTS idx_products_client_id ON products(client_id);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);

-- Carrier Exception indexes
CREATE INDEX IF NOT EXISTS idx_shipments_client_id ON shipments(client_id);
CREATE INDEX IF NOT EXISTS idx_shipments_carrier_id ON shipments(carrier_id);
CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipments_tracking ON shipments(tracking_number);
CREATE INDEX IF NOT EXISTS idx_shipment_items_shipment_id ON shipment_items(shipment_id);
CREATE INDEX IF NOT EXISTS idx_exceptions_shipment_id ON exceptions(shipment_id);
CREATE INDEX IF NOT EXISTS idx_exceptions_type ON exceptions(exception_type);

-- Email Triage indexes
CREATE INDEX IF NOT EXISTS idx_emails_category ON emails(category);
CREATE INDEX IF NOT EXISTS idx_emails_action ON emails(action_taken);
CREATE INDEX IF NOT EXISTS idx_emails_received ON emails(received_at);

-- Profitability indexes
CREATE INDEX IF NOT EXISTS idx_labor_client_id ON labor_entries(client_id);
CREATE INDEX IF NOT EXISTS idx_labor_employee_id ON labor_entries(employee_id);
CREATE INDEX IF NOT EXISTS idx_labor_date ON labor_entries(work_date);
CREATE INDEX IF NOT EXISTS idx_labor_service ON labor_entries(service_type);
CREATE INDEX IF NOT EXISTS idx_invoices_client_id ON invoices(client_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice_id ON invoice_line_items(invoice_id);

-- Rate Shopping indexes
CREATE INDEX IF NOT EXISTS idx_orders_client_id ON orders(client_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_rates_order_id ON rates(order_id);
CREATE INDEX IF NOT EXISTS idx_rates_carrier_id ON rates(carrier_id);
CREATE INDEX IF NOT EXISTS idx_labels_order_id ON labels(order_id);

-- Chargeback Defense indexes
CREATE INDEX IF NOT EXISTS idx_chargebacks_retailer_id ON chargebacks(retailer_id);
CREATE INDEX IF NOT EXISTS idx_chargebacks_client_id ON chargebacks(client_id);
CREATE INDEX IF NOT EXISTS idx_chargebacks_status ON chargebacks(status);
CREATE INDEX IF NOT EXISTS idx_chargebacks_violation ON chargebacks(violation_code);
CREATE INDEX IF NOT EXISTS idx_evidence_chargeback_id ON evidence_files(chargeback_id);
CREATE INDEX IF NOT EXISTS idx_disputes_chargeback_id ON disputes(chargeback_id);

-- Inventory & Receiving indexes
CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_client_id ON inventory(client_id);
CREATE INDEX IF NOT EXISTS idx_receiving_client_id ON receiving_records(client_id);
CREATE INDEX IF NOT EXISTS idx_receiving_status ON receiving_records(status);
CREATE INDEX IF NOT EXISTS idx_receiving_items_receiving_id ON receiving_items(receiving_id);

-- LTL Automation indexes
CREATE INDEX IF NOT EXISTS idx_ltl_quotes_client_id ON ltl_quotes(client_id);
CREATE INDEX IF NOT EXISTS idx_ltl_quotes_carrier_id ON ltl_quotes(carrier_id);
CREATE INDEX IF NOT EXISTS idx_ltl_bookings_quote_id ON ltl_bookings(quote_id);
