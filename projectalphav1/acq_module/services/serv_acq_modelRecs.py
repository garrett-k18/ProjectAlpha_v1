"""
Model Recommendation Service

WHAT: Service to auto-populate acquisition models and probabilities based on asset characteristics
WHY: Provide intelligent defaults based on loan metrics to streamline acquisition analysis
WHERE: Called by acquisition analysis endpoints
HOW: Analyzes asset metrics (LTV, status, delinquency) to recommend disposition models

Business Rules:
- NPL loans with high LTV → Higher FC/REO probability
- Performing/RPL loans → Modification or note sale preferred  
- High equity loans → Short sale more viable
- FC flag active → Higher FC probability
- Delinquency level affects model mix
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ..models.model_acq_seller import SellerRawData
from ..logic.ll_metrics import get_single_asset_metrics


@dataclass
class ModelRecommendation:
    """Data class for a single model recommendation"""
    model_key: str
    model_name: str
    probability: int  # Percentage 0-100
    reasons: List[str]
    is_recommended: bool
    display_order: int


class ModelRecommendationService:
    """
    Service class for generating model recommendations based on asset characteristics.
    
    Usage:
        service = ModelRecommendationService(seller_raw_data)
        recommendations = service.get_recommendations()
    """
    
    # Model definitions with display metadata
    MODEL_DEFINITIONS = {
        'fc_sale': {'name': 'FC Sale', 'order': 1},
        'reo_sale': {'name': 'REO Sale', 'order': 2},
        'short_sale': {'name': 'Short Sale', 'order': 3},
        'modification': {'name': 'Modification', 'order': 4},
        'note_sale': {'name': 'Note Sale', 'order': 5},
    }
    
    def __init__(self, asset: SellerRawData):
        """
        Initialize service with an asset.
        
        Args:
            asset: SellerRawData instance to analyze
        """
        self.asset = asset
        self._recommendations: Optional[List[ModelRecommendation]] = None
    
    def get_recommendations(self) -> List[ModelRecommendation]:
        """
        Get model recommendations for the asset.
        
        Returns:
            List of ModelRecommendation objects sorted by display order
        """
        if self._recommendations is None:
            self._recommendations = self._calculate_recommendations()
        return self._recommendations
    
    def get_recommendations_dict(self) -> Dict:
        """
        Get recommendations as a dictionary suitable for API serialization.
        
        Returns:
            Dict with models list and metadata
        """
        recommendations = self.get_recommendations()
        return {
            'asset_id': self.asset.asset_hub_id,
            'asset_status': self.asset.asset_status,
            'models': [
                {
                    'model_key': rec.model_key,
                    'model_name': rec.model_name,
                    'probability': rec.probability,
                    'reasons': rec.reasons,
                    'is_recommended': rec.is_recommended,
                    'display_order': rec.display_order,
                }
                for rec in recommendations
            ],
            'metrics': self._get_asset_metrics(),
        }
    
    def _get_asset_metrics(self) -> Dict:
        """
        Calculate key metrics for the asset using backend ll_metrics functions.
        
        Returns:
            Dict of calculated metrics
        """
        # Use existing backend calculation functions for consistency
        # This ensures we don't duplicate logic and calculations match across the system
        return get_single_asset_metrics(self.asset.asset_hub_id)
    
    
    def _calculate_recommendations(self) -> List[ModelRecommendation]:
        """
        Main calculation logic for model recommendations.
        
        Returns:
            List of ModelRecommendation objects
        """
        # Initialize all models with zero probability
        recommendations = {
            key: ModelRecommendation(
                model_key=key,
                model_name=meta['name'],
                probability=0,
                reasons=[],
                is_recommended=False,
                display_order=meta['order'],
            )
            for key, meta in self.MODEL_DEFINITIONS.items()
        }
        
        # Get asset metrics using backend calculations
        metrics = self._get_asset_metrics()
        ltv = metrics.get('ltv')
        months_dlq = metrics.get('months_dlq', 0)
        fc_flag = metrics.get('is_foreclosure', False)
        asset_status = self.asset.asset_status
        
        # ====================================================================
        # BUSINESS LOGIC: Asset Status Based Recommendations
        # ====================================================================
        
        if asset_status == 'NPL':
            self._apply_npl_logic(recommendations, ltv, months_dlq, fc_flag)
        
        elif asset_status == 'REO':
            self._apply_reo_logic(recommendations)
        
        elif asset_status in ('PERF', 'RPL'):
            self._apply_performing_logic(recommendations, ltv, asset_status)
        
        else:
            # Unknown status - provide conservative default
            self._apply_default_logic(recommendations)
        
        # Normalize probabilities to sum to 100
        self._normalize_probabilities(recommendations)
        
        # Return sorted by display order
        return sorted(recommendations.values(), key=lambda x: x.display_order)
    
    def _apply_npl_logic(
        self, 
        recs: Dict[str, ModelRecommendation], 
        ltv: Optional[Decimal],
        months_dlq: int,
        fc_flag: bool
    ):
        """Apply recommendation logic for Non-Performing Loans"""
        fc = recs['fc_sale']
        reo = recs['reo_sale']
        short = recs['short_sale']
        mod = recs['modification']
        note = recs['note_sale']
        
        # Mark FC and REO as recommended for NPL
        fc.is_recommended = True
        reo.is_recommended = True
        
        # High LTV (>95%) = Higher FC/REO probability
        if ltv and ltv > 95:
            fc.probability = 50
            fc.reasons.append(f'High LTV ({ltv:.1f}%) suggests limited short sale viability')
            reo.probability = 30
            reo.reasons.append('High LTV increases likelihood of REO outcome')
            short.probability = 10
            mod.probability = 10
        
        # Medium LTV (70-95%) = Balanced approach
        elif ltv and 70 <= ltv <= 95:
            fc.probability = 40
            fc.reasons.append(f'Medium LTV ({ltv:.1f}%) allows for multiple resolution paths')
            reo.probability = 25
            short.probability = 20
            short.reasons.append('Moderate LTV makes short sale viable')
            short.is_recommended = True
            mod.probability = 15
        
        # Low LTV (<70%) = More options available
        elif ltv and ltv < 70:
            fc.probability = 25
            reo.probability = 20
            short.probability = 35
            short.reasons.append(f'Low LTV ({ltv:.1f}%) makes short sale highly viable')
            short.is_recommended = True
            mod.probability = 20
            mod.reasons.append('Good equity position supports modification')
            mod.is_recommended = True
        
        # No LTV data = Conservative default
        else:
            fc.probability = 40
            fc.reasons.append('Default NPL distribution (no LTV data available)')
            reo.probability = 30
            short.probability = 15
            mod.probability = 15
        
        # Adjust for foreclosure flag
        if fc_flag:
            fc.probability += 10
            fc.reasons.append('Foreclosure already initiated')
            reo.probability += 5
            short.probability = max(0, short.probability - 10)
            mod.probability = max(0, mod.probability - 5)
        
        # Adjust for high delinquency (12+ months)
        if months_dlq >= 12:
            fc.probability += 5
            fc.reasons.append(f'Severely delinquent ({months_dlq} months)')
            mod.probability = max(0, mod.probability - 5)
        
        # Note sale consideration for early stage NPL
        if months_dlq < 6:
            note.probability = 10
            note.reasons.append(f'Early stage delinquency ({months_dlq} months) suitable for note sale')
            note.is_recommended = True
    
    def _apply_reo_logic(self, recs: Dict[str, ModelRecommendation]):
        """Apply recommendation logic for REO assets"""
        reo = recs['reo_sale']
        note = recs['note_sale']
        
        reo.is_recommended = True
        reo.probability = 90
        reo.reasons.append('Asset already in REO status')
        
        note.probability = 10
        note.reasons.append('Potential bulk REO sale consideration')
    
    def _apply_performing_logic(
        self,
        recs: Dict[str, ModelRecommendation],
        ltv: Optional[Decimal],
        asset_status: str
    ):
        """Apply recommendation logic for Performing/Re-Performing loans"""
        fc = recs['fc_sale']
        reo = recs['reo_sale']
        mod = recs['modification']
        note = recs['note_sale']
        
        # Mark modification and note sale as recommended
        mod.is_recommended = True
        note.is_recommended = True
        
        # Check LTV for modification viability
        if ltv and ltv <= 95:
            mod.probability = 50
            mod.reasons.append(f'{asset_status} status with acceptable LTV ({ltv:.1f}%)')
            note.probability = 40
            note.reasons.append('Performing loans attractive for note buyers')
            fc.probability = 5
            reo.probability = 5
        
        elif ltv and ltv > 95:
            mod.probability = 40
            mod.reasons.append(f'High LTV ({ltv:.1f}%) may require principal reduction')
            note.probability = 35
            fc.probability = 15
            fc.reasons.append('High LTV reduces modification viability')
            reo.probability = 10
        
        else:
            # No LTV data
            mod.probability = 45
            mod.reasons.append(f'{asset_status} status suggests modification potential')
            note.probability = 45
            note.reasons.append('Performing loans suitable for note sale')
            fc.probability = 5
            reo.probability = 5
        
        # Re-performing gets slightly higher modification probability
        if asset_status == 'RPL':
            mod.probability += 5
            mod.reasons.append('Re-performing status shows borrower cooperation')
            note.probability = max(0, note.probability - 5)
    
    def _apply_default_logic(self, recs: Dict[str, ModelRecommendation]):
        """Apply conservative default logic when asset status is unknown"""
        fc = recs['fc_sale']
        reo = recs['reo_sale']
        short = recs['short_sale']
        mod = recs['modification']
        
        # Equal distribution across likely outcomes
        fc.probability = 30
        fc.reasons.append('Default distribution (asset status unknown)')
        reo.probability = 25
        short.probability = 20
        mod.probability = 25
        
        fc.is_recommended = True
        reo.is_recommended = True
    
    def _normalize_probabilities(self, recs: Dict[str, ModelRecommendation]):
        """Normalize all probabilities to sum to 100%"""
        total = sum(rec.probability for rec in recs.values())
        
        if total == 0:
            # If all zero, give equal distribution to recommended models
            recommended = [rec for rec in recs.values() if rec.is_recommended]
            if recommended:
                equal_prob = 100 // len(recommended)
                for rec in recommended:
                    rec.probability = equal_prob
                # Handle remainder
                recommended[0].probability += 100 - (equal_prob * len(recommended))
            return
        
        # Normalize to 100
        for rec in recs.values():
            rec.probability = round((rec.probability / total) * 100)
        
        # Handle rounding errors - adjust largest probability
        total_after = sum(rec.probability for rec in recs.values())
        if total_after != 100:
            max_rec = max(recs.values(), key=lambda x: x.probability)
            max_rec.probability += (100 - total_after)


def get_model_recommendations(asset_hub_id: int) -> Dict:
    """
    Convenience function to get model recommendations for an asset.
    
    Args:
        asset_hub_id: The asset hub ID
        
    Returns:
        Dict with recommendations and metadata
        
    Raises:
        SellerRawData.DoesNotExist: If asset not found
    """
    asset = SellerRawData.objects.select_related('asset_hub').get(asset_hub_id=asset_hub_id)
    service = ModelRecommendationService(asset)
    return service.get_recommendations_dict()


