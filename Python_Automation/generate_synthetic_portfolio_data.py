"""
Generate deterministic synthetic datasets for the portfolio showcase.

Example:
    python generate_synthetic_portfolio_data.py

This script creates fictitious CSV files for gym analytics, SaaS revenue,
and IT service operations. All entities, names, and business events are synthetic.
"""

from __future__ import annotations

import csv
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

SEED = 20260423
REFERENCE_DATE = date(2026, 4, 15)
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "Synthetic_Data"

PLAN_PRICES = {
    "Basic": 79.0,
    "Premium": 129.0,
    "Premium Plus": 179.0,
    "Corporate": 249.0,
}

SAAS_PLAN_MRR = {
    "starter": 250,
    "growth": 650,
    "professional": 1250,
    "enterprise": 2400,
}

PARTNERS = [
    {"partner_id": "P001", "partner_name": "North Peak Fitness", "region": "North", "contract_status": "active"},
    {"partner_id": "P002", "partner_name": "Atlas Wellness Club", "region": "Midwest", "contract_status": "active"},
    {"partner_id": "P003", "partner_name": "Blue Harbor Gym", "region": "South", "contract_status": "active"},
    {"partner_id": "P004", "partner_name": "Urban Motion Hub", "region": "West", "contract_status": "active"},
    {"partner_id": "P005", "partner_name": "Prime Core Studio", "region": "East", "contract_status": "active"},
]

SAAS_ACCOUNTS = [
    ("A001", "Nova Desk", "North America", "Healthcare"),
    ("A002", "Bright Metrics", "North America", "Retail"),
    ("A003", "Cloud Harbor", "Europe", "Technology"),
    ("A004", "Summit Care", "Europe", "Healthcare"),
    ("A005", "Orbit Field", "Latin America", "Logistics"),
    ("A006", "Signal Forge", "North America", "Manufacturing"),
    ("A007", "Clear Ledger", "Europe", "Finance"),
    ("A008", "Pulse Transit", "Latin America", "Mobility"),
]

SAAS_ACCOUNT_SEQUENCES = {
    "A001": ["growth", "growth", "professional", "professional", "professional", "enterprise"],
    "A002": ["starter", "starter", "starter", "growth", "growth", "growth"],
    "A003": ["professional", "professional", "professional", "professional", "professional", "professional"],
    "A004": ["growth", "growth", "starter", "starter", "starter", "starter"],
    "A005": [None, None, "starter", "starter", "growth", "growth"],
    "A006": ["growth", "growth", "growth", "growth", None, None],
    "A007": ["enterprise", "enterprise", "enterprise", "enterprise", "professional", "professional"],
    "A008": ["starter", "growth", "growth", "growth", "professional", "professional"],
}

TECHNICIANS = ["Avery Cole", "Jordan Ellis", "Taylor Brooks", "Morgan Reed", "Cameron Shaw"]
SUPPORT_TEAMS = ["Field Support", "Workshop", "Remote Support"]
TICKET_CATEGORIES = ["Hardware Repair", "Software Issue", "Warranty", "Preventive Maintenance", "Network Setup"]
CUSTOMER_SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
CHANNELS = ["WhatsApp", "Email", "Phone", "Portal"]

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

MEMBER_PROFILE_SEQUENCE = [
    "highly_engaged",
    "highly_engaged",
    "consistent",
    "consistent",
    "consistent",
    "slipping",
    "slipping",
    "inactive",
    "reactivated",
    "never_activated",
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


def build_members(rng: random.Random) -> list[dict[str, object]]:
    members: list[dict[str, object]] = []
    member_count = 50
    signup_start = date(2025, 1, 10)
    signup_end = date(2026, 3, 5)

    for member_number in range(1, member_count + 1):
        first_name = FIRST_NAMES[(member_number - 1) % len(FIRST_NAMES)]
        last_name = LAST_NAMES[(member_number * 2 - 1) % len(LAST_NAMES)]
        member_id = f"M{member_number:03d}"
        full_name = f"{first_name} {last_name}"
        partner = PARTNERS[(member_number - 1) % len(PARTNERS)]
        activity_profile = MEMBER_PROFILE_SEQUENCE[(member_number - 1) % len(MEMBER_PROFILE_SEQUENCE)]

        if activity_profile == "never_activated":
            membership_status = "active"
        elif activity_profile == "inactive" and member_number % 2 == 0:
            membership_status = "paused"
        elif member_number in {17, 34, 49}:
            membership_status = "cancelled"
        else:
            membership_status = "active"

        plan_name = (
            "Corporate"
            if member_number % 11 == 0
            else "Premium Plus"
            if member_number % 5 == 0
            else "Premium"
            if member_number % 3 == 0
            else "Basic"
        )

        signup_date = random_date_between(rng, signup_start, signup_end)
        email = f"{normalize_text_for_email(full_name)}.{member_id.lower()}@example.com"

        members.append(
            {
                "member_id": member_id,
                "full_name": full_name,
                "email": email,
                "partner_id": partner["partner_id"],
                "partner_name": partner["partner_name"],
                "signup_date": signup_date,
                "membership_status": membership_status,
                "plan_name": plan_name,
                "monthly_fee": PLAN_PRICES[plan_name],
                "activity_profile": activity_profile,
            }
        )

    return members


def build_dim_member_rows(members: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "member_id": member["member_id"],
            "full_name": member["full_name"],
            "email": member["email"],
            "partner_id": member["partner_id"],
            "signup_date": member["signup_date"].isoformat(),
            "membership_status": member["membership_status"],
        }
        for member in members
    ]


