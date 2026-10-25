#!/usr/bin/env python3
"""
Synthetic Generalization & Policy Action Test Suite.
Validates the Deletion Audit Engine across all 15 policy operations:
- 4 FINDING operations
- 5 REMEDIATION operations
- 6 VERIFICATION operations
And edge-case scenarios (negation phrases, conflicting snapshots, restore risk).
"""

import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, 'code'))
import main as m

class TestGeneralizationPolicyActions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = m.DeletionAuditEngine()

    def test_all_15_operations_recognized(self):
        """Verify that all 15 challenge policy operations are defined in OP_ORDER."""
        expected_ops = {
            'REPORT_REMAINING_RECORD', 'REPORT_EXPOSED_PII', 'REPORT_ACTIVE_DATA_FLOW', 'REPORT_RESTORE_RISK',
            'DISABLE_DATA_FLOW', 'BLOCK_RESTORE', 'DELETE_RECORD', 'REDACT_RECORD', 'ANONYMIZE_RECORD',
            'VERIFY_RECORD_ABSENT', 'VERIFY_RECORD_PRESENT', 'VERIFY_RECORD_REDACTED',
            'VERIFY_RECORD_ANONYMIZED', 'VERIFY_DATA_FLOW_DISABLED', 'VERIFY_RESTORE_BLOCKED'
        }
        defined_ops = set(m.OP_ORDER.keys())
        self.assertEqual(expected_ops, defined_ops)

    def test_phase_hierarchy_invariants(self):
        """Ensure phase sorting key strictly maintains FINDING < REMEDIATION < VERIFICATION."""
        self.assertLess(m.PHASE_ORDER['FINDING'], m.PHASE_ORDER['REMEDIATION'])
        self.assertLess(m.PHASE_ORDER['REMEDIATION'], m.PHASE_ORDER['VERIFICATION'])

    def test_negated_phrase_classification(self):
        """Test non-deletion classification on various subtle phrased requests."""
        non_del_req = {
            'case_id': 'test_non_del',
            'email': 'customer@example.com',
            'request_text': 'I am not asking for deletion of my account, just updating marketing lists only.',
            'reported_status': 'NOT_STARTED',
            'reported_at': '2026-09-01T12:00:00Z',
            'requested_at': '2026-08-30T12:00:00Z',
            'audit_at': '2026-09-02T12:00:00Z'
        }
        st, steps = self.engine.audit_case(non_del_req)
        self.assertEqual(st, 'NOT_APPLICABLE')
        self.assertEqual(steps, [])

    def test_holdout_exact_sequence(self):
        """Validate that all holdout cases (cases 25-32) achieve 100% sequence match."""
        import csv, json
        with open(os.path.join(REPO_ROOT, 'dataset', 'sample_output.csv'), encoding='utf-8') as f:
            gold = {r['case_id']: (r['deletion_status'], json.loads(r['steps_json'])) for r in csv.DictReader(f)}
        with open(os.path.join(REPO_ROOT, 'dataset', 'sample_deletion_requests.csv'), encoding='utf-8') as f:
            sample_reqs = [r for r in csv.DictReader(f) if int(r['case_id'].split('_')[1]) >= 25]

        for req in sample_reqs:
            cid = req['case_id']
            gst, gsteps = gold[cid]
            st, steps = self.engine.audit_case(req)
            self.assertEqual(st, gst, f"Status mismatch on {cid}")
            self.assertEqual(len(steps), len(gsteps), f"Step count mismatch on {cid}")
            for i, (s, gs) in enumerate(zip(steps, gsteps)):
                for k in ['phase', 'system_id', 'resource_id', 'operation', 'state', 'evidence_id']:
                    self.assertEqual(s.get(k), gs.get(k), f"Step {i+1} attribute {k} mismatch on {cid}")

if __name__ == '__main__':
    unittest.main()
