from pathlib import Path

from ctmkit.promote.promoter import promote


def test_promote_transforms_then_deploys(tmp_path):
    src = tmp_path / "folders"
    src.mkdir()
    (src / "D0225_F.json").write_text('{"STG#D0225_F": {"Type": "Folder"}}')
    desc = tmp_path / "from-development.json"
    desc.write_text('{"DeployDescriptor": []}')
    transformed, deployed = [], []

    def fake_transform(path: Path, descriptor: Path) -> str:
        transformed.append(path.name)
        return '{"STG#D0225_F": {"Type": "Folder"}}'

    def fake_deploy_text(text: str, name: str) -> None:
        deployed.append(name)

    report = promote(src, descriptor=desc, transform_fn=fake_transform,
                     deploy_text_fn=fake_deploy_text)
    assert transformed == ["D0225_F.json"]
    assert deployed == ["D0225_F.json"]
    assert report.ok
