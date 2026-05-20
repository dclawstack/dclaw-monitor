"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "monitored_services",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("url", sa.String(2000), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("interval_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_monitored_services_name", "monitored_services", ["name"])

    op.create_table(
        "uptime_checks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("error", sa.String(1000), nullable=True),
        sa.Column("checked_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["monitored_services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_uptime_checks_service_id", "uptime_checks", ["service_id"])
    op.create_index("ix_uptime_checks_checked_at", "uptime_checks", ["checked_at"])

    op.create_table(
        "alert_rules",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=True),
        sa.Column("metric_name", sa.String(200), nullable=False),
        sa.Column("operator", sa.String(10), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="warning"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["monitored_services.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alert_rules_service_id", "alert_rules", ["service_id"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("rule_id", sa.UUID(), nullable=True),
        sa.Column("service_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="warning"),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("fired_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["rule_id"], ["alert_rules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["service_id"], ["monitored_services.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_rule_id", "alerts", ["rule_id"])
    op.create_index("ix_alerts_service_id", "alerts", ["service_id"])
    op.create_index("ix_alerts_status", "alerts", ["status"])
    op.create_index("ix_alerts_fired_at", "alerts", ["fired_at"])

    op.create_table(
        "metric_samples",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("labels", sa.JSON(), nullable=True),
        sa.Column("sampled_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["monitored_services.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_metric_samples_service_id", "metric_samples", ["service_id"])
    op.create_index("ix_metric_samples_name", "metric_samples", ["name"])
    op.create_index("ix_metric_samples_sampled_at", "metric_samples", ["sampled_at"])

    op.create_table(
        "log_entries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=True),
        sa.Column("level", sa.String(20), nullable=False, server_default="info"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("source", sa.String(500), nullable=True),
        sa.Column("attributes", sa.JSON(), nullable=True),
        sa.Column("logged_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["monitored_services.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_log_entries_service_id", "log_entries", ["service_id"])
    op.create_index("ix_log_entries_level", "log_entries", ["level"])
    op.create_index("ix_log_entries_logged_at", "log_entries", ["logged_at"])


def downgrade() -> None:
    op.drop_table("log_entries")
    op.drop_table("metric_samples")
    op.drop_table("alerts")
    op.drop_table("alert_rules")
    op.drop_table("uptime_checks")
    op.drop_table("monitored_services")
