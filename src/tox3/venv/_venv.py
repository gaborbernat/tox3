import sys
import venv


class EnvB(venv.EnvBuilder):
    executable = None
    bin_path = None

    def post_setup(self, context):
        self.bin_path = context.bin_path
        self.executable = context.env_exe


env_dir = sys.argv[1]
venv.create(env_dir, with_pip=True)
env_build = EnvB(with_pip=True)
env_build.create(env_dir)

print(env_build.bin_path)
print(env_build.executable)
