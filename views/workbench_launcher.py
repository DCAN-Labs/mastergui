import os
import glob
import subprocess


def default_map_dir(config):
    return config._data["default_maps"]


def default_map_paths(config):
    root_dir = default_map_dir(config)

    return glob.glob(os.path.join(root_dir, "*"))


def launch(config, cifti_output_path):
    base_image_paths = default_map_paths(config)

    # wb_view_path_prefix is an optional key.  if the system path has wb_view in it it may be unnecessary
    # on a local mac a value of /Applications/connectomeworkbench/bin_macosx64/ might work though it depends of course on your setup
    wb_view_part = os.path.join(config.getOptional("wb_view_path_prefix"), "wb_view")

    all_parts = [wb_view_part] + base_image_paths + [cifti_output_path]

    subprocess.Popen(all_parts)
