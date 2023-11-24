import unittest

import common

class TestIsMetricallyPermissible(unittest.TestCase):
    def test_invalid_sedes(self):
        for sedes in (0, 0.5, 1.1, 13.5):
            with self.assertRaises(ValueError, msg = sedes):
                common.is_metrically_permissible("", sedes)

    def test_invalid_shape(self):
        for shape in ("a", "b", "-+"):
            with self.assertRaises(KeyError):
                common.is_metrically_permissible(shape, 1)

    def test(self):
        F = False
        T = True
        for shape, cases in (
            #            1   2 2.5   3   4 4.5   5   6 6.5   7   8 8.5   9  10 10.5 11  12  13
            (       "", (T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T)),
            (      "⏑", (F,  T,  T,  F,  T,  T,  F,  T,  T,  F,  T,  T,  F,  T,  T,  F,  F,  F)),
            (      "–", (T,  T,  F,  T,  T,  F,  T,  T,  F,  T,  T,  F,  T,  T,  F,  T,  T,  F)),
            (     "⏑⏑", (F,  T,  F,  F,  T,  F,  F,  T,  F,  F,  T,  F,  F,  T,  F,  F,  F,  F)),
            (     "––", (T,  T,  F,  T,  T,  F,  T,  T,  F,  T,  T,  F,  T,  T,  F,  T,  F,  F)),
            (    "⏑–⏑", (F,  F,  T,  F,  F,  T,  F,  F,  T,  F,  F,  T,  F,  F,  F,  F,  F,  F)),
            (    "–⏑–", (F,  F,  F,  F,  F,  F,  F,  F,  F,  F,  F,  F,  F,  F,  F,  F,  F,  F)),
            ("–––⏑⏑––", (T,  F,  F,  T,  F,  F,  T,  F,  F,  T,  F,  F,  F,  F,  F,  F,  F,  F)),
            ("–––⏑⏑–⏑", (T,  F,  F,  T,  F,  F,  T,  F,  F,  F,  F,  F,  F,  F,  F,  F,  F,  F)),
        ):
            for sedes, expected in zip(map(float, common.KNOWN_SEDES + ("13",)), cases):
                self.assertEqual(common.is_metrically_permissible(shape, sedes), expected, (shape, sedes))
