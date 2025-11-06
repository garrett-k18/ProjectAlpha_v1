"""
File Processing Module

WHAT: Reads and decrypts Excel/CSV files
WHY: Handles various file formats and password-protected files
HOW: Uses pandas for reading, msoffcrypto for decryption

USAGE:
    processor = FileProcessor(file_path, password="SA12345$")
    df = processor.read(sheet=0, skip_rows=0)
"""

import os
import io
import logging
from pathlib import Path
from typing import Optional, Any, Tuple

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class FileProcessor:
    """
    WHAT: Handles reading Excel/CSV files with optional password decryption
    WHY: Centralizes file reading logic and password handling
    HOW: Uses pandas and msoffcrypto-tool for decryption
    """

    def __init__(self, file_path: Path, password: Optional[str] = None, auto_detect_headers: bool = True, stdout=None):
        """
        Initialize file processor

        Args:
            file_path: Path to Excel/CSV file
            password: Optional password for encrypted files
            auto_detect_headers: Automatically detect where data starts (default: True)
            stdout: Django stdout for progress messages
        """
        self.file_path = Path(file_path)
        self.password = password
        self.auto_detect_headers = auto_detect_headers
        self.stdout = stdout

    def read(self, sheet: Any = 0, skip_rows: int = 0) -> pd.DataFrame:
        """
        WHAT: Read Excel or CSV file into a pandas DataFrame
        WHY: Supports multiple file formats commonly used for data sharing
        HOW: Uses pandas read_excel() or read_csv() based on file extension

        DOCS: https://pandas.pydata.org/docs/reference/io.html

        Args:
            sheet: Sheet name or index for Excel files (default: 0)
            skip_rows: Number of rows to skip at beginning (default: 0)

        Returns:
            DataFrame with file data

        Raises:
            ValueError: If file format unsupported or reading fails
        """
        file_ext = self.file_path.suffix.lower()

        try:
            # Auto-detect header row if enabled and skip_rows is 0 (not manually set)
            if self.auto_detect_headers and skip_rows == 0:
                # STEP 1: Read file WITHOUT headers (header=None) for detection
                if file_ext in ['.xlsx', '.xls']:
                    df_raw = self._read_excel(sheet, skip_rows=0, header=None)
                elif file_ext == '.csv':
                    df_raw = self._read_csv(skip_rows=0, header=None)
                else:
                    raise ValueError(f'Unsupported file format: {file_ext}. Use .xlsx, .xls, or .csv')

                # STEP 2: Detect where headers actually are
                header_row, data_start_row = self._detect_header_row(df_raw)

                if self.stdout:
                    self.stdout.write(
                        f'      [AUTO-DETECT] Found headers at row {header_row + 1}, '
                        f'data starts at row {data_start_row + 1}\n'
                    )

                # STEP 3: Re-read with correct header row
                # skiprows: skip all rows BEFORE header_row
                # header: use next row (row 0 after skipping) as column names
                if file_ext in ['.xlsx', '.xls']:
                    df = self._read_excel(sheet, skip_rows=header_row, header=0)
                else:
                    df = self._read_csv(skip_rows=header_row, header=0)

                # STEP 4: Skip any intermediate rows between header and data_start
                # After reading with header at header_row, data_start_row becomes relative
                rows_to_skip = data_start_row - header_row - 1
                if rows_to_skip > 0:
                    if self.stdout:
                        self.stdout.write(f'      [DEBUG] Skipping {rows_to_skip} rows between header and data\n')
                    df = df.iloc[rows_to_skip:].reset_index(drop=True)
            else:
                # No auto-detection, read normally
                if file_ext in ['.xlsx', '.xls']:
                    df = self._read_excel(sheet, skip_rows, header=0)
                elif file_ext == '.csv':
                    df = self._read_csv(skip_rows, header=0)
                else:
                    raise ValueError(f'Unsupported file format: {file_ext}. Use .xlsx, .xls, or .csv')

            # Clean column names: strip whitespace, replace special chars
            df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

            # Debug logging for final DataFrame
            if self.stdout and self.auto_detect_headers:
                self.stdout.write(f'      [DEBUG] Final DataFrame shape: {df.shape[0]} rows, {df.shape[1]} columns\n')
                self.stdout.write(f'      [DEBUG] Column names: {", ".join(df.columns[:5].tolist())}{"..." if len(df.columns) > 5 else ""}\n')
                if len(df) > 0:
                    first_row_sample = df.iloc[0].head(3).tolist()
                    self.stdout.write(f'      [DEBUG] First data row sample: {first_row_sample}\n')

            return df

        except Exception as e:
            raise ValueError(f'Error reading file: {str(e)}')

    def _read_excel(self, sheet: Any, skip_rows: int, header: Any = 0) -> pd.DataFrame:
        """
        WHAT: Read Excel file with password support
        WHY: Many seller files are password-protected
        HOW: Decrypt with msoffcrypto if password provided, then read with pandas

        Args:
            sheet: Sheet name or index
            skip_rows: Rows to skip
            header: Row to use as column names (default: 0), or None to not use headers

        Returns:
            DataFrame with Excel data
        """
        file_ext = self.file_path.suffix.lower()

        read_kwargs = {
            'sheet_name': sheet,
            'skiprows': skip_rows,
            'header': header,
            'dtype': str,  # Read all as string initially for safer processing
            'na_values': ['', 'NA', 'N/A', 'null', 'NULL', 'None']
        }

        if file_ext == '.xlsx':
            read_kwargs['engine'] = 'openpyxl'

            # Handle password-protected files
            if self.password:
                try:
                    import msoffcrypto

                    # Decrypt the file
                    decrypted = io.BytesIO()
                    with open(self.file_path, 'rb') as f:
                        office_file = msoffcrypto.OfficeFile(f)
                        office_file.load_key(password=self.password)
                        office_file.decrypt(decrypted)

                    decrypted.seek(0)
                    df = pd.read_excel(decrypted, **read_kwargs)

                except ImportError:
                    if self.stdout:
                        self.stdout.write(
                            '   [WARNING] msoffcrypto-tool not installed. '
                            'Install with: pip install msoffcrypto-tool\n'
                        )
                    # Try without password
                    df = pd.read_excel(self.file_path, **read_kwargs)

                except Exception as decrypt_error:
                    raise ValueError(f'Failed to decrypt password-protected Excel: {str(decrypt_error)}')
            else:
                df = pd.read_excel(self.file_path, **read_kwargs)

        else:  # .xls
            read_kwargs['engine'] = 'xlrd'
            df = pd.read_excel(self.file_path, **read_kwargs)

        return df

    def _read_csv(self, skip_rows: int, header: Any = 0) -> pd.DataFrame:
        """
        WHAT: Read CSV file with intelligent encoding detection
        WHY: Some sellers provide CSV files in various encodings (UTF-8, Windows-1252, ISO-8859-1, etc.)
        HOW: Try multiple encodings in order of likelihood, with detailed error reporting

        ENCODING FALLBACK CHAIN:
        1. utf-8-sig (UTF-8 with BOM handling) - most modern files
        2. utf-8 (standard UTF-8) - common for exports
        3. windows-1252 (CP1252) - Windows Excel exports, handles byte 0xa0 as non-breaking space
        4. iso-8859-1 (Latin-1) - older files, handles bytes 0x80-0xFF
        5. cp1252 (Windows code page) - alias for windows-1252
        6. latin-1 - another alias for ISO-8859-1
        
        DOCS: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

        Args:
            skip_rows: Rows to skip
            header: Row to use as column names (default: 0), or None to not use headers

        Returns:
            DataFrame with CSV data
        
        Raises:
            ValueError: If file cannot be read with any encoding
        """
        # List of encodings to try in order of likelihood
        # Docs: https://docs.python.org/3/library/codecs.html#standard-encodings
        encodings = [
            'utf-8-sig',      # UTF-8 with BOM (most common modern format)
            'utf-8',          # Standard UTF-8
            'windows-1252',   # Windows Excel (handles 0xa0 as non-breaking space)
            'iso-8859-1',     # Latin-1 (handles all single bytes)
            'cp1252',         # Windows code page (common for legacy files)
            'latin-1',        # Alias for ISO-8859-1
        ]
        
        last_error = None
        
        # Try each encoding in sequence
        for encoding in encodings:
            try:
                if self.stdout:
                    self.stdout.write(f'      [FILE READ] Attempting to read CSV with encoding: {encoding}\n')
                
                # Attempt to read the CSV file with current encoding
                df = pd.read_csv(
                    self.file_path,
                    skiprows=skip_rows,
                    header=header,
                    dtype=str,  # Read all as string initially for safer processing
                    na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                    encoding=encoding,
                    encoding_errors='strict'  # Fail fast if encoding doesn't match
                )
                
                if self.stdout:
                    self.stdout.write(f'      [SUCCESS] Successfully read CSV with encoding: {encoding}\n')
                
                return df
                
            except (UnicodeDecodeError, UnicodeError) as e:
                # Store error for potential final error message
                last_error = e
                if self.stdout:
                    self.stdout.write(
                        f'      [ENCODING FAIL] {encoding} failed at position {getattr(e, "start", "unknown")}: '
                        f'{str(e)[:100]}\n'
                    )
                continue  # Try next encoding
                
            except Exception as e:
                # Non-encoding errors should fail immediately
                if self.stdout:
                    self.stdout.write(f'      [ERROR] Non-encoding error: {type(e).__name__}: {str(e)}\n')
                raise
        
        # If we exhausted all encodings, raise a detailed error
        error_msg = (
            f'Failed to read CSV file with any supported encoding. '
            f'Tried: {", ".join(encodings)}. '
            f'Last error: {str(last_error)}'
        )
        if self.stdout:
            self.stdout.write(f'      [FATAL] {error_msg}\n')
        raise ValueError(error_msg)

    def _detect_header_row(self, df: pd.DataFrame) -> Tuple[int, int]:
        """
        WHAT: Intelligently detect which row contains the actual column headers
        WHY: Many seller files have title rows, logos, or metadata before the data table
        HOW: Uses heuristics to find the row with the most column-like values

        DETECTION LOGIC:
        1. Look for row with most non-empty values (likely headers)
        2. Check for common header keywords (ID, Name, Balance, Address, etc.)
        3. Verify next row has different data (not duplicate headers)
        4. Optional: Use AI if ANTHROPIC_API_KEY available

        Args:
            df: DataFrame read with header=0 (may be wrong)

        Returns:
            Tuple of (header_row_index, data_start_row_index)
            Returns (0, 1) if data already starts at row 0
        """
        # If DataFrame is too small, assume it's correct
        if len(df) < 2:
            return (0, 1)

        # TRY AI FIRST: Much smarter than heuristics
        ai_result = self._ai_detect_header_row(df)
        if ai_result:
            return ai_result

        # FALLBACK: Heuristic detection if AI unavailable
        # HEURISTIC 1: Find row with most non-empty, unique values that looks like headers
        max_score = 0
        best_row = 0

        # Check first 20 rows (data rarely starts after row 20)
        for idx in range(min(20, len(df))):
            row = df.iloc[idx]

            # Count non-empty values
            non_empty_count = row.notna().sum()

            # Skip rows with very few values (like single cell "SA20771-1025")
            if non_empty_count < 3:
                continue

            # Count unique values (headers should be unique)
            unique_count = len(row.dropna().unique())

            # Check if values look like headers (text, not mostly numbers)
            header_like_count = 0
            for val in row.dropna():
                val_str = str(val).strip()
                # Headers usually contain letters and are not pure numbers
                if val_str and not val_str.replace('.', '').replace(',', '').isdigit():
                    header_like_count += 1

            # Score: prioritize rows with many non-empty, unique, header-like values
            header_ratio = header_like_count / non_empty_count if non_empty_count > 0 else 0
            score = non_empty_count * 0.4 + unique_count * 0.3 + header_ratio * 0.3

            if score > max_score:
                max_score = score
                best_row = idx

        # HEURISTIC 2: Check if candidate row has header-like values
        candidate_row = df.iloc[best_row]
        header_score = self._score_header_row(candidate_row)

        # If current row 0 has high header score, it's probably correct
        if best_row == 0 and header_score > 0.5:
            return (0, 1)

        # If we found a better row, use it
        if best_row > 0 and header_score > 0.3:
            # Find actual data start (may be 1+ rows after header due to empty rows)
            data_start = best_row + 1
            while data_start < len(df) and data_start < best_row + 5:  # Check up to 4 rows after header
                next_row = df.iloc[data_start]
                # If row has substantial data (>30% non-empty), it's likely data start
                if next_row.notna().sum() > len(next_row) * 0.3:
                    break
                data_start += 1
            return (best_row, data_start)

        # HEURISTIC 3: Check if first row is all empty or has title text
        first_row = df.iloc[0]
        first_row_empty_count = first_row.isna().sum()

        # If first row is mostly empty (>50%), skip it
        if first_row_empty_count > len(first_row) * 0.5:
            # Look for next non-empty row
            for idx in range(1, min(20, len(df))):
                row = df.iloc[idx]
                if row.notna().sum() > len(row) * 0.5:
                    if self.stdout:
                        self.stdout.write(
                            f'      [AUTO-DETECT] First row mostly empty, using row {idx + 1}\n'
                        )
                    return (idx, idx + 1)

        # Default: assume current structure is correct
        return (0, 1)

    def _ai_detect_header_row(self, df: pd.DataFrame) -> Optional[Tuple[int, int]]:
        """
        WHAT: Use AI to intelligently detect header and data start rows
        WHY: AI can understand context much better than heuristics
        HOW: Send first 15 rows to Claude with clear instructions

        Args:
            df: DataFrame to analyze

        Returns:
            Tuple of (header_row_index, data_start_row_index) or None if AI unavailable
        """
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                return None

            # Get first 15 rows for analysis (enough context, not too much data)
            sample_rows = min(15, len(df))
            sample_df = df.head(sample_rows)

            # Convert to readable format for AI
            rows_text = ""
            for idx, row in sample_df.iterrows():
                # Show first 10 columns to avoid overwhelming AI
                row_values = []
                for col_idx, val in enumerate(row.head(10)):
                    if pd.isna(val) or val == '':
                        row_values.append('[EMPTY]')
                    else:
                        row_values.append(str(val)[:50])  # Truncate long values
                
                rows_text += f"Row {idx + 1}: {' | '.join(row_values)}\n"

            prompt = f"""Analyze this Excel/CSV data to find the header row and data start row.

DATA SAMPLE:
{rows_text}

INSTRUCTIONS:
1. Find the row that contains column headers (like "Loan Number", "Property Address", "Balance", etc.)
2. Find the row where actual data starts (usually right after headers, but may have empty rows between)
3. Ignore title rows, logos, single-cell values, or metadata at the top
4. Headers typically contain descriptive text, not numbers or IDs

EXAMPLES:
- Row with "Loan Number | Property Address | City" = HEADER ROW
- Row with "1025175274 | 165 WINDMILL RD | Huntsville" = DATA START ROW
- Row with just "SA20771-1025" = IGNORE (single value, not headers)

RESPONSE FORMAT:
Return exactly: "HEADER_ROW:X,DATA_START:Y" where X and Y are row numbers (1-indexed)
If headers are at row 1, return: "HEADER_ROW:1,DATA_START:2"
If no clear headers found, return: "NO_HEADERS"

Response:"""

            client = anthropic.Anthropic(api_key=api_key)

            message = client.messages.create(
                model="claude-3-5-haiku-20241022",  # Fast for data analysis
                max_tokens=50,  # Short response expected
                temperature=0,  # Deterministic output
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract response
            response_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text
                elif isinstance(block, dict) and 'text' in block:
                    response_text += block['text']

            response = response_text.strip()

            # Parse AI response
            if "NO_HEADERS" in response:
                return (0, 1)  # Default to first row
            
            if "HEADER_ROW:" in response and "DATA_START:" in response:
                try:
                    parts = response.split(',')
                    header_part = [p for p in parts if 'HEADER_ROW:' in p][0]
                    data_part = [p for p in parts if 'DATA_START:' in p][0]
                    
                    header_row = int(header_part.split(':')[1]) - 1  # Convert to 0-indexed
                    data_start = int(data_part.split(':')[1]) - 1    # Convert to 0-indexed
                    
                    # Validate results
                    if 0 <= header_row < len(df) and 0 <= data_start < len(df):
                        if self.stdout:
                            self.stdout.write(f'      [AI-DETECT] Headers at row {header_row + 1}, data starts at row {data_start + 1}\n')
                        return (header_row, data_start)
                except (ValueError, IndexError):
                    pass

        except Exception as e:
            if self.stdout:
                self.stdout.write(f'      [AI-DETECT] Failed: {e}\n')

        return None

    def _score_header_row(self, row: pd.Series) -> float:
        """
        WHAT: Score a row based on how likely it is to be a header row
        WHY: Headers have distinctive patterns (keywords, short text, no numbers)
        HOW: Check for common loan tape header keywords and patterns

        Args:
            row: Pandas Series (one row of data)

        Returns:
            Float score between 0 and 1 (higher = more likely to be header)
        """
        # Common loan tape header keywords
        HEADER_KEYWORDS = [
            'id', 'loan', 'number', 'name', 'balance', 'amount', 'date', 'address',
            'street', 'city', 'state', 'zip', 'property', 'borrower', 'rate',
            'maturity', 'type', 'status', 'upb', 'original', 'current', 'value',
            'bpo', 'appraisal', 'lien', 'note', 'interest', 'payment', 'delin',
            'dlq', 'foreclosure', 'bankruptcy', 'modification', 'servicer'
        ]

        score = 0.0
        total_values = 0

        for val in row:
            if pd.isna(val) or val == '':
                continue

            total_values += 1
            val_str = str(val).lower().strip()

            # Check for header keywords
            for keyword in HEADER_KEYWORDS:
                if keyword in val_str:
                    score += 1.0
                    break  # Only count once per column

            # Penalize if value looks like data (all numbers, long text, dates)
            # Headers are typically short descriptive text
            if val_str.replace('.', '').replace(',', '').replace('$', '').isdigit():
                score -= 0.5  # Looks like numeric data
            elif len(val_str) > 50:
                score -= 0.3  # Headers are usually short

        # Normalize score
        if total_values == 0:
            return 0.0

        return max(0.0, min(1.0, score / total_values))

    def use_ai_detection(self, df: pd.DataFrame) -> Tuple[int, int]:
        """
        WHAT: Use Claude AI to detect header row (future enhancement)
        WHY: AI can understand context better than heuristics
        HOW: Send first 20 rows to Claude, ask it to identify header row

        Args:
            df: DataFrame to analyze

        Returns:
            Tuple of (header_row_index, data_start_row_index)

        Note: Currently returns heuristic result. Implement AI logic as needed.
        """
        api_key = os.getenv('ANTHROPIC_API_KEY')

        if not api_key:
            # Fall back to heuristics
            return self._detect_header_row(df)

        # TODO: Implement AI-based detection
        # For now, use heuristics
        logger.info('AI detection not yet implemented, using heuristics')
        return self._detect_header_row(df)
