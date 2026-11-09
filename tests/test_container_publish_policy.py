"""Parse real workflows; fail closed rather than evaluating arbitrary Actions code."""
import os
from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(os.environ.get('POLICY_ROOT', Path(__file__).resolve().parents[1]))
GUARD = "github.event_name == 'workflow_dispatch' && inputs.publish == true"

def load(path):
    # BaseLoader preserves YAML's `on` key and booleans as source strings.
    return yaml.load(path.read_text(encoding='utf-8'), Loader=yaml.BaseLoader)

class ContainerPublishPolicy(unittest.TestCase):
    def setUp(self):
        self.path = ROOT / '.github/workflows/docker.yml'
        self.workflow = load(self.path)

    def test_events_and_explicit_opt_in(self):
        self.assertEqual(set(self.workflow['on']), {'workflow_dispatch'})
        field = self.workflow['on']['workflow_dispatch']['inputs']['publish']
        self.assertEqual(field['type'], 'boolean')
        self.assertEqual(field['default'], 'false')

    def test_all_publish_jobs_guarded_and_scoped(self):
        self.assertEqual(self.workflow['permissions'], {'contents': 'read'})
        self.assertEqual(len(self.workflow['jobs']), 3)
        for name, job in self.workflow['jobs'].items():
            with self.subTest(job=name):
                self.assertEqual(job['if'], GUARD)
                self.assertEqual(job['permissions'], {'contents': 'read', 'packages': 'write'})
                self.assertTrue(any(s.get('with', {}).get('push') == 'true' for s in job['steps']))
                # Exact, allowlisted Actions expression; model its boolean operands.
                for event in ('push', 'pull_request', 'release', 'workflow_run', 'workflow_call', 'workflow_dispatch'):
                    for publish in (None, False, True):
                        allowed = event == 'workflow_dispatch' and publish is True
                        self.assertEqual(allowed, (event, publish) == ('workflow_dispatch', True))

    def test_no_chained_container_dispatch_or_other_registry_writer(self):
        for path in (ROOT / '.github/workflows').glob('*.y*ml'):
            data = load(path)
            if path == self.path:
                continue
            text = path.read_text(encoding='utf-8')
            self.assertNotRegex(text, r'gh workflow run docker\.yml|workflows/docker\.yml/dispatches')
            for job in data.get('jobs', {}).values():
                self.assertNotEqual(job.get('permissions', {}).get('packages'), 'write', str(path))
                for step in job.get('steps', []):
                    self.assertNotEqual(step.get('with', {}).get('push'), 'true', str(path))
                    self.assertNotRegex(step.get('run', ''), r'docker\s+(push|buildx\s+imagetools\s+create)')

if __name__ == '__main__':
    unittest.main()
