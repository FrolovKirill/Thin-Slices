from my_model import resource_path
import os

def test_resource_path_normal():
    p = resource_path("file.txt")
    assert p.endswith("file.txt")
    assert os.path.isabs(p)
