# Import models to make them available when importing from am_module.models
# DEPRECATED: SellerBoardedData - use SellerRawData from acq_module instead
# from .boarded_data import SellerBoardedData
from .model_am_servicersCleaned import ServicerLoanData, ServicerTrialBalanceData, ServicerTrackingPayoffData

# Import BlendedOutcomeModel, ReUWAMProjections, and UWCashFlows from model_am_modeling.py
from .model_am_modeling import BlendedOutcomeModel, ReUWAMProjections, UWCashFlows

# Import outcome models and tasks from model_am_amData.py (CRITICAL: Required for Django model registry)
from .model_am_tracksTasks import (
    REOData, REOtask,  # Note: REOtask has lowercase 't' in the model definition
    FCSale, FCTask,
    DIL, DILTask,
    ShortSale, ShortSaleTask,
    Modification, ModificationTask,
    NoteSale, NoteSaleTask,
    PerformingTrack, PerformingTask,
    DelinquentTrack, DelinquentTask,
)

from .model_am_amData import (
    AssetCRMContact,
    REOScope,
    Offers,
    AMNote,
    AMMetrics,
    AuditLog,
)

# Import custom list model (AM user-defined asset lists)
from .model_am_customLists import CustomAssetList

# Import DIL-specific models
from .model_am_dil import HeirContact

__all__ = [
    # Servicer data
    'ServicerLoanData',
    'ServicerTrialBalanceData',
    'ServicerTrackingPayoffData',
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
    'NoteSale', 'NoteSaleTask',
    'PerformingTrack', 'PerformingTask',
    'DelinquentTrack', 'DelinquentTask',
    'REOScope',
    'Offers',
    'AMNote',
    'AMMetrics',
    'AuditLog',
    'HeirContact',
    'CustomAssetList',
]