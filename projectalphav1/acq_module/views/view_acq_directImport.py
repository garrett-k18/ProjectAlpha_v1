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
import tempfile
import subprocess
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.uploadedfile import UploadedFile
import logging

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
        
        # Debug logging
        logger.info(f'Import request - seller_name: {seller_name}, trade_name: {trade_name}, dry_run: {dry_run}, no_ai: {no_ai}, limit_rows: {limit_rows}')
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
            # Clean up temporary file
            # WHAT: Delete temporary file after processing
            # WHY: Prevent disk space issues from accumulating temp files
            # HOW: os.unlink to remove file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f'Failed to delete temp file {temp_file_path}: {e}')
    
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
