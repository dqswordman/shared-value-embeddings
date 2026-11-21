"""Compare two edit triples from the first frozen condition on one test world."""
import csv
import json
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    condition = json.loads((ROOT/'config/conditions.json').read_text())[0]
    with (ROOT/'inputs/WORLDS_R5.csv').open(encoding='utf-8', newline='') as stream:
        world = next(row for row in csv.DictReader(stream) if row['world_id'] == 'TEST0000')
    pairs = []
    for values in condition['permutations']:
        cities = [world['city'+str(index)] for index in values]
        pairs.extend((set(cities[:2]), set(cities[2:])))
    for design in ['STAR', 'CYCLE']:
        triple = condition[design][0]
        edges = [pairs[index] for index in triple]
        assert all(len(left & right) == 1 for left, right in combinations(edges, 2))
        shared = sorted(set.intersection(*edges))
        assert len(shared) == (1 if design == 'STAR' else 0)
        print(json.dumps({'world':world['world_id'], 'condition':condition['id'], 'design':design,
                          'city_swaps':[sorted(edge) for edge in edges], 'shared_by_all_three':shared}))
if __name__=='__main__':
    main()
