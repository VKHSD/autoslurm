#                    )      )   (      (      
#                 ( /(   ( /(   )\ )   )\ )   
#       (   (     )\())  )\()) (()/(  (()/(   
#       )\  )\  |((_)\  ((_)\   /(_))  /(_))  
#      ((_)((_) |_ ((_)  _((_) (_))   (_))_   
#      \ \ / /  | |/ /  | || | / __|   |   \  
#       \ V /     ' <   | __ | \__ \   | |) | 
#        \_/     _|\_\  |_||_| |___/   |___/  

import os
import shutil
import tkinter as tk
from tkinter import filedialog

DOCUMENTS_FOLDER = os.path.join(os.path.expanduser("~"), "Documents")
AUTO_SLURM_FOLDER = os.path.join(DOCUMENTS_FOLDER, "AutoSlurm")
CONFIG_FILE_PATH = os.path.join(AUTO_SLURM_FOLDER, "autoslurm.txt")

os.makedirs(AUTO_SLURM_FOLDER, exist_ok=True)

def get_user_input(prompt, default=""):
    return input(f"{prompt} [{default}]: ").strip() or default

def load_settings():
    settings = {}

    if not os.path.exists(CONFIG_FILE_PATH):
        print("\nSetting up AutoSlurm for the first time.")

        settings["USER_NUMBER"] = get_user_input("TACC user number")
        settings["USERNAME"] = get_user_input("TACC username")
        settings["PROJECT_ID"] = get_user_input("TACC project ID", "ex., CHEM123")
        settings["EMAIL"] = get_user_input("Email for SLURM notifications")

        settings["REGISTRY_FOLDER"] = AUTO_SLURM_FOLDER

        with open(CONFIG_FILE_PATH, "w") as f:
            for key, value in settings.items():
                f.write(f"{key}={value}\n")

        print(f"\nConfiguration saved at {CONFIG_FILE_PATH}")

    else:
        print(f"\nLoading configuration from {CONFIG_FILE_PATH}")
        with open(CONFIG_FILE_PATH, "r") as f:
            for line in f:
                key, value = line.strip().split("=", 1)
                settings[key] = value

    return settings

def process_gjf_file(input_path, output_path, settings):
    gauss_dir = f"/home1/{settings['USER_NUMBER']}/{settings['USERNAME']}/gaussian"
    job_name = os.path.splitext(os.path.basename(input_path))[0]

    new_header = f"""%nprocshared=12
%rwf={gauss_dir}/{job_name}.rwf
%chk={gauss_dir}/{job_name}.chk
%mem=56GB
%NProcs=12
"""

    with open(input_path, "r") as f:
        lines = f.readlines()

    modified_lines = lines[1:]

    with open(output_path, "w", newline="\n") as f:
        f.write(new_header)
        f.writelines(modified_lines)

    print(f"Processed: {output_path}")

def create_slurm_script(filename, settings):
    job_name = os.path.splitext(filename)[0]
    gauss_dir = f"/home1/{settings['USER_NUMBER']}/{settings['USERNAME']}/gaussian"

    slurm_content = f"""#!/bin/bash
#SBATCH -J {job_name}
#SBATCH -o {job_name}.%j.out
#SBATCH -e {job_name}.%j.error
#SBATCH -p normal
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -A {settings['PROJECT_ID']}
#SBATCH -t 47:50:00
#SBATCH --mail-user={settings['EMAIL']}
#SBATCH --mail-type=all

echo "Starting job on $(date)"
module load gaussian
module list

mkdir -p {gauss_dir}

export GAUSS_SCRDIR={gauss_dir}

time g16 < {gauss_dir}/{job_name}.inp > {gauss_dir}/{job_name}.log
"""

    slurm_path = os.path.join(settings['REGISTRY_FOLDER'], f"{job_name}.slurm")

    with open(slurm_path, "w", newline="\n") as f:
        f.write(slurm_content)

    print(f"SLURM created: {slurm_path}")

def select_and_process_files():
    settings = load_settings()
    os.makedirs(settings['REGISTRY_FOLDER'], exist_ok=True)

    print("\nSelect .gjf files...")
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select .gjf Files", filetypes=[("Gaussian Job Files", "*.gjf")])

    if not file_paths:
        print("No files selected.")
        return

    for file_path in file_paths:
        filename = os.path.basename(file_path)
        base_name, ext = os.path.splitext(filename)

        if ext.lower() != ".gjf":
            print(f"Skipping: {filename} (not a .gjf file)")
            continue

        new_inp_filename = f"{base_name}.inp"
        new_inp_path = os.path.join(settings['REGISTRY_FOLDER'], new_inp_filename)

        process_gjf_file(file_path, new_inp_path, settings)

        gauss_dir = f"/home1/{settings['USER_NUMBER']}/{settings['USERNAME']}/gaussian"
        os.makedirs(gauss_dir, exist_ok=True)

        shutil.copy(new_inp_path, os.path.join(gauss_dir, f"{base_name}.inp"))
        print(f"Moved {filename} → {gauss_dir}")

        create_slurm_script(base_name, settings)

    print("\nAll files processed!")

if __name__ == "__main__":
    select_and_process_files()
