Development of automatic application of betsi to a directory of isotherms (`.csv`). 

If `betsi` and `autobetsi` are installed on your system, running `python -m autobetsi` in the parent director of a `./csv/` will run a standard betsi analysis on all files in `./csv/`. Results are then added to `./betsi/`. If analysis fails, conditions are made iteratively less restrictive until a result is obtained. 

Finally, for convenience results are tabulated for each analysis present in `./betsi/` 
