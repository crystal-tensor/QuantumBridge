"""Dependency diagnostics cannot erase exits, change SDK versions or claim Native support."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import record_arrow_coexistence_review as review


class ImportReviewTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name)
        self.rows=[]
        for profile,sdk in review.SDK.items():
            versions={"qiskit":sdk[0],"pennylane":sdk[1],"tensorflow":"2.21.0","pyarrow":"24.0.0"}
            for case,order in review.ORDERS.items():
                output=dict(modules=[dict(requested=name,version=versions[name],arrow_already_loaded=False) for name in order],
                    quantumbridge_imported=False,arrow_pool_setting="system" if case.endswith("_system_pool") else None,
                    native_accepted=False)
                stdout=(json.dumps(output)+"\n").encode()
                (self.root/(profile+"-"+case+".stdout")).write_bytes(stdout)
                (self.root/(profile+"-"+case+".stderr")).write_bytes(b"")
                self.rows.append(dict(profile=profile,case=case,native_accepted=False,terminal=True,
                    process_exit=0,probe_source_sha256="fixture",observations=output,
                    stdout_sha256=review.sha(stdout),stderr_sha256=review.sha(b"")))
        self.write(self.rows)

    def write(self,rows):
        (self.root/"import-controls.json").write_text(json.dumps(dict(rows=rows)))

    def test_full_import_matrix_is_only_an_observation(self):
        rows=review.import_matrix(self.root,"","24.0.0","fixture")
        self.assertEqual(len(rows),12)
        self.assertTrue(all(r["native_accepted"] is False for r in rows))

    def test_missing_or_duplicate_control_is_not_a_complete_matrix(self):
        for rows in (self.rows[:-1],self.rows[:-1]+[self.rows[0]]):
            with self.subTest(count=len(rows)):
                self.write(rows)
                with self.assertRaisesRegex(ValueError,"population"):
                    review.import_matrix(self.root,"","24.0.0","fixture")

    def test_sdk_replacement_false_acceptance_and_nonterminal_results_refuse(self):
        for change in ("sdk","acceptance","native_import","exit","terminal","code"):
            with self.subTest(change=change):
                rows=copy.deepcopy(self.rows)
                row=next(r for r in rows if r["case"]=="qiskit_arrow")
                if change=="sdk":row["observations"]["modules"][0]["version"]="different"
                elif change=="acceptance":row["native_accepted"]=True
                elif change=="native_import":row["observations"]["quantumbridge_imported"]=True
                elif change=="exit":row["process_exit"]="TIMEOUT"
                elif change=="terminal":row["terminal"]=False
                else:row["probe_source_sha256"]="changed"
                self.write(rows)
                with self.assertRaisesRegex(ValueError,"identity"):
                    review.import_matrix(self.root,"","24.0.0","fixture")

    def test_modified_raw_stdout_is_not_recertified_by_its_json(self):
        (self.root/"main-arrow_only.stdout").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError,"receipt changed"):
            review.import_matrix(self.root,"","24.0.0","fixture")


if __name__=="__main__":
    unittest.main()
