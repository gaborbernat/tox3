from pathlib import Path

import pytest

from toxn.config import ToxConfig


@pytest.mark.network
@pytest.mark.venv
@pytest.mark.asyncio_process_pool
async def test_setuptools_build(project):
    proj = project({
        'pyproject.toml': f'''
[build-system]
requires = ['setuptools >= 38.2.4']
build-backend = 'setuptools.build_meta'

[tool.toxn]
default_tasks = ['py']

[tool.toxn.task.build]
python="python"  
        ''',
        'setup.py': f'''
            from setuptools import setup, find_packages
            setup(
                name='package',
                version='0.1.1',
                packages=find_packages('src'),
                python_requires='>=3.6',
                setup_requires=['setuptools_scm >= 1.15.6, <2'],
                install_requires=['py'])
        ''',
        Path('src') / 'main.py': f'''
            def main():
                print("test")
        '''})
    result = await proj.run()
    assert result == 0
    conf: ToxConfig = proj.conf_obj

    assert conf.build.envsitepackagesdir
    assert conf.build.envbindir
    assert conf.build.envpython
    assert conf.build.envdir
