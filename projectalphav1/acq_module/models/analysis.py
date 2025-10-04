from __future__ import annotations

class FCSaleAnalysis(models.Model):
    asset_hub = models.ForeignKey('core.AssetIdHub', on_delete=models.CASCADE)
    