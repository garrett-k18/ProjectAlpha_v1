"""Add trade settlement statement ETL models."""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Migration for trade settlement statement document + ETL models."""

    dependencies = [
        ("etl", "0016_eomtrialbalancedata_eomtrusttrackingdata"),
        ("acq_module", "0044_servicerloanextract_servicertransactionextract"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TradeSettlementStatementDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file_name", models.CharField(max_length=255)),
                ("file_path", models.CharField(max_length=1024)),
                ("file_mime_type", models.CharField(blank=True, max_length=100)),
                ("file_size_bytes", models.BigIntegerField(blank=True, null=True)),
                ("uploaded_at", models.DateTimeField()),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("in_progress", "In Progress"),
                            ("partial", "Partial"),
                            ("complete", "Complete"),
                            ("failed", "Failed"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("status_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="trade_settlement_documents",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "etl_trade_settlement_document",
                "ordering": ["-uploaded_at"],
            },
        ),
        migrations.CreateModel(
            name="TradeSettlementStatementETL",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("statement_date", models.CharField(blank=True, db_index=True, max_length=20)),
                ("settlement_date", models.CharField(blank=True, db_index=True, max_length=20)),
                ("trade_name", models.CharField(blank=True, max_length=255)),
                ("seller_name", models.CharField(blank=True, max_length=255)),
                ("buyer_name", models.CharField(blank=True, max_length=255)),
                ("accepted_bid_amount", models.CharField(blank=True, max_length=50)),
                ("deposit_amount", models.CharField(blank=True, max_length=50)),
                ("pool_name", models.CharField(blank=True, max_length=100)),
                ("currency_code", models.CharField(blank=True, max_length=3)),
                ("total_upb", models.CharField(blank=True, max_length=50)),
                ("total_purchase_price", models.CharField(blank=True, max_length=50)),
                ("total_adjustments", models.CharField(blank=True, max_length=50)),
                ("net_purchase_price", models.CharField(blank=True, max_length=50)),
                ("notes", models.TextField(blank=True)),
                ("extracted_at", models.DateTimeField(auto_now_add=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="trade_settlement_statements_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="statements",
                        to="etl.tradesettlementstatementdocument",
                    ),
                ),
                (
                    "trade",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="trade_settlement_statements",
                        to="acq_module.trade",
                    ),
                ),
            ],
            options={
                "db_table": "etl_trade_settlement_statement",
                "ordering": ["-statement_date", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="TradeSettlementStatementLineItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("line_number", models.IntegerField()),
                ("description", models.CharField(blank=True, max_length=255)),
                ("amount", models.CharField(blank=True, max_length=50)),
                ("category", models.CharField(blank=True, max_length=100)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "statement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="line_items",
                        to="etl.tradesettlementstatementetl",
                    ),
                ),
            ],
            options={
                "db_table": "etl_trade_settlement_statement_line_item",
                "ordering": ["statement_id", "line_number"],
            },
        ),
        migrations.AddIndex(
            model_name="tradesettlementstatementetl",
            index=models.Index(fields=["trade"], name="etl_stst_trade_idx"),
        ),
        migrations.AddIndex(
            model_name="tradesettlementstatementetl",
            index=models.Index(fields=["settlement_date"], name="etl_stst_sett_dt_idx"),
        ),
        migrations.AddIndex(
            model_name="tradesettlementstatementetl",
            index=models.Index(fields=["statement_date"], name="etl_stst_stmt_dt_idx"),
        ),
        migrations.AddIndex(
            model_name="tradesettlementstatementlineitem",
            index=models.Index(fields=["statement"], name="etl_stst_line_stmt_idx"),
        ),
        migrations.AddIndex(
            model_name="tradesettlementstatementlineitem",
            index=models.Index(fields=["line_number"], name="etl_stst_line_num_idx"),
        ),
    ]
