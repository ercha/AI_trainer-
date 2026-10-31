"""不联网、不下载模型的零基础课程与安装策略回归测试。"""
from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest.mock import patch

import install_torch

ROOT = Path(__file__).resolve().parent


class BeginnerCourseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = (ROOT / "beginner_course_data.js").read_text(encoding="utf-8")
        prefix = "window.BEGINNER_COURSE="
        assert script.startswith("//")
        payload = script[script.index(prefix) + len(prefix):].strip().removesuffix(";")
        cls.modules = json.loads(payload)["modules"]

    def test_only_five_modules_with_six_lessons_each(self):
        self.assertEqual([m["id"] for m in self.modules], list("ABCDE"))
        self.assertTrue(all(len(m["steps"]) == 6 for m in self.modules))

    def test_lessons_have_complete_content(self):
        seen = set()
        for module in self.modules:
            for lesson in module["steps"]:
                self.assertNotIn(lesson["id"], seen)
                seen.add(lesson["id"])
                self.assertTrue(all(lesson[k] for k in
                    ("title", "concept", "code", "steps", "challenge", "solution", "exam")))
                q = lesson["quiz"]
                self.assertTrue(0 <= q["answer"] < len(q["options"]))
                self.assertTrue(q["reason"])

    def test_five_valid_notebooks_with_compilable_code_cells(self):
        for module in "ABCDE":
            path = ROOT / "beginner_notebooks" / f"{module}.ipynb"
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["nbformat"], 4)
            cells = data["cells"]
            self.assertGreaterEqual(len(cells), 5)
            for cell in cells:
                if cell["cell_type"] == "code":
                    compile("".join(cell["source"]), str(path), "exec")

    def test_beginner_page_assets_and_exam_deeplink(self):
        page = (ROOT / "beginner_course.html").read_text(encoding="utf-8")
        self.assertIn("beginner_course_data.js", page)
        self.assertIn("beginner_course_app.js", page)
        app = (ROOT / "beginner_course_app.js").read_text(encoding="utf-8")
        self.assertIn("practice.html?question=", app)
        self.assertIn("localStorage", app)


class TorchInstallerTests(unittest.TestCase):
    def test_choose_cpu_without_nvidia(self):
        self.assertEqual(install_torch.choose_backend("auto", "Windows", False), "cpu")
        self.assertEqual(install_torch.choose_backend("auto", "Linux", False), "cpu")

    def test_choose_cuda_for_nvidia(self):
        self.assertEqual(install_torch.choose_backend("auto", "Windows", True), "cuda")
        self.assertEqual(install_torch.choose_backend("gpu", "Linux", True), "cuda")

    def test_manual_override_and_missing_gpu(self):
        self.assertEqual(install_torch.choose_backend("cpu", "Windows", True), "cpu")
        with self.assertRaises(RuntimeError):
            install_torch.choose_backend("gpu", "Windows", False)

    def test_macos_wheel(self):
        self.assertEqual(install_torch.choose_backend("auto", "Darwin", False), "mps")

    @patch("install_torch.shutil.which", return_value=None)
    def test_missing_nvidia_smi(self, _mock_which):
        self.assertFalse(install_torch.detect_nvidia()[0])


if __name__ == "__main__":
    unittest.main()
