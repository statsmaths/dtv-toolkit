from os import makedirs
from os.path import exists, join, abspath
import tempfile

import pytest

from dvt.cli import run_cli


class TestCli:
    def test_with_default(self):
        finput = abspath(join("test-data", "video-clip.mp4"))
        dname = tempfile.mkdtemp()  # creates directory

        run_cli(["python", "video-viz", "--dirout", dname, finput])

        assert exists(join(dname, "video-clip"))
        assert exists(join(dname, "video-clip", "img"))
        assert exists(join(dname, "video-clip", "img-display"))
        assert exists(join(dname, "video-clip", "img-thumb"))
        assert exists(join(dname, "video-clip", "img-flow"))
        assert exists(join(dname, "video-clip", "data.json"))

    def test_input_not_found(self):
        finput = abspath(join("test-data", "video-clip-fake.mp4"))
        dname = tempfile.mkdtemp()  # creates directory

        with pytest.raises(FileNotFoundError) as e_info:
            run_cli(["python",  "video-viz", "--dirout", dname, finput])
