import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from model.my_model import run_full_analysis
from PIL import Image
import numpy as np

def make_test_image(size=(64, 64)):
    arr = np.zeros((size[0], size[1], 3), dtype=np.uint8)
    arr[16:48, 16:48] = [255, 128, 0]
    return Image.fromarray(arr)

def test_run_full_analysis(tmp_path, monkeypatch):
    img = make_test_image()
    img_path = tmp_path / "img.png"
    img.save(img_path)

    (tmp_path / "media/analysis").mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(tmp_path)

    m1, m2, h1, ov, d = run_full_analysis(str(img_path))
    assert isinstance(m1, float)
    assert isinstance(m2, float)
    assert isinstance(d, list)
    assert os.path.exists(h1)
    assert os.path.exists(ov)
