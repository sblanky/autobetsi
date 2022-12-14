Development of automatic application of betsi to a directory of isotherms (`.csv`). 

Running `python -m autobetsi` in the parent director of a `./csv/` will run a standard betsi analysis on all files in `./csv/`, adding results to `./betsi/`. If analysis fails, conditions are made iteratively less restrictive until a result is obtained. Finally, for convenience results are tabulated for each isotherm in `./csv/`.
