import multiprocessing as mp
from subprocess import Popen, PIPE
import shlex
from pathlib import Path


class AfniRunner:
    """
    Class to run afni commands in python
    """

    def __init__(self, env_path="/opt/afni", num_processes=4):
        """

        :param num_processes: number of CPUs to run in parallel
        """
        self.num_processes = num_processes
        self.pool = mp.Pool(self.num_processes)
        self.env_path = [env_path]

    def add_to_env(self, path):
        self.env_path.append(path)

    def run_cmd(self, cmd):
        env = {"PATH": ":".join(self.env_path)}
        self.print_cmd(cmd)
        p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, env=env)
        stdout, stderr = p.communicate()
        print(stdout.decode("UTF-8"))
        print(stderr.decode("UTF-8"))
        return p.returncode, stdout, stderr

    def preproc_cmds(self, cmd):
        """Multiline cmds are nice to look at but bad to run"""
        return " ".join(cmd.split())

    def run_motion_correction(self, image, output_name="NULL"):
        """Run 3dvolreg, override to change command"""
        VOLREG_CMD = """
        3dvolreg -Fourier -1Dfile {out_folder}/{name}.1D
        -prefix {output_name} 
        -zpad 4 
        {filepath}
        """
        p = Path(image)
        out_folder = p.parent  # out_folder is the same folder as image
        name = p.name.split(".")[0]  # output name

        cmd = VOLREG_CMD.format(out_folder=out_folder, name=name, output_name=output_name, filepath=image)
        cmd = self.preproc_cmds(cmd)
        ret, stdout, stderr = self.run_cmd(cmd)
        return ret, "{out_folder}/{name}.1D".format(out_folder=out_folder, name=name)


    def test_afni(self):
        ret, _, _ = self.run_cmd("afni -ver")
        # if return code != 0
        if ret:
            raise FileNotFoundError(
                "afni -ver did not run on the system. is the path right?"
            )
        else:
            print("afni -ver was successful")
        return ret

    @staticmethod
    def print_cmd(cmd_str):
        print(cmd_str.replace(" -", "\n -"))
