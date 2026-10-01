import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import kh1_synthesis as synth
from kh1_reference import EQUIPMENT


class SynthesisTests(unittest.TestCase):
    def test_recipe_names_exist_in_reference(self):
        names = {item["name"] for item in EQUIPMENT}
        for name, number, materials in synth.RECIPES:
            self.assertIn(name, names)
            self.assertIn(number, synth.LIST_NAMES)
            for material, quantity in materials:
                self.assertIn(material, names)
                self.assertGreater(quantity, 0)

    def test_list_sizes_and_ultima(self):
        counts = {}
        for _name, number, _m in synth.RECIPES:
            counts[number] = counts.get(number, 0) + 1
        self.assertEqual(counts, {1: 6, 2: 6, 3: 6, 4: 6, 5: 6, 6: 3})
        self.assertEqual(
            sum(1 for n, number, _m in synth.RECIPES if number <= 5), 30
        )

    def test_progress_unlocks(self):
        lists = [name for name, number, _m in synth.RECIPES if number <= 5]
        self.assertEqual(synth.progress(set())["highest_list"], 1)
        self.assertEqual(synth.progress(set(lists[:3]))["highest_list"], 2)
        info = synth.progress(set(lists[:29]))
        self.assertFalse(info["ultima_unlocked"])
        self.assertTrue(synth.progress(set(lists))["ultima_unlocked"])

    def test_recipe_status_and_totals(self):
        materials = (("Lucid Shard", 1), ("Bright Shard", 1))
        status = synth.recipe_status(materials, {"Lucid Shard": 1})
        self.assertFalse(status["ready"])
        self.assertEqual(status["rows"][1]["short"], 1)
        everything = {name for name, _n, _m in synth.RECIPES}
        self.assertEqual(synth.remaining_materials(everything, {}), [])

    def test_checklist_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sub" / "check.json"
            synth.save_checklist("a#slot1", {"Cottage", "Bogus"}, path)
            synth.save_checklist("a#slot2", {"Ribbon"}, path)
            self.assertEqual(synth.load_checklist("a#slot1", path), {"Cottage"})
            self.assertEqual(synth.load_checklist("a#slot2", path), {"Ribbon"})
            self.assertEqual(synth.load_checklist("missing", path), set())


if __name__ == "__main__":
    unittest.main()
