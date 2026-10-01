#!/usr/bin/env python3
"""Exercise the release workflow against disposable local Git remotes."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/bump-version.yml"


def publication_script():
    lines = WORKFLOW.read_text().splitlines()
    start = lines.index("      - name: Publish version and v1 alias atomically")
    run = lines.index("        run: |", start) + 1
    script = []
    for line in lines[run:]:
        if line and not line.startswith("          "):
            break
        script.append(line[10:])
    return "\n".join(script)


class ReleaseTags(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="academic-tag-contract-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote.git"
        self.work = self.root / "work"
        self.git("init", "--bare", str(self.remote), cwd=self.root)
        self.git("init", str(self.work), cwd=self.root)
        self.git("config", "core.hooksPath", os.devnull)
        self.git("--git-dir", str(self.remote), "config", "core.hooksPath", os.devnull)
        self.git("config", "user.name", "Release contract test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("remote", "add", "origin", str(self.remote))
        self.git("commit", "--allow-empty", "-m", "old")
        self.old = self.git("rev-parse", "HEAD")
        self.git("commit", "--allow-empty", "-m", "release")
        self.new = self.git("rev-parse", "HEAD")
        self.git("commit", "--allow-empty", "-m", "other writer")
        self.other = self.git("rev-parse", "HEAD")
        self.git("checkout", "--detach", self.new)
        self.git("push", "origin", f"{self.other}:refs/heads/fixture")

    def git(self, *args, cwd=None):
        result = subprocess.run(
            ["git", *args], cwd=cwd or self.work, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
        )
        return result.stdout.strip()

    def set_remote(self, ref, oid):
        self.git("--git-dir", str(self.remote), "update-ref", ref, oid)

    def refs(self):
        output = self.git("--git-dir", str(self.remote), "for-each-ref",
                          "--format=%(refname) %(objectname)", "refs/tags")
        return dict(line.split() for line in output.splitlines())

    def publish(self, expected):
        env = dict(os.environ, NEW_TAG="v1.1.14", EXPECTED_V1=expected)
        return subprocess.run(["bash", "-c", publication_script()], cwd=self.work,
                              env=env, text=True, capture_output=True)

    def assert_rejected_unchanged(self, expected):
        before = self.refs()
        result = self.publish(expected)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.refs(), before)

    def test_existing_alias_moves_with_new_version(self):
        self.set_remote("refs/tags/v1", self.old)
        self.assertEqual(self.publish(self.old).returncode, 0)
        self.assertEqual(self.refs(), {"refs/tags/v1": self.new,
                                      "refs/tags/v1.1.14": self.new})

    def test_first_release_creates_both_refs(self):
        self.assertEqual(self.publish("").returncode, 0)
        self.assertEqual(self.refs(), {"refs/tags/v1": self.new,
                                      "refs/tags/v1.1.14": self.new})

    def test_alias_race_creates_no_partial_version(self):
        self.set_remote("refs/tags/v1", self.other)
        self.assert_rejected_unchanged(self.old)

    def test_version_collision_leaves_alias_unchanged(self):
        self.set_remote("refs/tags/v1", self.old)
        self.set_remote("refs/tags/v1.1.14", self.other)
        self.assert_rejected_unchanged(self.old)

    def test_identical_version_remains_immutable_on_retry(self):
        self.set_remote("refs/tags/v1", self.old)
        self.set_remote("refs/tags/v1.1.14", self.new)
        self.assertEqual(self.publish(self.old).returncode, 0)
        self.assertEqual(self.refs(), {"refs/tags/v1": self.new,
                                      "refs/tags/v1.1.14": self.new})

    def test_annotated_alias_uses_tag_object_lease(self):
        self.git("tag", "-a", "v1", self.old, "-m", "old alias")
        tag_object = self.git("rev-parse", "refs/tags/v1")
        self.git("push", "origin", "refs/tags/v1")
        self.assertEqual(self.publish(tag_object).returncode, 0)
        self.assertEqual(self.refs()["refs/tags/v1"], self.new)

    def test_remote_without_atomic_support_preserves_both_refs(self):
        self.set_remote("refs/tags/v1", self.old)
        self.git("--git-dir", str(self.remote), "config", "receive.advertiseAtomic", "false")
        self.assert_rejected_unchanged(self.old)


if __name__ == "__main__":
    unittest.main()
