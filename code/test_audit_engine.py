#!/usr/bin/env python3
"""
Regression and Edge-Case Test Suite for Northstar Deletion Audit Agent
Covers temporal reconciliation, identity aliases, policy exceptions, and schema constraints.
"""

import unittest
import os
import sys
import json
import csv

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(REPO_ROOT, 'code'))
import main

class TestDeletionAuditEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = main.DeletionAuditEngine()
        cls.dataset_dir = os.path.join(REPO_ROOT, 'dataset')
        with open(os.path.join(cls.dataset_dir, 'sample_deletion_requests.csv'), encoding='utf-8') as f:
            cls.sample_reqs = list(csv.DictReader(f))
        with open(os.path.join(cls.dataset_dir, 'sample_output.csv'), encoding='utf-8') as f:
            cls.sample_truth = {r['case_id']: r for r in csv.DictReader(f)}

    def test_non_deletion_requests(self):
        """Verify non-deletion requests are correctly classified as NOT_APPLICABLE with empty steps."""
        test_cases = [
            ("I am not asking for deletion, just please send me my data export.", "NOT_APPLICABLE"),
            ("Please do not close my account, I only want marketing lists removed.", "NOT_APPLICABLE"),
            ("Can you provide copies of my invoices? Do not delete anything.", "NOT_APPLICABLE"),
            ("I only want my email address corrected, please leave my profile active.", "NOT_APPLICABLE"),
        ]
        for text, expected in test_cases:
            req = {
                'case_id': 'test_na',
                'email': 'dummy@example.com',
                'requested_at': '2026-09-01T10:00:00Z',
                'reported_at': '2026-09-02T10:00:00Z',
                'audit_at': '2026-09-10T10:00:00Z',
                'request_text': text,
                'reported_status': 'COMPLETE'
            }
            status, steps = self.engine.audit_case(req)
            self.assertEqual(status, expected)
            self.assertEqual(steps, [])

    def test_sample_status_accuracy(self):
        """Verify 100% status classification accuracy across all 32 labeled cases."""
        correct = 0
        for req in self.sample_reqs:
            cid = req['case_id']
            truth = self.sample_truth[cid]
            pred_status, _ = self.engine.audit_case(req)
            if pred_status == truth['deletion_status']:
                correct += 1
        self.assertEqual(correct, len(self.sample_reqs), f"Expected 32/32, got {correct}/32")

    def test_stale_snapshot_ignored(self):
        """Verify evidence captured prior to deletion request is not treated as a lingering finding."""
        req = self.sample_reqs[6] # case_07: priya.raman@gmail.com, requested 2026-08-31
        pred_status, pred_steps = self.engine.audit_case(req)
        # evidence_46 was captured 2026-02-13, should not appear in findings
        cited_findings = [s['evidence_id'] for s in pred_steps if s['phase'] == 'FINDING']
        self.assertNotIn('evidence_46', cited_findings)

    def test_step_sequence_and_numbering(self):
        """Verify consecutive 1-indexed numbering and monotonic phase ordering."""
        phase_map = {'FINDING': 1, 'REMEDIATION': 2, 'VERIFICATION': 3}
        for req in self.sample_reqs:
            _, steps = self.engine.audit_case(req)
            last_phase_rank = 0
            for i, s in enumerate(steps, start=1):
                self.assertEqual(s['step_no'], i)
                curr_rank = phase_map[s['phase']]
                self.assertGreaterEqual(curr_rank, last_phase_rank)
                last_phase_rank = curr_rank

    def test_allowed_operations(self):
        """Verify every step operation is strictly one of the 15 allowed operations."""
        allowed_ops = {
            'REPORT_REMAINING_RECORD', 'REPORT_EXPOSED_PII', 'REPORT_ACTIVE_DATA_FLOW', 'REPORT_RESTORE_RISK',
            'DISABLE_DATA_FLOW', 'BLOCK_RESTORE', 'DELETE_RECORD', 'REDACT_RECORD', 'ANONYMIZE_RECORD',
            'VERIFY_RECORD_ABSENT', 'VERIFY_RECORD_PRESENT', 'VERIFY_RECORD_REDACTED', 'VERIFY_RECORD_ANONYMIZED',
            'VERIFY_DATA_FLOW_DISABLED', 'VERIFY_RESTORE_BLOCKED'
        }
        for req in self.sample_reqs:
            _, steps = self.engine.audit_case(req)
            for s in steps:
                self.assertIn(s['operation'], allowed_ops)

if __name__ == '__main__':
    unittest.main()
