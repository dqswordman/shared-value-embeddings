# Beyond Pairwise Overlap: Shared-Value Observations for Compositional Text Embeddings

**Wenzhang Du** · [Open Research Reports](https://dqswordman.github.io/open-research/) · November 2026

Two 23-state observation plans differ in which city their edits share. On atomic text the shared-value plan reduces reconstruction error by 53.4% for BGE and 36.0% for E5.

[Manuscript PDF](paper/manuscript.pdf) · [Technical report](https://dqswordman.github.io/technical-reports/shared-value-embeddings/) · [中文技术报告](https://dqswordman.github.io/zh/technical-reports/shared-value-embeddings/) · [Interactive explorer](https://huggingface.co/spaces/DQSWORDMAN/shared-value-embeddings) · [Download v1.0.0](https://github.com/dqswordman/shared-value-embeddings/releases/tag/v1.0.0)

![City swaps sharing one value compared with a cycle of pairwise-shared cities.](figures/design.png)

## Read the evidence

Two sets of 23 observations see the same pairwise overlap pattern. Following the identity of the shared city changes how well they reconstruct a held-out directory. The study concerns a finite synthetic directory and fixed encoders. Qwen uses a preselected subset of the original test pool.

| Result | Open the evidence |
| --- | --- |
| Two-encoder comparison · Table 1 | [Frozen records](data/units.csv.xz) · [Analysis or reference](reference/primary_contrasts.csv) |
| Query strata and rankings | [Frozen records](data/query_strata_world.csv.xz) · [Analysis or reference](reference/query_strata.csv) |
| Qwen transfer check | [Frozen records](data/qwen/unit_results.csv.xz) · [Analysis or reference](reference/qwen/primary.csv) |

## Reproduce on CPU

From the extracted release, run the following with Python 3.12. Results go into an empty directory of your choice.

```sh
python -m pip install -r requirements.txt
python -B verify_manifest.py
python -B reproduce.py --out replay
```

For one worked example, run `python -B example.py`. The [reproduction guide](docs/reproduction.md) maps files to scientific claims. Both technical reports are available offline in [English](docs/report.en.md) and [中文](docs/report.zh.md).

## Cite and reuse

Wenzhang Du (2026). *Beyond Pairwise Overlap: Shared-Value Observations for Compositional Text Embeddings*. Open Research Reports, v1.0.0. [Manuscript](https://dqswordman.github.io/assets/reports/shared-value-embeddings/manuscript.pdf). [Machine-readable citation](CITATION.cff) · [BibTeX](citation.bib)

Wenzhang Du is the sole author. The attached PDF preserves the supplied anonymous title page. Original software uses the [MIT License](LICENSE). The author’s original report, figures, constructed data and measurements use [CC BY 4.0](licenses/CC-BY-4.0.txt). Third-party material retains its own terms and attribution. [Source notices](THIRD_PARTY_NOTICES.md)