def build_fact_membership_rows(rng: random.Random, members: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for member in members:
        membership_end_date = ""
        if member["membership_status"] == "cancelled":
            membership_end_date = (
                REFERENCE_DATE - timedelta(days=rng.randint(10, 65))
            ).isoformat()

        rows.append(
            {
                "member_id": member["member_id"],
                "plan_name": member["plan_name"],
                "monthly_fee": f"{member['monthly_fee']:.2f}",
                "membership_start_date": member["signup_date"].isoformat(),
                "membership_end_date": membership_end_date,
            }
        )

    return rows


def build_checkin_offsets(profile: str, rng: random.Random) -> list[int]:
    if profile == "highly_engaged":
        recent_offsets = rng.sample(range(1, 28), 9)
        older_offsets = rng.sample(range(28, 96), 12)
        return sorted(set(recent_offsets + older_offsets))

    if profile == "consistent":
        recent_offsets = rng.sample(range(2, 32), 5)
        older_offsets = rng.sample(range(32, 88), 8)
        return sorted(set(recent_offsets + older_offsets))

    if profile == "slipping":
        return sorted(rng.sample(range(25, 92), 9))

    if profile == "inactive":
        return sorted(rng.sample(range(55, 125), 6))

    if profile == "reactivated":
        recent_offsets = [4, 11, 18]
        older_offsets = rng.sample(range(76, 118), 5)
        return sorted(set(recent_offsets + older_offsets))

    return []


def build_fact_checkin_rows(rng: random.Random, members: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for member in members:
        signup_date: date = member["signup_date"]
        checkin_offsets = build_checkin_offsets(str(member["activity_profile"]), rng)

        for offset in checkin_offsets:
            checkin_date = REFERENCE_DATE - timedelta(days=offset)
            if checkin_date < signup_date:
                continue

            hour = 6 + (offset % 12)
            minute = 15 if offset % 2 == 0 else 45
            checkin_timestamp = datetime.combine(checkin_date, time(hour=hour, minute=minute))

            rows.append(
                {
                    "member_id": member["member_id"],
                    "checkin_timestamp": checkin_timestamp.isoformat(timespec="minutes"),
                }
            )

    rows.sort(key=lambda row: (row["member_id"], row["checkin_timestamp"]))
    return rows


def build_fact_class_booking_rows(
    rng: random.Random,
    members: list[dict[str, object]],
    fact_checkins: list[dict[str, object]],
) -> list[dict[str, object]]:
    latest_checkins_by_member: dict[str, list[str]] = {}
    for row in fact_checkins:
        latest_checkins_by_member.setdefault(str(row["member_id"]), []).append(str(row["checkin_timestamp"]))

    rows: list[dict[str, object]] = []
    booking_counter = 1

    for member in members:
        member_checkins = latest_checkins_by_member.get(str(member["member_id"]), [])
        if not member_checkins:
            continue

        profile = str(member["activity_profile"])
        limit = 6 if profile == "highly_engaged" else 4 if profile == "consistent" else 3

        for timestamp_text in member_checkins[:limit]:
            checkin_timestamp = datetime.fromisoformat(timestamp_text)
            class_start_at = checkin_timestamp + timedelta(hours=2)

            if profile == "highly_engaged":
                booking_status = "completed" if booking_counter % 6 else "cancelled"
            elif profile == "consistent":
                booking_status = "completed" if booking_counter % 4 else "no_show"
            elif profile == "reactivated":
                booking_status = "completed" if booking_counter % 3 else "cancelled"
            else:
                booking_status = "completed" if booking_counter % 2 else "no_show"

            rows.append(
                {
                    "booking_id": f"B{booking_counter:04d}",
                    "member_id": member["member_id"],
                    "class_start_at": class_start_at.isoformat(timespec="minutes"),
                    "booking_status": booking_status,
                }
            )
            booking_counter += 1

    return rows


def build_membership_export_raw_rows(
    members: list[dict[str, object]],
    fact_checkins: list[dict[str, object]],
) -> list[dict[str, object]]:
    last_checkin_by_member: dict[str, str] = {}
    for row in fact_checkins:
        last_checkin_by_member[str(row["member_id"])] = str(row["checkin_timestamp"]).split("T")[0]

    raw_plan_values = {
        "Basic": " basic plan ",
        "Premium": "PREMIUM",
        "Premium Plus": "premium plus",
        "Corporate": "Corporate ",
    }

    rows: list[dict[str, object]] = []

    for member in members:
        membership_status = str(member["membership_status"]).upper() if member["member_id"] in {"M003", "M018"} else f" {member['membership_status']} "

        rows.append(
            {
                " Member ID ": member["member_id"],
                "Full Name": str(member["full_name"]).upper() if member["member_id"] == "M005" else member["full_name"],
                "Email ": str(member["email"]).upper() if member["member_id"] == "M007" else member["email"],
                "Signup Date": member["signup_date"].isoformat(),
                "Last Checkin Date": last_checkin_by_member.get(str(member["member_id"]), ""),
                "Membership Status": membership_status,
                "Plan Name": raw_plan_values[str(member["plan_name"])],
                "Monthly Fee": f"{member['monthly_fee']:.2f}",
                "Partner Name": f" {member['partner_name']} ",
            }
        )

    return rows


def build_dim_account_rows() -> list[dict[str, object]]:
    return [
        {
            "account_id": account_id,
            "account_name": account_name,
            "region": region,
            "industry": industry,
        }
        for account_id, account_name, region, industry in SAAS_ACCOUNTS
    ]


def build_dim_plan_rows() -> list[dict[str, object]]:
    return [
        {"plan_id": "PLN001", "plan_name": "Starter", "plan_tier": "starter"},
        {"plan_id": "PLN002", "plan_name": "Growth", "plan_tier": "growth"},
        {"plan_id": "PLN003", "plan_name": "Professional", "plan_tier": "professional"},
        {"plan_id": "PLN004", "plan_name": "Enterprise", "plan_tier": "enterprise"},
    ]


def build_fact_subscription_snapshot_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    plan_id_by_tier = {
        "starter": "PLN001",
        "growth": "PLN002",
        "professional": "PLN003",
        "enterprise": "PLN004",
    }
    snapshot_months = [
        date(2025, 11, 1),
        date(2025, 12, 1),
        date(2026, 1, 1),
        date(2026, 2, 1),
        date(2026, 3, 1),
        date(2026, 4, 1),
    ]

    for account_id, *_ in SAAS_ACCOUNTS:
        tier_sequence = SAAS_ACCOUNT_SEQUENCES[account_id]
        last_known_tier = "starter"

        for snapshot_date, tier in zip(snapshot_months, tier_sequence):
            if tier is not None:
                last_known_tier = tier

            rows.append(
                {
                    "snapshot_date": snapshot_date.isoformat(),
                    "account_id": account_id,
                    "plan_id": plan_id_by_tier[last_known_tier],
                    "mrr_amount": SAAS_PLAN_MRR[tier] if tier is not None else 0,
                    "subscription_status": "active" if tier is not None else "cancelled",
                }
            )

    return rows


def build_it_service_ticket_rows(rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    start_date = date(2026, 1, 3)
    end_date = REFERENCE_DATE

    for ticket_number in range(1, 61):
        opened_date = random_date_between(rng, start_date, end_date)
        opened_at = datetime.combine(opened_date, time(hour=8 + ticket_number % 8, minute=15))

        priority = ["low", "medium", "high", "critical"][ticket_number % 4]
        sla_target_hours = {
            "low": 72,
            "medium": 48,
            "high": 24,
            "critical": 8,
        }[priority]

        first_response_hours = max(1, (ticket_number * 3) % 14)
        first_response_at = opened_at + timedelta(hours=first_response_hours)

        is_open_ticket = ticket_number % 5 == 0
        if is_open_ticket:
            resolved_at = ""
            status = ["open", "in_progress", "pending_customer"][ticket_number % 3]
            resolution_hours = ""
            breached_sla = "true" if (REFERENCE_DATE - opened_date).days * 24 > sla_target_hours else "false"
        else:
            resolution_delay = {
                "low": 18 + ticket_number % 60,
                "medium": 10 + ticket_number % 42,
                "high": 6 + ticket_number % 24,
                "critical": 2 + ticket_number % 12,
            }[priority]
            resolved_timestamp = opened_at + timedelta(hours=resolution_delay)
            resolved_at = resolved_timestamp.isoformat(timespec="minutes")
            status = "resolved"
            resolution_hours = resolution_delay
            breached_sla = "true" if resolution_delay > sla_target_hours else "false"

        rows.append(
            {
                "ticket_id": f"T{ticket_number:04d}",
                "opened_at": opened_at.isoformat(timespec="minutes"),
                "first_response_at": first_response_at.isoformat(timespec="minutes"),
                "resolved_at": resolved_at,
                "priority": priority,
                "status": status,
                "channel": CHANNELS[ticket_number % len(CHANNELS)],
                "support_team": SUPPORT_TEAMS[ticket_number % len(SUPPORT_TEAMS)],
                "technician_name": TECHNICIANS[ticket_number % len(TECHNICIANS)],
                "customer_segment": CUSTOMER_SEGMENTS[ticket_number % len(CUSTOMER_SEGMENTS)],
                "category": TICKET_CATEGORIES[ticket_number % len(TICKET_CATEGORIES)],
                "sla_target_hours": sla_target_hours,
                "first_response_hours": first_response_hours,
                "resolution_hours": resolution_hours,
                "breached_sla": breached_sla,
            }
        )

    return rows


def main() -> None:
    rng = random.Random(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    members = build_members(rng)
    fact_checkins = build_fact_checkin_rows(rng, members)

    write_csv(
        OUTPUT_DIR / "dim_partner.csv",
        ["partner_id", "partner_name", "region", "contract_status"],
        PARTNERS,
    )
    write_csv(
        OUTPUT_DIR / "dim_member.csv",
        ["member_id", "full_name", "email", "partner_id", "signup_date", "membership_status"],
        build_dim_member_rows(members),
    )
    write_csv(
        OUTPUT_DIR / "fact_membership.csv",
        ["member_id", "plan_name", "monthly_fee", "membership_start_date", "membership_end_date"],
        build_fact_membership_rows(rng, members),
    )
    write_csv(
        OUTPUT_DIR / "fact_checkin.csv",
        ["member_id", "checkin_timestamp"],
        fact_checkins,
    )
    write_csv(
        OUTPUT_DIR / "fact_class_booking.csv",
        ["booking_id", "member_id", "class_start_at", "booking_status"],
        build_fact_class_booking_rows(rng, members, fact_checkins),
    )
    write_csv(
        OUTPUT_DIR / "membership_export_raw.csv",
        [
            " Member ID ",
            "Full Name",
            "Email ",
            "Signup Date",
            "Last Checkin Date",
            "Membership Status",
            "Plan Name",
            "Monthly Fee",
            "Partner Name",
        ],
        build_membership_export_raw_rows(members, fact_checkins),
    )
    write_csv(
        OUTPUT_DIR / "dim_account.csv",
        ["account_id", "account_name", "region", "industry"],
        build_dim_account_rows(),
    )
    write_csv(
        OUTPUT_DIR / "dim_plan.csv",
        ["plan_id", "plan_name", "plan_tier"],
        build_dim_plan_rows(),
    )
    write_csv(
        OUTPUT_DIR / "fact_subscription_snapshot.csv",
        ["snapshot_date", "account_id", "plan_id", "mrr_amount", "subscription_status"],
        build_fact_subscription_snapshot_rows(),
    )
    write_csv(
        OUTPUT_DIR / "it_service_tickets.csv",
        [
            "ticket_id",
            "opened_at",
            "first_response_at",
            "resolved_at",
            "priority",
            "status",
            "channel",
            "support_team",
            "technician_name",
            "customer_segment",
            "category",
            "sla_target_hours",
            "first_response_hours",
            "resolution_hours",
            "breached_sla",
        ],
        build_it_service_ticket_rows(rng),
    )


if __name__ == "__main__":
    main()

