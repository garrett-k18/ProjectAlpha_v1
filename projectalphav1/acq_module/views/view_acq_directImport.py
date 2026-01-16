"""
API endpoint for importing seller data tapes via file upload.

WHAT: Handles file upload and triggers the ETL management command
WHY: Allows users to import Excel/CSV files from the frontend UI
HOW: Receives file, saves temporarily, executes Django management command, returns results

Documentation reviewed:
- Django file uploads: https://docs.djangoproject.com/en/5.2/topics/http/file-uploads/
- DRF APIView: https://www.django-rest-framework.org/api-guide/views/
- Django management commands: https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/
- sys.executable: https://docs.python.org/3/library/sys.html#sys.executable
"""
import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.uploadedfile import UploadedFile
import logging

from acq_module.models.model_acq_seller import SellerRawData
from core.models.model_core_notification import Notification

logger = logging.getLogger(__name__)


@api_view(['POST'])
def import_seller_tape(request):
    """
    WHAT: API endpoint to upload and import seller data tape files
    WHY: Provides UI-driven import functionality using the ETL command
    HOW: Saves uploaded file temporarily, calls management command, returns results
    
    Request body:
    - file: Excel/CSV file (multipart/form-data)
    - seller_name: str (required)
    - trade_name: str (optional)
    - auto_create: bool (default: true)
    - dry_run: bool (default: false)
    
    Returns:
    - 200: Success with import results
    - 400: Validation error
    - 500: Import failed
    """
    try:
        # Validate file upload
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file: UploadedFile = request.FILES['file']
        # Use request.POST for multipart/form-data (not request.data)
        seller_name = request.POST.get('seller_name', '').strip()
        trade_name = request.POST.get('trade_name', '').strip()
        dry_run = request.POST.get('dry_run', 'false').lower() == 'true'
        no_ai = request.POST.get('no_ai', 'false').lower() == 'true'  # Disable AI column mapping for speed
        limit_rows = request.POST.get('limit_rows', '').strip()  # Limit to N rows for testing
        
        # Get manual column mapping if provided
        column_mapping_str = request.POST.get('column_mapping', '').strip()
        column_mapping = None
        if column_mapping_str:
            try:
                column_mapping = json.loads(column_mapping_str)
                logger.info(f'Manual column mapping provided with {len(column_mapping)} mappings')
            except json.JSONDecodeError as e:
                logger.warning(f'Failed to parse column_mapping JSON: {e}')
        
        # Debug logging
        logger.info(f'Import request - seller_name: {seller_name}, trade_name: {trade_name}, dry_run: {dry_run}, no_ai: {no_ai}, limit_rows: {limit_rows}, has_manual_mapping: {column_mapping is not None}')
        logger.info(f'POST data: {dict(request.POST)}')
        
        # Validate seller name
        if not seller_name:
            return Response(
                {'error': 'Seller name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file extension
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in ['.xlsx', '.xls', '.csv']:
            return Response(
                {'error': f'Invalid file type: {file_ext}. Only Excel (.xlsx, .xls) and CSV (.csv) files are supported.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save file to temporary location
        # WHAT: Create temporary file to store upload
        # WHY: Management command needs a file path to read from
        # HOW: Use tempfile to create secure temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            # Write uploaded file to temp location
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Build management command arguments
            # WHAT: Construct command to call import_seller_data management command
            # WHY: Reuse existing ETL logic instead of duplicating code
            # HOW: Use subprocess with sys.executable to ensure venv Python is used
            # DOCS: sys.executable returns path to Python interpreter running Django server
            cmd = [
                sys.executable,  # Use current Python interpreter (with venv packages)
                '-u',  # Unbuffered output for real-time logging visibility
                'manage.py',
                'import_seller_data',
                '--file', temp_file_path,
                '--seller-name', seller_name,
                '--auto-create',  # Always auto-create seller/trade from UI imports
            ]
            
            if trade_name:
                cmd.extend(['--trade-name', trade_name])
            
            if dry_run:
                cmd.append('--dry-run')
            
            if no_ai:
                cmd.append('--no-ai')  # Disable AI column mapping for faster imports
            
            if limit_rows:
                cmd.extend(['--limit-rows', limit_rows])  # Limit rows for testing
            
            # If manual column mapping provided, save to temp config file
            # Also auto-disable AI to skip AI value validation (major speed boost)
            config_file_path = None
            if column_mapping:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as config_file:
                    config = {
                        'version': '1.0',
                        'description': 'Manual column mapping from UI',
                        'column_mapping': column_mapping
                    }
                    json.dump(config, config_file)
                    config_file_path = config_file.name
                cmd.extend(['--config', config_file_path])
                # IMPORTANT: When using manual mapping, disable AI value validation
                # Otherwise each choice field (occupancy, property_type, etc.) triggers AI calls per unique value
                if '--no-ai' not in cmd:
                    cmd.append('--no-ai')
                    logger.info('Auto-disabled AI for manual mapping (skipping AI value validation)')
                logger.info(f'Saved manual mapping to temp config: {config_file_path}')
            
            # Execute management command
            # WHAT: Run the import command and capture output
            # WHY: Need to return results to frontend
            # HOW: subprocess.run with capture_output=True and unbuffered output
            # TIMEOUT: 20 minutes for large files (600+ records with AI processing)
            # NOTE: Output is buffered until completion - for real-time progress, consider WebSockets
            logger.info(f'Executing import command: {" ".join(cmd)}')
            logger.info(f'Import starting at {__import__("datetime").datetime.now().isoformat()}')
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),  # Project root
                timeout=1200,  # 20 minute timeout for large imports with AI column mapping
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}  # Force unbuffered output
            )
            
            logger.info(f'Import completed at {__import__("datetime").datetime.now().isoformat()}')
            
            # Check if command succeeded
            if result.returncode == 0:
                # Parse output to extract seller/trade IDs and stats
                output = result.stdout
                seller_id = None
                trade_id = None
                records_imported = 0
                
                # Extract seller ID from output like "Created new Seller: HUD (ID: 123)"
                import re
                seller_match = re.search(r'Seller.*\(ID: (\d+)\)', output)
                if seller_match:
                    seller_id = int(seller_match.group(1))
                
                # Extract trade ID from output like "Created NEW Trade: HUD - 10.28.25 (ID: 456)"
                trade_match = re.search(r'Trade.*\(ID: (\d+)\)', output)
                if trade_match:
                    trade_id = int(trade_match.group(1))
                
                # Extract record count from output like "Created: 50, Updated: 0, Skipped: 0"
                records_match = re.search(r'Created: (\d+)', output)
                if records_match:
                    records_imported = int(records_match.group(1))

                Notification.objects.create(
                    event_type=Notification.EventType.TRADE_IMPORT,
                    title="Trade Import Completed",
                    message=f"Imported {records_imported} records for seller {seller_name}.",
                    created_by=getattr(request, 'user', None) if getattr(request, 'user', None) and request.user.is_authenticated else None,
                    metadata={
                        "seller_id": seller_id,
                        "trade_id": trade_id,
                        "seller_name": seller_name,
                        "records_imported": records_imported,
                    },
                )
                
                # Success
                return Response({
                    'success': True,
                    'message': f'Successfully imported {records_imported} records!',
                    'seller_id': seller_id,
                    'trade_id': trade_id,
                    'seller_name': seller_name,
                    'records_imported': records_imported,
                    'output': output,
                    'stderr': result.stderr,  # Include stderr for debugging
                    'dry_run': dry_run
                })
            else:
                # Command failed
                logger.error(f'Import command failed: {result.stderr}')
                return Response({
                    'error': 'Import failed',
                    'details': result.stderr or result.stdout,
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        finally:
            # Clean up temporary files
            # WHAT: Delete temporary files after processing
            # WHY: Prevent disk space issues from accumulating temp files
            # HOW: os.unlink to remove files
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f'Failed to delete temp file {temp_file_path}: {e}')
            
            # Clean up config file if created
            if config_file_path:
                try:
                    os.unlink(config_file_path)
                except Exception as e:
                    logger.warning(f'Failed to delete config file {config_file_path}: {e}')
    
    except subprocess.TimeoutExpired as timeout_err:
        # WHAT: Handle timeout but return partial output for debugging
        # WHY: User needs to see where the import got stuck
        # HOW: Capture stdout/stderr from the TimeoutExpired exception
        partial_output = ''
        if hasattr(timeout_err, 'stdout') and timeout_err.stdout:
            partial_output += 'STDOUT:\n' + timeout_err.stdout
        if hasattr(timeout_err, 'stderr') and timeout_err.stderr:
            partial_output += '\n\nSTDERR:\n' + timeout_err.stderr
        
        logger.error(f'Import timeout after 20 minutes. Partial output:\n{partial_output}')
        
        return Response({
            'error': 'Import timeout',
            'details': (
                'Import took longer than 20 minutes. '
                'Check the output below to see where it got stuck.\n\n'
                'Consider breaking the file into smaller batches or disabling AI with --no-ai flag.'
            ),
            'output': partial_output or 'No output captured before timeout'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.exception('Unexpected error during import')
        return Response({
            'error': 'Import failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def preview_seller_tape(request):
    """
    WHAT: Preview file headers for manual column mapping
    WHY: Allow users to see source columns and map them manually before import
    HOW: Uses FileProcessor to detect headers, returns source columns and target field options
    
    Request body:
    - file: Excel/CSV file (multipart/form-data)
    
    Returns:
    - 200: Success with source columns, detected header row, and available target fields
    - 400: Validation error
    - 500: Preview failed
    """
    try:
        # Validate file upload
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file: UploadedFile = request.FILES['file']
        
        # Validate file extension
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in ['.xlsx', '.xls', '.csv']:
            return Response(
                {'error': f'Invalid file type: {file_ext}. Only Excel (.xlsx, .xls) and CSV (.csv) files are supported.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Use FileProcessor to read headers
            from etl.services import FileProcessor
            processor = FileProcessor(Path(temp_file_path), auto_detect_headers=True)
            df = processor.read(sheet=0, skip_rows=0)
            
            # Get source columns from file
            source_columns = list(df.columns)
            
            # Get available target fields from SellerRawData model
            target_fields = []
            for field in SellerRawData._meta.get_fields():
                if field.auto_created or field.name in ['asset_hub', 'seller', 'trade']:
                    continue
                field_type = field.get_internal_type()
                help_text = getattr(field, 'help_text', '') or ''
                target_fields.append({
                    'name': field.name,
                    'type': field_type,
                    'description': help_text or f'{field.name} ({field_type})'
                })
            
            # Sort target fields alphabetically for easier selection
            target_fields.sort(key=lambda x: x['name'])
            
            # Get sample data (first 3 rows) for each column to help with mapping
            sample_data = {}
            for col in source_columns:
                samples = df[col].dropna().head(3).tolist()
                sample_data[col] = [str(s)[:50] for s in samples]  # Truncate long values
            
            return Response({
                'success': True,
                'source_columns': source_columns,
                'target_fields': target_fields,
                'sample_data': sample_data,
                'row_count': len(df),
                'file_name': uploaded_file.name
            })
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f'Failed to delete temp file {temp_file_path}: {e}')
    
    except Exception as e:
        logger.exception('Unexpected error during file preview')
        return Response({
            'error': 'Preview failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
