# Method implementation

The [observation design](../code/design_reference.py) and [rendering, relevance and ranking](../code/query_reference.py) modules define the finite task. The [original paired inference implementation](../code/paired_intervals.py) computes ordinary and simultaneous uncertainty. The CPU method check recovers the eight primary comparisons and their family-wise 95% intervals from the 2,048 world-level paired records using 10,000 shared draws.

From the release root, run `python -B check_methods.py`. The resampling unit is the world. All methods and conditions inside it use the same draw.
