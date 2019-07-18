import pytest
from sas_select import pack_entitlement


@pytest.mark.parametrize(
    ("pack_size", "maximum_qty", "message"),
    (
            (5, "10m", "Your medicare entitlement is 2 packs per month"),
            (6, "20m", "Your medicare entitlement is 3 packs per month"),
            (10, "5m", "Your medicare entitlement is 1 pack per 2 months"),
            (1, "12a", "Your medicare entitlement is 12 packs per year"),
            (5, "1a", "Your medicare entitlement is 1 pack per 5 years"),
    )
)
def test_pack_entitlement(pack_size, maximum_qty, message):
    """Test different values for pack_entitlement"""

    s = pack_entitlement(pack_size, maximum_qty)
    assert message in s
