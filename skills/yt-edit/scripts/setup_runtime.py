#!/usr/bin/env python3
"""Materialize GSAP in a prepared project. No proprietary dependency is redistributed.

Downloads the pinned npm artifact with SHA-512 integrity verification, or copies
an existing GSAP 3.15.0 file supplied with --gsap-file. Existing files are retained.
"""
import argparse
import base64
import hashlib
import io
import json
import shutil
import tarfile
import urllib.request
from pathlib import Path

VERSION = "3.15.0"


def setup(project, gsap_file=None):
    project = Path(project).resolve()
    if not (project / "project.json").is_file():
        raise ValueError("Run prep.py first")
    target = project / "public/vendor/gsap.min.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if f"GSAP {VERSION}".encode() not in target.read_bytes()[:200]:
            raise ValueError("A different runtime already exists; use a new project")
        print("Pinned GSAP already present")
        return
    if gsap_file:
        data = Path(gsap_file).read_bytes()
        if f"GSAP {VERSION}".encode() not in data[:200]:
            raise ValueError(f"Expected GSAP {VERSION}")
        with target.open("xb") as f:
            f.write(data)
    else:
        with urllib.request.urlopen(f"https://registry.npmjs.org/gsap/{VERSION}", timeout=30) as response:
            metadata = json.load(response)
        dist = metadata["dist"]
        expected = dist["integrity"]
        if not expected.startswith("sha512-"):
            raise ValueError("Expected a SHA-512 npm integrity record")
        with urllib.request.urlopen(dist["tarball"], timeout=60) as response:
            archive = response.read()
        actual = "sha512-" + base64.b64encode(hashlib.sha512(archive).digest()).decode()
        if actual != expected:
            raise ValueError("Dependency checksum mismatch")
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            member = tar.extractfile("package/dist/gsap.min.js")
            if member is None:
                raise ValueError("Runtime missing from dependency")
            data = member.read()
            if f"GSAP {VERSION}".encode() not in data[:200]:
                raise ValueError("Dependency version mismatch")
            with target.open("xb") as f:
                f.write(data)
            for item in tar.getmembers():
                if item.name in ("package/LICENSE", "package/LICENSE.txt", "package/LICENSE.md"):
                    license_file = tar.extractfile(item)
                    if license_file:
                        with (target.parent / "GSAP-LICENSE.txt").open("xb") as f:
                            f.write(license_file.read())
        (target.parent / "dependency-provenance.json").write_text(json.dumps({
            "name":"gsap", "version":VERSION, "tarball":dist["tarball"], "integrity":expected
        }, indent=2) + "\n")
    print("GSAP materialized locally. HyperFrames uses the pinned project launcher on first command.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("project"); p.add_argument("--gsap-file")
    a = p.parse_args(); setup(a.project, a.gsap_file)
