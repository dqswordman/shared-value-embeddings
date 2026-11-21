"""Stage the scientific mirror and interactive browser explorer; publish with --publish."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
NAME = "shared-value-embeddings"
HUB = "DQSWORDMAN/" + NAME
GITHUB = "https://github.com/dqswordman/" + NAME
TAG = "v1.0.0"
ASSET = NAME + "-v1.0.0.zip"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def online(url, limit):
    with urlopen(Request(url,headers={"User-Agent":"research-report-publisher"}),timeout=60) as response:
        data = response.read(limit+1)
    if len(data)>limit:
        raise ValueError("Remote file exceeds its allowed size")
    return data


def dump(path, obj):
    path.write_bytes((json.dumps(obj,ensure_ascii=False,indent=2)+"\n").encode())


def prepare(dest, local_zip):
    dest.mkdir(parents=True,exist_ok=True)
    if any(dest.iterdir()):
        raise ValueError("Choose an empty staging folder")
    head = git("rev-parse","HEAD").decode().strip()
    frozen = git("rev-parse",TAG+"^{commit}").decode().strip()
    with ZipFile(io.BytesIO(git("archive","--format=zip",head))) as archive:
        for entry in archive.infolist():
            src = entry.filename
            if entry.is_dir() or src.startswith("."):
                continue
            name = src.removeprefix("space/") if src.startswith("space/") else "GITHUB_README.md" if src=="README.md" else src
            path = dest/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(archive.read(entry))
    if local_zip:
        if local_zip.stat().st_size>100_000_000:
            raise ValueError("ZIP exceeds publication limit")
        blob = local_zip.read_bytes()
    else:
        release = json.loads(online("https://api.github.com/repos/dqswordman/"+NAME+"/releases/tags/v1.0.0",1_000_000))
        asset = next(a for a in release["assets"] if a["name"]==ASSET)
        blob = online(asset["browser_download_url"],100_000_000)
        if len(blob)!=asset["size"] or "sha256:"+digest(blob)!=asset["digest"]:
            raise ValueError("Download differs from GitHub release asset")
    with ZipFile(io.BytesIO(blob)) as z:
        prefix = ASSET[:-4]+"/"
        manifest = json.loads(z.read(prefix+"MANIFEST.json"))
        frozen_manifest = git("show", frozen+":MANIFEST.json")
        if z.testzip() or z.read(prefix+"MANIFEST.json") != frozen_manifest:
            raise ValueError("Unexpected release archive")
        expected = {prefix+row["path"]:row["sha256"] for row in manifest["files"]}
        names = {name for name in z.namelist() if not name.endswith("/")}
        if names != set(expected) | {prefix+"MANIFEST.json"}:
            raise ValueError("Release contents differ from the tagged manifest")
        if any(digest(z.read(name)) != checksum for name,checksum in expected.items()):
            raise ValueError("Release file checksum mismatch")
    (dest/ASSET).write_bytes(blob)
    if not json.loads((dest/"evidence.json").read_text(encoding="utf-8")):
        raise ValueError("The public explorer needs a measured record")
    manifest_path = dest / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["distribution"] = "Hugging Face static Space"
    manifest["files"] = []
    files = {}
    for path in sorted(dest.rglob("*")):
        if not path.is_file() or path == manifest_path:
            continue
        name = path.relative_to(dest).as_posix()
        checksum = digest(path.read_bytes())
        manifest["files"].append({"path": name, "size_bytes": path.stat().st_size, "sha256": checksum})
        files[name] = checksum
    dump(manifest_path, manifest)
    files["MANIFEST.json"] = digest(manifest_path.read_bytes())
    dump(dest/"SNAPSHOT.json",{"github_commit":head,"github_repository":GITHUB,"frozen_release":{
        "name":ASSET,"bytes":len(blob),"sha256":digest(blob),"scientific_commit":frozen},"sha256":files})
    return head


def publish(dest, head):
    from huggingface_hub import HfApi
    api = HfApi()
    if git("ls-remote","--heads",GITHUB+".git","refs/heads/main").decode().split()[0]!=head:
        raise ValueError("GitHub main changed; reload before publishing")
    previous = api.space_info(HUB)
    if previous.private or previous.sdk!="static":
        raise ValueError("Expected the designated public static Space")
    commit = api.upload_folder(repo_type="space",repo_id=HUB,folder_path=dest,parent_commit=previous.sha,
                               commit_message=f"Mirror GitHub {head[:12]}",delete_patterns=["*","**/*"],
                               ignore_patterns=[".gitattributes"])
    base = f"https://huggingface.co/spaces/{HUB}/resolve/{commit.oid}/"
    for name in ("SNAPSHOT.json","evidence.json","index.html",ASSET):
        expected = (dest/name).read_bytes()
        if online(base+name,len(expected))!=expected:
            raise ValueError("Published file differs: "+name)
    print(commit.commit_url)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination",type=Path)
    parser.add_argument("--zip",type=Path,help="Use a locally verified release ZIP for staging")
    parser.add_argument("--publish",action="store_true")
    args=parser.parse_args()
    revision=prepare(args.destination.resolve(),args.zip)
    if args.publish:
        publish(args.destination.resolve(),revision)
