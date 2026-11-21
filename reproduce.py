"""Rebuild the two-encoder panel and the paired Qwen transfer result on CPU."""
import argparse
import csv
import json
import lzma
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"code"))
from csv_codec import decode_row, schema

def rows(path):
    opener = lzma.open if path.suffix == ".xz" else open
    with opener(path,"rt",encoding="utf-8-sig",newline="") as stream:
        yield from csv.DictReader(stream)

def main(output):
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Choose an empty output directory")
    primary = {"STAR23","CYCLE23"}
    sums = defaultdict(lambda: np.zeros(4))
    seen = set()
    all_units = 0
    for row in rows(ROOT/"data/units.csv.xz"):
        all_units += 1
        if row["method"] not in primary or row["split"] != "TEST":
            continue
        key=(row["model"],row["renderer"],row["method"],row["world_id"])
        assert row["valid"] == "True" and (key,row["condition"]) not in seen
        seen.add((key,row["condition"]))
        r=decode_row(row, schema("unit_results.csv"), {"R22"})
        sums[key] += [float(r["NMSE"]),float(r["R22"]),float(r["Q2_balanced"]),1]
    ref={(r["model"],r["renderer"],r["method"],r["world_id"]):r for r in rows(ROOT/"data/world_summary.csv.xz") if r["method"] in primary and r["split"]=="TEST"}
    assert set(sums)==set(ref) and len(sums)==2*2*2*2048
    cells=defaultdict(list)
    for (model,render,method,world), (nmse,r22,q,count) in sums.items():
        assert count==6
        observed=np.array([nmse,r22,q])/count
        saved=ref[model,render,method,world]
        np.testing.assert_allclose(observed[[0,2]], [float(saved["NMSE"]),float(saved["Q2_balanced"])],rtol=0,atol=1e-12)
        cells[model,render,method].append(observed)
    panel={}
    levels={k:np.mean(v,axis=0) for k,v in cells.items()}
    for row in rows(ROOT/"reference/primary_contrasts.csv"):
        model,render=row["model"],row["renderer"]
        star,cycle=levels[model,render,"STAR23"],levels[model,render,"CYCLE23"]
        index=0 if row["metric"]=="NMSE" else 2
        signed=(star[index]-cycle[index])*int(row["contrast_sign"])
        assert math.isclose(signed,float(row["estimate"]),abs_tol=1e-11)
        panel[model+"/"+render]=dict(worlds=2048,star=star.tolist(),cycle=cycle.tolist())
    audit=list(rows(ROOT/"data/qwen/paired_world_audit.csv.xz"))
    assert len(audit)==len({r["world_id"] for r in audit})==512
    s=np.array([float(r["STAR23_NMSE"]) for r in audit]);c=np.array([float(r["CYCLE23_NMSE"]) for r in audit])
    idx=np.random.default_rng(2026111006).integers(0,len(s),(10000,len(s)),dtype=np.int64)
    estimate=float(1-s.mean()/c.mean()); low,high=np.quantile(1-s[idx].mean(axis=1)/c[idx].mean(axis=1),[.025,.975])
    rho=next(r for r in rows(ROOT/"reference/qwen/primary.csv") if r["quantity"]=="rho")
    np.testing.assert_allclose([estimate,low,high],[float(rho[k]) for k in ("estimate","ci_low","ci_high")],rtol=0,atol=1e-12)
    calibration=[r for r in rows(ROOT/"reference/cal_selection.csv") if r["method"]=="CAL_TRI70_G"]
    assert len(calibration)==24 and all(r["status"]=="complete" for r in calibration)
    result={"status":"PASS","unit_rows":all_units,"primary_world_condition_rows":len(seen),"primary_contrasts":8,
            "metrics":["NMSE","R22","balanced_nDCG5"],"table1":panel,"calibration_cells":len(calibration),
            "qwen":{"n":512,"relative_reduction":estimate,"paired_95":[low,high]}}
    body=json.dumps(result,indent=2)+"\n"
    (output/"panel.json").write_text(body,encoding="utf8")
    print(body)
if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    main(parser.parse_args().out)
