# Import models to make them available when importing from am_module.models
# DEPRECATED: SellerBoardedData - use SellerRawData from acq_module instead
# from .boarded_data import SellerBoardedData
from .servicers import ServicerLoanData

# Import BlendedOutcomeModel, ReUWAMProjections, and UWCashFlows from model_am_modeling.py
from .model_am_modeling import BlendedOutcomeModel, ReUWAMProjections, UWCashFlows

# Import outcome models and tasks from model_am_amData.py (CRITICAL: Required for Django model registry)
from .model_am_amData import (
    AssetCRMContact,
    REOData, REOtask,  # Note: REOtask has lowercase 't' in the model definition
    FCSale, FCTask,
    DIL, DILTask,
    ShortSale, ShortSaleTask,
    Modification, ModificationTask,
    REOScope,
    Offers,
    AMNote,
    AMMetrics,
    AuditLog,
)

# Import DIL-specific models
from .model_am_dil import HeirContact

__all__ = [
    # Servicer data
    'ServicerLoanData',
    # Outcome models
    'BlendedOutcomeModel',
    'ReUWAMProjections',
    'UWCashFlows',
    'AssetCRMContact',
    'REOData', 'REOtask',
    'FCSale', 'FCTask',
    'DIL', 'DILTask',
    'ShortSale', 'ShortSaleTask',
    'Modification', 'ModificationTask',
    'REOScope',
    'Offers',
    'AMNote',
    'AMMetrics',
    'AuditLog',
    'HeirContact',
]