"""No paid request may start unless its maximum charge fits the local task budget."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/design_budget.py'

class BudgetTests(unittest.TestCase):
    def module(self):
        self.assertTrue(SCRIPT.exists(), 'Missing fail-closed request budget')
        spec = importlib.util.spec_from_file_location('design_budget', SCRIPT)
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_reservation_blocks_a_request_that_could_cross_cap(self):
        mod = self.module()
        with self.assertRaises(ValueError): mod.reserve({'charged': 19.8, 'pending': 0}, .3, 20)

    def test_pending_calls_count_against_budget(self):
        mod = self.module()
        with self.assertRaises(ValueError): mod.reserve({'charged': 19, 'pending': .8}, .3, 20)

    def test_small_request_is_reserved_before_network_call(self):
        mod = self.module()
        state = {'charged': 1.2, 'pending': 0}
        mod.reserve(state, .25, 20)
        self.assertEqual(state['pending'], .25)

    def test_unknown_or_negative_prices_fail_closed(self):
        mod = self.module()
        for value in [None, -1, float('nan')]:
            with self.assertRaises((ValueError, TypeError)): mod.reserve({'charged': 0, 'pending': 0}, value, 20)

if __name__ == '__main__': unittest.main()
