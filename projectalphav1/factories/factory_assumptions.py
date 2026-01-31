import factory
from factory.django import DjangoModelFactory

from acq_module.models.model_acq_assumptions import LoanLevelAssumption, TradeLevelAssumption
from acq_module.models.model_acq_seller import Trade
from factories.factory_core import AssetIdHubFactory
from core.models.model_co_assumptions import Servicer


class TradeLevelAssumptionFactory(DjangoModelFactory):
    class Meta:
        model = TradeLevelAssumption

    trade = factory.SubFactory("projectalphav1.factories.factory_acq.TradeFactory")
    servicer = factory.LazyFunction(lambda: Servicer.objects.filter(is_default_for_trade_assumptions=True).first())


class LoanLevelAssumptionFactory(DjangoModelFactory):
    class Meta:
        model = LoanLevelAssumption

    asset_hub = factory.SubFactory(AssetIdHubFactory)
