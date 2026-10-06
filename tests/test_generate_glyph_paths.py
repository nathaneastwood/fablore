"""The committed SVG-export outlines must match the font files they came from."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("generate_glyph_paths", ROOT / "scripts" / "generate_glyph_paths.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


def test_committed_outlines_are_current():
    for key, font_file in gen.SCRIPTS.items():
        committed = json.loads((gen.OUT / f"{key}.json").read_text())
        assert committed == json.loads(
            json.dumps(gen.build(font_file))
        ), f"{key}.json is stale; run scripts/generate_glyph_paths.py"


def test_every_face_outlines_every_letter():
    for key in gen.SCRIPTS:
        face = json.loads((gen.OUT / f"{key}.json").read_text())
        assert set(face["adv"]) == set(gen.CHARS)
        assert set(face["d"]) == set(gen.CHARS) - {" "}
