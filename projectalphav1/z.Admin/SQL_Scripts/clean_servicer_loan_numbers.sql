-- ============================================================================
-- Clean loan_number fields in Servicer models by removing leading zeros
-- ============================================================================
-- WHAT: Removes leading zeros from loan_number fields in all ServicerXxxData tables
-- WHY: Ensures consistency with AssetIdHub.servicer_id format
-- HOW: Uses LTRIM to strip leading zeros, preserving at least one digit
-- ============================================================================

-- Preview changes before applying
-- Uncomment to see what will be updated:

-- SELECT 
--     'ServicerCommentData' as table_name,
--     id,
--     loan_number as old_value,
--     CASE 
--         WHEN LTRIM(loan_number, '0') = '' THEN '0'
--         ELSE LTRIM(loan_number, '0')
--     END as new_value
-- FROM am_module_servicercommentdata
-- WHERE loan_number ~ '^0[0-9]+'
-- LIMIT 10;

-- ============================================================================
-- UPDATE STATEMENTS
-- ============================================================================

BEGIN;

-- 1. ServicerCommentData
UPDATE am_module_servicercommentdata
SET loan_number = CASE 
    WHEN LTRIM(loan_number, '0') = '' THEN '0'
    ELSE LTRIM(loan_number, '0')
END
WHERE loan_number ~ '^0[0-9]+';

-- 2. ServicerPayHistoryData
UPDATE am_module_servicerpayhistorydata
SET loan_number = CASE 
    WHEN LTRIM(loan_number, '0') = '' THEN '0'
    ELSE LTRIM(loan_number, '0')
END
WHERE loan_number ~ '^0[0-9]+';

-- 3. ServicerTransactionData
UPDATE am_module_servicertransactiondata
SET loan_number = CASE 
    WHEN LTRIM(loan_number, '0') = '' THEN '0'
    ELSE LTRIM(loan_number, '0')
END
WHERE loan_number ~ '^0[0-9]+';

-- 4. ServicerArmData (uses loan_number field)
UPDATE am_module_servicerarmdata
SET loan_number = CASE 
    WHEN LTRIM(loan_number, '0') = '' THEN '0'
    ELSE LTRIM(loan_number, '0')
END
WHERE loan_number ~ '^0[0-9]+';

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these after the update to verify no leading zeros remain:

-- Check ServicerCommentData
SELECT COUNT(*) as remaining_with_leading_zeros
FROM am_module_servicercommentdata
WHERE loan_number ~ '^0[0-9]+';

-- Check ServicerPayHistoryData
SELECT COUNT(*) as remaining_with_leading_zeros
FROM am_module_servicerpayhistorydata
WHERE loan_number ~ '^0[0-9]+';

-- Check ServicerTransactionData
SELECT COUNT(*) as remaining_with_leading_zeros
FROM am_module_servicertransactiondata
WHERE loan_number ~ '^0[0-9]+';

-- Check ServicerArmData
SELECT COUNT(*) as remaining_with_leading_zeros
FROM am_module_servicerarmdata
WHERE loan_number ~ '^0[0-9]+';

-- ============================================================================
-- SUMMARY STATISTICS
-- ============================================================================
-- Get counts of updated records per table:

SELECT 
    'ServicerCommentData' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN loan_number ~ '^0[0-9]+' THEN 1 END) as records_with_leading_zeros
FROM am_module_servicercommentdata
UNION ALL
SELECT 
    'ServicerPayHistoryData',
    COUNT(*),
    COUNT(CASE WHEN loan_number ~ '^0[0-9]+' THEN 1 END)
FROM am_module_servicerpayhistorydata
UNION ALL
SELECT 
    'ServicerTransactionData',
    COUNT(*),
    COUNT(CASE WHEN loan_number ~ '^0[0-9]+' THEN 1 END)
FROM am_module_servicertransactiondata
UNION ALL
SELECT 
    'ServicerArmData',
    COUNT(*),
    COUNT(CASE WHEN loan_number ~ '^0[0-9]+' THEN 1 END)
FROM am_module_servicerarmdata;
