"""Canonical food and drink definitions.

``food_drink_id`` hashes ``"name|kind"``, so ``kind`` is part of the identity in
exactly the way a location's ``region`` is: the same item entered once as
``kind="Drink"`` and once as anything else is two rows, silently. Define each item
once, here. Story modules reference these as ``food.NAME``.
"""

from __future__ import annotations

from db import FoodDrinkEntry


ALDER_CIDER = FoodDrinkEntry("Alder Cider", kind="Drink")
BLACKJACK_S_WHISKEY = FoodDrinkEntry("Blackjack's Whiskey", kind="Drink")
