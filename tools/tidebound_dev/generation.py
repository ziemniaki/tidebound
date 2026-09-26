"""Stage generated outputs, then publish changes with rollback on I/O failure."""

from contextlib import contextmanager
from pathlib import Path
import os
import shutil
import tempfile

from .files import equivalent


def publish(root, stage, outputs):
    """Replace changed files only; restore originals if publication raises.

    This is rollback for ordinary I/O errors, not crash-atomic multi-file storage.
    A killed process requires a successful rebuild before playing. If rollback
    itself fails, retain the recovery directory and report its path.
    """
    changes = []
    for directory in outputs:
        for source in sorted((stage / directory).rglob("*")):
            if not source.is_file():
                continue
            relative = source.relative_to(stage)
            target = root / relative
            if target.is_file() and equivalent(target, source):
                continue
            changes.append((relative, source, target))
    if not changes:
        return
    recovery = Path(tempfile.mkdtemp(prefix=".tidebound-publish-", dir=root.parent))
    applied = []
    keep_recovery = False
    try:
        # Prepare all replacement files and backups before changing a live file.
        for relative, source, target in changes:
            prepared = recovery / "new" / relative
            prepared.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, prepared)
            if target.exists():
                backup = recovery / "old" / relative
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
        for relative, source, target in changes:
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(recovery / "new" / relative, target)
            applied.append((relative, target))
    except BaseException:
        failures = []
        for relative, target in reversed(applied):
            try:
                backup = recovery / "old" / relative
                if backup.exists():
                    os.replace(backup, target)
                else:
                    target.unlink()
            except OSError as error:
                failures.append(f"{relative}: {error}")
        if failures:
            keep_recovery = True
            raise RuntimeError(
                f"Publication and rollback failed; recovery files remain at {recovery}: "
                + "; ".join(failures)
            )
        raise
    finally:
        if not keep_recovery:
            shutil.rmtree(recovery)


@contextmanager
def staged_outputs(root, *, inputs, outputs):
    """Give a generator only copied inputs; publish only its output directories."""
    root = Path(root).resolve()
    with tempfile.TemporaryDirectory(prefix="tidebound-generate-") as temp:
        stage = Path(temp)
        for directory in inputs:
            source = root / directory
            if source.is_dir():
                shutil.copytree(source, stage / directory)
            elif source.is_file():
                target = stage / directory
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        for directory in outputs:
            (stage / directory).mkdir(parents=True, exist_ok=True)
        yield stage
        publish(root, stage, outputs)
