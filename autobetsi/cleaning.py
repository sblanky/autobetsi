from os.path import exists
from os import mkdir
import os
import pandas as pd
import glob
import pygaps.parsing as pgp
import pandas as pd
import warnings


def strictly_increasing(List):
    increasing = [x < y for x, y in zip(List, List[1:])]
    increasing.append(increasing[-1])
    return increasing


def clean_isotherms(
    input_dir: str = './',
    output_dir: str = './clean/'
):
    print(f'Cleaning isotherms in {input_dir} and placing in {output_dir}...')
    if not exists(output_dir):
        mkdir(output_dir)

    files = glob.glob(f'{input_dir}*.csv')
    for f in files:
        print(f)
        isotherm = pd.read_csv(
            f,
            names=['relative_pressure', 'loading'],
            header=0,
        )

        relative_pressure = isotherm['relative_pressure'].to_list()
        increasing = strictly_increasing(relative_pressure)
        isotherm = isotherm.assign(increasing=increasing)
        isotherm = isotherm[isotherm.increasing == True]
        isotherm = isotherm.drop(columns=['increasing'])

        isotherm.to_csv(
            f'{output_dir}{f.split(input_dir)[1]}',
            index=False,
        )

    print(
        f'...{len(files)} cleaned and saved in {output_dir}\n\n'
    )

    return output_dir


def convert_aif(
    file: str,
    output_dir:str = './csv/',
):
    filename = os.path.split(file)[1]
    name, ext = os.path.splitext(filename)
    if ext[1:] not in ['aif', 'aiff']:
        return

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        isotherm = pgp.isotherm_from_aif(file)

    pressure = isotherm.data_raw['pressure']
    loading = isotherm.data_raw['loading']
    if 'pressure_saturation' in isotherm.data_raw:
        pressure = pressure / \
        isotherm.data_raw['pressure_saturation']

    df = pd.DataFrame(list
                      (zip(
                          pressure, loading
                      )
                      ), columns=['P/P0', 'loading']
                     )

    if not exists(output_dir):
        mkdir(output_dir)
    df.to_csv(f'{output_dir}{name}.csv')

