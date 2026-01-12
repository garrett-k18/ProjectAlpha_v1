from __future__ import annotations

import csv
import os
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from core.management.utils.prod_db_helper import add_prod_db_args, setup_prod_db, check_db_connection
from core.models import AssetIdHub

from am_module.models.model_am_amData import (
    FCSale,
    FCTask,
    REOData,
    REOtask,
    DIL,
    DILTask,
    ShortSale,
    ShortSaleTask,
    Modification,
    ModificationTask,
    NoteSale,
    NoteSaleTask,
)


class Command(BaseCommand):
    help = 'Backfill AM tracks and tasks from CSV using servicer_id'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            required=True,
            help='Path to CSV file relative to project root',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created/updated without writing to DB',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=200,
            help='Number of records to process per batch (default: 200)',
        )
        add_prod_db_args(parser)

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        batch_size = options['batch_size']

        # Setup database connection
        if not options.get('prod') and not options.get('dev'):
            # Default behavior for this project: use NEWDEV connection from .env when not specified
            os.environ['DATABASE_URL'] = os.getenv('DB_NEWDEV')
            db_alias = 'default'
        else:
            db_alias = setup_prod_db(options)

        check_db_connection(options, self)

        project_root = Path(__file__).resolve().parents[3]
        csv_path = project_root / csv_file
        if not csv_path.exists():
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Reading CSV from: {csv_path}'))
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE: No records will be created/updated.'))

        rows = self._read_csv(csv_path)
        if not rows:
            self.stdout.write(self.style.WARNING('No rows found in CSV'))
            return

        stats = {
            'processed': 0,
            'created_tracks': 0,
            'created_tasks': 0,
            'updated_tasks': 0,
            'skipped_invalid': 0,
            'not_found': 0,
            'errors': 0,
        }

        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            try:
                with transaction.atomic(using=db_alias):
                    for row in batch:
                        try:
                            result = self._process_row(row=row, db_alias=db_alias, dry_run=dry_run)
                            if result is None:
                                stats['skipped_invalid'] += 1
                            else:
                                for k, v in result.items():
                                    stats[k] += v
                            stats['processed'] += 1
                        except AssetIdHub.DoesNotExist:
                            stats['not_found'] += 1
                            stats['processed'] += 1
                        except Exception:
                            stats['errors'] += 1
                            stats['processed'] += 1
            except Exception:
                # If any exception escapes the per-row handler, count the whole batch as errors
                stats['errors'] += len(batch)

        self.stdout.write(self.style.SUCCESS('\n=== Import Complete ==='))
        self.stdout.write(f"Processed:       {stats['processed']}")
        self.stdout.write(f"Tracks created:  {stats['created_tracks']}")
        self.stdout.write(f"Tasks created:   {stats['created_tasks']}")
        self.stdout.write(f"Tasks updated:   {stats['updated_tasks']}")
        self.stdout.write(f"Not Found:       {stats['not_found']}")
        self.stdout.write(f"Skipped invalid: {stats['skipped_invalid']}")
        self.stdout.write(f"Errors:          {stats['errors']}")

    def _read_csv(self, csv_path: Path):
        required = {'servicer_id', 'track', 'task_type'}
        rows = []
        with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return []
            missing = required - set(h.strip() for h in reader.fieldnames)
            if missing:
                raise ValueError(f"CSV missing required columns: {sorted(missing)}")
            for row in reader:
                rows.append(row)
        return rows

    def _parse_date(self, raw: str | None):
        if raw is None:
            return None
        s = str(raw).strip()
        if not s:
            return None
        # Expect YYYY-MM-DD
        return datetime.strptime(s, '%Y-%m-%d').date()

    def _process_row(self, row, db_alias: str, dry_run: bool):
        servicer_id = (row.get('servicer_id') or '').strip()
        track = (row.get('track') or '').strip().lower()
        task_type = (row.get('task_type') or '').strip().lower()
        task_started = self._parse_date(row.get('task_started'))

        if not servicer_id or not track or not task_type:
            return None

        mapping = {
            'fc': {
                'outcome_model': FCSale,
                'task_model': FCTask,
                'task_fk_name': 'fc_sale',
            },
            'reo': {
                'outcome_model': REOData,
                'task_model': REOtask,
                'task_fk_name': 'reo_outcome',
            },
            'dil': {
                'outcome_model': DIL,
                'task_model': DILTask,
                'task_fk_name': 'dil',
            },
            'short_sale': {
                'outcome_model': ShortSale,
                'task_model': ShortSaleTask,
                'task_fk_name': 'short_sale',
            },
            'modification': {
                'outcome_model': Modification,
                'task_model': ModificationTask,
                'task_fk_name': 'modification',
            },
            'note_sale': {
                'outcome_model': NoteSale,
                'task_model': NoteSaleTask,
                'task_fk_name': 'note_sale',
            },
        }

        if track not in mapping:
            return None

        asset_hub = AssetIdHub.objects.using(db_alias).get(servicer_id=servicer_id)

        outcome_model = mapping[track]['outcome_model']
        task_model = mapping[track]['task_model']
        task_fk_name = mapping[track]['task_fk_name']

        created_tracks = 0
        created_tasks = 0
        updated_tasks = 0

        if dry_run:
            # Just simulate existence checks
            outcome_exists = outcome_model.objects.using(db_alias).filter(asset_hub_id=asset_hub.id).exists()
            if not outcome_exists:
                created_tracks = 1

            task_qs = task_model.objects.using(db_alias).filter(asset_hub_id=asset_hub.id, task_type=task_type)
            if task_qs.exists():
                updated_tasks = 1
            else:
                created_tasks = 1

            return {
                'created_tracks': created_tracks,
                'created_tasks': created_tasks,
                'updated_tasks': updated_tasks,
            }

        outcome_obj, created = outcome_model.objects.using(db_alias).get_or_create(asset_hub=asset_hub)
        if created:
            created_tracks = 1

        defaults = {
            'asset_hub': asset_hub,
            task_fk_name: outcome_obj,
        }
        if task_started is not None:
            defaults['task_started'] = task_started

        obj, created_task = task_model.objects.using(db_alias).update_or_create(
            asset_hub=asset_hub,
            task_type=task_type,
            defaults=defaults,
        )

        if created_task:
            created_tasks = 1
        else:
            updated_tasks = 1

        return {
            'created_tracks': created_tracks,
            'created_tasks': created_tasks,
            'updated_tasks': updated_tasks,
        }
