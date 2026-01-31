import factory
from factory import Faker
from factory.django import DjangoModelFactory

from core.models.model_co_assetIdHub import AssetIdHub, AssetDetails
from core.models.model_co_enrichment import LlDataEnrichment


class AssetIdHubFactory(DjangoModelFactory):
    class Meta:
        model = AssetIdHub

    sellertape_id = factory.Sequence(lambda n: f"TAPE-{n:06d}")
    servicer_id = factory.Sequence(lambda n: f"SRV-{n:06d}")


class AssetDetailsFactory(DjangoModelFactory):
    class Meta:
        model = AssetDetails

    asset = factory.SubFactory(AssetIdHubFactory)
    asset_status = AssetDetails.AssetStatus.ACTIVE
    asset_class = factory.Iterator([c[0] for c in AssetDetails.AssetClass.choices], cycle=True)


class LlDataEnrichmentFactory(DjangoModelFactory):
    class Meta:
        model = LlDataEnrichment

    asset_hub = factory.SubFactory(AssetIdHubFactory)
    geocode_lat = None
    geocode_lng = None
    geocode_used_address = Faker("street_address")
    geocode_full_address = Faker("address")
    geocode_display_address = Faker("street_address")
