import random
import factory
from factory import Faker
from factory.django import DjangoModelFactory

from acq_module.models.model_acq_seller import (
    Seller,
    Trade,
    AcqAsset,
    AcqLoan,
    AcqProperty,
    AcqForeclosureTimeline,
    AcqBankruptcy,
    AcqModification,
)
from factories.factory_core import AssetIdHubFactory


class SellerFactory(DjangoModelFactory):
    class Meta:
        model = Seller

    name = Faker("company")
    broker = Faker("company")
    email = Faker("company_email")
    poc = Faker("name")


class TradeFactory(DjangoModelFactory):
    class Meta:
        model = Trade

    seller = factory.SubFactory(SellerFactory)
    trade_name = factory.Sequence(lambda n: f"Trade-{n:04d}")
    status = Trade.Status.INDICATIVE


class AcqAssetFactory(DjangoModelFactory):
    class Meta:
        model = AcqAsset

    asset_hub = factory.SubFactory(AssetIdHubFactory)
    seller = factory.SubFactory(SellerFactory)
    trade = factory.SubFactory(TradeFactory, seller=factory.SelfAttribute("..seller"))
    asset_status = factory.LazyFunction(lambda: random.choice([c[0] for c in AcqAsset.AssetStatus.choices]))
    acq_status = AcqAsset.AcquisitionStatus.KEEP
    asset_class = factory.LazyFunction(lambda: random.choice([c[0] for c in AcqAsset.AssetClass.choices]))


class AcqLoanFactory(DjangoModelFactory):
    class Meta:
        model = AcqLoan

    asset = factory.SubFactory(AcqAssetFactory)
    sellertape_id = factory.LazyAttribute(
        lambda obj: obj.asset.asset_hub.sellertape_id or f"TAPE-{obj.asset.pk}"
    )
    sellertape_altid = factory.LazyFunction(lambda: f"ALT-{random.randint(100000, 999999)}")
    current_balance = factory.LazyFunction(lambda: random.randint(50000, 500000))
    total_debt = factory.LazyFunction(lambda: random.randint(60000, 550000))
    interest_rate = factory.LazyFunction(lambda: round(random.uniform(0.03, 0.12), 4))
    next_due_date = Faker("date_between", start_date="-30d", end_date="+30d")
    origination_date = Faker("date_between", start_date="-10y", end_date="-1y")
    original_balance = factory.LazyAttribute(lambda obj: obj.current_balance or random.randint(50000, 500000))
    product_type = factory.LazyFunction(lambda: random.choice([c[0] for c in AcqLoan.ProductType.choices]))


class AcqPropertyFactory(DjangoModelFactory):
    class Meta:
        model = AcqProperty

    asset = factory.SubFactory(AcqAssetFactory)
    street_address = Faker("street_address")
    city = Faker("city")
    state = Faker("state_abbr")
    zip = Faker("postcode")
    occupancy = factory.LazyFunction(lambda: random.choice([c[0] for c in AcqProperty.Occupancy.choices]))
    year_built = factory.LazyFunction(lambda: random.randint(1950, 2022))
    sq_ft = factory.LazyFunction(lambda: random.randint(800, 4500))
    lot_size = factory.LazyFunction(lambda: random.randint(1000, 15000))
    beds = factory.LazyFunction(lambda: random.randint(1, 6))
    baths = factory.LazyFunction(lambda: random.randint(1, 4))


class AcqForeclosureTimelineFactory(DjangoModelFactory):
    class Meta:
        model = AcqForeclosureTimeline

    asset = factory.SubFactory(AcqAssetFactory)
    fc_flag = factory.LazyFunction(lambda: random.choice([True, False]))
    fc_first_legal_date = Faker("date_between", start_date="-2y", end_date="today")
    fc_referred_date = Faker("date_between", start_date="-2y", end_date="today")
    fc_judgement_date = Faker("date_between", start_date="-2y", end_date="today")
    fc_scheduled_sale_date = Faker("date_between", start_date="today", end_date="+1y")
    fc_sale_date = Faker("date_between", start_date="today", end_date="+2y")
    fc_starting = factory.LazyFunction(lambda: random.randint(10000, 50000))


class AcqBankruptcyFactory(DjangoModelFactory):
    class Meta:
        model = AcqBankruptcy

    loan = factory.SubFactory(AcqLoanFactory)
    bk_flag = factory.LazyFunction(lambda: random.choice([True, False]))
    bk_chapter = factory.LazyFunction(lambda: random.choice(["7", "11", "13"]))


class AcqModificationFactory(DjangoModelFactory):
    class Meta:
        model = AcqModification

    loan = factory.SubFactory(AcqLoanFactory)
    mod_flag = factory.LazyFunction(lambda: random.choice([True, False]))
    mod_date = Faker("date_between", start_date="-2y", end_date="today")
    mod_maturity_date = Faker("date_between", start_date="today", end_date="+10y")
    mod_term = factory.LazyFunction(lambda: random.randint(60, 360))
    mod_rate = factory.LazyFunction(lambda: round(random.uniform(0.02, 0.09), 4))
    mod_initial_balance = factory.LazyFunction(lambda: random.randint(50000, 500000))
