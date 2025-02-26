# The MIT License (MIT)
# Copyright (c) 2018 by the xcube development team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import click
from xcube.api.gen.defaults import DEFAULT_OUTPUT_PATH
__author__ = "Norman Fomferra (Brockmann Consult GmbH)"


# noinspection PyShadowingBuiltins
@click.command(name='apply', hidden=True)
@click.argument('script')
@click.argument('cube', nargs=-1)
@click.option('--output', '-o', metavar='OUTPUT', default=DEFAULT_OUTPUT_PATH,
              help=f'Output path. Defaults to {DEFAULT_OUTPUT_PATH!r}')
@click.option('--params', '-p', metavar='PARAMS',
              help="Keyword arguments passed to apply() and init() functions in <script>.")
@click.option('--variables', '--vars', metavar='VARIABLES',
              help="Comma-separated list of variable names.")
@click.option('--dask', metavar='DASK',
              default='forbidden',
              type=click.Choice(['forbidden', 'allowed', 'parallelized']),
              help="Mode of operation for the Dask library.")
@click.option('--format', '-f', metavar='FORMAT',
              default='zarr',
              type=click.Choice(['zarr', 'nc']),
              help="Output format.")
@click.option('--dtype', metavar='DTYPES',
              default='float64',
              type=click.Choice(["uint8", "int8", "uint16", "int16", "uint32", "int32", "float32", "float64"]),
              help="Output data type.")
def apply(script: str,
          cube: str,
          output: str,
          params: str,
          variables: str,
          dask: str,
          format: str,
          dtype: str):
    """
    Apply a function to data cubes.
    The function is used to transform N chunks of equal shape to a new chunk of same shape.
    N is the number of variables from all data cubes.

    Uses the Python program SCRIPT to transform data cubes
    given by CUBEs into a new xcube dataset given by OUTPUT.

    The <script> must define a function ``apply(*variables, **params)`` where variables
    are numpy arrays (chunks) in the order given by VARIABLES or given by the variables returned by
    an optional ``init()`` function that my be defined in SCRIPT.
    If neither VARIABLES nor an ``init()`` function is defined, all variables are passed in arbitrary order.

    The optional ``init(*cubes, **params)`` function can be used to validate the data cubes,
    extract the desired variables in desired order and to provide some extra processing parameters passed to
    the ``apply()`` function. The ``init()`` argument *cubes* are the ``xarray.Dataset`` objects
    according to CUBEs and *params* are according to PARAMS. The return value of ``init()`` is
    a tuple (*variables*, *new_params*) where *variables* is a list of ``xarray.DataArray`` objects and
    *new_params* are newly computed parameters passed to ``apply()``.
    """

    input_paths = cube
    output_path = output
    apply_function_name = "apply"
    init_function_name = "init"

    with open(script, "r") as fp:
        code = fp.read()

    locals_dict = dict()
    exec(code, globals(), locals_dict)

    var_names = list(map(lambda s: s.strip(), variables.split(","))) if variables else None

    init_function = locals_dict.get(init_function_name)
    if init_function is not None and not callable(init_function):
        raise click.ClickException(f"{init_function_name!r} in {script} is not a callable")

    apply_function = locals_dict.get(apply_function_name)
    if apply_function is None:
        raise click.ClickException(f"missing function {apply_function_name!r} in {script}")
    if not callable(apply_function):
        raise click.ClickException(f"{apply_function!r} in {script} is not a callable")

    from xcube.api import read_cube
    from xcube.util.cliutil import parse_cli_kwargs
    from xcube.util.dsio import guess_dataset_format, find_dataset_io

    kwargs = parse_cli_kwargs(params, "PARAMS")
    input_cube_0 = None
    input_cubes = []
    for input_path in input_paths:
        input_cube = read_cube(input_path=input_path)
        if input_cube_0 is None:
            input_cube_0 = input_cube
        else:
            # TODO (forman): make sure input_cube's and input_cube_0's coords and chunking are compatible
            pass
        input_cubes.append(input_cube)

    if var_names:
        input_cubes = [input_cube.drop(labels=set(input_cube.data_vars).difference(set(var_names)))
                       for input_cube in input_cubes]

    import xarray as xr
    if init_function:
        variables, params = init_function(*input_cubes, **kwargs)
    else:
        variables, params = xr.merge(input_cubes).data_vars.values(), kwargs

    output_variable = xr.apply_ufunc(apply_function,
                                     *variables,
                                     dask=dask,
                                     output_dtypes=[dtype] if dask == "parallelized" else None)

    format = format or guess_dataset_format(output_path)
    dataset_io = find_dataset_io(format, {"w"})
    dataset_io.write(xr.Dataset(dict(output=output_variable)), output_path)
