"""Canonical food and drink definitions.

``food_drink_id`` hashes ``"name|form"``, so ``form`` is part of the identity in
exactly the way a location's ``region`` is: the same item entered once as
``form="Drink"`` and once as anything else is two rows, silently. Define each item
once, here. Story modules reference these as ``food.NAME``.
"""

from __future__ import annotations

from db import FoodDrinkEntry


ALDER_CIDER = FoodDrinkEntry("Alder Cider", form="Drink")
BLACKJACK_S_WHISKEY = FoodDrinkEntry("Blackjack's Whiskey", form="Drink")
GOLDKISS_RUM = FoodDrinkEntry("Goldkiss Rum", form="Drink")
SEPULCHRE_RUM = FoodDrinkEntry("Sepulchre Rum", form="Drink")
"""form must stay "Drink": food_drink_id hashes "name|form", and row FDb173b37b0c
already exists with that value. A different form here mints a second row."""
