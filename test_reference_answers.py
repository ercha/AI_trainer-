"""参考答案展示回归：完整性、只读边界及 HTTP 错误处理。"""

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

import exam_grading as grading
import reference_answers as answers
import serve_practice as server


class ReferenceAnswerTests(unittest.TestCase):
    def test_all_sixty_answers_and_forty_code_answers(self):
        files = list(grading.ANSWERS.glob("*_答案.md"))
        self.assertEqual(len(files), 60)
        count = 0
        for path in files:
            qid = path.stem.split("_")[0]
            with self.subTest(qid=qid):
                answer = answers.get_reference_answer(qid, server.ROOT)
                self.assertTrue(answer["markdown"])
                if answer["code"]:
                    ast.parse(answer["code"])
                    count += 1
        self.assertEqual(count, 40)

    def test_fifteen_advanced_answers_keep_complete_scaffold_and_inputs(self):
        for qid in [f"6.{i}.{j}" for i in range(1, 6) for j in range(1, 4)]:
            with self.subTest(qid=qid):
                paths = [grading.ANSWERS / f"{qid}_答案.md", grading.SOURCE / qid / f"{qid}.ipynb"]
                before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
                answer = answers.get_reference_answer(qid, server.ROOT)
                self.assertIn("import ", answer["code"])
                self.assertNotIn("_____________", answer["code"])
                self.assertGreater(len(answer["code"]), len(grading.code_blocks(paths[0].read_text(encoding="utf-8"))[0]))
                self.assertEqual(before, [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths])

    def test_onnx_view_uses_standalone_solution_not_duplicate_fill_list(self):
        answer = answers.get_reference_answer("3.2.2", server.ROOT)
        self.assertEqual(answer["code"].count("import onnxruntime"), 1)
        self.assertEqual(answer["code"].count("ort_session ="), 1)
        self.assertIn("ipynb中需要填写", answer["markdown"])

    def test_document_question_preserves_full_prose_without_fake_code(self):
        answer = answers.get_reference_answer("4.1.1", server.ROOT)
        self.assertEqual(answer["code"], "")
        self.assertGreater(len(answer["markdown"]), 100)

    def test_advanced_image_thresholds_and_transforms_are_expressions(self):
        code = answers.get_reference_answer("6.1.3", server.ROOT)["code"]
        assignments = [node for node in ast.walk(ast.parse(code)) if isinstance(node, ast.Assign)]
        for name in ("bright", "dark"):
            node = next(node for node in assignments if isinstance(node.targets[0], ast.Name) and node.targets[0].id == name)
            self.assertIsInstance(node.value, ast.Subscript)
        flower = answers.get_reference_answer("6.3.2", server.ROOT)["code"]
        self.assertIn("transforms.RandomRotation(15)", flower)
        self.assertIn("nn.BatchNorm2d(24)", flower)
        self.assertIn("nn.Dropout(0.4)", flower)
        resnet = answers.get_reference_answer("6.3.3", server.ROOT)["code"]
        self.assertIn("for p in model.parameters(): p.requires_grad = False", resnet)
        self.assertIn("for p in model.layer4.parameters(): p.requires_grad = True", resnet)

    def test_mismatched_fragments_are_not_presented_as_complete_code(self):
        with self.assertRaises(ValueError):
            answers.complete_advanced_code("6.1.1", {"cells": [{"cell_type": "code", "source": "x = _____________"}]}, "1\n2")

    def test_http_answers_errors_and_read_only_session(self):
        http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.PracticalHandler)
        thread = threading.Thread(target=http.serve_forever, daemon=True)
        thread.start()
        session, last = server.ACTIVE_SESSION, server.LAST_RESULT
        try:
            base = f"http://127.0.0.1:{http.server_port}"
            with urlopen(base + "/api/answer?qid=6.1.1") as response:
                answer = json.load(response)
                self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertIn("augmentation_preview.png", answer["code"])
            for qid, expected in (("../serve_practice.py", 400), ("unknown", 400), ("9.9.9", 404)):
                with self.subTest(qid=qid), self.assertRaises(HTTPError) as caught:
                    urlopen(base + "/api/answer?qid=" + qid)
                self.assertEqual(caught.exception.code, expected)
            self.assertIs(server.ACTIVE_SESSION, session)
            self.assertIs(server.LAST_RESULT, last)
        finally:
            http.shutdown()
            http.server_close()
            thread.join()

    @unittest.skipUnless(importlib.util.find_spec("cv2"), "需要 OpenCV")
    def test_completed_image_answers_run_only_in_temporary_workspace(self):
        for qid, output in (("6.1.1", "summary.json"), ("6.1.3", "defect_report.csv")):
            with self.subTest(qid=qid), tempfile.TemporaryDirectory(prefix="trainer-answer-test-") as folder:
                shutil.copytree(grading.SOURCE / qid, folder, dirs_exist_ok=True)
                code = answers.get_reference_answer(qid, server.ROOT)["code"]
                result = subprocess.run([sys.executable, "-c", "import matplotlib; matplotlib.use('Agg')\n" + code],
                                        cwd=folder, capture_output=True, text=True, encoding="utf-8", timeout=60)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((Path(folder) / output).is_file())


if __name__ == "__main__":
    unittest.main()
