"""Test authentication cache behavior."""

import hashlib
from typing import Any

import pytest
from homeassistant.const import ATTR_NAME

from tests.helpers import setup_alarmo_entry, patch_alarmo_integration_dependencies
from tests.factories import AreaFactory, UserFactory, SensorFactory
from custom_components.alarmo import const


@pytest.mark.asyncio
async def test_auth_cache_populated_and_cleared(
    hass: Any, enable_custom_integrations: Any
) -> None:
    """Verify auth cache is populated and cleared on user update."""
    users = {
        "user_1": UserFactory.create_user(
            user_id="user_1",
            name="User 1",
            code="1234",
            can_arm=True,
            can_disarm=True,
        )
    }
    areas = [AreaFactory.create_area(area_id="area_1", name="Test Area 1")]
    sensors = [
        SensorFactory.create_door_sensor(
            entity_id="binary_sensor.test_door",
            name="Test Door",
            area="area_1",
        )
    ]
    storage, entry = setup_alarmo_entry(
        hass,
        areas=areas,
        sensors=sensors,
        entry_id="test_auth_cache",
        users=users,
    )

    with patch_alarmo_integration_dependencies(storage):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        coordinator = hass.data[const.DOMAIN]["coordinator"]
        await coordinator.async_authenticate_user("1234")

        cache_key = (hashlib.sha256(b"1234").hexdigest(), None)
        assert cache_key in coordinator._auth_cache

        await coordinator.async_update_user_config(
            "user_1", {ATTR_NAME: "User 1 Updated"}
        )
        assert coordinator._auth_cache == {}
