Features planned to be added before first release (stable API):

1. Python should be range specify-able, instead of hard coded against one version:
      ```
      python_requires='>=2.7,!=3.0.*,!=3.1.*'
      ```
2. Plugin system to allow custom env creation (e.g. DPKG/ docker) -
   use https://packaging.python.org/guides/creating-and-discovering-plugins and allow to
   specify plugin order (per entry point)
   - maybe make pip+venv(fallback virtualenv) a built in plugin
3. Reporting at the end of execution
   - console summary
   - xml/json
4. Environment generation
   - allow to generate combination of environments, and then allow conditional settings for per env
  could take a look at Travis/AppVeyor how they do this
5. Various:
   - platform specific tox envs, run only if sys.platforms matches (maybe a general filter logic)
   - look at tox, to find out ``default-passenvs`` we should apply
   - a flag for ```alwayscopy venv```
   - provide a way to allow failing a command (e.g. ``ignore_error``)
   - allow to have envs that may fail (``ignore_outcome``)
6. Finish and write documentation
