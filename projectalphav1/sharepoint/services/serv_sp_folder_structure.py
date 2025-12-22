"""
SharePoint Folder Structure Service
====================================
Defines and manages SharePoint folder hierarchy.
Creates folder structure that mirrors Django entity organization.

File Naming Convention: serv_sp_folder_structure.py
Module: SharePoint (sp)
Purpose: Manage folder creation and path generation
"""

from typing import Dict, List


class FolderStructure:
    """
    Defines SharePoint folder structure.
    All folders created eagerly when trade/asset created in platform.
    """
    
    # Root structure
    ROOT_TRADES = "Trades"
    
    # Trade-level folders
    TRADE_FOLDERS = [
        "Trade Level",
        "Asset Level",  # Container for all assets
    ]
    
    # Trade Level subfolders
    TRADE_LEVEL_FOLDERS = [
        "Seller Data Dump",
        "Due Diligence",
        "Bid",
        "Award",
        "Settlement",
        "Entity",
        "Legal",
        "Servicing",
        "Asset Management",
    ]
    
    # Nested Trade Level subfolders (e.g., within Settlement)
    TRADE_LEVEL_SUBFOLDERS = {
        "Settlement": [
            "Award Package",
            "Bid Confirmation Letter",
            "Consent to Assignment & Assignment and Assumption",
            "Goodbye Letters",
            "POA",
            "Settlement Statement and MLS",
            "Transfer Instructions",
        ],
    }
    
    # Asset-level folders (within each asset)
    ASSET_FOLDERS = [
        "Valuation",
        "Loan File",
        "Title",
        "Legal",
        "Financials",
        "Tax & Insurance",
        "Servicing",
        "Asset Management",
        "Liquidations",
    ]
    
    # Tags for Valuation files only (replaces BPO/Appraisal/Inspection subfolders)
    VALUATION_TAGS = ["BPO", "Appraisal", "Inspection Report"]
    
    # No subfolders - flat structure with tags for Valuation
    ASSET_SUBFOLDERS = {
        "Loan File": [
            "Loan Origination",
            "Collateral",
            "Borrower",
            "Appraisal",
            "Title",
            "AOM",
        ]
    }
    
    @staticmethod
    def get_trade_base_path(trade_id: str) -> str:
        """
        Get base path for a trade.
        
        Args:
            trade_id: Trade identifier (e.g., TRD-2024-001)
            
        Returns:
            Base path like: /Trades/TRD-2024-001
        """
        return f"/{FolderStructure.ROOT_TRADES}/{trade_id}"
    
    @staticmethod
    def get_trade_folders(trade_id: str) -> List[str]:
        """
        Get all folder paths for a trade (trade-level folders only).
        
        Args:
            trade_id: Trade identifier
            
        Returns:
            List of folder paths to create
        """
        base_path = FolderStructure.get_trade_base_path(trade_id)
        folders = [f"{base_path}/{folder}" for folder in FolderStructure.TRADE_FOLDERS]

        trade_level_base = f"{base_path}/Trade Level"
        # First-level Trade Level folders (Seller Data Dump, Due Diligence, Bid, Award, Settlement, etc.)
        folders.extend([f"{trade_level_base}/{folder}" for folder in FolderStructure.TRADE_LEVEL_FOLDERS])

        # Nested Trade Level subfolders (e.g., Settlement children)
        for parent_name, children in FolderStructure.TRADE_LEVEL_SUBFOLDERS.items():
            parent_path = f"{trade_level_base}/{parent_name}"
            for child_name in children:
                folders.append(f"{parent_path}/{child_name}")

        return folders
    
    @staticmethod
    def get_asset_base_path(trade_id: str, asset_id: str) -> str:
        """
        Get base path for an asset within a trade.
        
        Args:
            trade_id: Trade identifier
            asset_id: Asset identifier
            
        Returns:
            Base path like: /Trades/TRD-2024-001/Asset Level/ASSET-12345
        """
        return f"/{FolderStructure.ROOT_TRADES}/{trade_id}/Asset Level/{asset_id}"
    
    @staticmethod
    def get_asset_folders(trade_id: str, asset_id: str) -> List[str]:
        """
        Get all folder paths for an asset, including subfolders.
        
        Args:
            trade_id: Trade identifier
            asset_id: Asset identifier
            
        Returns:
            List of folder paths to create (includes main folders + subfolders)
        """
        base_path = FolderStructure.get_asset_base_path(trade_id, asset_id)
        folders = []
        
        # Add main category folders
        for folder in FolderStructure.ASSET_FOLDERS:
            folders.append(f"{base_path}/{folder}")
            
            # Add subfolders if defined for this category
            if folder in FolderStructure.ASSET_SUBFOLDERS:
                for subfolder in FolderStructure.ASSET_SUBFOLDERS[folder]:
                    folders.append(f"{base_path}/{folder}/{subfolder}")
        
        return folders
    
    @staticmethod
    def get_document_path(trade_id: str, asset_id: str, category: str, file_name: str) -> str:
        """
        Get full path for a document.
        Enforces rule: files MUST be in category folders, never at root.
        
        Args:
            trade_id: Trade identifier
            asset_id: Asset identifier (None for trade-level docs)
            category: Document category (maps to folder name)
            file_name: Name of the file
            
        Returns:
            Full document path
            
        Raises:
            ValueError: If trying to place file at root level
        """
        if not category:
            raise ValueError("Category is required - files cannot be at root level")
        
        # Map category to folder name
        category_folder_map = {
            'trade_seller_data_dump': 'Seller Data Dump',
            'trade_due_diligence': 'Due Diligence',
            'trade_bid': 'Bid',
            'trade_settlement': 'Settlement',
            'trade_entity': 'Entity',
            'trade_legal': 'Legal',
            'trade_servicing': 'Servicing',
            'trade_asset_management': 'Asset Management',
            'asset_valuation': 'Valuation',
            'asset_loan_file': 'Loan File',
            'asset_legal': 'Legal',
            'asset_title': 'Title',
            'asset_financials': 'Financials',
            'asset_tax_insurance': 'Tax & Insurance',
            'asset_servicing': 'Servicing',
            'asset_asset_management': 'Asset Management',
            'asset_liquidations': 'Liquidations',
        }
        
        folder_name = category_folder_map.get(category)
        if not folder_name:
            raise ValueError(f"Invalid category: {category}")
        
        # Build path based on whether it's trade-level or asset-level
        if asset_id:
            # Asset-level document
            return f"/{FolderStructure.ROOT_TRADES}/{trade_id}/Asset Level/{asset_id}/{folder_name}/{file_name}"

        # Trade-level document
        return f"/{FolderStructure.ROOT_TRADES}/{trade_id}/Trade Level/{folder_name}/{file_name}"
    
    @staticmethod
    def validate_file_path(file_path: str) -> tuple[bool, str]:
        """
        Validate that file is in a category folder, not at root.
        
        Args:
            file_path: Path to validate
            
        Returns:
            (is_valid, error_message)
        """
        parts = [p for p in file_path.split('/') if p]
        
        # Minimum depth: Trades/TRADE_ID/CATEGORY/file.pdf (4 parts)
        # Asset depth: Trades/TRADE_ID/Assets/ASSET_ID/CATEGORY/file.pdf (6 parts)
        
        if len(parts) < 4:
            return False, "File must be in a category folder (minimum depth not met)"
        
        # Check that file is not directly in Trades or Asset Level folder
        if parts[0] == FolderStructure.ROOT_TRADES:
            # Should have at least: Trades/ID/Category/file
            if len(parts) == 3:  # Trades/ID/file - WRONG
                return False, f"File cannot be directly in trade folder: /{'/'.join(parts[:2])}"
            
            if 'Asset Level' in parts:
                asset_level_idx = parts.index('Asset Level')
                # Should have at least: Trades/ID/Asset Level/ASSET_ID/Category/file
                if len(parts) - asset_level_idx < 3:  # Asset Level/ASSET_ID/file - WRONG
                    return False, f"File cannot be directly in asset folder"
        
        return True, ""
    
    @staticmethod
    def get_all_category_folders() -> Dict[str, List[str]]:
        """
        Get mapping of categories to valid folder names.
        Useful for validation and UI dropdowns.
        
        Returns:
            Dict with 'trade_level' and 'asset_level' keys
        """
        return {
            'trade_level': FolderStructure.TRADE_LEVEL_FOLDERS,
            'asset_level': FolderStructure.ASSET_FOLDERS,
        }

