import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath("."))

from app.platform.database import get_session
from app.models.tables import User, Organization, OrgMembership, AuditLog
from app.platform.security import hash_password
from sqlalchemy import select

DEMO_EMAIL = "operator@finsentinel.io"
DEMO_PASSWORD = "Str0ngPassw0rd123"

async def seed():
    async for session in get_session():
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == DEMO_EMAIL))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                id=uuid.uuid4(),
                email=DEMO_EMAIL,
                password_hash=hash_password(DEMO_PASSWORD),
                display_name="Operations Lead",
                is_admin=True,
            )
            session.add(user)
            await session.flush()
            print(f"Created user: {user.email}")
        else:
            user.password_hash = hash_password(DEMO_PASSWORD)
            user.is_admin = True
            await session.flush()
            print(f"Updated user: {user.email}")

        # Check or create an organization
        org_result = await session.execute(select(Organization).limit(1))
        org = org_result.scalar_one_or_none()

        if not org:
            org = Organization(
                id=uuid.uuid4(),
                name="FinSentinel Apex Corp",
                slug="finsentinel-apex",
            )
            session.add(org)
            await session.flush()
            print(f"Created organization: {org.name}")

        # Check or create membership
        mem_result = await session.execute(
            select(OrgMembership).where(
                OrgMembership.user_id == user.id,
                OrgMembership.org_id == org.id,
            )
        )
        membership = mem_result.scalar_one_or_none()
        if not membership:
            membership = OrgMembership(
                user_id=user.id,
                org_id=org.id,
                role="owner",
            )
            session.add(membership)
            await session.flush()
            print(f"Assigned owner role to {user.email} in {org.name}")

        # Add initial audit log entries if empty
        audit_count = await session.execute(select(AuditLog).limit(1))
        if not audit_count.scalar_one_or_none():
            audit_events = [
                ("auth.login", "user", str(user.id), {"method": "password"}),
                ("ingestion.csv_batch", "batch", str(uuid.uuid4()), {"records": 1500, "status": "processed"}),
                ("reconciliation.run_created", "recon_run", str(uuid.uuid4()), {"total": 1500, "matched": 1492}),
                ("fingraph.node_added", "service", "payment-router-prod", {"critical": True}),
                ("threat.sms_analyzed", "threat_event", str(uuid.uuid4()), {"risk": "critical", "source": "smishing"}),
                ("regimpact.rule_reviewed", "rule", str(uuid.uuid4()), {"decision": "confirmed"}),
            ]
            for action, r_type, r_id, payload in audit_events:
                audit = AuditLog(
                    id=uuid.uuid4(),
                    actor_user_id=user.id,
                    action=action,
                    resource_type=r_type,
                    resource_id=r_id,
                    ip_address="127.0.0.1",
                    payload=payload,
                    occurred_at=datetime.now(timezone.utc),
                )
                session.add(audit)
            print("Added sample audit log entries")

        await session.commit()
        print("\n--- SEED COMPLETE ---")
        print(f"Login Email:    {DEMO_EMAIL}")
        print(f"Login Password: {DEMO_PASSWORD}")
        print(f"Role:           owner (Admin)")
        print(f"Organization:   {org.name} ({org.id})")
        break

if __name__ == "__main__":
    asyncio.run(seed())
