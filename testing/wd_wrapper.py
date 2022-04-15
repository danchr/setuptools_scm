import itertools
from pathlib import Path
from typing import List


class WorkDir:
    """a simple model for a"""

    commit_command: str
    signed_commit_command: str
    add_command: str

    def __repr__(self):
        return f"<WD {self.cwd}>"

    def __init__(self, cwd: Path) -> None:
        self.cwd = cwd
        self.__counter = itertools.count()

    def __call__(self, cmd: "List[str] | str", **kw):
        if kw:
            assert isinstance(cmd, str), "formatting the command requires text input"
            cmd = cmd.format(**kw)
        from setuptools_scm.utils import do

        return do(cmd, self.cwd)

    def write(self, name: str, value: "str | bytes", **kw: object) -> Path:
        filename = self.cwd / name
        if kw:
            assert isinstance(value, str)
            value = value.format(**kw)
        if isinstance(value, bytes):
            filename.write_bytes(value)
        else:
            filename.write_text(value)
        return filename

    def _reason(self, given_reason: "str | None") -> str:
        if given_reason is None:
            return f"number-{next(self.__counter)}"
        else:
            return given_reason

    def add_and_commit(self, reason: "str | None" = None, **kwargs):
        self(self.add_command)
        self.commit(reason, **kwargs)

    def commit(self, reason: "str | None" = None, signed: bool = False) -> None:
        reason = self._reason(reason)
        self(
            self.commit_command if not signed else self.signed_commit_command,
            reason=reason,
        )

    def commit_testfile(self, reason: "str | None" = None, signed: bool = False):
        reason = self._reason(reason)
        self.write("test.txt", "test {reason}", reason=reason)
        self(self.add_command)
        self.commit(reason=reason, signed=signed)

    def get_version(self, **kw):
        __tracebackhide__ = True
        from setuptools_scm import get_version

        version = get_version(root=str(self.cwd), fallback_root=str(self.cwd), **kw)
        print(version)
        return version

    @property
    def version(self):
        __tracebackhide__ = True
        return self.get_version()
