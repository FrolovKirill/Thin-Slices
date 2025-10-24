import torch
from PIL import Image
from my_model import classify_image

def test_classify_image_mock(monkeypatch, tmp_path):
    dummy_img = Image.new("RGB", (224, 224), (128, 128, 128))
    dummy_path = tmp_path / "test.png"
    dummy_img.save(dummy_path)

    class DummyModel:
        def __call__(self, x): 
            return torch.tensor([[0.1, 0.8, 0.1]])

    monkeypatch.setattr("main.loaded_model", DummyModel())

    result = classify_image(str(dummy_path))
    assert result in [0, 1, 2]
