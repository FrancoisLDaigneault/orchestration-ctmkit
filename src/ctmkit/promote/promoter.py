"""Promote (or retrofit) a set of definition files through a deploy descriptor."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

TransformFn = Callable[[Path, Path], str]
DeployTextFn = Callable[[str, str], None]


@dataclass
class PromoteReport:
    """Outcome of a promotion.

    Attributes:
        promoted: File names that were transformed + deployed.
        ok: True when every file promoted without error.
    """

    promoted: list[str] = field(default_factory=list)
    ok: bool = True


def promote(src_dir: Path, *, descriptor: Path, transform_fn: TransformFn,
            deploy_text_fn: DeployTextFn) -> PromoteReport:
    """Transform each source file with ``descriptor`` then deploy the result.

    Args:
        src_dir: Directory of source definition files (``*.json``).
        descriptor: Deploy-descriptor file applied to every source file.
        transform_fn: Callable ``(path, descriptor) -> transformed_json_text``.
        deploy_text_fn: Callable ``(transformed_text, file_name) -> None``.

    Returns:
        A :class:`PromoteReport`.
    """
    report = PromoteReport()
    for path in sorted(Path(src_dir).glob("*.json")):
        text = transform_fn(path, descriptor)
        deploy_text_fn(text, path.name)
        report.promoted.append(path.name)
    return report
