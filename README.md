Development of automatic application of betsi[^1] to a directory of isotherms (`.csv`). Hopes to make use of [betsi](https://github.com/nakulrampal/betsi-gui) more convenient. Works on Linux, (Rocky Linux 9.1 (Blue Onyx) x86_64) no idea on other systems. I hope it is useful to the adsorption community. 

# Installation

- Follow instructions to install [betsi-gui](https://github.com/nakulrampal/betsi-gui) in a conda virtual environment.
- Activate venv.
- clone this repo.
- `cd` into the cloned repo, and do `pip install .`

# Basic use

Running `autobetsi` from the command line in a directory `.` runs `betsi` on the contents of `./csv/`. Initial parameters;

| Parameter		| Value		|
| -------------------- 	| ------------- |
| 'max_perc_error' 	| 20.0		|
| 'min_num_pts'		| 10		|
| 'min_r2'		| 0.995		|
| 'use_rouq1'		| True		|
| 'use_rouq2'		| True		|
| 'use_rouq3'		| True		|
| 'use_rouq4'		| True		|
| 'use_rouq5'		| False		|

If an isotherm throws an exception, this typically means that a BET area cannot be found with the current conditions. Any such files are added to a list of exceptions, then reattempted with iteratively reduced `'min_num_points'` until a result is achieved.

Finally, for convenience results are tabulated for each analysis present in `./betsi/` 

You can test it on isotherms in [`./autobetsi/csv/`](./autobetsi/csv/). These are copied from [betsi-gui](https://github.com/nakulrampal/betsi-gui).

# Advanced

The functions in `autobetsi.py` can be imported and used in further scripts.

# TODO

- `betsi` is picky about isotherms. ~~Make cleaning/conversion function.~~ Expand cleaning function!
- Allow use of tags from commandline.
- ~~Silence `betsi`'s warnings from `seaborn`, `matplotlib` etc.~~
- Give up less hard; standard autobetsi to try combinations of iteratively looser parameters instead of just reducing `'min_num_points'`. Requires logical progression, and minimum strictness.
- Threading ???


[^1]: Osterrieth, Johannes WM, James Rampersad, David Madden, Nakul Rampal, Luka Skoric, Bethany Connolly, Mark D. Allendorf et al. "How reproducible are surface areas calculated from the BET equation?." _Advanced Materials_ (2022): 2201502.
