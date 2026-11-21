# Reproducing the reported results

**Beyond Pairwise Overlap: Shared-Value Observations for Compositional Text Embeddings** · Wenzhang Du · v1.0.0

```sh
python -m pip install -r requirements.txt
python -B verify_manifest.py
python -B reproduce.py --out replay
```

Run the commands at the root of the extracted archive with Python 3.12. CPU verification uses NumPy 2.5.3, the version used to check this release. The manifest verifies the publication files before replay. A successful run prints `PASS` and writes its derived tables or summary into the empty output directory.

| Study result | Files | Unit and operation |
| --- | --- | --- |
| Two-encoder comparison · Table 1 | [Input](../data/units.csv.xz) · [Reference](../reference/primary_contrasts.csv) | Average six conditions within a world, then compare Star23 and Cycle23 across 2,048 worlds for each encoder and rendering. |
| Query strata and rankings | [Input](../data/query_strata_world.csv.xz) · [Reference](../reference/query_strata.csv) | World-level metrics cover the tested query strata. The two worked ranking files in fixtures/ retain the BGE atomic comparison for TEST0000 and condition AD_C0_E. |
| Qwen transfer check | [Input](../data/qwen/unit_results.csv.xz) · [Reference](../reference/qwen/primary.csv) | The 512 preselected worlds share the original test pool. The script rebuilds the relative effect and the 10,000-draw paired interval. |

## Evidence boundaries

The archive stores the measured per-condition and per-world scalars used by the primary checks, fixed synthetic inputs, observation matrices, original analysis settings and the 512-world Qwen study. Individual rankings for the full primary BGE/E5 population and native hidden vectors are outside this distribution. Encoding new documents requires the pinned upstream checkpoints.

The study concerns a finite synthetic directory and fixed encoders. Qwen uses a preselected subset of the original test pool. For a single worked case, run `python -B example.py`. [Original manuscript](../paper/manuscript.pdf) · [English report](report.en.md) · [中文报告](report.zh.md) · [Third-party terms](../THIRD_PARTY_NOTICES.md)
