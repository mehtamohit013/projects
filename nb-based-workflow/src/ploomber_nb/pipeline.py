"""
Launch an interactive session:

To run:
"""
from pathlib import Path

from ploomber_nb import functions

from ploomber import DAGConfigurator, SourceLoader
from ploomber.tasks import NotebookRunner, PythonCallable
from ploomber.products import File


def make():
    # Small notebooks are easier to debug and manage than a big monolithic one
    # It is hard to make diffs on .ipynb files (they are JSON strings), this
    # makes pull requests complicated, we use regular .py files that are
    # converted on demand to notebooks instead. We can also exploit the
    # dependency structure to run things in parallel

    cfg = DAGConfigurator()
    cfg.params.hot_reload = True
    dag = cfg.create()

    # Our notebook declaration is minimal, we just specify where the source code
    # is located and where to save the executed notebooks and any other files
    # the notebook will save
    out = Path('output')
    out.mkdir(exist_ok=True)

    loader = SourceLoader(path='notebooks', module='ploomber_nb')

    # avoid hardcoding paths to files, instead, add them during execution,
    # this makes easy to switch folders (e.g. for a different developer storing
    # results in a different location).

    # static analysis prevents notebooks with errors from being executed, saving
    # us time if the notebook performs long-running computations

    # notebooks do not have to be in Python, they can be in R, Julia or any
    # other language supported by Jupyter
    load = PythonCallable(functions.load,
                          product=File(out / 'data.csv'),
                          dag=dag,
                          name='load')

    clean = NotebookRunner(loader['clean.py'],
                           product={'nb': File(out / 'clean.ipynb'),
                                    'data': File(out / 'ficlean.csv')},
                           dag=dag,
                           kernelspec_name='python3',
                           static_analysis=True)

    plot = NotebookRunner(loader['plot.py'],
                          File(out / 'plot.ipynb'),
                          dag=dag,
                          kernelspec_name='python3',
                          static_analysis=True)

    # declare execution dependencies
    load >> clean >> plot

    return dag