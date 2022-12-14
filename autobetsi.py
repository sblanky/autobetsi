import glob
import betsi.lib as bl
from os.path import exists
import pandas as pd


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
    try:
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
        e = analyse_file(file, output_dir, **kwargs)
        if e is not None:
            e.append(exception)
            files_exception.append(file)

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

    print(f'Attempting analysis of {file} with {parameter} between'
          f'{min(steps)}, and {max(steps)}.'
          f'-------------------------------'
         )
    for s in steps:
        kwargs[parameter] = s
        try:
            analyse_file(file, **kwargs)
        except AssertionError as a:
            print(f'{parameter} = \t{s} \t{a}')
            continue
        except Exception as e:
            print(f'{parameter} = \t{s} \t{e}')
            continue
        print(f'{parameter} = \t{s} SUCCESS!')


if __name__ == "__main__":
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
        **kwargs
    ) # initial attempt to analyse. Failures added to list

    for file in files_exception['files']:
        analyse_reduce_accuracy(
            file,
            'min_num_points', [9, 8, 7, 6, 5]
            **kwargs
        ) # Reattempt failed files with incrementally reducing number of points 

    results = pd.DataFrame.from_dict( 
        tabulate_results(),
        orient='index'
    )

    results.to_csv('./betsi_results.csv')
