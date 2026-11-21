"""Rebuild the eight simultaneous primary intervals from the paired test-world records."""
import csv
import json
import lzma
import sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
from paired_intervals import simultaneous

def main():
    with (ROOT/'reference/primary_contrasts.csv').open(encoding='utf-8-sig',newline='') as stream:
        reference=list(csv.DictReader(stream))
    with lzma.open(ROOT/'data/world_summary.csv.xz','rt',encoding='utf-8-sig',newline='') as stream:
        rows={(r['world_id'],r['model'],r['renderer'],r['method']):r for r in csv.DictReader(stream)
              if r['split']=='TEST' and r['method'] in {'STAR23','CYCLE23'}}
    worlds=sorted({key[0] for key in rows})
    assert len(worlds)==2048
    vectors={}
    for r in reference:
        vector=[]
        for world in worlds:
            key=(world,r['model'],r['renderer'])
            star=float(rows[key+('STAR23',)][r['metric']])
            cycle=float(rows[key+('CYCLE23',)][r['metric']])
            vector.append((star-cycle)*int(r['contrast_sign']))
        vectors[r['key']]=np.asarray(vector)
    catalog,_,critical,_=simultaneous(vectors,int(reference[0]['bootstrap_seed']),int(reference[0]['bootstrap_replicates']))
    assert len(catalog)==8
    for r in reference:
        for field in ('estimate','ordinary_low','ordinary_high','simultaneous_low','simultaneous_high'):
            np.testing.assert_allclose(catalog[r['key']][field],float(r[field]),atol=1e-11,rtol=0)
    print(json.dumps({'status':'PASS','paired_worlds':len(worlds),'primary_intervals':len(catalog),'draws':10000,'simultaneous_critical_value':critical},indent=2))
if __name__=='__main__':main()
