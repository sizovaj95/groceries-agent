from unittest import TestCase

import pandas as pd
from pandas.testing import assert_frame_equal

import constants as co
import src.preprocessing.extracting_agent as mod


class TestExtractingAgent(TestCase):
    def test_convert_items_list_to_pandas_df_preserves_item_data_and_order(self):
        test_data = [
            co.ItemData(
                name="Salmon Fillets",
                brand="ASDA",
                price=3.80,
                quantity=2,
                group="Fish & Seafood",
                weight=0.26,
                volume=None,
                number_per_pack=2,
                is_substitute=True,
            ),
            co.ItemData(
                name="Milk",
                brand=None,
                price=1.50,
                quantity=None,
                group="Dairy & Eggs",
                weight=None,
                volume=1.0,
                number_per_pack=None,
            ),
        ]
        expected = pd.DataFrame(
            {
                "name": ["Salmon Fillets", "Milk"],
                "brand": ["ASDA", None],
                "price": [3.80, 1.50],
                "quantity": [2, None],
                "group": ["Fish & Seafood", "Dairy & Eggs"],
                "weight": [0.26, None],
                "volume": [None, 1.0],
                "number_per_pack": [2, None],
                "is_substitute": [True, False],
            }
        )

        result = mod.convert_items_list_to_pandas_df(test_data)

        assert_frame_equal(expected, result)

    def test_convert_items_list_to_pandas_df_empty_list_retains_columns(self):
        result = mod.convert_items_list_to_pandas_df([])

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual((0, 9), result.shape)
        self.assertEqual(
            [
                "name",
                "brand",
                "price",
                "quantity",
                "group",
                "weight",
                "volume",
                "number_per_pack",
                "is_substitute",
            ],
            result.columns.tolist(),
        )
