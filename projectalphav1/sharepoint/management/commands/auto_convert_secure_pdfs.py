"""
Convert Secure HTML PDFs to Actual PDFs
========================================
Bypasses DRM/secure PDFs by rendering HTML and saving as PDF or images.
Uses Playwright to render and convert.

Usage:
    python manage.py auto_convert_secure_pdfs --source "C:\Downloads" --output "C:\converted"
    python manage.py auto_convert_secure_pdfs --source "C:\Downloads" --format png

File Naming Convention: auto_convert_secure_pdfs.py
Module: SharePoint
Purpose: Convert secure .PDF.html files to usable PDFs/images
"""

from django.core.management.base import BaseCommand
from pathlib import Path
import os


class Command(BaseCommand):
    help = 'Convert secure .PDF.html files to actual PDFs or images'
    
    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, required=True, help='Source folder with .PDF.html files')
        parser.add_argument('--output', type=str, help='Output folder (default: source/converted)')
        parser.add_argument('--format', type=str, choices=['pdf', 'png'], default='pdf', help='Output format')
        parser.add_argument('--connect', action='store_true', help='Connect to running Chrome (port 9222)')
        parser.add_argument('--dry-run', action='store_true', help='Preview only')
    
    def handle(self, *args, **options):
        source = Path(options['source'])
        output = Path(options.get('output') or source / 'converted')
        format_type = options['format']
        dry_run = options.get('dry_run', False)
        connect_mode = options.get('connect', False)
        
        if not source.exists():
            self.stdout.write(self.style.ERROR(f'Source folder not found: {source}'))
            return
        
        # Find all .PDF.html files
        html_files = list(source.glob('**/*.PDF.html')) + list(source.glob('**/*.pdf.html'))
        
        if not html_files:
            self.stdout.write('No .PDF.html files found')
            return
        
        self.stdout.write(f'\nFound {len(html_files)} files to convert\n')
        self.stdout.write(f'Source: {source}')
        self.stdout.write(f'Output: {output}')
        self.stdout.write(f'Format: {format_type.upper()}\n')
        
        if dry_run:
            for file in html_files:
                out_name = file.stem.replace('.PDF', f'.{format_type}').replace('.pdf', f'.{format_type}')
                self.stdout.write(f'[DRY RUN] {file.name} → {out_name}')
            return
        
        # Create output folder
        output.mkdir(parents=True, exist_ok=True)
        
        # Import Playwright
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.stdout.write(self.style.ERROR('Playwright not installed!'))
            self.stdout.write('Run: pip install playwright && playwright install chromium')
            return
        
        # Process files
        converted = 0
        failed = 0
        
        with sync_playwright() as p:
            if connect_mode:
                # Connect to running Chrome
                self.stdout.write(self.style.SUCCESS('Connecting to running Chrome...\n'))
                try:
                    browser = p.chromium.connect_over_cdp('http://localhost:9222')
                    self.stdout.write(self.style.SUCCESS(f'✓ Connected! Contexts: {len(browser.contexts)}'))
                    context = browser.contexts[0] if browser.contexts else browser.new_context()
                    page = context.pages[0] if context.pages else context.new_page()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'✗ Connection failed: {str(e)}'))
                    self.stdout.write('\nStart Chrome with: & "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
                    return
            else:
                # Launch browser for interactive login
                self.stdout.write(self.style.SUCCESS('Opening browser...\n'))
                browser = p.chromium.launch(headless=False, channel='chrome')
                context = browser.new_context()
                page = context.new_page()
            
            # Open first file so user can login
            if html_files:
                first_file = html_files[0]
                self.stdout.write(f'Opening first file for login: {first_file.name}')
                page.goto(f'file:///{str(first_file.absolute()).replace(os.sep, "/")}')
                
                self.stdout.write(self.style.WARNING('\n' + '='*80))
                self.stdout.write(self.style.WARNING('LOGIN TO VERA IN THE BROWSER'))
                self.stdout.write(self.style.WARNING('='*80))
                self.stdout.write('\n1. Complete Vera login in the browser window')
                self.stdout.write('2. Wait for PDF to load')
                self.stdout.write('3. Press ENTER here to start batch conversion\n')
                input('Press ENTER when logged in and PDF is visible >>> ')
                
                self.stdout.write(self.style.SUCCESS('\n✓ Starting batch conversion with your session...\n'))
            
            for idx, html_file in enumerate(html_files, 1):
                try:
                    # Output filename
                    out_name = html_file.stem.replace('.PDF', '').replace('.pdf', '')
                    
                    if format_type == 'pdf':
                        out_file = output / f"{out_name}.pdf"
                    else:
                        out_file = output / f"{out_name}.png"
                    
                    self.stdout.write(f'[{idx}/{len(html_files)}] Converting: {html_file.name}')
                    
                    # Load HTML file
                    page.goto(f'file:///{str(html_file.absolute()).replace(os.sep, "/")}')
                    
                    # Wait for content to load
                    page.wait_for_load_state('networkidle', timeout=10000)
                    
                    # Convert based on format
                    if format_type == 'pdf':
                        page.pdf(
                            path=str(out_file),
                            format='Letter',
                            print_background=True,
                            margin={'top': '0.5in', 'right': '0.5in', 'bottom': '0.5in', 'left': '0.5in'}
                        )
                    else:
                        # Full page screenshot
                        page.screenshot(path=str(out_file), full_page=True)
                    
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Saved: {out_file.name}'))
                    converted += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed: {str(e)[:100]}'))
                    failed += 1
            
            browser.close()
        
        # Summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS(f'✓ Converted: {converted}'))
        if failed > 0:
            self.stdout.write(self.style.ERROR(f'✗ Failed: {failed}'))
        self.stdout.write(f'\nOutput folder: {output}')
        self.stdout.write('\nNext: Upload converted files to SharePoint via platform!')

