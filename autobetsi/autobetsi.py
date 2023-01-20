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


from time import sleep
import glob
import betsi.lib as bl
from os.path import exists
from os import mkdir
import pandas as pd
import warnings
from .cleaning import clean_isotherms


def check_analysed(
    file: str,
    input_dir: str = '.',
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
    print('tabulating results for convenience...')
    results_files = glob.glob(f'{output_dir}*.csv/results.txt')
    results_dict = {}
    for f in results_files:
        name = f.split(output_dir)[1].split('.csv/results.txt')[0]
        results_dict[name] = get_results_summary(f)

    return results_dict


def analyse_directory(
    input_dir: str = '.',
    output_dir: str = './betsi/',
    overwrite: bool = False,
    **kwargs,
):
    files = glob.glob(f'{input_dir}*.csv')

    print(f'{len(files)} files found in directory {input_dir}\n'
          f'Initial analysis parameters\n'
          f'------------------------------------------'
         )
    for key, value in kwargs.items():
        print(f'{key: <20}{value}'
             )
    print(f'------------------------------------------')
    sleep(2)

    if overwrite is False:
        analysed = [f for f in files if check_analysed(f, input_dir, output_dir)==True]
        files = [f for f in files if f not in analysed]
        if len(analysed) > 0:
            print(f'\nRemoving following {len(analysed)} files that are already analysed:')
            print(*analysed, sep='\n')
            print('If you wish to analyse these isotherms again, please '
                  'specify overwrite=True, or specify a different output_dir\n'
                 )
            sleep(2)

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
            print('SUCCESS!\n')

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
            return True


def run():
    from art import tprint

    tprint('autobetsi\n')
    print(
        'Automatically applies betsi criteria to a group'
        'of isotherms, and doesn\'t give up!\n\n'
    )
    sleep(1)

    input_dir = clean_isotherms()
    sleep(1)

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
    sleep(1)

    output_dir = './betsi/'
    files_exception = analyse_directory(
        input_dir,
        output_dir,
        **kwargs,
    )  # initial attempt to analyse. Failures added to list
    sleep(1)

    kwargs['max_perc_error'] = 60
    for file in files_exception['files']:
        points_success = analyse_reduce_accuracy(
            file,
            'min_num_points', [9, 8, 7, 6, 5,],
            **kwargs
        )  # Reattempt failed files with incrementally reducing number of points
        if points_success is not True:
            analyse_reduce_accuracy(
                file,
                'min_r2', [0.99, 0.98, 0.97, 0.96, 0.95],
                **kwargs,
            )

    results = pd.DataFrame.from_dict(
        tabulate_results(),
        orient='index',
    )

    tabulated_out = f'./{output_dir}/betsi_results.csv'
    results.to_csv(tabulated_out)
    print(f'...saved to {tabulated_out}')


if __name__ == "__main__":
    run()
