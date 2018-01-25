Features planned to be added before stable:

1. Better configuration fine tune:
   a. support env var (with default) substitution
   b. support posargs default value
   c. ability to refer to other configs (e.g. ``deps = tox3.deps``
2. Python should be range specify-able, instead of hard coded against one version:
  ```
  python_requires='>=2.7,!=3.0.*,!=3.1.*'
  ```
3. Plugin system to allow custom env creation (e.g. DPKG/ docker) -
   use https://packaging.python.org/guides/creating-and-discovering-plugins and allow to
   specify plugin order (per entry point)
   maybe make the whole pip thing a built in plugin
4. Reporting
   - console summary
   - xml/json
5. Environment generation
  - allow to generate combination of environments, and then allow conditional settings for per env
  could take a look at Travis/AppVeyor how they do this
6. Various:
   - platform specific tox envs, run only if sys.platforms matches (maybe a general filter logic)
   - look at tox, to find out ``default-passenvs`` we should apply
   - a flag for ```alwayscopy venv```
   - provide a way to allow failing a command (e.g. ``ignore_error``)
   - allow to have envs that may fail (``ignore_outcome``)
7. Finish and write documentation
