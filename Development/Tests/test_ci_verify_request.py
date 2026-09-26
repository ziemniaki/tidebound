from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ci_verify_request import requested_sha


class VerifyRequestTests(unittest.TestCase):
    def setUp(self):
        self.event = {'action': 'created', 'comment': {'body': '/verify', 'user': {'login': 'maintainer'}},
                      'issue': {'number': 7, 'pull_request': { 'url': 'unused' }}}
        self.pr = {'state': 'open', 'base': {'repo': {'full_name': 'owner/game'}},
                   'head': {'sha': 'a' * 40}}

    def request(self, call):
        return requested_sha(self.event, 'issue_comment', 'owner/game', 'ignored', call)

    def test_exact_command_only_and_only_on_prs(self):
        for body in ('/verify extra', 'please /verify', '/verify\necho injected'):
            self.event['comment']['body'] = body
            call = Mock()
            self.assertIsNone(self.request(call))
            call.assert_not_called()
        self.event['comment']['body'] = '/verify'
        self.event['issue'].pop('pull_request')
        self.assertIsNone(self.request(Mock()))

    def test_read_only_user_cannot_start_build(self):
        call = Mock(return_value={'permission': 'read'})
        with self.assertRaises(PermissionError):
            self.request(call)
        self.assertEqual(call.call_count, 1)

    def test_request_is_bound_to_current_head_not_default_branch(self):
        call = Mock(side_effect=[{'permission': 'write'}, self.pr])
        self.assertEqual(self.request(call), 'a' * 40)
        self.assertEqual(call.call_args_list[0].args[0], 'repos/owner/game/collaborators/maintainer/permission')
        self.pr['head']['sha'] = 'b' * 40
        self.assertEqual(self.request(Mock(side_effect=[{'permission': 'write'}, self.pr])), 'b' * 40)

    def test_closed_pr_is_rejected(self):
        self.pr['state'] = 'closed'
        with self.assertRaises(ValueError):
            self.request(Mock(side_effect=[{'permission': 'admin'}, self.pr]))

    def test_dispatch_also_checks_permissions(self):
        with self.assertRaises(PermissionError):
            requested_sha({'inputs': {'pr': '7'}}, 'workflow_dispatch', 'owner/game', 'reader',
                          Mock(return_value={'permission': 'read'}))


if __name__ == '__main__':
    unittest.main()
