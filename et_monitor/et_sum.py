import h5py
import numpy as np
import os
from datetime import datetime

def process_et_files(input_dir, output_dir, et_range=None, date_range=("01-01", "12-31")):
    """
    Process ET files by filtering, summing, and saving results with metadata.

    Args:
        input_dir (str): Directory containing input HDF5 files.
        output_dir (str): Directory to save output HDF5 files.
        et_range (tuple, optional): Tuple of (min_ET, max_ET) for filtering valid ET values.
        date_range (tuple, optional): Tuple of (date_start, date_end) for filtering date range.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    today = datetime.today().date().strftime('%d/%m/%Y')
    date_range_start, date_range_end = date_range

    # Iterate through all input HDF5 files
    for file_name in os.listdir(input_dir):
        if file_name.startswith("ETMonitor.DailyET") and file_name.endswith(".h5"):
            input_path = os.path.join(input_dir, file_name)

            # Extract year and other identifiers from the file name
            parts = file_name.split(".")
            year = parts[2][:4]
            tile = parts[3]

            first_day = datetime(int(year), 1, 1)

            date_start_str = year + "-" + date_range_start
            date_start = datetime.strptime(date_start_str, '%Y-%m-%d')
            doy_start = (date_start - first_day).days + 1

            date_end_str = year + "-" + date_range_end
            date_end = datetime.strptime(date_end_str, '%Y-%m-%d')
            doy_end = (date_end - first_day).days + 1

            # print("doy [", doy_start, ", ",  doy_end, "]")

            with h5py.File(input_path, "r") as f:
                et_data = f["ET"][doy_start -1: doy_end]  # Shape: (365, 1200, 1200)

                if et_range:
                    min_et, max_et = et_range
                    et_data = np.where((et_data >= min_et) & (et_data <= max_et), et_data, 0)
                et_sum = np.sum(et_data, axis=0)
                # et_sum = np.multiply(et_sum, 0.01)

                global_attrs = dict(f.attrs)
                et_attrs = dict(f["ET"].attrs)

                # Adjust global or variable attributes
                global_attrs["Processed_By"] = "zhangych"
                global_attrs["Contact Person"] = "zhangych"
                global_attrs["EMail"] = "zhangych@lreis.ac.cn"

                global_attrs["Reference"] = ""
                global_attrs["TemporalResolution"] = "Yearly"
                global_attrs["AlgorithmName"] = ""
                global_attrs["DataSize"] = "1200S, 1200S, 1S"
                global_attrs["Institute"] = "Institute of Geographic Sciences and Natural Resources Research, CAS"
                global_attrs["FileCreationTime"] = today

                et_attrs["LongName"] ="total evapotranspiration (mm)"
                et_attrs["Description"] = "Summed ET values across year/season"

            output_file_name = "ETMonitor.SumET.{}.{}.h5".format(year, tile)
            output_path = os.path.join(output_dir, output_file_name)

            with h5py.File(output_path, "w") as out_f:
                et_sum_dataset = out_f.create_dataset("ET", data=et_sum, dtype=np.dtype(np.int32))
                out_f.attrs.update(global_attrs)  # Global attributes
                et_sum_dataset.attrs.update(et_attrs)  # Variable attributes
                # print(f"Saved summed ET and metadata to {output_path}")
                print("Saved summed ET and metadata to {}.".format(output_path))


# Example usage
input_dir = os.path.join(os.getcwd(), "data")   # Replace with the path to your input files
output_dir = os.path.join(os.getcwd(), "data2") # Replace with the desired output directory

et_range = (0, 5000)    # ET range filter: valid ET values between 0 and 5000 ( 50mm )
# date_range = ("01-01", "12-31")
date_range = ("04-01", "10-25")

process_et_files(input_dir, output_dir, et_range, date_range)