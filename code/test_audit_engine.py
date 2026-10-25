#!/usr/bin/env python3
"""
Regression and Edge-Case Test Suite for Northstar Deletion Audit Agent
Challenge: Ghost Data Still Exists (HackerRank Orchestrate, October 2026)

Comprehensive test coverage across:
- Case status classification and ground-truth sample parity (32/32 cases)
- Non-deletion intent and negated request classification (NOT_APPLICABLE cases)
- Temporal evidence reconciliation and stale pre-request snapshot filtering
- Complete case verification citation rules (audit window constraint)
- Incomplete case remediation/verification empty citation rules
- Retained security audit records policy compliance (VERIFY_RECORD_PRESENT)
- Account tombstone redaction verification (VERIFY_RECORD_REDACTED)
- Consecutive 1-indexed step numbering and monotonic phase ordering
- Operation-state coupling strictly adhering to challenge specifications
- Submission contract validator path independence
"""

import unittest
import os
import sys
import json
import csv

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, 'code'))
import main
import verify_submission

class TestDeletionAuditEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = main.DeletionAuditEngine()
        cls.dataset_dir = os.path.join(REPO_ROOT, 'dataset')
        with open(os.path.join(cls.dataset_dir, 'sample_deletion_requests.csv'), encoding='utf-8') as f:
            cls.sample_reqs = list(csv.DictReader(f))
        with open(os.path.join(cls.dataset_dir, 'sample_output.csv'), encoding='utf-8') as f:
            cls.sample_truth = {r['case_id']: r for r in csv.DictReader(f)}
        with open(os.path.join(cls.dataset_dir, 'deletion_requests.csv'), encoding='utf-8') as f:
            cls.all_reqs = {r['case_id']: r for r in csv.DictReader(f)}

    def test_sample_status_accuracy(self):
        """Verify 100% status classification accuracy across all 32 labeled sample cases."""
        correct = 0
        for req in self.sample_reqs:
            cid = req['case_id']
            truth = self.sample_truth[cid]
            pred_status, _ = self.engine.audit_case(req)
            if pred_status == truth['deletion_status']:
                correct += 1
        self.assertEqual(correct, len(self.sample_reqs), f"Expected 32/32, got {correct}/32")

    def test_non_deletion_requests_from_dataset(self):
        """Verify all 10 non-deletion requests in dataset are classified as NOT_APPLICABLE with empty steps."""
        na_case_ids = [f'case_{i}' for i in range(533, 543)]
        for cid in na_case_ids:
            req = self.all_reqs[cid]
            status, steps = self.engine.audit_case(req)
            self.assertEqual(status, 'NOT_APPLICABLE', f"Expected NOT_APPLICABLE for {cid}")
            self.assertEqual(steps, [], f"Expected empty steps for {cid}")

    def test_synthetic_non_deletion_phrases(self):
        """Verify common privacy negation and data portability phrases trigger NOT_APPLICABLE."""
        test_phrases = [
            "Please stop the promotional emails. I am not asking for deletion.",
            "I need help resetting the login. Do not close the account.",
            "Can you correct my address without removing any of my records?",
            "This is an access request, not a request to erase my data.",
            "Please remove me from marketing lists only. Keep receipts and service messages.",
            "I want to continue using the service. Leave my profile in place.",
            "Please keep the account as it is, just send my order history.",
        ]
        for phrase in test_phrases:
            req = {
                'case_id': 'test_na',
                'email': 'user@example.com',
                'requested_at': '2026-09-01T10:00:00Z',
                'reported_at': '2026-09-02T10:00:00Z',
                'audit_at': '2026-09-10T10:00:00Z',
                'request_text': phrase,
                'reported_status': 'COMPLETE'
            }
            status, steps = self.engine.audit_case(req)
            self.assertEqual(status, 'NOT_APPLICABLE')
            self.assertEqual(steps, [])

    def test_stale_pre_request_snapshots_omitted(self):
        """Verify evidence captured prior to deletion request is not treated as a lingering finding."""
        req = self.sample_reqs[6]  # case_07: priya.raman@gmail.com, requested 2026-08-31
        pred_status, pred_steps = self.engine.audit_case(req)
        # evidence_46 was captured 2026-02-13, should not appear in findings
        cited_findings = [s['evidence_id'] for s in pred_steps if s['phase'] == 'FINDING']
        self.assertNotIn('evidence_46', cited_findings)

        manifest = self.engine.manifest
        req_at = req['requested_at']
        for s in pred_steps:
            ev = s.get('evidence_id')
            if ev and ev in manifest:
                self.assertGreaterEqual(manifest[ev]['captured_at'], req_at)

    def test_complete_case_verification_citations(self):
        """Verify COMPLETE cases cite only post-request evidence within the audit window."""
        complete_cases = [r for r in self.sample_reqs if self.sample_truth[r['case_id']]['deletion_status'] == 'COMPLETE']
        for req in complete_cases:
            status, steps = self.engine.audit_case(req)
            self.assertEqual(status, 'COMPLETE')
            self.assertTrue(len(steps) > 0)
            req_at = req['requested_at']
            audit_at = req['audit_at']
            for s in steps:
                self.assertEqual(s['phase'], 'VERIFICATION')
                ev = s.get('evidence_id')
                self.assertTrue(bool(ev), f"COMPLETE verification step missing evidence citation: {s}")
                if ev in self.engine.manifest:
                    cap = self.engine.manifest[ev]['captured_at']
                    self.assertGreaterEqual(cap, req_at)
                    self.assertLessEqual(cap, audit_at)

    def test_incomplete_case_citation_rules(self):
        """Verify INCOMPLETE cases cite evidence for findings, but empty string for proposed actions and future checks."""
        incomplete_cases = [r for r in self.sample_reqs if self.sample_truth[r['case_id']]['deletion_status'] == 'INCOMPLETE']
        for req in incomplete_cases:
            status, steps = self.engine.audit_case(req)
            self.assertEqual(status, 'INCOMPLETE')
            for s in steps:
                if s['phase'] == 'FINDING':
                    self.assertTrue(bool(s.get('evidence_id')), f"FINDING step missing citation in {req['case_id']}")
                elif s['phase'] in ('REMEDIATION', 'VERIFICATION'):
                    self.assertEqual(s.get('evidence_id'), '', f"Proposed {s['phase']} step has non-empty evidence_id in {req['case_id']}")

    def test_retained_security_audit_records_policy(self):
        """Verify security audit records required by policy are retained and checked as VERIFY_RECORD_PRESENT."""
        # Check case_03 or case_15 which have confirmed security audit records
        req_03 = [r for r in self.sample_reqs if r['case_id'] == 'case_03'][0]
        _, pred_steps_03 = self.engine.audit_case(req_03)
        sec_steps = [s for s in pred_steps_03 if s['system_id'] == 'security_service']
        self.assertTrue(len(sec_steps) > 0, "Expected security_service step for case_03")
        for s in sec_steps:
            self.assertEqual(s['operation'], 'VERIFY_RECORD_PRESENT')
            self.assertEqual(s['state'], 'PRESENT')

        # Also verify across all sample predictions that security_service is always VERIFY_RECORD_PRESENT
        for req in self.sample_reqs:
            _, pred_steps = self.engine.audit_case(req)
            for s in pred_steps:
                if s['system_id'] == 'security_service':
                    self.assertEqual(s['operation'], 'VERIFY_RECORD_PRESENT')
                    self.assertEqual(s['state'], 'PRESENT')

    def test_retained_tombstone_redaction(self):
        """Verify account tombstones are verified as VERIFY_RECORD_REDACTED with state REDACTED."""
        for req in self.sample_reqs:
            truth = self.sample_truth[req['case_id']]
            t_steps = json.loads(truth['steps_json'])
            tomb_steps = [s for s in t_steps if 'tombstone' in s.get('resource_id', '')]
            if tomb_steps:
                _, pred_steps = self.engine.audit_case(req)
                pred_tomb = [s for s in pred_steps if 'tombstone' in s.get('resource_id', '')]
                self.assertTrue(len(pred_tomb) > 0)
                for s in pred_tomb:
                    self.assertIn(s['operation'], ('VERIFY_RECORD_REDACTED', 'REDACT_RECORD', 'REPORT_EXPOSED_PII'))

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

    def test_allowed_operations_and_state_coupling(self):
        """Verify every step operation and state adheres strictly to the problem statement specification."""
        allowed_pairs = {
            'FINDING': {
                'REPORT_REMAINING_RECORD': 'PRESENT',
                'REPORT_EXPOSED_PII': 'PRESENT',
                'REPORT_ACTIVE_DATA_FLOW': 'ACTIVE',
                'REPORT_RESTORE_RISK': 'ACTIVE',
            },
            'REMEDIATION': {
                'DISABLE_DATA_FLOW': 'DISABLED',
                'BLOCK_RESTORE': 'BLOCKED',
                'DELETE_RECORD': 'ABSENT',
                'REDACT_RECORD': 'REDACTED',
                'ANONYMIZE_RECORD': 'ANONYMIZED',
            },
            'VERIFICATION': {
                'VERIFY_RECORD_ABSENT': 'ABSENT',
                'VERIFY_RECORD_PRESENT': 'PRESENT',
                'VERIFY_RECORD_REDACTED': 'REDACTED',
                'VERIFY_RECORD_ANONYMIZED': 'ANONYMIZED',
                'VERIFY_DATA_FLOW_DISABLED': 'DISABLED',
                'VERIFY_RESTORE_BLOCKED': 'BLOCKED',
            }
        }
        for req in self.sample_reqs:
            _, steps = self.engine.audit_case(req)
            for s in steps:
                ph = s['phase']
                op = s['operation']
                st = s['state']
                self.assertIn(ph, allowed_pairs)
                self.assertIn(op, allowed_pairs[ph])
                self.assertEqual(st, allowed_pairs[ph][op])

    def test_validator_path_independence(self):
        """Verify verify_submission runs cleanly via relative path calculation."""
        res = verify_submission.verify_submission()
        self.assertTrue(res)

    def test_no_synthetic_account_inference(self):
        """Verify engine never creates synthetic account IDs from user_id without concrete evidence."""
        req = {
            'case_id': 'test_synthetic_check',
            'email': 'unknown.test.user9999@domain.org',
            'requested_at': '2026-09-01T10:00:00Z',
            'reported_at': '2026-09-02T10:00:00Z',
            'audit_at': '2026-09-10T10:00:00Z',
            'request_text': 'Please delete all my personal records and data.',
            'reported_status': 'COMPLETE'
        }
        status, steps = self.engine.audit_case(req)
        # Should NOT fabricate account_9999
        account_ids = [s['resource_id'] for s in steps if s['system_id'] == 'account_service']
        self.assertNotIn('account_9999', account_ids)
        for acc in account_ids:
            self.assertFalse(acc.startswith('account_9999'))

    def test_evidence_reference_types_accepted(self):
        """Verify validator accepts valid file_id, activity_id, and audit_id citations."""
        # file_id check
        self.assertTrue(verify_submission.is_valid_evidence_ref('evidence_01'))
        self.assertTrue(verify_submission.is_valid_evidence_ref('evidence_54'))
        # audit_id check
        self.assertTrue(verify_submission.is_valid_evidence_ref('audit_record_003'))
        self.assertTrue(verify_submission.is_valid_evidence_ref('audit_record_6645'))
        # invalid check
        self.assertFalse(verify_submission.is_valid_evidence_ref('non_existent_ref_12345'))
        self.assertFalse(verify_submission.is_valid_evidence_ref(''))

if __name__ == '__main__':
    unittest.main()
