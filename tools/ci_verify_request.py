"""Authorize full verification and report on its immutable PR commit.

Run only from a trusted workflow checkout. Build jobs receive a separate,
read-only token; no PR-controlled code runs in these status-writing jobs.
"""
from pathlib import Path
import json
import os
import re
import subprocess
import sys
from urllib.parse import quote


def api(endpoint, data=None):
    args = ['gh', 'api', '--method', 'GET' if data is None else 'POST', endpoint]
    if data is not None:
        args += ['--input', '-']
    return json.loads(subprocess.check_output(
        args, input=None if data is None else json.dumps(data), text=True))


def requested_sha(event, event_name, repo, actor, call=api):
    if event_name == 'issue_comment':
        if (event.get('action') != 'created' or
                event.get('comment', {}).get('body') != '/verify' or
                not event.get('issue', {}).get('pull_request')):
            return None
        number = event['issue']['number']
        actor = event['comment']['user']['login']
    elif event_name == 'workflow_dispatch':
        number = event.get('inputs', {}).get('pr', '')
    else:
        raise ValueError('Unsupported request event')
    if not re.fullmatch(r'[1-9][0-9]*', str(number)):
        raise ValueError('Expected a positive PR number')
    permission = call(f'repos/{repo}/collaborators/{quote(actor, safe="")}/permission')
    if permission.get('permission') not in ('admin', 'maintain', 'write'):
        raise PermissionError('Full verification requires repository write permission')
    pr = call(f'repos/{repo}/pulls/{number}')
    if pr['state'] != 'open' or pr['base']['repo']['full_name'] != repo:
        raise ValueError('Expected an open pull request in this repository')
    sha = pr['head']['sha']
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Invalid PR commit')
    return sha


def post_status(repo, sha, state, description):
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Invalid status commit')
    url = f"{os.environ['GITHUB_SERVER_URL']}/{repo}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    api(f'repos/{repo}/statuses/{sha}', {
        'state': state, 'context': 'Full verification',
        'description': description, 'target_url': url})


def main(mode):
    repo = os.environ['GITHUB_REPOSITORY']
    if mode == 'request':
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
        sha = requested_sha(event, os.environ['GITHUB_EVENT_NAME'], repo, os.environ['GITHUB_ACTOR'])
        if sha is None:
            return
        post_status(repo, sha, 'pending', 'Full build and native tests requested')
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
            output.write(f'sha={sha}\n')
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
            summary.write(f'Full verification requested for `{sha}`.\n')
    elif mode == 'report':
        result = os.environ['VERIFY_RESULT']
        state = 'success' if result == 'success' else 'failure'
        post_status(repo, os.environ['VERIFIED_SHA'], state, f'Full verification: {result}')
    else:
        raise ValueError('Expected request or report')


if __name__ == '__main__':
    main(sys.argv[1])
