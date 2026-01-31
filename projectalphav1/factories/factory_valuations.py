import random
import factory
from factory import Faker
from factory.django import DjangoModelFactory

from core.models.model_co_valuations import Valuation, ValuationGradeReference
from factories.factory_core import AssetIdHubFactory


class ValuationGradeReferenceFactory(DjangoModelFactory):
    class Meta:
        model = ValuationGradeReference

    code = factory.Iterator(["A+", "A", "B", "C", "D", "F"], cycle=True)
    label = factory.LazyAttribute(lambda obj: f"Grade {obj.code}")
    description = factory.LazyAttribute(lambda obj: f"{obj.code} grade property")
    sort_order = factory.Sequence(lambda n: n)


class ValuationFactory(DjangoModelFactory):
    class Meta:
        model = Valuation

    asset_hub = factory.SubFactory(AssetIdHubFactory)
    source = Valuation.Source.SELLER_PROVIDED
    asis_value = factory.LazyFunction(lambda: random.randint(60000, 550000))
    arv_value = factory.LazyFunction(lambda: random.randint(70000, 650000))
    value_date = Faker("date_between", start_date="-2y", end_date="today")
