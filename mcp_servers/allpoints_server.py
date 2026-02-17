"""All Points Operations Intelligence — Combined MCP Server.

29 tools across 6 domains: Carrier Exceptions, Email Triage, Profitability,
Rate Shopping, Chargeback Defense, and LTL Automation.

Deploy via: arcade deploy -e mcp_servers/allpoints_server.py
"""

import json
import sys
from pathlib import Path
from typing import Annotated

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.database import get_connection
from shared.formatters import format_output
from shared.constants import VIOLATION_DESCRIPTIONS

from arcade_mcp_server import MCPApp

app = MCPApp(name="allpoints")


def _row_to_dict(row) -> dict:
    return dict(row) if row else {}


def _rows_to_list(rows) -> list[dict]:
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════════════════════
# CARRIER EXCEPTIONS (5 tools)
# ═══════════════════════════════════════════════════════════════════════════════

@app.tool()
def detect_exceptions(
    status_filter: Annotated[str, "Filter by exception type (e.g., 'damaged', 'lost'). Leave empty for all."] = "",
    client_name: Annotated[str, "Filter by client name. Leave empty for all clients."] = "",
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "List of shipments with active exceptions, split into critical and standard."]:
    """Find all active (unresolved) shipment exceptions."""
    conn = get_connection()
    query = """
        SELECT s.shipment_number, s.order_number, c.name as client_name,
               ct.first_name || ' ' || ct.last_name as customer_name, ct.email as customer_email,
               cr.name as carrier, s.service, s.tracking_number, s.status as shipment_status,
               s.ship_date, s.expected_delivery, s.weight_lbs, s.zone,
               e.exception_type, e.exception_message, e.is_critical, e.days_overdue,
               e.detected_at
        FROM exceptions e
        JOIN shipments s ON e.shipment_id = s.id
        JOIN clients c ON s.client_id = c.id
        JOIN carriers cr ON s.carrier_id = cr.id
        LEFT JOIN contacts ct ON s.contact_id = ct.id
        WHERE e.resolved_at IS NULL
    """
    params = []
    if status_filter:
        query += " AND e.exception_type = ?"
        params.append(status_filter)
    if client_name:
        query += " AND c.name LIKE ?"
        params.append(f"%{client_name}%")
    query += " ORDER BY e.is_critical DESC, e.days_overdue DESC"

    rows = _rows_to_list(conn.execute(query, params).fetchall())
    critical = [r for r in rows if r["is_critical"]]
    standard = [r for r in rows if not r["is_critical"]]

    if output_format != "json":
        return format_output(rows, fmt=output_format)

    return json.dumps({
        "total_exceptions": len(rows),
        "critical_count": len(critical),
        "standard_count": len(standard),
        "critical": critical,
        "standard": standard,
    }, indent=2, default=str)


