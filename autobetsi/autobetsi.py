"""
    autobetsi; automatic application of betsi criteria to determine BET area from
    isotherms.
    Copyright (C) 2022 L. Scott Blankenship.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import glob
import betsi.lib as bl
from os.path import exists
from os import mkdir
import pandas as pd
import warnings


def strictly_increasing(List):
    increasing = [x < y for x, y in zip(List, List[1:])]
    increasing.append(increasing[-1])
    return increasing


def clean_isotherms(
    input_dir: str = './csv/',
    output_dir: str = './csv_clean/'
):
    print(f'Cleaning isotherms in {input_dir} and placing in {output_dir}...')
    if not exists(output_dir):
        mkdir(output_dir)

    files = glob.glob(f'{input_dir}*.csv')
    for f in files:
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

    print(f'...{len(files)} cleaned and saved in {output_dir}')

    return output_dir


def check_analysed(
    file: str,
    input_dir: str = './csv/',
    output_dir: str = './betsi/',
):
    filename = file.split(input_dir)[1]
    name = filename[:-4]
    plot_path = f'{output_dir}{filename}/{name}_combined_plot.pdf'
    if exists(plot_path):
        return True


def analyse_file(
    file: str,
    output_dir: str = './betsi/',
    **kwargs,
):
    if not exists(output_dir):
        mkdir(output_dir)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            bl.analyse_file(
                file,
                output_dir,
                **kwargs
            )

    except Exception as e:
        return e


def get_results_summary(
    file
):
    results = {}
    with open(file) as f:
        for line in f:
            key, value = line.partition(':')[::2]
            try:
                results[key.strip()] = float(value)
            except ValueError:
                continue
    return results


def tabulate_results(
    output_dir: str = './betsi/'
):
    results_files = glob.glob(f'{output_dir}*.csv/results.txt')
    results_dict = {}
    for f in results_files:
        name = f.split(output_dir)[1].split('.csv/results.txt')[0]
        results_dict[name] = get_results_summary(f)

    return results_dict


def analyse_directory(
    input_dir: str = './csv/',
    output_dir: str = './betsi/',
    overwrite: bool = False,
    **kwargs,
):
    files = glob.glob(f'{input_dir}*.csv')

    print(f'analysing {len(files)} files in directory {input_dir} using parameters;\n'
          f'------------------------------------------'
         )
    for key, value in kwargs.items():
        print(f'{key: <20}{value}'
             )
    print(f'------------------------------------------')

    if overwrite is False:
        analysed = [f for f in files if check_analysed(f, input_dir, output_dir)==True]
        files = [f for f in files if f not in analysed]
        if len(analysed) > 0:
            print(f'Removing following {len(analysed)} files that are already analysed:')
            print(*analysed, sep='\n')
            print(f'If you wish to analyse these isotherms again, please '
                  f'specify overwrite=True, or specify a differnt output_dir'
                 )

    files_exception = []
    exception = []
    for file in files:
        print(f'first analysis of {file}')
        e = analyse_file(file, output_dir, **kwargs)
        if e is not None:
            print(e)
            exception.append(e)
            files_exception.append(file)
        else:
            print(f'success!\n')

    return {
        'files': files_exception,
        'exception': exception,
    }


def analyse_reduce_accuracy(
    file: str,
    parameter: str,
    steps: 'list[float]',
    **kwargs
):
    if parameter not in ['min_r2', 'min_num_points', 'max_pc_error']:
        return

    if not exists(file):
        return

    print(f'Attempting analysis of {file} with {parameter} between '
          f'{max(steps)}, and {min(steps)}. '
          f'\n-------------------------------'
         )
    for s in steps:
        kwargs[parameter] = s
        e = analyse_file(file, **kwargs)
        if e is not None:
            print(f'{parameter} =\t{s}\t{e}')
        else:
            print(f'{parameter} =\t{s}\tSUCCESS!')
            break


def run():
    input_dir = clean_isotherms()

    kwargs = {
              'max_perc_error': 20.0,
              'min_num_pts': 10,
              'min_r2': 0.995,
              'use_rouq1': True,
              'use_rouq2': True,
              'use_rouq3': True,
              'use_rouq4': True,
              'use_rouq5': False
             }

    files_exception = analyse_directory(
        input_dir,
        **kwargs,
    )  # initial attempt to analyse. Failures added to list

    for file in files_exception['files']:
        analyse_reduce_accuracy(
            file,
            'min_num_points', [9, 8, 7, 6, 5, 4, 3],
            **kwargs
        )  # Reattempt failed files with incrementally reducing number of points

    results = pd.DataFrame.from_dict(
        tabulate_results(),
        orient='index',
    )

    results.to_csv('./betsi_results.csv')


if __name__ == "__main__":
    run()
