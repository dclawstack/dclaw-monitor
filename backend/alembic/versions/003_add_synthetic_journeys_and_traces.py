"""add synthetic journeys and traces

Revision ID: 003
Revises: 001
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Incidents table
    op.create_table(
        "incidents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("severity", sa.String(20), nullable=False, server_default="warning"),
        sa.Column("service_id", sa.UUID(), nullable=True),
        sa.Column("alert_ids", sa.JSON(), nullable=True),
        sa.Column("rca_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["service_id"], ["monitored_services.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_incidents_status", "incidents", ["status"])
    op.create_index("ix_incidents_service_id", "incidents", ["service_id"])
    op.create_index("ix_incidents_created_at", "incidents", ["created_at"])

    # Synthetic journeys table
    op.create_table(
        "synthetic_journeys",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=True),
        sa.Column("steps", sa.JSON(), nullable=True),
        sa.Column("interval_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["monitored_services.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_synthetic_journeys_service_id", "synthetic_journeys", ["service_id"])

    # Trace spans table
    op.create_table(
        "trace_spans",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("span_id", sa.String(64), nullable=False),
        sa.Column("parent_span_id", sa.String(64), nullable=True),
        sa.Column("service_id", sa.UUID(), nullable=True),
        sa.Column("operation_name", sa.String(500), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("duration_ms", sa.Float(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="ok"),
        sa.Column("attributes", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["service_id"], ["monitored_services.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trace_spans_trace_id", "trace_spans", ["trace_id"])
    op.create_index("ix_trace_spans_service_id", "trace_spans", ["service_id"])
    op.create_index("ix_trace_spans_start_time", "trace_spans", ["start_time"])


def downgrade() -> None:
    op.drop_table("trace_spans")
    op.drop_table("synthetic_journeys")
    op.drop_table("incidents")
