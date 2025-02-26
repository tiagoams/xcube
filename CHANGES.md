## Changes in 0.2.0.dev2 (in dev)

* Reorganisation of the Documentation and Examples Section (partly addressing #106)
* Loosened python conda environment to satisfy conda-forge requirements

### New

* Added first version of the [xcube documentation](https://xcube.readthedocs.io/) generated from `./docs` folder.

### Enhancements

* Making CLI parameters consistent and removing or changing parameter abbreviations in case they were used twice for different params. (partly addressing #91)
  For every CLI command which is generating an output a path must be provided by the option `-o`, `--output`. If not provided by the user, a default output_path is generated.
  The following CLI parameter have changed and their abbreviation is not enabled anymore : 

    - `xcube gen -v` is now only `xcube gen --vars` or `xcube gen --variables` 
    - `xcube gen -p` is now  `xcube gen -P` 
    - `xcube gen -i` is now  `xcube gen -I` 
    - `xcube gen -r` is now  `xcube gen -R`
    - `xcube gen -s` is now  `xcube gen -S` 
    - `xcube chunk -c`  is now  `xcube chunk -C`
    - `xcube level -l` is now `xcube level -L`
    - `xcube dump -v` is now `xcube dump --variable` or `xcube dump --var`
    - `xcube dump -e` is now `xcube dump -E` 
    - `xcube vars2dim -v` is now `xcube vars2dim --variable` or `xcube vars2dim --var`
    - `xcube vars2dim --var_name` is now `xcube vars2dim --variable` or `xcube vars2dim --var`
    - `xcube vars2dim -d` is now `xcube vars2dim -D` 
    - `xcube grid res -d` is now `xcube grid res -D`
    - `xcube grid res -c` is now `xcube grid res --cov` or `xcube grid res --coverage` 
    - `xcube grid res -n` is now `xcube grid res -N` or `xcube grid res --num_results` 
    - `xcube serve -p` is now `xcube serve -P` 
    - `xcube serve -a` is now `xcube serve -A` 
    
* Added option `inclStDev` and `inclCount` query parameters to `ts/{dataset}/{variable}/geometry` and derivates.
  If used with `inclStDev=1`, Xcube Viewer will show error bars for each time series point.
* `xcube.api.new_cube` function now accepts callables as values for variables.
  This allows to compute variable values depending on the (t, y, x) position
  in the cube. Useful for testing.

### Fixes

* It was no longer possible to use the `xcube gen` CLI with `--proc` option. (#120)
* `totalCount` attribute of time series returned by Web API `ts/{dataset}/{variable}/{geom-type}` now
   contains the correct number of possible observations. Was always `1` before.
* Renamed Web API function `ts/{dataset}/{variable}/places` into
  `ts/{dataset}/{variable}/features`.
* `xcube gen` is now taking care that when new time slices are added to an existing
   cube, this is done by maintaining the chronological order. New time slices are
   either appended, inserted, or replaced. (#64) (#139)

## Changes in 0.2.0.dev1

### Enhancements

* `xcube.api` now exports the `MaskSet` class which is useful for decoding flag values encoding following the
  [CF conventions](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/cf-conventions.html#flags).
* Added new CLI tool `xcube optimize` and API function `xcube.api.optimize_dataset` 
  optimizes data cubes for cloud object storage deployment. (#141)
* Added two new spatial dataset operations to Python API `xcube.api` (#148):
  * `mask_dataset_by_geometry(dataset, geometry)` clip and mask a dataset by geometry
  * `clip_dataset_by_geometry(dataset, geometry)` just clip a dataset by geometry 
* Changed the dev version tag from 0.2.0.dev3 to 0.2.0.dev
* The behavior of web API `/datasets?details=1` has changed.
  The call no longer includes associated vector data as GeoJSON. Instead new API
  has beed added to fetch new vector data on demand:
  `/datasets/{dataset}/places` and `/datasets/{dataset}/places/{place}` (#130)
* `xcube serve` accepts custom SNAP colormaps. The path to a SAP .cpd file can be passed via the server
   configuration file with the paramter [ColorFile] instead of [ColorBar]. (#84)
* `xcube serve` can now be configured to serve cubes that are associated 
   with another cube with same data but different chunking (#115). 
   E.g. using chunks such as `time=512,lat=1,lon=1` can drastically improve 
   time-series extractions. 
   Have a look at the demo config in `xube/webapi/res/demo/config.yml`.     
* `xcube serve` does now offer a AWS S3 compatible data access API (#97):
   - List bucket objects: `/s3bucket`, see AWS 
     docs [GET](https://docs.aws.amazon.com/AmazonS3/latest/API/v2-RESTBucketGET.html)
   - Get bucket object: `/s3bucket/{ds_id}/{path}`, 
     see AWS docs [HEAD](https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectHEAD.html) 
     and [GET](https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectGET.html)
* `xcube serve` now verifies that a configured cube is valid once it is opened. (#107)
* Added new CLI command `xcube verify` performing xcube dataset verification. (#19)
* Reworked `xcube extract` to be finally useful and effective for point data extraction. (#102) 
* `xcube server`can now filter datasets by point coordinate, e.g. `/datasets?point=12.5,52.8`. (#50) 
* `xcube server`can now limit time series to a maximum number of 
  valid (not NaN) values. To activate, pass optional query parameter `maxValids` to the various `/ts`
  functions. The special value `-1` will restrict the result to contain only valid values. (#113) 
* Reworked `xcube gen` to be more user-friendly and more consistent with other tools. 
  The changes are
  - Removed `--dir` and `--name` options and replaced it by single `--output` option, 
    whose default value is `out.zarr`. (#45)
  - The `--format` option no longer has a default value. If not given, 
    format is guessed from `--output` option.
  - Renamed following parameters in the configuration file:
    + `input_files` into `input_paths`, also because paths may point into object storage 
      locations (buckets);  
    + `output_file` into `output_path`, to be consistent with `input_paths`.  
* Added new CLI command `xcube prune`. The tool deletes all block files associated with empty (NaN-
  only) chunks in given INPUT cube, which must have ZARR format. This can drastically reduce files 
  in sparse cubes and improve cube reading performance. (#92)
* `xcube serve` has a new `prefix` option which is a path appended to the server's host.
  The `prefix` option replaces the `name` option which is now deprecated but kept 
  for backward compatibility. (#79)
* Added new CLI command `xcube resample` that is used to generate temporarily up- or downsampled
  data cubes from other data cubes.
* `xcube serve` can now be run with xcube dataset paths and styling information given via the CLI rather 
  than a configuration file. For example `xcube serve --styles conc_chl=(0,20,"viridis") /path/to/my/chl-cube.zarr`.
  This allows for quick inspection of newly generated cubes via `xcube gen`.
  Also added option `--show` that starts the Xcube viewer on desktop environments in a browser. 
* Added new `xcube apply` command that can be used to generate an output cube computed from a Python function 
  that is applied to one or more input cubes. 
  The command is still in development and therefore hidden.
* Added new `xcube timeit` command that can be used to measure the time required for 
  parameterized command invocations. 
  The command is still in development and therefore hidden.
* Added global `xcube --scheduler SCHEDULER` option for Dask distributed computing (#58)
* Added global `xcube --traceback` option, removed local `xcube gen --traceback` option
* Completed version 1 of an xcube developer guide.
* Added `xcube serve` command (#43) 
* `xcube serve`: Time-series web API now also returns "uncertainty" (#48)
* Added `xcube level` command to allow for creating spatial pyramid levels (#38)
* `xcube gen` accepts multiple configuration files that will be merged in order (#21)
* Added `xcube gen` option `--sort` when input data list should be sorted (#33)    
* Added `xcube vars2dim` command to make variables a cube dimension (#31)
* Added `xcube serve` option `--traceperf` that allows switching on performance diagnostics.
* Included possibility to read the input file paths from a text file. (#47)
* Restructured and clarified code base (#27)
* Moved to Python 3.7 (#25)
* Excluding all input processors except for the default one. They are now plugins and have own repositories within the 
xcube's organisation. (#49)

### Fixes

* Fixed `xcube serve` issue with WMTS KVP method `GetTile` with query parameter `time` 
  whose value can now also have the two forms `<start-date>/<end-date>` and just `<date>`. (#132) 
* Fixed `xcube extract` regression that stopped working after Pandas update (#95) 
* Fixed problem where CTRL+C didn't function anymore with `xcube serve`. (#87)
* Fixed error `indexes along dimension 'y' are not equal` occurred when using 
  `xcube gen` with processed variables that used flag values (#86)
* Fixed `xcube serve` WMTS KVP API to allow for case-insensitive query parameters. (#77)
* Fixed error in plugins when importing `xcube.api.gen` (#62)
* Fixed import of plugins only when executing `xcube.cli` (#66)


## Changes in 0.1.0

* Respecting chunk sizes when computing tile sizes [#44](https://github.com/dcs4cop/xcube-server/issues/44)
* The RESTful tile operations now have a query parameter `debug=1` which toggles tile 
  computation performance diagnostics.
* Can now associate place groups with datasets.
* Major revision of API. URLs are now more consistent.
* Request for obtaining a legend for a layer of given by a variable of a data set was added.
* Added a Dockerfile to build an xcube docker image and to run the demo
* The RESTful time-series API now returns ISO-formatted UTC dates [#26](https://github.com/dcs4cop/xcube-server/issues/26)

