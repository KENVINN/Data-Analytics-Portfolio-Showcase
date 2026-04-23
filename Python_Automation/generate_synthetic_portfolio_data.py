"""
Generate deterministic synthetic datasets for the portfolio showcase.

Example:
    python generate_synthetic_portfolio_data.py

This script creates fictitious CSV files for a Maker Info-style service
operations system, including service orders, cost control, SLA tracking,
and customer recall workflows. All entities, names, and business events are synthetic.
"""

from __future__ import annotations

import csv
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

SEED = 20260423
REFERENCE_DATE = date(2026, 4, 15)
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "Synthetic_Data"

COMPANIES = [
    {
        "company_id": "CO001",
        "company_name": "Retail Direct",
        "account_type": "Retail",
        "city": "Cuiaba",
        "region": "Midwest",
        "contract_status": "active",
    },
    {
        "company_id": "CO002",
        "company_name": "Orion Legal Group",
        "account_type": "B2B",
        "city": "Cuiaba",
        "region": "Midwest",
        "contract_status": "active",
    },
    {
        "company_id": "CO003",
        "company_name": "Verde Health Clinic",
        "account_type": "B2B",
        "city": "Cuiaba",
        "region": "Midwest",
        "contract_status": "active",
    },
    {
        "company_id": "CO004",
        "company_name": "Atlas Logistics Hub",
        "account_type": "B2B",
        "city": "Varzea Grande",
        "region": "Midwest",
        "contract_status": "active",
    },
    {
        "company_id": "CO005",
        "company_name": "Prime Edu Center",
        "account_type": "B2B",
        "city": "Sinop",
        "region": "North",
        "contract_status": "active",
    },
    {
        "company_id": "CO006",
        "company_name": "Nova Realty Partners",
        "account_type": "B2B",
        "city": "Rondonopolis",
        "region": "South",
        "contract_status": "active",
    },
]

TECHNICIANS = [
    {
        "technician_id": "TECH001",
        "technician_name": "Avery Cole",
        "squad_name": "Workshop",
        "specialty": "Computer Repair",
    },
    {
        "technician_id": "TECH002",
        "technician_name": "Jordan Ellis",
        "squad_name": "Workshop",
        "specialty": "Mobile Repair",
    },
    {
        "technician_id": "TECH003",
        "technician_name": "Taylor Brooks",
        "squad_name": "Field Support",
        "specialty": "Onsite Support",
    },
    {
        "technician_id": "TECH004",
        "technician_name": "Morgan Reed",
        "squad_name": "B2B Operations",
        "specialty": "Contract Accounts",
    },
    {
        "technician_id": "TECH005",
        "technician_name": "Cameron Shaw",
        "squad_name": "Workshop",
        "specialty": "Mixed Devices",
    },
]

SERVICE_LINE_DEVICE_MAP = {
    "Computer Repair": ["Notebook", "Desktop", "All In One", "Printer"],
    "Mobile Repair": ["Smartphone", "Tablet"],
    "B2B Support": ["Notebook", "Printer", "POS Terminal", "Network Router"],
    "Onsite Visit": ["Network Router", "POS Terminal", "Office Notebook"],
}

STATUS_VARIATIONS = {
    "delivered": [" delivered ", "DELIVERED", "Delivered"],
    "ready_for_pickup": ["ready for pickup", "READY FOR PICKUP", " Ready For Pickup "],
    "in_repair": ["in repair", "IN REPAIR", " In Repair "],
    "awaiting_part": ["awaiting part", "AWAITING PART", " Awaiting Part "],
    "quote_rejected": ["quote rejected", "QUOTE REJECTED", " Quote Rejected "],
    "cancelled": ["cancelled", "CANCELLED", " Cancelled "],
}

SERVICE_LINE_VARIATIONS = {
    "Computer Repair": [" computer repair ", "COMPUTER REPAIR", "Computer Repair"],
    "Mobile Repair": ["mobile repair", "MOBILE REPAIR", " Mobile Repair "],
    "B2B Support": ["b2b support", "B2B SUPPORT", " B2B Support "],
    "Onsite Visit": ["onsite visit", "ONSITE VISIT", " Onsite Visit "],
}