@app.tool()
def get_shipment_details(
    shipment_number: Annotated[str, "The shipment ID (e.g., 'SH-40221')."],
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Full shipment details including items and exceptions."]:
    """Get full details for a specific shipment including items and any exceptions."""
    conn = get_connection()
    row = conn.execute("""
        SELECT s.*, c.name as client_name, cr.name as carrier_name,
               ct.first_name || ' ' || ct.last_name as customer_name, ct.email as customer_email,
               oa.city as origin_city, oa.state as origin_state,
               da.city as dest_city, da.state as dest_state, da.zip_code as dest_zip
        FROM shipments s
        JOIN clients c ON s.client_id = c.id
        JOIN carriers cr ON s.carrier_id = cr.id
        LEFT JOIN contacts ct ON s.contact_id = ct.id
        LEFT JOIN addresses oa ON s.origin_address_id = oa.id
        LEFT JOIN addresses da ON s.dest_address_id = da.id
        WHERE s.shipment_number = ?
    """, (shipment_number,)).fetchone()

    if not row:
        return json.dumps({"error": f"Shipment {shipment_number} not found"})

    shipment = _row_to_dict(row)

    items = _rows_to_list(conn.execute("""
        SELECT p.sku, p.name, si.quantity
        FROM shipment_items si JOIN products p ON si.product_id = p.id
        WHERE si.shipment_id = ?
    """, (shipment["id"],)).fetchall())

    exceptions = _rows_to_list(conn.execute("""
        SELECT exception_type, exception_message, is_critical, days_overdue, detected_at, resolved_at
        FROM exceptions WHERE shipment_id = ?
    """, (shipment["id"],)).fetchall())

    shipment["items"] = items
    shipment["exceptions"] = exceptions

    if output_format != "json":
        return format_output([shipment], fmt=output_format)
    return json.dumps(shipment, indent=2, default=str)


@app.tool()
def get_client_shipments(
    client_name: Annotated[str, "Client name (exact or partial match)."],
    status: Annotated[str, "Filter by status (on_time, in_transit, delayed, exception, delivered). Leave empty for all."] = "",
    limit: Annotated[int, "Maximum number of results (default 50)."] = 50,
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Shipments for the specified client."]:
    """Get shipments for a specific client, optionally filtered by status."""
    conn = get_connection()
    query = """
        SELECT s.shipment_number, s.order_number, s.tracking_number, cr.name as carrier,
               s.service, s.status, s.ship_date, s.expected_delivery, s.actual_delivery,
               s.weight_lbs, s.zone
        FROM shipments s
        JOIN clients c ON s.client_id = c.id
        JOIN carriers cr ON s.carrier_id = cr.id
        WHERE c.name LIKE ?
    """
    params = [f"%{client_name}%"]
    if status:
        query += " AND s.status = ?"
        params.append(status)
    query += " ORDER BY s.ship_date DESC LIMIT ?"
    params.append(limit)

    rows = _rows_to_list(conn.execute(query, params).fetchall())
    return format_output(rows, fmt=output_format)


@app.tool()
def get_exception_summary(
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Aggregate exception stats by type, client, and carrier."]:
    """Get aggregate exception stats: counts by type, by client, by carrier."""
    conn = get_connection()

    by_type = _rows_to_list(conn.execute("""
        SELECT e.exception_type, count(*) as count,
               sum(e.is_critical) as critical_count
        FROM exceptions e WHERE e.resolved_at IS NULL
        GROUP BY e.exception_type ORDER BY count DESC
    """).fetchall())

    by_client = _rows_to_list(conn.execute("""
        SELECT c.name as client_name, count(*) as exception_count,
               sum(e.is_critical) as critical_count
        FROM exceptions e
        JOIN shipments s ON e.shipment_id = s.id
        JOIN clients c ON s.client_id = c.id
        WHERE e.resolved_at IS NULL
        GROUP BY c.name ORDER BY exception_count DESC
    """).fetchall())

    by_carrier = _rows_to_list(conn.execute("""
        SELECT cr.name as carrier, count(*) as exception_count
        FROM exceptions e
        JOIN shipments s ON e.shipment_id = s.id
        JOIN carriers cr ON s.carrier_id = cr.id
        WHERE e.resolved_at IS NULL
        GROUP BY cr.name ORDER BY exception_count DESC
    """).fetchall())

    total = conn.execute("SELECT count(*) FROM exceptions WHERE resolved_at IS NULL").fetchone()[0]
    critical = conn.execute("SELECT count(*) FROM exceptions WHERE resolved_at IS NULL AND is_critical = 1").fetchone()[0]

    result = {
        "total_active_exceptions": total,
        "critical_count": critical,
        "standard_count": total - critical,
        "by_type": by_type,
        "by_client": by_client,
        "by_carrier": by_carrier,
    }

    if output_format == "markdown":
        return format_output(by_type, fmt="markdown")
    return json.dumps(result, indent=2, default=str)


@app.tool()
def get_tracking_info(
    tracking_number: Annotated[str, "The carrier tracking number."],
) -> Annotated[str, "Shipment status and any active exceptions for the tracking number."]:
    """Look up a shipment by tracking number and return its current status."""
    conn = get_connection()
    row = conn.execute("""
        SELECT s.shipment_number, s.order_number, cr.name as carrier, s.service,
               s.tracking_number, s.status, s.ship_date, s.expected_delivery, s.actual_delivery,
               c.name as client_name, s.weight_lbs, s.zone
        FROM shipments s
        JOIN clients c ON s.client_id = c.id
        JOIN carriers cr ON s.carrier_id = cr.id
        WHERE s.tracking_number = ?
    """, (tracking_number,)).fetchone()

    if not row:
        return json.dumps({"error": f"No shipment found for tracking number {tracking_number}"})

    shipment = _row_to_dict(row)

    exceptions = _rows_to_list(conn.execute("""
        SELECT exception_type, exception_message, is_critical, days_overdue
        FROM exceptions WHERE shipment_id = (
            SELECT id FROM shipments WHERE tracking_number = ?
        ) AND resolved_at IS NULL
    """, (tracking_number,)).fetchall())

    shipment["active_exceptions"] = exceptions
    return json.dumps(shipment, indent=2, default=str)


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL TRIAGE (4 tools)
# ═══════════════════════════════════════════════════════════════════════════════

@app.tool()
def get_unread_emails(
    limit: Annotated[int, "Maximum number of emails to return (default 20)."] = 20,
    category: Annotated[str, "Filter by category (tracking_request, delivery_confirmation, inventory_question, billing_question, shipping_issue, complex_issue). Leave empty for all."] = "",
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Unread emails from the inbox."]:
    """Fetch unread emails from the inbox, optionally filtered by category."""
    conn = get_connection()
    query = """
        SELECT e.id, e.message_id, e.sender_name, e.sender_email, e.subject,
               e.body_preview, e.received_at, e.category, e.confidence, e.action_taken,
               c.name as client_name
        FROM emails e
        LEFT JOIN clients c ON e.client_id = c.id
        WHERE e.is_read = 0
    """
    params = []
    if category:
        query += " AND e.category = ?"
        params.append(category)
    query += " ORDER BY e.received_at DESC LIMIT ?"
    params.append(limit)

    rows = _rows_to_list(conn.execute(query, params).fetchall())
    return format_output(rows, fmt=output_format)


@app.tool()
def get_email_by_id(
    email_id: Annotated[int, "The email database ID."],
) -> Annotated[str, "Full email details including the full body text."]:
    """Get full details for a specific email including the full body text."""
    conn = get_connection()
    row = conn.execute("""
        SELECT e.*, c.name as client_name
        FROM emails e
        LEFT JOIN clients c ON e.client_id = c.id
        WHERE e.id = ?
    """, (email_id,)).fetchone()

    if not row:
        return json.dumps({"error": f"Email {email_id} not found"})
    return json.dumps(dict(row), indent=2, default=str)


@app.tool()
def get_email_templates(
    category: Annotated[str, "Email category to get templates for. Leave empty for all templates."] = "",
) -> Annotated[str, "Response templates for the specified category."]:
    """Get response templates, optionally filtered by email category."""
    conn = get_connection()
    if category:
        rows = conn.execute(
            "SELECT * FROM email_templates WHERE category = ? AND is_active = 1",
            (category,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM email_templates WHERE is_active = 1"
        ).fetchall()

    return json.dumps(_rows_to_list(rows), indent=2, default=str)


@app.tool()
def get_inbox_summary(
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Inbox summary with counts by category, action status, and urgency."]:
    """Get a summary of the inbox: counts by category, action status, and urgency."""
    conn = get_connection()

    total_unread = conn.execute("SELECT count(*) FROM emails WHERE is_read = 0").fetchone()[0]

    by_category = _rows_to_list(conn.execute("""
        SELECT category, count(*) as count,
               sum(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread
        FROM emails
        GROUP BY category ORDER BY count DESC
    """).fetchall())

    by_action = _rows_to_list(conn.execute("""
        SELECT action_taken, count(*) as count
        FROM emails
        GROUP BY action_taken ORDER BY count DESC
    """).fetchall())

    needs_attention = conn.execute("""
        SELECT count(*) FROM emails
        WHERE is_read = 0 AND (action_taken IS NULL OR action_taken = 'pending')
    """).fetchone()[0]

    auto_resolved = conn.execute(
        "SELECT count(*) FROM emails WHERE action_taken = 'auto_resolved'"
    ).fetchone()[0]

    result = {
        "total_unread": total_unread,
        "needs_attention": needs_attention,
        "auto_resolved_total": auto_resolved,
        "by_category": by_category,
        "by_action": by_action,
    }

    if output_format == "markdown":
        return format_output(by_category, fmt="markdown")
    return json.dumps(result, indent=2, default=str)


# ═══════════════════════════════════════════════════════════════════════════════
# PROFITABILITY (5 tools)
# ═══════════════════════════════════════════════════════════════════════════════

@app.tool()
def get_client_profitability(
    client_name: Annotated[str, "Client name (partial match). Leave empty for all clients ranked by margin."] = "",
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Profitability analysis with revenue, labor cost, profit, and margin."]:
    """Analyze profitability for one or all clients: revenue, labor cost, profit, margin.

    Compares invoice revenue against labor costs to calculate profit and margin percentage.
    Categories: Excellent (>=25%), Good (>=15%), Acceptable (>=5%), Poor (>=0%), Losing Money (<0%).
    """
    conn = get_connection()
    query = """
        SELECT c.name as client_name,
               COALESCE(inv.total_revenue, 0) as revenue,
               COALESCE(inv.paid_amount, 0) as paid,
               COALESCE(inv.pending_amount, 0) as pending,
               COALESCE(inv.overdue_amount, 0) as overdue,
               COALESCE(lab.total_cost, 0) as labor_cost,
               COALESCE(lab.total_hours, 0) as labor_hours,
               COALESCE(inv.total_revenue, 0) - COALESCE(lab.total_cost, 0) as profit
        FROM clients c
        LEFT JOIN (
            SELECT client_id,
                   SUM(total_amount) as total_revenue,
                   SUM(CASE WHEN status = 'paid' THEN total_amount ELSE 0 END) as paid_amount,
                   SUM(CASE WHEN status = 'pending' THEN total_amount ELSE 0 END) as pending_amount,
                   SUM(CASE WHEN status = 'overdue' THEN total_amount ELSE 0 END) as overdue_amount
            FROM invoices GROUP BY client_id
        ) inv ON c.id = inv.client_id
        LEFT JOIN (
            SELECT le.client_id,
                   SUM(le.hours * e.hourly_rate) as total_cost,
                   SUM(le.hours) as total_hours
            FROM labor_entries le JOIN employees e ON le.employee_id = e.id
            GROUP BY le.client_id
        ) lab ON c.id = lab.client_id
    """
    params = []
    if client_name:
        query += " WHERE c.name LIKE ?"
        params.append(f"%{client_name}%")
    query += " ORDER BY profit DESC"

    rows = _rows_to_list(conn.execute(query, params).fetchall())

    for row in rows:
        rev = row["revenue"]
        margin = round((row["profit"] / rev) * 100, 1) if rev > 0 else 0
        row["profit_margin_pct"] = margin
        if margin >= 25:
            row["category"] = "Excellent"
        elif margin >= 15:
            row["category"] = "Good"
        elif margin >= 5:
            row["category"] = "Acceptable"
        elif margin >= 0:
            row["category"] = "Poor"
        else:
            row["category"] = "Losing Money"
        row["profit"] = round(row["profit"], 2)
        row["labor_cost"] = round(row["labor_cost"], 2)

    return format_output(rows, fmt=output_format)


@app.tool()
def get_labor_summary(
    client_name: Annotated[str, "Client name (partial match). Leave empty for all clients."] = "",
    date_from: Annotated[str, "Start date filter (YYYY-MM-DD). Leave empty for no lower bound."] = "",
    date_to: Annotated[str, "End date filter (YYYY-MM-DD). Leave empty for no upper bound."] = "",
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Labor hours and costs broken down by service type and employee."]:
    """Get labor hours and costs broken down by service type and employee."""
    conn = get_connection()

    query_svc = """
        SELECT c.name as client_name, le.service_type,
               round(SUM(le.hours), 1) as hours,
               round(SUM(le.hours * e.hourly_rate), 2) as cost
        FROM labor_entries le
        JOIN employees e ON le.employee_id = e.id
        JOIN clients c ON le.client_id = c.id
        WHERE 1=1
    """
    params = []
    if client_name:
        query_svc += " AND c.name LIKE ?"
        params.append(f"%{client_name}%")
    if date_from:
        query_svc += " AND le.work_date >= ?"
        params.append(date_from)
    if date_to:
        query_svc += " AND le.work_date <= ?"
        params.append(date_to)
    query_svc += " GROUP BY c.name, le.service_type ORDER BY c.name, cost DESC"

    rows = _rows_to_list(conn.execute(query_svc, params).fetchall())
    return format_output(rows, fmt=output_format)


@app.tool()
def get_invoice_status(
    client_name: Annotated[str, "Client name (partial match). Leave empty for all."] = "",
    status: Annotated[str, "Filter by status (paid, pending, overdue). Leave empty for all."] = "",
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Invoice details with payment status."]:
    """Get invoice details with payment status."""
    conn = get_connection()
    query = """
        SELECT c.name as client_name, i.invoice_number, i.invoice_date, i.due_date,
               i.total_amount, i.status, i.payment_date
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        WHERE 1=1
    """
    params = []
    if client_name:
        query += " AND c.name LIKE ?"
        params.append(f"%{client_name}%")
    if status:
        query += " AND i.status = ?"
        params.append(status)
    query += " ORDER BY i.invoice_date DESC"

    rows = _rows_to_list(conn.execute(query, params).fetchall())
    return format_output(rows, fmt=output_format)


@app.tool()
def get_profitability_overview(
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "High-level profitability overview across all clients with totals."]:
    """Get a high-level profitability overview across all clients with totals."""
    conn = get_connection()

    total_revenue = conn.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices").fetchone()[0]
    total_paid = conn.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE status = 'paid'").fetchone()[0]
    total_pending = conn.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE status = 'pending'").fetchone()[0]
    total_overdue = conn.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE status = 'overdue'").fetchone()[0]
    total_labor = conn.execute(
        "SELECT COALESCE(SUM(le.hours * e.hourly_rate), 0) FROM labor_entries le JOIN employees e ON le.employee_id = e.id"
    ).fetchone()[0]
    total_hours = conn.execute("SELECT COALESCE(SUM(hours), 0) FROM labor_entries").fetchone()[0]

    profit = total_revenue - total_labor
    margin = round((profit / total_revenue) * 100, 1) if total_revenue > 0 else 0

    result = {
        "total_revenue": round(total_revenue, 2),
        "total_paid": round(total_paid, 2),
        "total_pending": round(total_pending, 2),
        "total_overdue": round(total_overdue, 2),
        "total_labor_cost": round(total_labor, 2),
        "total_labor_hours": round(total_hours, 1),
        "total_profit": round(profit, 2),
        "overall_margin_pct": margin,
        "invoice_count": conn.execute("SELECT count(*) FROM invoices").fetchone()[0],
        "client_count": conn.execute("SELECT count(*) FROM clients").fetchone()[0],
    }

    if output_format != "json":
        return format_output([result], fmt=output_format)
    return json.dumps(result, indent=2, default=str)


@app.tool()
def get_service_breakdown(
    client_name: Annotated[str, "Client name (partial match). Leave empty for company-wide breakdown."] = "",
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Labor costs broken down by service type."]:
    """Break down labor costs by service type (pick_and_pack, receiving, kitting, returns, shipping, special_projects).

    Shows which service types consume the most labor hours and cost, useful for identifying
    where operational efficiency can be improved.
    """
    conn = get_connection()
    query = """
        SELECT le.service_type,
               round(SUM(le.hours), 1) as total_hours,
               round(SUM(le.hours * e.hourly_rate), 2) as total_cost,
               count(DISTINCT le.client_id) as client_count,
               count(DISTINCT le.employee_id) as employee_count
        FROM labor_entries le
        JOIN employees e ON le.employee_id = e.id
    """
    params = []
    if client_name:
        query += " JOIN clients c ON le.client_id = c.id WHERE c.name LIKE ?"
        params.append(f"%{client_name}%")
    query += " GROUP BY le.service_type ORDER BY total_cost DESC"

    rows = _rows_to_list(conn.execute(query, params).fetchall())
    return format_output(rows, fmt=output_format)


# ═══════════════════════════════════════════════════════════════════════════════
# RATE SHOPPING (5 tools)
# ═══════════════════════════════════════════════════════════════════════════════

@app.tool()
def get_open_orders(
    client_name: Annotated[str, "Client name (partial match). Leave empty for all clients."] = "",
    limit: Annotated[int, "Maximum number of results (default 50)."] = 50,
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Orders awaiting shipment with product and destination details."]:
    """Get all orders awaiting shipment, optionally filtered by client."""
    conn = get_connection()
    query = """
        SELECT o.order_number, c.name as client_name, o.order_date, o.status,
               o.total_weight_oz, round(o.total_weight_oz / 16.0, 2) as weight_lbs,
               o.zone, o.is_residential, o.declared_value,
               p.sku, p.name as product_name, oi.quantity,
               a.city as dest_city, a.state as dest_state, a.zip_code as dest_zip
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        LEFT JOIN addresses a ON o.ship_to_address_id = a.id
        WHERE o.status = 'awaiting_shipment'
    """
    params = []
    if client_name:
        query += " AND c.name LIKE ?"
        params.append(f"%{client_name}%")
    query += " ORDER BY o.order_date ASC LIMIT ?"
    params.append(limit)

    rows = _rows_to_list(conn.execute(query, params).fetchall())
    return format_output(rows, fmt=output_format)


@app.tool()
def get_rates_for_order(
    order_number: Annotated[str, "The order number (e.g., 'APO-2000')."],
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "All carrier rate quotes for the order, sorted cheapest first."]:
    """Get all carrier rate quotes for a specific order, sorted cheapest first."""
    conn = get_connection()
    rates = _rows_to_list(conn.execute("""
        SELECT r.service_name, cr.name as carrier, r.base_rate, r.fuel_surcharge,
               r.residential_surcharge, r.total_amount, r.billable_weight_lbs,
               r.delivery_days, r.delivery_date, r.zone, r.is_cheapest
        FROM rates r
        JOIN carriers cr ON r.carrier_id = cr.id
        JOIN orders o ON r.order_id = o.id
        WHERE o.order_number = ?
        ORDER BY r.total_amount ASC
    """, (order_number,)).fetchall())

    if not rates:
        return json.dumps({"error": f"No rates found for order {order_number}"})

    if output_format != "json":
        return format_output(rates, fmt=output_format)

    cheapest = rates[0]
    most_expensive = rates[-1]
    savings = round(most_expensive["total_amount"] - cheapest["total_amount"], 2)
    savings_pct = round((savings / most_expensive["total_amount"]) * 100, 1) if most_expensive["total_amount"] > 0 else 0

    return json.dumps({
        "order_number": order_number,
        "rates": rates,
        "cheapest": cheapest,
        "most_expensive": most_expensive,
        "potential_savings": {
            "amount": savings,
            "percent": savings_pct,
            "comparison": f"${cheapest['total_amount']:.2f} vs ${most_expensive['total_amount']:.2f}",
        },
    }, indent=2, default=str)


@app.tool()
def get_cheapest_rate(
    order_number: Annotated[str, "The order number (e.g., 'APO-2000')."],
) -> Annotated[str, "The cheapest carrier rate for the specified order."]:
    """Get just the cheapest carrier rate for an order."""
    conn = get_connection()
    row = conn.execute("""
        SELECT r.service_name, cr.name as carrier, r.total_amount, r.delivery_days,
               r.delivery_date, r.billable_weight_lbs, r.zone
        FROM rates r
        JOIN carriers cr ON r.carrier_id = cr.id
        JOIN orders o ON r.order_id = o.id
        WHERE o.order_number = ? AND r.is_cheapest = 1
    """, (order_number,)).fetchone()

    if not row:
        return json.dumps({"error": f"No rates found for order {order_number}"})
    return json.dumps(dict(row), indent=2, default=str)


@app.tool()
def rate_shop_batch(
    client_name: Annotated[str, "Client name (partial match). Leave empty for all clients."] = "",
    limit: Annotated[int, "Maximum orders to process (default 50)."] = 50,
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Batch rate shopping results with cheapest carrier per order and total savings."]:
    """Rate shop all open orders at once. Shows the cheapest carrier for each order and total savings.

    This is the batch operation — processes all awaiting_shipment orders and summarizes the
    savings opportunity across the entire batch.
    """
    conn = get_connection()
    query = """
        SELECT o.id, o.order_number, c.name as client_name,
               round(o.total_weight_oz / 16.0, 2) as weight_lbs, o.zone, o.is_residential
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        WHERE o.status = 'awaiting_shipment'
    """
    params = []
    if client_name:
        query += " AND c.name LIKE ?"
        params.append(f"%{client_name}%")
    query += " ORDER BY o.order_date ASC LIMIT ?"
    params.append(limit)

    orders = _rows_to_list(conn.execute(query, params).fetchall())
    results = []
    total_savings = 0.0

    for order in orders:
        rates = _rows_to_list(conn.execute("""
            SELECT cr.name as carrier, r.service_name, r.total_amount, r.is_cheapest
            FROM rates r
            JOIN carriers cr ON r.carrier_id = cr.id
            WHERE r.order_id = ?
            ORDER BY r.total_amount ASC
        """, (order["id"],)).fetchall())

        if not rates:
            continue

        cheapest = rates[0]
        most_expensive = rates[-1]
        savings = round(most_expensive["total_amount"] - cheapest["total_amount"], 2)
        total_savings += savings

        results.append({
            "order_number": order["order_number"],
            "client_name": order["client_name"],
            "weight_lbs": order["weight_lbs"],
            "zone": order["zone"],
            "cheapest_carrier": cheapest["carrier"],
            "cheapest_rate": cheapest["total_amount"],
            "most_expensive_rate": most_expensive["total_amount"],
            "savings": savings,
        })

    if output_format != "json":
        return format_output(results, fmt=output_format)

    carrier_wins = {}
    for r in results:
        c = r["cheapest_carrier"]
        carrier_wins[c] = carrier_wins.get(c, 0) + 1

    return json.dumps({
        "orders_processed": len(results),
        "total_savings": round(total_savings, 2),
        "avg_savings_per_order": round(total_savings / len(results), 2) if results else 0,
        "carrier_wins": carrier_wins,
        "results": results,
    }, indent=2, default=str)


@app.tool()
def get_savings_summary(
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Overview of rate shopping savings potential across all open orders."]:
    """Get an overview of rate shopping savings potential across all open orders."""
    conn = get_connection()

    open_count = conn.execute("SELECT count(*) FROM orders WHERE status = 'awaiting_shipment'").fetchone()[0]
    shipped_count = conn.execute("SELECT count(*) FROM orders WHERE status = 'shipped'").fetchone()[0]
    label_count = conn.execute("SELECT count(*) FROM labels").fetchone()[0]

    savings_data = _rows_to_list(conn.execute("""
        SELECT o.order_number,
               min(r.total_amount) as cheapest,
               max(r.total_amount) as most_expensive
        FROM orders o
        JOIN rates r ON o.id = r.order_id
        WHERE o.status = 'awaiting_shipment'
        GROUP BY o.id
    """).fetchall())

    total_savings = sum(row["most_expensive"] - row["cheapest"] for row in savings_data)

    carrier_wins = _rows_to_list(conn.execute("""
        SELECT cr.name as carrier, count(*) as cheapest_wins
        FROM rates r
        JOIN carriers cr ON r.carrier_id = cr.id
        WHERE r.is_cheapest = 1
        GROUP BY cr.name ORDER BY cheapest_wins DESC
    """).fetchall())

    result = {
        "open_orders": open_count,
        "shipped_orders": shipped_count,
        "labels_created": label_count,
        "total_savings_potential": round(total_savings, 2),
        "avg_savings_per_order": round(total_savings / len(savings_data), 2) if savings_data else 0,
        "carrier_performance": carrier_wins,
    }

    if output_format != "json":
        return format_output([result], fmt=output_format)
    return json.dumps(result, indent=2, default=str)


# ═══════════════════════════════════════════════════════════════════════════════
# CHARGEBACK DEFENSE (5 tools)
# ═══════════════════════════════════════════════════════════════════════════════

@app.tool()
def get_open_chargebacks(
    client_name: Annotated[str, "Client name (partial match). Leave empty for all clients."] = "",
    retailer: Annotated[str, "Retailer name (partial match). Leave empty for all retailers."] = "",
    status: Annotated[str, "Filter by status (new, reviewing, disputed, won, lost, expired). Leave empty for all."] = "",
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Chargebacks needing attention with deadline and violation details."]:
    """Get chargebacks that need attention, optionally filtered by client, retailer, or status."""
    conn = get_connection()
    query = """
        SELECT cb.chargeback_number, cb.po_number, cb.violation_code,
               cb.chargeback_amount, cb.chargeback_date, cb.dispute_deadline,
               cb.status, cb.ship_date, cb.delivery_date, cb.tracking_number,
               cb.units_shipped, cb.cartons, cb.pallets,
               c.name as client_name, r.name as retailer_name, r.portal_name,
               cr.name as carrier_name,
               julianday(cb.dispute_deadline) - julianday('now') as days_until_deadline
        FROM chargebacks cb
        JOIN clients c ON cb.client_id = c.id
        JOIN retailers r ON cb.retailer_id = r.id
        LEFT JOIN carriers cr ON cb.carrier_id = cr.id
        WHERE 1=1
    """
    params = []
    if client_name:
        query += " AND c.name LIKE ?"
        params.append(f"%{client_name}%")
    if retailer:
        query += " AND r.name LIKE ?"
        params.append(f"%{retailer}%")
    if status:
        query += " AND cb.status = ?"
        params.append(status)
    query += " ORDER BY cb.dispute_deadline ASC"

    rows = _rows_to_list(conn.execute(query, params).fetchall())

    for row in rows:
        code = row["violation_code"]
        row["violation_description"] = VIOLATION_DESCRIPTIONS.get(code, code)
        row["days_until_deadline"] = round(row["days_until_deadline"], 0) if row["days_until_deadline"] else None

    return format_output(rows, fmt=output_format)


@app.tool()
def get_chargeback_details(
    chargeback_number: Annotated[str, "The chargeback ID (e.g., 'CB-10000')."],
) -> Annotated[str, "Full chargeback details including evidence files and dispute history."]:
    """Get full details for a specific chargeback including evidence files and dispute history."""
    conn = get_connection()
    row = conn.execute("""
        SELECT cb.*, c.name as client_name, r.name as retailer_name, r.portal_name,
               r.dispute_window_days, cr.name as carrier_name,
               julianday(cb.dispute_deadline) - julianday('now') as days_until_deadline
        FROM chargebacks cb
        JOIN clients c ON cb.client_id = c.id
        JOIN retailers r ON cb.retailer_id = r.id
        LEFT JOIN carriers cr ON cb.carrier_id = cr.id
        WHERE cb.chargeback_number = ?
    """, (chargeback_number,)).fetchone()

    if not row:
        return json.dumps({"error": f"Chargeback {chargeback_number} not found"})

    cb = dict(row)
    cb["violation_description"] = VIOLATION_DESCRIPTIONS.get(cb["violation_code"], cb["violation_code"])
    cb["days_until_deadline"] = round(cb["days_until_deadline"], 0) if cb["days_until_deadline"] else None

    evidence = _rows_to_list(conn.execute("""
        SELECT evidence_type, file_name, description, source, is_auto_compiled, url
        FROM evidence_files WHERE chargeback_id = ?
        ORDER BY evidence_type
    """, (cb["id"],)).fetchall())

    disputes = _rows_to_list(conn.execute("""
        SELECT dispute_reference, letter_subject, status, evidence_count, submitted_at
        FROM disputes WHERE chargeback_id = ?
        ORDER BY created_at DESC
    """, (cb["id"],)).fetchall())

    cb["evidence_files"] = evidence
    cb["disputes"] = disputes
    cb["evidence_count"] = len(evidence)

    return json.dumps(cb, indent=2, default=str)


@app.tool()
def get_evidence(
    chargeback_number: Annotated[str, "The chargeback ID (e.g., 'CB-10000')."],
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Evidence files compiled for the specified chargeback."]:
    """Get all evidence files compiled for a specific chargeback."""
    conn = get_connection()
    rows = _rows_to_list(conn.execute("""
        SELECT ef.evidence_type, ef.file_name, ef.description, ef.source,
               ef.is_auto_compiled, ef.url, cb.chargeback_number
        FROM evidence_files ef
        JOIN chargebacks cb ON ef.chargeback_id = cb.id
        WHERE cb.chargeback_number = ?
        ORDER BY ef.evidence_type
    """, (chargeback_number,)).fetchall())

    if not rows:
        return json.dumps({"error": f"No evidence found for chargeback {chargeback_number}"})
    return format_output(rows, fmt=output_format)


@app.tool()
def get_expiring_chargebacks(
    days: Annotated[int, "Number of days to look ahead (default 7)."] = 7,
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Chargebacks with dispute deadlines expiring within the specified window."]:
    """Get chargebacks with dispute deadlines expiring within N days. Urgency view."""
    conn = get_connection()
    rows = _rows_to_list(conn.execute("""
        SELECT cb.chargeback_number, cb.po_number, cb.violation_code,
               cb.chargeback_amount, cb.dispute_deadline, cb.status,
               c.name as client_name, r.name as retailer_name,
               round(julianday(cb.dispute_deadline) - julianday('now'), 0) as days_remaining
        FROM chargebacks cb
        JOIN clients c ON cb.client_id = c.id
        JOIN retailers r ON cb.retailer_id = r.id
        WHERE cb.status IN ('new', 'reviewing')
          AND julianday(cb.dispute_deadline) - julianday('now') <= ?
          AND julianday(cb.dispute_deadline) - julianday('now') >= 0
        ORDER BY cb.dispute_deadline ASC
    """, (days,)).fetchall())

    for row in rows:
        row["violation_description"] = VIOLATION_DESCRIPTIONS.get(row["violation_code"], row["violation_code"])

    if output_format != "json":
        return format_output(rows, fmt=output_format)

    total_at_risk = sum(r["chargeback_amount"] for r in rows)
    return json.dumps({
        "expiring_within_days": days,
        "count": len(rows),
        "total_amount_at_risk": round(total_at_risk, 2),
        "chargebacks": rows,
    }, indent=2, default=str)


@app.tool()
def get_chargeback_summary(
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Aggregate chargeback stats by status, retailer, violation type, and win rate."]:
    """Get aggregate chargeback stats: totals by status, by retailer, by violation type, and win rate."""
    conn = get_connection()

    by_status = _rows_to_list(conn.execute("""
        SELECT status, count(*) as count, round(sum(chargeback_amount), 2) as total_amount
        FROM chargebacks GROUP BY status ORDER BY count DESC
    """).fetchall())

    by_retailer = _rows_to_list(conn.execute("""
        SELECT r.name as retailer, count(*) as count,
               round(sum(cb.chargeback_amount), 2) as total_amount
        FROM chargebacks cb JOIN retailers r ON cb.retailer_id = r.id
        GROUP BY r.name ORDER BY total_amount DESC
    """).fetchall())

    by_violation = _rows_to_list(conn.execute("""
        SELECT violation_code, count(*) as count,
               round(sum(chargeback_amount), 2) as total_amount
        FROM chargebacks GROUP BY violation_code ORDER BY total_amount DESC
    """).fetchall())

    for row in by_violation:
        row["violation_description"] = VIOLATION_DESCRIPTIONS.get(row["violation_code"], row["violation_code"])

    total = conn.execute("SELECT count(*) FROM chargebacks").fetchone()[0]
    total_amount = conn.execute("SELECT COALESCE(sum(chargeback_amount), 0) FROM chargebacks").fetchone()[0]
    won = conn.execute("SELECT count(*) FROM chargebacks WHERE status = 'won'").fetchone()[0]
    disputed = conn.execute("SELECT count(*) FROM chargebacks WHERE status IN ('disputed', 'won', 'lost')").fetchone()[0]
    win_rate = round((won / disputed) * 100, 1) if disputed > 0 else 0

    result = {
        "total_chargebacks": total,
        "total_amount": round(total_amount, 2),
        "disputes_filed": disputed,
        "won": won,
        "win_rate_pct": win_rate,
        "by_status": by_status,
        "by_retailer": by_retailer,
        "by_violation": by_violation,
    }

    if output_format == "markdown":
        return format_output(by_status, fmt="markdown")
    return json.dumps(result, indent=2, default=str)


# ═══════════════════════════════════════════════════════════════════════════════
# LTL AUTOMATION (5 tools)
# ═══════════════════════════════════════════════════════════════════════════════

@app.tool()
def get_ltl_quotes(
    client_name: Annotated[str, "Client name (partial match). Leave empty for all clients."] = "",
    destination_zip: Annotated[str, "Destination ZIP code. Leave empty for all destinations."] = "",
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "LTL freight quotes sorted by cost."]:
    """Get LTL freight quotes, optionally filtered by client or destination."""
    conn = get_connection()
    query = """
        SELECT q.quote_number, c.name as client_name, cr.name as carrier,
               q.origin_zip, q.destination_zip, q.weight_lbs, q.freight_class,
               q.pieces, q.base_rate, q.fuel_surcharge, q.accessorials,
               q.total_cost, q.transit_days, q.estimated_delivery,
               q.service_level, q.valid_until, q.is_cheapest
        FROM ltl_quotes q
        JOIN clients c ON q.client_id = c.id
        JOIN carriers cr ON q.carrier_id = cr.id
        WHERE 1=1
    """
    params = []
    if client_name:
        query += " AND c.name LIKE ?"
        params.append(f"%{client_name}%")
    if destination_zip:
        query += " AND q.destination_zip = ?"
        params.append(destination_zip)
    query += " ORDER BY q.total_cost ASC"

    rows = _rows_to_list(conn.execute(query, params).fetchall())
    return format_output(rows, fmt=output_format)


@app.tool()
def compare_ltl_carriers(
    client_name: Annotated[str, "Client name (partial match)."],
    destination_zip: Annotated[str, "Destination ZIP to compare on a single lane. Leave empty to compare across all lanes."] = "",
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Carrier comparison grouped by lane with savings calculations."]:
    """Compare LTL carriers for a client's shipments. Groups quotes by lane and shows cheapest option."""
    conn = get_connection()
    query = """
        SELECT q.destination_zip, cr.name as carrier, q.quote_number,
               q.weight_lbs, q.freight_class, q.total_cost, q.transit_days,
               q.is_cheapest
        FROM ltl_quotes q
        JOIN clients c ON q.client_id = c.id
        JOIN carriers cr ON q.carrier_id = cr.id
        WHERE c.name LIKE ?
    """
    params = [f"%{client_name}%"]
    if destination_zip:
        query += " AND q.destination_zip = ?"
        params.append(destination_zip)
    query += " ORDER BY q.destination_zip, q.total_cost ASC"

    rows = _rows_to_list(conn.execute(query, params).fetchall())

    if output_format != "json":
        return format_output(rows, fmt=output_format)

    lanes = {}
    for row in rows:
        dest = row["destination_zip"]
        if dest not in lanes:
            lanes[dest] = []
        lanes[dest].append(row)

    comparisons = []
    total_savings = 0.0
    for dest, quotes in lanes.items():
        if len(quotes) < 2:
            continue
        cheapest = quotes[0]
        most_expensive = quotes[-1]
        savings = round(most_expensive["total_cost"] - cheapest["total_cost"], 2)
        total_savings += savings
        comparisons.append({
            "destination_zip": dest,
            "cheapest_carrier": cheapest["carrier"],
            "cheapest_rate": cheapest["total_cost"],
            "cheapest_transit": cheapest["transit_days"],
            "most_expensive_rate": most_expensive["total_cost"],
            "savings": savings,
            "quote_count": len(quotes),
        })

    return json.dumps({
        "client": client_name,
        "lanes_compared": len(comparisons),
        "total_potential_savings": round(total_savings, 2),
        "comparisons": comparisons,
    }, indent=2, default=str)


@app.tool()
def get_booking_details(
    bol_number: Annotated[str, "The Bill of Lading number (e.g., 'BOL-20260216101234')."],
) -> Annotated[str, "Full booking details including quote, carrier, and client info."]:
    """Get full details for a specific LTL booking by BOL number."""
    conn = get_connection()
    row = conn.execute("""
        SELECT b.*, q.quote_number, q.weight_lbs, q.freight_class, q.pieces,
               q.total_cost, q.transit_days, q.origin_zip, q.destination_zip,
               cr.name as carrier, c.name as client_name
        FROM ltl_bookings b
        JOIN ltl_quotes q ON b.quote_id = q.id
        JOIN carriers cr ON q.carrier_id = cr.id
        JOIN clients c ON q.client_id = c.id
        WHERE b.bol_number = ?
    """, (bol_number,)).fetchone()

    if not row:
        return json.dumps({"error": f"Booking with BOL {bol_number} not found"})
    return json.dumps(dict(row), indent=2, default=str)


@app.tool()
def get_open_bookings(
    client_name: Annotated[str, "Client name (partial match). Leave empty for all clients."] = "",
    status: Annotated[str, "Filter by status (confirmed, picked_up, in_transit, delivered, cancelled). Leave empty for all."] = "",
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "LTL bookings with carrier, cost, and status details."]:
    """Get LTL bookings, optionally filtered by client or status."""
    conn = get_connection()
    query = """
        SELECT b.bol_number, b.pro_number, b.confirmation_number, b.status,
               b.pickup_date, b.pickup_window, b.consignee_name,
               cr.name as carrier, c.name as client_name,
               q.weight_lbs, q.freight_class, q.total_cost,
               q.origin_zip, q.destination_zip, q.transit_days
        FROM ltl_bookings b
        JOIN ltl_quotes q ON b.quote_id = q.id
        JOIN carriers cr ON q.carrier_id = cr.id
        JOIN clients c ON q.client_id = c.id
        WHERE 1=1
    """
    params = []
    if client_name:
        query += " AND c.name LIKE ?"
        params.append(f"%{client_name}%")
    if status:
        query += " AND b.status = ?"
        params.append(status)
    query += " ORDER BY b.pickup_date DESC"

    rows = _rows_to_list(conn.execute(query, params).fetchall())
    return format_output(rows, fmt=output_format)


@app.tool()
def get_ltl_summary(
    output_format: Annotated[str, "Output format: 'json', 'csv', or 'markdown'."] = "json",
) -> Annotated[str, "Overview of LTL activity including quote counts, bookings, carrier performance, and spend."]:
    """Get an overview of LTL activity: quote counts, booking counts, carrier performance, and spend."""
    conn = get_connection()

    total_quotes = conn.execute("SELECT count(*) FROM ltl_quotes").fetchone()[0]
    total_bookings = conn.execute("SELECT count(*) FROM ltl_bookings").fetchone()[0]
    total_spend = conn.execute("""
        SELECT COALESCE(sum(q.total_cost), 0)
        FROM ltl_bookings b JOIN ltl_quotes q ON b.quote_id = q.id
    """).fetchone()[0]

    by_carrier = _rows_to_list(conn.execute("""
        SELECT cr.name as carrier, count(*) as quote_count,
               round(avg(q.total_cost), 2) as avg_cost,
               sum(q.is_cheapest) as cheapest_wins
        FROM ltl_quotes q
        JOIN carriers cr ON q.carrier_id = cr.id
        GROUP BY cr.name ORDER BY cheapest_wins DESC
    """).fetchall())

    by_status = _rows_to_list(conn.execute("""
        SELECT status, count(*) as count
        FROM ltl_bookings GROUP BY status ORDER BY count DESC
    """).fetchall())

    avg_savings = conn.execute("""
        SELECT round(avg(max_cost - min_cost), 2) FROM (
            SELECT destination_zip, max(total_cost) as max_cost, min(total_cost) as min_cost
            FROM ltl_quotes
            GROUP BY client_id, destination_zip
            HAVING count(*) > 1
        )
    """).fetchone()[0] or 0

    result = {
        "total_quotes": total_quotes,
        "total_bookings": total_bookings,
        "total_booked_spend": round(total_spend, 2),
        "avg_savings_per_lane": avg_savings,
        "carrier_performance": by_carrier,
        "booking_status": by_status,
    }

    if output_format == "markdown":
        return format_output(by_carrier, fmt="markdown")
    return json.dumps(result, indent=2, default=str)


# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(transport="stdio")
