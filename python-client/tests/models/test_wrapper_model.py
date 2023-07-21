import tempfile

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from giskard import Dataset, Model
from giskard.models.base.wrapper import WrapperModel


def test_wrapper_model_handles_batching():
    class CustomModel(WrapperModel):
        expected_batch_size = []

        def model_predict(self, data):
            assert len(data) in self.expected_batch_size
            return [0] * len(data)

        @classmethod
        def load_model(cls):
            pass

        def save_model(self, path):
            pass

    dataset = Dataset(pd.DataFrame({"A": np.ones(101)}))

    model = CustomModel(None, model_type="regression")
    model.expected_batch_size = [101]

    model.predict(dataset)

    model = CustomModel(None, model_type="regression", batch_size=1)
    model.expected_batch_size = [1]

    model.predict(dataset)

    model = CustomModel(None, model_type="regression", batch_size=20)
    model.expected_batch_size = [20, 1]

    model.predict(dataset)


def test_wrapper_model_saves_and_loads_batch_size():
    base_model = LogisticRegression()
    model = Model(
        base_model.predict_proba,
        model_type="classification",
        feature_names=["one", "two"],
        classification_threshold=0.5,
        classification_labels=[0, 1],
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        model.batch_size = 127
        model.save(tmpdir)
        loaded_model = Model.load(tmpdir)

        assert loaded_model.batch_size == 127