FIRST_NAMES = [
    "Alex",
    "Jordan",
    "Taylor",
    "Morgan",
    "Casey",
    "Riley",
    "Jamie",
    "Cameron",
    "Drew",
    "Avery",
    "Parker",
    "Logan",
    "Harper",
    "Skyler",
    "Blake",
]

LAST_NAMES = [
    "Carter",
    "Mason",
    "Hayes",
    "Perry",
    "Brooks",
    "Price",
    "Reed",
    "Ward",
    "Bennett",
    "Parker",
    "Diaz",
    "Gray",
    "Jordan",
    "Morris",
    "Turner",
]


def write_csv(file_path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def random_date_between(rng: random.Random, start_date: date, end_date: date) -> date:
    day_span = (end_date - start_date).days
    return start_date + timedelta(days=rng.randint(0, day_span))


def normalize_text_for_email(value: str) -> str:
    return value.lower().replace(" ", ".")


def company_lookup() -> dict[str, dict[str, object]]:
    return {company["company_id"]: company for company in COMPANIES}


def choose_service_line(account_type: str, order_number: int) -> str:
    if account_type == "Retail":
        return "Mobile Repair" if order_number % 3 == 0 else "Computer Repair"

    sequence = ["B2B Support", "Computer Repair", "Onsite Visit", "B2B Support"]
    return sequence[order_number % len(sequence)]


def choose_device_type(service_line: str, order_number: int) -> str:
    device_options = SERVICE_LINE_DEVICE_MAP[service_line]
    return device_options[order_number % len(device_options)]


def choose_priority(service_line: str, order_number: int) -> str:
    if service_line == "Onsite Visit":
        return "high"
    if service_line == "B2B Support":
        return "high" if order_number % 4 == 0 else "medium"
    if service_line == "Mobile Repair":
        return "medium"
    return "medium" if order_number % 5 else "low"


def choose_service_mode(service_line: str, order_number: int) -> str:
    if service_line == "Onsite Visit":
        return "onsite"
    if service_line == "B2B Support":
        return "pickup" if order_number % 2 == 0 else "onsite"
    return "in_store"


def choose_final_status(order_number: int) -> str:
    if order_number % 15 == 0:
        return "quote_rejected"
    if order_number % 13 == 0:
        return "cancelled"
    if order_number % 11 == 0:
        return "awaiting_part"
    if order_number % 9 == 0:
        return "ready_for_pickup"
    if order_number % 7 == 0:
        return "in_repair"
    return "delivered"


def determine_amounts(service_line: str, device_type: str, order_number: int, status: str) -> tuple[float, float]:
    base_amount = {
        "Computer Repair": 420.0,
        "Mobile Repair": 360.0,
        "B2B Support": 920.0,
        "Onsite Visit": 690.0,
    }[service_line]
    device_modifier = {
        "Notebook": 120.0,
        "Desktop": 70.0,
        "All In One": 90.0,
        "Printer": 110.0,
        "Smartphone": 80.0,
        "Tablet": 40.0,
        "POS Terminal": 180.0,
        "Network Router": 140.0,
        "Office Notebook": 150.0,
    }.get(device_type, 0.0)

    quoted_amount = base_amount + device_modifier + (order_number % 6) * 35
    approved_revenue = quoted_amount

    if status in {"quote_rejected", "cancelled"}:
        approved_revenue = 0.0
    elif status in {"awaiting_part", "in_repair", "ready_for_pickup"}:
        approved_revenue = quoted_amount - (20 + (order_number % 3) * 10)
    else:
        approved_revenue = quoted_amount - (order_number % 4) * 15

    return round(quoted_amount, 2), round(approved_revenue, 2)


def build_dim_customer_rows(rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    weighted_company_ids = (
        ["CO001"] * 18
        + ["CO002"] * 6
        + ["CO003"] * 6
        + ["CO004"] * 6
        + ["CO005"] * 6
        + ["CO006"] * 6
    )
    companies_by_id = company_lookup()

    for customer_number, company_id in enumerate(weighted_company_ids, start=1):
        company = companies_by_id[company_id]
        first_name = FIRST_NAMES[(customer_number - 1) % len(FIRST_NAMES)]
        last_name = LAST_NAMES[(customer_number * 2 - 1) % len(LAST_NAMES)]
        phone_number = f"+55 65 9{rng.randint(1000, 9999)}-{rng.randint(1000, 9999)}"

        rows.append(
            {
                "customer_id": f"CUST{customer_number:03d}",
                "company_id": company_id,
                "customer_name": f"{first_name} {last_name}",
                "phone_number": phone_number,
                "city": company["city"],
                "customer_type": company["account_type"],
            }
        )

    return rows


def build_fact_service_order_rows(
    customers: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    companies_by_id = company_lookup()
    priority_to_sla = {"low": 72, "medium": 48, "high": 24}
    start_date = date(2026, 1, 5)

    for order_number in range(1, 73):
        customer = customers[(order_number * 7 + order_number // 4) % len(customers)]
        company = companies_by_id[str(customer["company_id"])]
        technician = TECHNICIANS[(order_number - 1) % len(TECHNICIANS)]
        service_line = choose_service_line(str(company["account_type"]), order_number)
        device_type = choose_device_type(service_line, order_number)
        priority = choose_priority(service_line, order_number)
        service_mode = choose_service_mode(service_line, order_number)
        order_status = choose_final_status(order_number)

        open_offset = min(order_number + (order_number % 6), 96)
        opened_at = datetime.combine(
            start_date + timedelta(days=open_offset),
            time(hour=8 + (order_number % 8), minute=15 if order_number % 2 else 45),
        )
        first_response_hours = {
            "low": 8 + (order_number % 8),
            "medium": 3 + (order_number % 9),
            "high": 1 + (order_number % 6),
        }[priority]
        first_response_at = opened_at + timedelta(hours=first_response_hours)
        quoted_at = first_response_at + timedelta(hours=6 + (order_number % 10))

        approved_at = None
        closed_at = None
        if order_status not in {"quote_rejected", "cancelled"}:
            approved_at = quoted_at + timedelta(hours=8 + (order_number % 20))
            if order_status == "delivered":
                closed_at = approved_at + timedelta(hours=18 + (order_number % 80))

        quoted_amount, approved_revenue = determine_amounts(
            service_line,
            device_type,
            order_number,
            order_status,
        )

        rows.append(
            {
                "order_id": f"SO{order_number:04d}",
                "customer_id": customer["customer_id"],
                "company_id": company["company_id"],
                "technician_id": technician["technician_id"],
                "service_line": service_line,
                "device_type": device_type,
                "service_mode": service_mode,
                "opened_at": opened_at.isoformat(timespec="minutes"),
                "first_response_at": first_response_at.isoformat(timespec="minutes"),
                "quoted_at": quoted_at.isoformat(timespec="minutes"),
                "approved_at": approved_at.isoformat(timespec="minutes") if approved_at else "",
                "closed_at": closed_at.isoformat(timespec="minutes") if closed_at else "",
                "order_status": order_status,
                "quoted_amount": quoted_amount,
                "approved_revenue": approved_revenue,
                "priority": priority,
                "sla_target_hours": priority_to_sla[priority],
            }
        )

    return rows


def build_fact_order_status_history_rows(
    service_orders: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    status_counter = 1

    for order in service_orders:
        order_id = str(order["order_id"])
        opened_at = datetime.fromisoformat(str(order["opened_at"]))
        first_response_at = datetime.fromisoformat(str(order["first_response_at"]))
        quoted_at = datetime.fromisoformat(str(order["quoted_at"]))
        approved_at = datetime.fromisoformat(str(order["approved_at"])) if order["approved_at"] else None
        closed_at = datetime.fromisoformat(str(order["closed_at"])) if order["closed_at"] else None
        order_status = str(order["order_status"])
        order_number = int(order_id.replace("SO", ""))

        timeline: list[tuple[str, datetime]] = [
            ("created", opened_at),
            ("diagnosis_started", first_response_at),
            ("quote_sent", quoted_at),
        ]

        if order_status == "quote_rejected":
            timeline.append(("quote_rejected", quoted_at + timedelta(hours=24 + order_number % 12)))
        elif order_status == "cancelled":
            timeline.append(("cancelled", quoted_at + timedelta(hours=18 + order_number % 10)))
        elif approved_at:
            timeline.append(("approved", approved_at))
            if order_status == "awaiting_part":
                timeline.append(("awaiting_part", approved_at + timedelta(hours=8 + order_number % 6)))
            elif order_status == "in_repair":
                timeline.append(("in_repair", approved_at + timedelta(hours=6 + order_number % 5)))
            elif order_status == "ready_for_pickup":
                repair_started = approved_at + timedelta(hours=6 + order_number % 5)
                ready_at = repair_started + timedelta(hours=20 + order_number % 18)
                timeline.extend(
                    [
                        ("in_repair", repair_started),
                        ("quality_check", ready_at - timedelta(hours=4)),
                        ("ready_for_pickup", ready_at),
                    ]
                )
            elif order_status == "delivered" and closed_at:
                repair_started = approved_at + timedelta(hours=6 + order_number % 5)
                ready_at = closed_at - timedelta(hours=6 + order_number % 4)
                quality_check_at = ready_at - timedelta(hours=4)
                timeline.extend(
                    [
                        ("in_repair", repair_started),
                        ("quality_check", quality_check_at),
                        ("ready_for_pickup", ready_at),
                        ("delivered", closed_at),
                    ]
                )

        timeline.sort(key=lambda item: item[1])

        for status_name, status_at in timeline:
            rows.append(
                {
                    "status_id": f"ST{status_counter:05d}",
                    "order_id": order_id,
                    "status_name": status_name,
                    "status_at": status_at.isoformat(timespec="minutes"),
                }
            )
            status_counter += 1

    return rows


def build_fact_cost_entry_rows(
    service_orders: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    cost_counter = 1

    for order in service_orders:
        order_id = str(order["order_id"])
        company_id = str(order["company_id"])
        approved_revenue = float(order["approved_revenue"])
        quoted_at = datetime.fromisoformat(str(order["quoted_at"]))
        approved_at = datetime.fromisoformat(str(order["approved_at"])) if order["approved_at"] else quoted_at
        order_number = int(order_id.replace("SO", ""))

        if approved_revenue > 0:
            if order_number % 10 == 0:
                total_ratio = 0.96
            elif order_number % 7 == 0:
                total_ratio = 0.78
            elif order_number % 4 == 0:
                total_ratio = 0.60
            else:
                total_ratio = 0.46

            total_cost = round(approved_revenue * total_ratio, 2)
            labor_cost = round(total_cost * 0.36, 2)
            parts_cost = round(total_cost * 0.44, 2)
            logistics_cost = round(total_cost - labor_cost - parts_cost, 2)

            for category, amount, offset_hours in [
                ("labor", labor_cost, 4),
                ("parts", parts_cost, 10),
                ("logistics", logistics_cost, 18),
            ]:
                if amount <= 0:
                    continue

                rows.append(
                    {
                        "cost_id": f"COST{cost_counter:05d}",
                        "order_id": order_id,
                        "company_id": company_id,
                        "cost_category": category,
                        "cost_amount": amount,
                        "linked_status": "linked",
                        "recorded_at": (approved_at + timedelta(hours=offset_hours)).isoformat(timespec="minutes"),
                    }
                )
                cost_counter += 1

            if order_number % 12 == 0:
                rows.append(
                    {
                        "cost_id": f"COST{cost_counter:05d}",
                        "order_id": order_id,
                        "company_id": company_id,
                        "cost_category": "external_service",
                        "cost_amount": round(approved_revenue * 0.08, 2),
                        "linked_status": "linked",
                        "recorded_at": (approved_at + timedelta(hours=22)).isoformat(timespec="minutes"),
                    }
                )
                cost_counter += 1

        if order_number % 8 == 0:
            rows.append(
                {
                    "cost_id": f"COST{cost_counter:05d}",
                    "order_id": "",
                    "company_id": company_id,
                    "cost_category": "unlinked_purchase",
                    "cost_amount": round(55 + order_number * 4.5, 2),
                    "linked_status": "unlinked",
                    "recorded_at": (quoted_at + timedelta(days=1)).isoformat(timespec="minutes"),
                }
            )
            cost_counter += 1

    return rows


def build_fact_customer_contact_rows(
    customers: list[dict[str, object]],
    service_orders: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    contact_counter = 1
    orders_by_customer: dict[str, list[dict[str, object]]] = {}

    for order in service_orders:
        orders_by_customer.setdefault(str(order["customer_id"]), []).append(order)

    customers_by_id = {customer["customer_id"]: customer for customer in customers}

    for customer_id, customer_orders in orders_by_customer.items():
        customer_orders.sort(key=lambda item: str(item["opened_at"]))
        customer = customers_by_id[customer_id]

        delivered_orders = [order for order in customer_orders if order["closed_at"]]
        for delivered_order in delivered_orders[:2]:
            if int(str(delivered_order["order_id"]).replace("SO", "")) % 2 == 0:
                rows.append(
                    {
                        "contact_id": f"CONT{contact_counter:05d}",
                        "customer_id": customer_id,
                        "company_id": delivered_order["company_id"],
                        "contact_type": "satisfaction_check",
                        "contact_channel": "WhatsApp",
                        "contact_at": (
                            datetime.fromisoformat(str(delivered_order["closed_at"])) + timedelta(days=5)
                        ).isoformat(timespec="minutes"),
                        "contact_outcome": "reached",
                    }
                )
                contact_counter += 1

        rejected_orders = [
            order for order in customer_orders if str(order["order_status"]) == "quote_rejected"
        ]
        for rejected_order in rejected_orders[:1]:
            rows.append(
                {
                    "contact_id": f"CONT{contact_counter:05d}",
                    "customer_id": customer_id,
                    "company_id": rejected_order["company_id"],
                    "contact_type": "quote_follow_up",
                    "contact_channel": "Phone",
                    "contact_at": (
                        datetime.fromisoformat(str(rejected_order["quoted_at"])) + timedelta(days=2)
                    ).isoformat(timespec="minutes"),
                    "contact_outcome": "no_response",
                }
            )
            contact_counter += 1

        if delivered_orders:
            last_delivered = max(
                datetime.fromisoformat(str(order["closed_at"])) for order in delivered_orders
            )
            customer_number = int(customer_id.replace("CUST", ""))

            if (REFERENCE_DATE - last_delivered.date()).days >= 45 and customer_number % 3 == 0:
                rows.append(
                    {
                        "contact_id": f"CONT{contact_counter:05d}",
                        "customer_id": customer_id,
                        "company_id": customer["company_id"],
                        "contact_type": "recall_campaign",
                        "contact_channel": "WhatsApp",
                        "contact_at": datetime.combine(
                            REFERENCE_DATE - timedelta(days=10 + customer_number % 11),
                            time(hour=10, minute=0),
                        ).isoformat(timespec="minutes"),
                        "contact_outcome": "scheduled_visit" if customer_number % 6 == 0 else "no_response",
                    }
                )
                contact_counter += 1

            if customer["customer_type"] == "B2B" and customer_number % 4 == 0:
                rows.append(
                    {
                        "contact_id": f"CONT{contact_counter:05d}",
                        "customer_id": customer_id,
                        "company_id": customer["company_id"],
                        "contact_type": "b2b_account_review",
                        "contact_channel": "Email",
                        "contact_at": datetime.combine(
                            REFERENCE_DATE - timedelta(days=14 + customer_number % 9),
                            time(hour=14, minute=30),
                        ).isoformat(timespec="minutes"),
                        "contact_outcome": "reached",
                    }
                )
                contact_counter += 1

    return rows


def build_service_orders_raw_rows(
    customers: list[dict[str, object]],
    service_orders: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    customers_by_id = {customer["customer_id"]: customer for customer in customers}
    companies_by_id = company_lookup()
    technicians_by_id = {technician["technician_id"]: technician for technician in TECHNICIANS}

    for order in service_orders:
        order_number = int(str(order["order_id"]).replace("SO", ""))
        customer = customers_by_id[str(order["customer_id"])]
        company = companies_by_id[str(order["company_id"])]
        technician = technicians_by_id[str(order["technician_id"])]
        service_line = str(order["service_line"])
        current_status = str(order["order_status"])

        rows.append(
            {
                " Order ID ": order["order_id"],
                "Customer Name": (
                    str(customer["customer_name"]).upper()
                    if order_number % 10 == 0
                    else customer["customer_name"]
                ),
                "Phone Number ": (
                    str(customer["phone_number"]).replace("+55 ", "")
                    if order_number % 6 == 0
                    else customer["phone_number"]
                ),
                "Company Name": (
                    str(company["company_name"]).upper()
                    if order_number % 9 == 0
                    else f" {company['company_name']} "
                ),
                "Service Line": SERVICE_LINE_VARIATIONS[service_line][order_number % 3],
                "Device Type": (
                    str(order["device_type"]).lower()
                    if order_number % 5 == 0
                    else order["device_type"]
                ),
                " Current Status ": STATUS_VARIATIONS[current_status][order_number % 3],
                "Opened At": order["opened_at"],
                "Closed At": order["closed_at"],
                "Quoted Amount (BRL)": (
                    f"R$ {order['quoted_amount']:,.2f}"
                    if order_number % 4 == 0
                    else f" {order['quoted_amount']:.2f} "
                ),
                "Approved Revenue (BRL)": (
                    f"R$ {order['approved_revenue']:,.2f}"
                    if order_number % 3 == 0
                    else f" {order['approved_revenue']:.2f} "
                ),
                "Technician Name": (
                    str(technician["technician_name"]).upper()
                    if order_number % 8 == 0
                    else f" {technician['technician_name']} "
                ),
                "City": (
                    str(customer["city"]).upper()
                    if order_number % 7 == 0
                    else f" {customer['city']} "
                ),
                "SLA Target Hours": f" {order['sla_target_hours']} ",
            }
        )

    return rows


def main() -> None:
    rng = random.Random(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    customers = build_dim_customer_rows(rng)
    service_orders = build_fact_service_order_rows(customers)

    write_csv(
        OUTPUT_DIR / "dim_company.csv",
        ["company_id", "company_name", "account_type", "city", "region", "contract_status"],
        COMPANIES,
    )
    write_csv(
        OUTPUT_DIR / "dim_customer.csv",
        ["customer_id", "company_id", "customer_name", "phone_number", "city", "customer_type"],
        customers,
    )
    write_csv(
        OUTPUT_DIR / "dim_technician.csv",
        ["technician_id", "technician_name", "squad_name", "specialty"],
        TECHNICIANS,
    )
    write_csv(
        OUTPUT_DIR / "fact_service_order.csv",
        [
            "order_id",
            "customer_id",
            "company_id",
            "technician_id",
            "service_line",
            "device_type",
            "service_mode",
            "opened_at",
            "first_response_at",
            "quoted_at",
            "approved_at",
            "closed_at",
            "order_status",
            "quoted_amount",
            "approved_revenue",
            "priority",
            "sla_target_hours",
        ],
        service_orders,
    )
    write_csv(
        OUTPUT_DIR / "fact_order_status_history.csv",
        ["status_id", "order_id", "status_name", "status_at"],
        build_fact_order_status_history_rows(service_orders),
    )
    write_csv(
        OUTPUT_DIR / "fact_cost_entry.csv",
        ["cost_id", "order_id", "company_id", "cost_category", "cost_amount", "linked_status", "recorded_at"],
        build_fact_cost_entry_rows(service_orders),
    )
    write_csv(
        OUTPUT_DIR / "fact_customer_contact.csv",
        ["contact_id", "customer_id", "company_id", "contact_type", "contact_channel", "contact_at", "contact_outcome"],
        build_fact_customer_contact_rows(customers, service_orders),
    )
    write_csv(
        OUTPUT_DIR / "service_orders_raw.csv",
        [
            " Order ID ",
            "Customer Name",
            "Phone Number ",
            "Company Name",
            "Service Line",
            "Device Type",
            " Current Status ",
            "Opened At",
            "Closed At",
            "Quoted Amount (BRL)",
            "Approved Revenue (BRL)",
            "Technician Name",
            "City",
            "SLA Target Hours",
        ],
        build_service_orders_raw_rows(customers, service_orders),
    )


if __name__ == "__main__":
    main()
