import numpy as np
from PIL import Image
from my_model import process_image, segment_image, create_overlay

def make_test_image(size=(64, 64)):
    arr = np.zeros((size[0], size[1], 3), dtype=np.uint8)
    arr[16:48, 16:48] = [255, 128, 0]
    return Image.fromarray(arr)

def test_process_image_output_shapes():
    img = make_test_image()
    mask, c1, c2, inter = process_image(img)
    assert mask.shape == c1.shape == c2.shape == inter.shape
    assert mask.dtype == np.uint8

def test_segment_image_outputs_positive():
    img = make_test_image()
    diam = segment_image(img)
    assert isinstance(diam, list)
    assert all(d > 0 for d in diam)

def test_create_overlay(tmp_path):
    img = make_test_image()
    mask = np.zeros((64, 64), dtype=np.uint8)
    mask[20:40, 20:40] = 1
    input_path = tmp_path / "img.png"
    save_path = tmp_path / "overlay.png"
    img.save(input_path)
    result_path = create_overlay(str(input_path), mask, str(save_path))
    assert result_path.endswith(".png")
    assert save_path.exists()
