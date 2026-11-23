# Method implementation

The [observation design](../code/design_reference.py) defines which 23 states each plan sees. The [query code](../code/query_reference.py) defines relevance for fact retrieval. Using the 2,048 paired worlds and the original 10,000 shared bootstrap draws, the [paired inference code](../code/paired_intervals.py) reconstructs the eight primary contrasts and their simultaneous 95% intervals.

From the release root, run `python -B check_methods.py`. The resampling unit is the world. All methods and conditions inside it use the same draw.
