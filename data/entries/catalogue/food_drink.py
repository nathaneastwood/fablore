"""Canonical food and drink definitions.

``food_drink_id`` hashes ``"name|form"``, so ``form`` is part of the identity in
exactly the way a location's ``region`` is: the same item entered once as
``form="Drink"`` and once as anything else is two rows, silently. Define each item
once, here. Story modules reference these as ``food.NAME``.
"""

from __future__ import annotations

from db import FoodDrinkEntry


ALDER_CIDER = FoodDrinkEntry("Alder Cider", form="Drink")
AMYGDAZZLA = FoodDrinkEntry("Amygdazzla", form="Drink")
BREAKERNUT_ALE = FoodDrinkEntry("Breakernut Ale", form="Drink")
BLACKJACK_S_WHISKEY = FoodDrinkEntry("Blackjack's Whiskey", form="Drink")
FESTIVE_FLARE = FoodDrinkEntry("Festive Flare", form="Drink")
GOLDKISS_RUM = FoodDrinkEntry("Goldkiss Rum", form="Drink")
ISENRI_SAKE = FoodDrinkEntry("Isenri Sake", form="Drink")
NUTRISLUG = FoodDrinkEntry("Nutrislug", form="Food")
OIL_COIL = FoodDrinkEntry("Oil-Coil", form="Drink")
SEPULCHRE_RUM = FoodDrinkEntry("Sepulchre Rum", form="Drink")
SEWER_CHICKEN = FoodDrinkEntry("Sewer Chicken", form="Food")
TINKER_TEA = FoodDrinkEntry("Tinker Tea", form="Drink")
