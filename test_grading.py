import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
from urllib.request import Request, urlopen
import unittest
from unittest.mock import patch

import audit_grading as audit
import exam_grading as grading
import serve_practice as server


class StructuralTests(unittest.TestCase):
    def test_all_forty_questions_have_rules_and_durations(self):
        self.assertEqual(len(server.QUESTION_PROFILES), 40)
        for qid in grading.QIDS:
            with self.subTest(qid=qid):
                self.assertTrue(grading.reference_rules(qid)[0])
                self.assertGreater(grading.duration_minutes(qid), 0)

    def test_reference_structure_and_aliases(self):
        for qid in ("1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "2.1.1"):
            with self.subTest(qid=qid):
                n = audit.answer_notebook(qid)
                for cell in n["cells"]:
                    cell["source"] = cell["source"].replace("import pandas as pd", "import pandas as pandas").replace("pd.", "pandas.").replace(".astype(int)", ".astype('int')").replace("data.head()", "data.head(5)")
                checks = grading.structure_checks(qid, n)
                self.assertTrue(all(c["ok"] for c in checks), [c for c in checks if not c["ok"]])

    def test_comments_strings_imports_do_not_pass_rules(self):
        for qid in grading.QIDS:
            n = audit.notebook_from_sources(["# pd.read_csv np.where groupby StandardScaler\nimport pandas\n'np.where data.to_csv'\nprint('audit')"])
            self.assertFalse(any(c["ok"] for c in grading.structure_checks(qid, n)), qid)

    def test_empty_imports_docstrings_and_pass_not_effective(self):
        for source in ("", "# comment", "import pandas as pd", "'docstring'", "pass"):
            self.assertFalse(server._is_effective_code_cell({"source": source}))

    def test_placeholder_column_name_and_comments_are_not_blanks(self):
        n = audit.notebook_from_sources(["# _____\nx = data['Do you exercise ___________ ?']\nx = _____"])
        self.assertEqual(grading.placeholders(n), 1)

    def test_missing_std_has_cell_and_expected_actual(self):
        n = audit.answer_notebook("1.1.4")
        n["cells"][1]["source"] = n["cells"][1]["source"].replace("/ data['ReviewScore'].std()", "/ data['ReviewScore']")
        checks = grading.structure_checks("1.1.4", n)
        found = [c for c in checks if not c["ok"] and c.get("cell") == 2 and "ReviewScore" in c.get("expected", "")]
        self.assertTrue(found)
        self.assertIn(".std()", found[0]["expected"])

    def test_duration_matches_thirteen_original_pages(self):
        for qid in [f"2.{j}.{i}" for j in (1, 2) for i in range(2, 6)] + [f"3.2.{i}" for i in range(1, 6)]:
            self.assertEqual(grading.duration_minutes(qid), 20)

    def test_advanced_scaffolds_have_no_unterminated_strings(self):
        for qid in ("6.5.1", "6.5.3"):
            n = json.loads((grading.SOURCE / qid / (qid + ".ipynb")).read_text(encoding="utf-8"))
            for cell in n["cells"]:
                if cell["cell_type"] == "code":
                    ast.parse(grading.source_text(cell))

    def test_no_execution_proof_cannot_score_full_marks(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "answer.ipynb"
            path.write_text(json.dumps(audit.answer_notebook("1.1.4")), encoding="utf-8")
            auto = {"available": True, "successful_cells": 3, "executed_cells": 3, "errors": [], "engine_error": ""}
            with patch.object(server, "_auto_execute_notebook", return_value=auto):
                r = server._analyze_notebook({"workspace": Path(folder), "notebook": path.name, "qid": "1.1.4"})
            self.assertLess(r["score"], 100)

    def test_empty_answer_is_zero_for_all_forty(self):
        for qid in grading.QIDS:
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "answer.ipynb"
                path.write_text(json.dumps(audit.notebook_from_sources(["# comment"])), encoding="utf-8")
                auto = {"available": True, "successful_cells": 0, "executed_cells": 0, "errors": [], "engine_error": ""}
                with patch.object(server, "_auto_execute_notebook", return_value=auto):
                    r = server._analyze_notebook({"workspace": Path(folder), "notebook": path.name, "qid": qid})
                self.assertEqual(r["score"], 0, qid)

    def test_onnx_prediction_overwrite_is_detected(self):
        snapshot = {"models":{"ort_session":{"type":"onnxruntime.capi.onnxruntime_inference_collection.InferenceSession"}},
                    "ort_outs":{"shape":[1,3],"values":[.1,.7,.2],"finite":True},"predicted_class":0}
        with tempfile.TemporaryDirectory() as folder:
            checks = grading.result_checks("3.2.2",Path(folder),snapshot)
        self.assertTrue(any(not c["ok"] and "argmax" in c["label"] for c in checks))


class ExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history_before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in server.HISTORY_ROOT.rglob("*") if p.is_file()}

    @classmethod
    def tearDownClass(cls):
        after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in server.HISTORY_ROOT.rglob("*") if p.is_file()}
        if cls.history_before != after:
            raise AssertionError("历史答卷或分数被修改")

    def run_answer(self, qid, notebook, stale=False):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            for source in (grading.SOURCE / qid).glob("*"):
                if source.is_file() and source.suffix != ".ipynb":
                    shutil.copyfile(source, path / source.name)
                elif source.is_dir():
                    shutil.copytree(source, path / source.name)
            if stale:
                (path / "cleaned_user_behavior_data.csv").write_text("fake\n1\n", encoding="utf-8")
            nb = path / (qid + ".ipynb")
            nb.write_text(json.dumps(notebook, ensure_ascii=False), encoding="utf-8")
            saved = nb.read_bytes()
            report = server._analyze_notebook({"workspace": path, "notebook": nb.name, "qid": qid})
            self.assertEqual(saved, nb.read_bytes())
            self.assertEqual(report["auto_engine_error"], "", report)
            return report

    def test_correct_basic_answers_pass_actual_result_checks(self):
        for qid in ("1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "2.1.1"):
            with self.subTest(qid=qid):
                r = self.run_answer(qid, audit.answer_notebook(qid))
                self.assertEqual(r["auto_errors"], [])
                self.assertEqual(r["score"], 100, [c for c in r["checks"] if not c["ok"]])

    def test_wrong_ratio_and_skipped_scaling_are_rejected(self):
        for qid, before, after in [("1.1.1", "/ len(data)", "/ 1"), ("2.1.1", "scaler.fit_transform(df[numeric_cols])", "df[numeric_cols]")]:
            n = audit.answer_notebook(qid)
            for cell in n["cells"]:
                cell["source"] = cell["source"].replace(before, after)
            r = self.run_answer(qid, n)
            self.assertEqual(r["auto_errors"], [])
            self.assertLess(r["score"], 100)
            self.assertTrue(any(c["kind"] == "result" and not c["ok"] for c in r["checks"]))

    def test_missing_std_and_overwrite_are_rejected(self):
        for variant in ("missing_std", "overwrite"):
            n = audit.answer_notebook("1.1.4")
            if variant == "missing_std":
                n["cells"][1]["source"] = n["cells"][1]["source"].replace("/ data['ReviewScore'].std()", "/ data['ReviewScore']")
            else:
                n["cells"][1]["source"] += "\ndata['ReviewScore'] = 0\n"
            r = self.run_answer("1.1.4", n)
            self.assertLess(r["score"], 100)
            self.assertTrue(any(c["kind"] == "result" and not c["ok"] for c in r["checks"]))

    def test_equivalent_integer_type_is_not_deducted(self):
        n = audit.answer_notebook("1.1.4")
        for cell in n["cells"]:
            cell["source"] = cell["source"].replace(".astype(int)", ".astype('int')")
        self.assertEqual(self.run_answer("1.1.4", n)["score"], 100)

    def test_comment_only_and_old_outputs_cannot_pass(self):
        n = audit.notebook_from_sources(["# pd.read_csv np.where value_counts pd.cut groupby"])
        self.assertEqual(self.run_answer("1.1.1", n)["score"], 0)
        n = audit.notebook_from_sources(["print('done')"])
        r = self.run_answer("1.1.4", n, stale=True)
        self.assertLess(r["score"], 100)
        self.assertTrue(any(not c["ok"] and "cleaned_user_behavior_data.csv" in c["label"] for c in r["checks"]))

    @unittest.skipUnless(importlib.util.find_spec("cv2"), "需要 OpenCV")
    def test_three_vision_result_validators(self):
        fills = {
            "6.1.1": ["cv2.Laplacian(gray,cv2.CV_64F).var()", "gray.mean()", "im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)", "im.rotate(15,expand=False)", "random.uniform(.8,1.2)"],
            "6.1.2": ["cv2.resize(img,(640,360))", "cv2.GaussianBlur(gray,(5,5),0)", "cv2.Canny(blur,50,150)", "cv2.morphologyEx(edges,cv2.MORPH_CLOSE,kernel,iterations=2)"],
            "6.1.3": ["clahe.apply(gray)", "cv2.threshold(enhanced,180,255,cv2.THRESH_BINARY)[1]", "cv2.threshold(enhanced,70,255,cv2.THRESH_BINARY_INV)[1]", "cv2.morphologyEx(cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel),cv2.MORPH_CLOSE,kernel,iterations=2)"],
        }
        for qid, values in fills.items():
            with self.subTest(qid=qid):
                n = json.loads((grading.SOURCE / qid / (qid + ".ipynb")).read_text(encoding="utf-8"))
                for cell in n["cells"]:
                    if cell["cell_type"] != "code": continue
                    text = grading.source_text(cell)
                    while "_____________" in text:
                        text = text.replace("_____________", values.pop(0), 1)
                    cell["source"] = text
                r = self.run_answer(qid, n)
                self.assertFalse(r["auto_errors"], r["auto_errors"])
                self.assertEqual(r["score"], 100, [c for c in r["checks"] if not c["ok"]])

    def test_clustering_result_validator(self):
        qid = "6.2.1"
        n = json.loads((grading.SOURCE / qid / (qid + ".ipynb")).read_text(encoding="utf-8"))
        values = ["SimpleImputer(strategy='median')", "StandardScaler()", "SimpleImputer(strategy='most_frequent')", "OneHotEncoder(handle_unknown='ignore')", "silhouette_score(X,labels)", "KMeans(n_clusters=best_k,random_state=42,n_init=10)"]
        for cell in n["cells"]:
            if cell["cell_type"] != "code": continue
            text = grading.source_text(cell)
            while "_____________" in text: text=text.replace("_____________",values.pop(0),1)
            cell["source"] = text
        r = self.run_answer(qid, n)
        self.assertFalse(r["auto_errors"])
        self.assertEqual(r["score"], 100, [c for c in r["checks"] if not c["ok"]])

    def test_two_offline_ai_routes_and_rag_metrics(self):
        for qid in ("6.5.1", "6.5.3"):
            with self.subTest(qid=qid):
                n = json.loads((grading.SOURCE / qid / (qid + ".ipynb")).read_text(encoding="utf-8"))
                reference = audit.answer_notebook(qid)
                values = [ast.unparse(node.value) for c in reference["cells"] for node in ast.parse(c["source"]).body if isinstance(node,ast.Expr)]
                for cell in n["cells"]:
                    if cell["cell_type"] != "code": continue
                    text = grading.source_text(cell)
                    while "_____________" in text: text=text.replace("_____________",values.pop(0),1)
                    cell["source"] = text
                with patch.dict(os.environ, {"OPENAI_BASE_URL":"", "OPENAI_API_KEY":"", "OPENAI_MODEL":""}):
                    r = self.run_answer(qid,n)
                self.assertFalse(r["auto_errors"], r["auto_errors"])
                self.assertEqual(r["score"],100,[c for c in r["checks"] if not c["ok"]])

    @unittest.skipUnless(importlib.util.find_spec("torch"), "需要 PyTorch")
    def test_neural_network_requires_actual_weight_update(self):
        source = """import torch, pandas as pd
model=torch.nn.Linear(1,1)
opt=torch.optim.SGD(model.parameters(),lr=.01)
x=torch.tensor([[1.],[2.]])
y=torch.tensor([[2.],[4.]])
history=[]
for epoch in range(2):
    opt.zero_grad()
    loss=((model(x)-y)**2).mean()
    loss.backward()
    opt.step()
    history.append({'epoch':epoch+1,'loss':loss.item()})
pd.DataFrame(history).to_csv('training_history.csv',index=False)
torch.save(model.state_dict(),'shape_cnn.pt')
"""
        for trained in (True,False):
            text = source if trained else source.replace("    opt.step()", "    pass")
            r = self.run_answer("6.3.1",audit.notebook_from_sources([text]))
            checks = [c for c in r["checks"] if c["kind"]=="result" and "优化步骤" in c["label"]]
            self.assertEqual(len(checks),1)
            self.assertEqual(checks[0]["ok"],trained,checks)

    def test_submit_and_review_http_flow_preserves_colliding_history(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            exam_root, history_root = root / "workspace", root / "history"
            workspace = exam_root / "temporary_grading_case"
            workspace.mkdir(parents=True)
            old = history_root / workspace.name
            old.mkdir(parents=True)
            (old / "keep.txt").write_text("old answer",encoding="utf-8")
            qid = "1.1.4"
            shutil.copyfile(grading.SOURCE / qid / "user_behavior_data.csv", workspace / "user_behavior_data.csv")
            notebook_path = workspace / (qid + ".ipynb")
            notebook_path.write_text(json.dumps(audit.answer_notebook(qid)),encoding="utf-8")
            session = {"id":workspace.name,"qid":qid,"workspace":workspace,"notebook":notebook_path.name,
                       "initial_files":server._list_relative_files(workspace),"started_at_ms":server._now_ms(),"duration_minutes":30}
            with patch.object(server,"EXAM_ROOT",exam_root), patch.object(server,"HISTORY_ROOT",history_root), patch.object(server,"ACTIVE_SESSION",session), patch.object(server,"LAST_RESULT",None), patch.object(server,"_stop_jupyter"):
                http = server.ThreadingHTTPServer(("127.0.0.1",0),server.PracticalHandler)
                thread = threading.Thread(target=http.serve_forever,daemon=True)
                thread.start()
                try:
                    base = f"http://127.0.0.1:{http.server_port}"
                    request = Request(base+"/api/exam/submit",data=json.dumps({"session_id":workspace.name}).encode(),headers={"Content-Type":"application/json"})
                    with urlopen(request,timeout=90) as response:
                        report=json.load(response)["report"]
                    self.assertEqual(report["score"],100)
                    self.assertEqual(report["grading_version"],2)
                    self.assertEqual(report["id"],workspace.name+"_1")
                    with urlopen(base+"/api/exam/record?id="+report["id"]) as response:
                        record=json.load(response)["record"]
                    self.assertEqual(record["score"]["score"],100)
                    self.assertEqual((old/"keep.txt").read_text(encoding="utf-8"),"old answer")
                finally:
                    http.shutdown()
                    http.server_close()
                    thread.join()


if __name__ == "__main__":
    unittest.main()
