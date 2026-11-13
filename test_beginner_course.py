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

    def test_detailed_lesson_material(self):
        content = (ROOT / "beginner_course_extras.js").read_text(encoding="utf-8")
        marker = "window.BEGINNER_COURSE_EXTRAS="
        self.assertIn(marker, content)
        details = json.loads(content.split(marker, 1)[1].strip().removesuffix(";"))["lessons"]
        all_ids = {step["id"] for module in self.modules for step in module["steps"]}
        self.assertEqual(set(details), all_ids)
        for lesson_id, detail in details.items():
            self.assertGreaterEqual(len(detail["terms"]), 3, lesson_id)
            self.assertGreaterEqual(len(detail["walkthrough"]), 3, lesson_id)
            self.assertGreaterEqual(len(detail["apis"]), 2, lesson_id)
            self.assertGreaterEqual(len(detail["pitfalls"]), 2, lesson_id)
            self.assertEqual(len(detail["levels"]), 3, lesson_id)
            self.assertTrue(detail["expected"], lesson_id)
            self.assertTrue(detail["check"], lesson_id)
            for api in detail["apis"]:
                self.assertTrue(all(api.get(key) for key in
                    ("api", "signature", "parameters", "returns", "tip")), lesson_id)

    def test_30_single_lesson_notebooks(self):
        all_lessons = [lesson for m in self.modules for lesson in m["steps"]]
        for lesson in all_lessons:
            lesson_id = lesson["id"]
            module = lesson_id[0]
            path = ROOT / "beginner_notebooks" / module / f"{lesson_id}.ipynb"
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["nbformat"], 4)
            self.assertEqual(data["metadata"]["ai_trainer"]["lesson_id"], lesson_id)
            cells = data["cells"]
            self.assertGreaterEqual(len(cells), 12)
            self.assertEqual(cells[3]["cell_type"], "code")
            self.assertEqual("".join(cells[3]["source"]), lesson["code"])
            for cell in cells:
                if cell["cell_type"] == "code":
                    compile("".join(cell["source"]), str(path), "exec")

    def test_all_30_executable_checkpoints(self):
        import numpy as np
        from beginner_checkpoints import CHECKPOINTS, check_lesson

        expected = {lesson["id"] for module in self.modules for lesson in module["steps"]}
        self.assertEqual(set(CHECKPOINTS), expected)
        for lesson_id in sorted(expected):
            path = ROOT / "beginner_notebooks" / lesson_id[0] / f"{lesson_id}.ipynb"
            notebook = json.loads(path.read_text(encoding="utf-8"))
            source = "\n".join("".join(cell["source"]) for cell in notebook["cells"])
            self.assertIn(f'check_lesson("{lesson_id}", globals())', source)
            self.assertIn("answer_" + lesson_id.lower(), source)
            with self.assertRaises(AssertionError):
                check_lesson(lesson_id, {}, save=False)

        result = check_lesson("A1", {"answer_a1": np.zeros((3, 3), dtype=np.uint8)}, save=False)
        self.assertTrue(result["passed"])
        with self.assertRaises(AssertionError):
            check_lesson("A1", {"answer_a1": np.zeros((3, 3))}, save=False)

    def test_python_primer_structure(self):
        path = ROOT / "beginner_notebooks" / "A" / "Python零基础预备.ipynb"
        primer = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(primer["nbformat"], 4)
        self.assertGreaterEqual(sum(cell["cell_type"] == "code" for cell in primer["cells"]), 6)
        for cell in primer["cells"]:
            if cell["cell_type"] == "code":
                compile("".join(cell["source"]), str(path), "exec")

    def test_webui_grade_sync_is_read_only(self):
        app = (ROOT / "beginner_course_app.js").read_text(encoding="utf-8")
        server = (ROOT / "serve_practice.py").read_text(encoding="utf-8")
        self.assertIn("syncAutoGrades", app)
        self.assertIn("/api/beginner/grades", server)
        self.assertIn("BEGINNER_GRADE_ROOT", server)

    def test_five_module_projects(self):
        projects = json.loads((ROOT / "beginner_projects" / "projects.json").read_text(encoding="utf-8"))
        self.assertEqual([x["id"] for x in projects], list("ABCDE"))
        for project in projects:
            mid = project["id"]
            for name in [f"{mid}_project.ipynb", f"solutions/{mid}_project_solution.ipynb"]:
                path = ROOT / "beginner_projects" / name
                notebook = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(notebook["nbformat"], 4)
                self.assertEqual(notebook["metadata"]["ai_trainer"]["project"], mid)
                for cell in notebook["cells"]:
                    if cell["cell_type"] == "code":
                        compile("".join(cell["source"]), str(path), "exec")

    def test_detailed_webui_and_progress_backup(self):
        page = (ROOT / "beginner_course.html").read_text(encoding="utf-8")
        app = (ROOT / "beginner_course_app.js").read_text(encoding="utf-8")
        self.assertIn("beginner_course_extras.js", page)
        self.assertIn("exportProgress", app)
        self.assertIn("importProgress", app)
        self.assertIn("beginner_notebooks/", app)
        self.assertIn("practice.html?question=", app)

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

    def test_driver_cuda_compatibility(self):
        self.assertEqual(
            install_torch.choose_backend("auto", "Windows", True, (13, 0)), "cpu"
        )
        self.assertEqual(
            install_torch.choose_backend("auto", "Windows", True, (13, 2)), "cuda"
        )
        with self.assertRaises(RuntimeError):
            install_torch.choose_backend("gpu", "Linux", True, (12, 9))

    @patch("install_torch.shutil.which", return_value="nvidia-smi")
    @patch("install_torch.subprocess.run")
    def test_parse_driver_cuda(self, mock_run, _mock_which):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "NVIDIA-SMI 600.10    CUDA Version: 13.2"
        self.assertEqual(install_torch.driver_cuda_version(), (13, 2))

    def test_macos_wheel(self):
        self.assertEqual(install_torch.choose_backend("auto", "Darwin", False), "mps")

    @patch("install_torch.shutil.which", return_value=None)
    def test_missing_nvidia_smi(self, _mock_which):
        self.assertFalse(install_torch.detect_nvidia()[0])


if __name__ == "__main__":
    unittest.main()
