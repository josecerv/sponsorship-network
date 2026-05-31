"""Diagnostic for PowerPoint repair warnings on the current deck."""
import os
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

PROJECT = Path(__file__).resolve().parent.parent.parent
DECK = PROJECT / "docs" / "UChicago-0410.pptx"

NSMAP = {
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def main():
    print(f"Diagnosing {DECK}")
    with zipfile.ZipFile(str(DECK)) as z:
        # 1. XML parse check
        print("\n[1] XML parse check")
        bad = 0
        for name in z.namelist():
            if name.endswith(".xml") or name.endswith(".rels"):
                try:
                    ET.fromstring(z.read(name))
                except ET.ParseError as e:
                    print(f"  PARSE ERROR: {name}: {e}")
                    bad += 1
        print(f"  {bad} parse errors")

        # 2. Relationship validation — every Target in every .rels file
        #    must resolve to an existing file in the zip (or be external).
        print("\n[2] Relationship target resolution")
        all_files = set(z.namelist())
        missing = 0
        for rel_name in sorted(z.namelist()):
            if not rel_name.endswith(".rels"):
                continue
            data = z.read(rel_name)
            try:
                root = ET.fromstring(data)
            except ET.ParseError:
                continue

            # The "part" whose rels this is — strip "/_rels/" + ".rels"
            # e.g. "ppt/slides/_rels/slide3.xml.rels" -> part is "ppt/slides/slide3.xml"
            base_dir = os.path.dirname(rel_name)
            if base_dir.endswith("/_rels"):
                # The rels file is for a part — its part lives one dir up
                part_dir = base_dir[: -len("/_rels")]
            else:
                part_dir = base_dir

            for rel in root.findall("rel:Relationship", NSMAP):
                target = rel.get("Target", "")
                target_mode = rel.get("TargetMode", "Internal")
                rtype = rel.get("Type", "")
                if target_mode == "External":
                    continue
                if target.startswith(("http://", "https://")):
                    continue
                # Resolve relative to part_dir
                # Targets like "../media/image1.png" or "slide1.xml"
                resolved = os.path.normpath(os.path.join(part_dir, target))
                resolved = resolved.replace(os.sep, "/").lstrip("/")
                if resolved not in all_files:
                    print(
                        f"  MISSING: {rel_name}\n"
                        f"    -> target={target!r} resolved={resolved!r}\n"
                        f"       type={rtype}"
                    )
                    missing += 1
        print(f"  {missing} unresolved relationships")

        # 3. Content types — every part in the zip (except .rels) should
        #    be declared in [Content_Types].xml
        print("\n[3] Content types registration")
        ct_xml = z.read("[Content_Types].xml").decode()
        ct_root = ET.fromstring(ct_xml)
        ns_ct = {"ct": "http://schemas.openxmlformats.org/package/2006/content-types"}
        defaults = {d.get("Extension"): d.get("ContentType")
                    for d in ct_root.findall("ct:Default", ns_ct)}
        overrides = {o.get("PartName"): o.get("ContentType")
                     for o in ct_root.findall("ct:Override", ns_ct)}
        print(f"  defaults: {list(defaults.keys())}")
        print(f"  overrides: {len(overrides)}")

        # Look for parts that exist but have no content-type override/default
        unreg = 0
        for name in sorted(z.namelist()):
            if name.endswith(".rels") or name == "[Content_Types].xml":
                continue
            part = "/" + name
            if part in overrides:
                continue
            ext = name.rsplit(".", 1)[-1] if "." in name else ""
            if ext in defaults:
                continue
            print(f"  UNREGISTERED: {name}")
            unreg += 1
        print(f"  {unreg} unregistered parts")

        # 4. Slides listed in presentation.xml's sldIdLst — every rId
        #    must resolve to an existing slide part
        print("\n[4] sldIdLst rId resolution")
        pres_rels = z.read("ppt/_rels/presentation.xml.rels").decode()
        pres_rels_root = ET.fromstring(pres_rels)
        rid_to_target = {
            r.get("Id"): r.get("Target")
            for r in pres_rels_root.findall("rel:Relationship", NSMAP)
        }
        pres_xml = z.read("ppt/presentation.xml").decode()
        # Extract all sldId @r:id values
        sld_ids = re.findall(
            r'<p:sldId[^/]*r:id="([^"]+)"', pres_xml
        )
        missing_rid = 0
        for rid in sld_ids:
            if rid not in rid_to_target:
                print(f"  MISSING rId {rid} in presentation.xml.rels")
                missing_rid += 1
                continue
            target = rid_to_target[rid]
            resolved = os.path.normpath(os.path.join("ppt", target))
            resolved = resolved.replace(os.sep, "/")
            if resolved not in all_files:
                print(f"  rId {rid} -> {target} resolved to missing file: {resolved}")
                missing_rid += 1
        print(f"  {missing_rid} sldIdLst issues ({len(sld_ids)} sldIds total)")

        # 5. Look for each new hook slide's raw XML
        print("\n[5] Hook slide raw XML size")
        for i in range(1, 6):
            name = f"ppt/slides/slide{i}.xml"
            if name in all_files:
                print(f"  {name}: {len(z.read(name))} bytes")


if __name__ == "__main__":
    main()
