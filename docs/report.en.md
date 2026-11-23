# Which edits reveal the embedding of an unseen directory?

Beyond Pairwise Overlap: Shared-Value Observations for Compositional Text Embeddings

Wenzhang Du · Open Research Reports · v1.0.2 · 2026-11-22

Three edits can overlap in pairs even when no single city is shared by all three. Two designs each encode 23 of 64 possible directories. On 2,048 synthetic worlds written as individual facts, observing triples that share a city reduces reconstruction error by 53.4% for BGE and 36.0% for E5 relative to observing a cycle. Better reconstruction does not consistently improve fact retrieval.

[Original PDF](../paper/manuscript.pdf) · [Online report](https://dqswordman.github.io/technical-reports/shared-value-embeddings/)

## When three swaps draw the same triangle

Swap Dublin with Accra in the residence field, Dublin with Seoul in the work field and Dublin with Athens in the study field. All three swaps touch Dublin. Now replace only the last swap with Accra–Seoul. Every pair of swaps still touches a common city, but each pair meets at a different one. A diagram with one edge per overlapping pair shows the same triangle in both cases.

![City swaps sharing one value compared with a cycle of pairwise-shared cities.](../figures/design.png)

Figure 1. In the star, one city belongs to all three swaps. In the cycle, each pair of swaps shares a different city. Counting the pairs that overlap gives the same answer in both panels.

## Two ways to spend 23 observations

Six binary edits define 64 versions of each four-person directory. Star23 and Cycle23 encode 23 states each and use the same quadratic reconstruction rule for the remaining states. The experiment varies which joint edits are observed while keeping the number of observations, target states and decoder fixed. Two renderings express the same facts as atomic sentences or compressed prose.

BGE-small and E5-small encode 2,048 synthetic test worlds. Three measures answer different questions. Normalized mean squared error measures distance to the true embedding. R22 asks whether the reconstruction identifies the correct directory among 22 candidates. Balanced query ranking asks whether a user seeking a fact retrieves the right record.

## A shared city improves reconstruction for both encoders

Across both text formats and both encoders, Star23 gives lower normalized reconstruction error than Cycle23. On records written as individual sentences, the relative reductions are 53.4% for BGE and 36.0% for E5. On compressed records the probability of identifying the exact state rises by 15.45 and 15.80 percentage points, respectively. In a separate atomic-text check on 512 preselected worlds from the same pool, Qwen3-Embedding-0.6B shows a 6.58% relative error reduction.

For each encoder and rendering, the left value is Star23 and the right value is Cycle23. Lower normalized mean squared error (NMSE) indicates closer reconstruction. Higher R22 means more correct identifications among 22 candidate states. Manuscript Table 1.

| Encoder · text | NMSE | R22 (%) |
| --- | --- | --- |
| BGE · Atomic | 0.01238 / 0.02657 | 99.02 / 96.00 |
| BGE · Compressed | 0.31746 / 0.72291 | 93.55 / 78.10 |
| E5 · Atomic | 0.01514 / 0.02367 | 98.15 / 96.80 |
| E5 · Compressed | 0.29736 / 0.69517 | 93.63 / 77.83 |

[Source table](https://github.com/dqswordman/shared-value-embeddings/blob/v1.0.1/reference/primary_contrasts.csv)

## Recovering the directory and finding a fact are different tasks

On BGE embeddings of atomic text, nDCG@5 rises by 0.12424 percentage points for same-entity queries and falls by 0.03569 points for different-entity queries. On compressed E5 text, the shared-city design identifies the right directory 15.80 points more often, yet balanced query nDCG@5 falls by 0.03542 percentage points. An index chosen for state identification therefore still needs evaluation on the queries it will serve.

The 23-state design, four-person directories and fixed checkpoints define this evidence. The Qwen comparison reuses a subset of the same world pool. Natural documents, larger edit systems and additional independent pools would test how far the shared-value pattern extends.

## Recalculate the paired differences by world

The CPU replay reads the released scalar measurements and averages the six conditions within each world before comparing designs. It verifies the eight primary contrasts and reconstructs the paired interval for 512 Qwen worlds using the original 10,000 bootstrap draws. The archive supplies the synthetic inputs, observation designs, calibration choices and saved rankings. Encoding new text requires the corresponding encoder.

Using the original inference code and shared bootstrap draws, the 2,048 paired worlds also reproduce all eight simultaneous 95% intervals. The family-wise critical value is 2.70526.

```sh
python -B verify_manifest.py
python -B reproduce.py --out replay
python -B check_methods.py
```

## Citation and materials

[Original manuscript · PDF](https://dqswordman.github.io/assets/reports/shared-value-embeddings/manuscript.pdf) · [Frozen release and checksums](https://github.com/dqswordman/shared-value-embeddings/releases/tag/v1.0.1) · [Result map and reproduction scope](https://github.com/dqswordman/shared-value-embeddings/blob/v1.0.1/docs/reproduction.md) · [Interactive evidence explorer](https://huggingface.co/spaces/DQSWORDMAN/shared-value-embeddings) · [Method implementation and worked checks](https://github.com/dqswordman/shared-value-embeddings/blob/v1.0.1/docs/methods.md)
