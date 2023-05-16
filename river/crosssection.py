import os
import numpy as np
import matplotlib.pyplot as plt


def find_min_value_and_index(arr):
    min_value = min(arr)
    min_index = arr.index(min_value)
    return min_value, min_index


def find_max_value_and_index_until(arr, min_index):
    sub_array = arr[:min_index]
    max_value = max(sub_array)
    max_index = sub_array.index(max_value)
    return max_value, max_index


def find_max_value_and_index_from(arr, min_index):
    sub_array = arr[min_index:]
    max_value = max(sub_array)
    max_index = sub_array.index(max_value) + min_index
    return max_value, max_index


# assuming elevations[0], elevations[len - 1] are valid ends that are heigher
# than all their neighbers
def calculate_polygon_areas(distances, elevations, target_elevation):
    min_end_elevation = min(elevations[0], elevations[-1])
    if target_elevation > min_end_elevation:
        return [0] * (len(elevations) - 1)
    polygon_areas = []
    for i in range(1, len(distances)):
        if elevations[i-1] >= target_elevation and elevations[i] >= target_elevation:
            polygon_areas.append(0)
            continue  # Skip line segments below the target elevations
        elif elevations[i-1] < target_elevation and elevations[i] < target_elevation:
            a = 0.5 * (distances[i] - distances[i-1]) * ((target_elevation - elevations[i]) + (target_elevation - elevations[i - 1]))
            polygon_areas.append(a)
        elif elevations[i-1] < target_elevation and elevations[i] >= target_elevation:
            x_intersect = distances[i-1] + (distances[i] - distances[i-1]) * (target_elevation - elevations[i-1]) / (elevations[i] - elevations[i-1])
            a = 0.5 * (x_intersect - distances[i-1]) * (target_elevation - elevations[i - 1])
            polygon_areas.append(a)
        elif elevations[i-1] >= target_elevation and elevations[i] < target_elevation:
            x_intersect = distances[i-1] + (distances[i] - distances[i-1]) * (target_elevation - elevations[i-1]) / (elevations[i] - elevations[i-1])
            a = 0.5 * (distances[i] - x_intersect) * (target_elevation - elevations[i])

            polygon_areas.append(a)
        else:
            print("something go wrong")

    return polygon_areas


def calculate_x_intersects(distances, elevations, target_elevation):
    min_end_elevation = min(elevations[0], elevations[-1])
    if target_elevation > min_end_elevation:
        return []

    x_intersects = []
    for i in range(1, len(distances)):
        if (elevations[i-1] >= target_elevation and elevations[i] >= target_elevation) or (elevations[i-1] < target_elevation and elevations[i] < target_elevation):
            continue
        elif (elevations[i-1] < target_elevation and elevations[i] >= target_elevation) or (elevations[i-1] >= target_elevation and elevations[i] < target_elevation):
            x_intersect = distances[i-1] + (distances[i] - distances[i-1]) * (target_elevation - elevations[i-1]) / (elevations[i] - elevations[i-1])
            x_intersects.append(x_intersect)
        else:
            print("something go wrong")

    return x_intersects


def calculate_polygon_area_with_target_elevation(distances, elevations, target_elevation):
    min, min_index = find_min_value_and_index(elevations)
    end_left, end_left_index = find_max_value_and_index_until(elevations, min_index)
    end_right, end_right_index = find_max_value_and_index_from(elevations, min_index)
    cross_section_range_msg = f'river cross section: [{distances[end_left_index]}, {distances[end_right_index]}] -- index: [{end_left_index}, {end_right_index}].'
    print(cross_section_range_msg)

    distances = distances[end_left_index: end_right_index + 1]
    elevations = elevations[end_left_index: end_right_index + 1]
    # Calculate polygon areas
    polygon_areas = calculate_polygon_areas(distances, elevations, target_elevation)

    return distances, elevations, polygon_areas


def calculate_cross_section_area_elevations(crs_id, distances, elevations, target_elevation_parameters):
    min_elv, min_index = find_min_value_and_index(elevations)
    end_left, end_left_index = find_max_value_and_index_until(elevations, min_index)
    end_right, end_right_index = find_max_value_and_index_from(elevations, min_index)
    cross_section_range_msg = f'river cross section: [{distances[end_left_index]}, {distances[end_right_index]}] -- index: [{end_left_index}, {end_right_index}].'
    print(cross_section_range_msg)

    min_target_elevation, max_target_elevation, elevation_count = get_target_elevation_parameter(target_elevation_parameters, crs_id, min_elv, min(end_left, end_right))

    target_elevations = np.linspace(min_target_elevation, max_target_elevation, num=elevation_count).tolist()

    distances = distances[end_left_index: end_right_index + 1]
    elevations = elevations[end_left_index: end_right_index + 1]
    # Calculate polygon areas
    results = []
    for target_elevation in target_elevations:
        polygon_areas = calculate_polygon_areas(distances, elevations, target_elevation)
        total_area = sum(polygon_areas)

        x_intersects = calculate_x_intersects(distances, elevations, target_elevation)
        width = 0
        if len(x_intersects) >= 2:
            width = x_intersects[-1] - x_intersects[0]

        results.append([target_elevation, total_area, width])

    return results


def get_target_elevation_parameter(target_elevation_parameters, crs_id, default_min_target_elevation, default_max_target_elevation):
    if crs_id in target_elevation_parameters:
        target_elevation_parameter = target_elevation_parameters[crs_id]
        if "min_elevation" in target_elevation_parameter:
            min_target_elevation = target_elevation_parameter["min_elevation"]
        else:
            min_target_elevation = default_min_target_elevation

        if "max_elevation" in target_elevation_parameter:
            max_target_elevation = target_elevation_parameter["max_elevation"]
        else:
            max_target_elevation = default_max_target_elevation
        elevation_count = target_elevation_parameter["count"]
    else:
        min_target_elevation = default_min_target_elevation
        max_target_elevation = default_max_target_elevation
        elevation_count = target_elevation_parameters["0"]["count"]
        print(f"{crs_id} use default parameters: {min_target_elevation}  {max_target_elevation}  {elevation_count}")

    return min_target_elevation, max_target_elevation, elevation_count

def read_cross_river_data(filename):
    distances = []
    elevations = []

    with open(filename, 'r') as file:
        next(file)  # Skip the header line
        for line in file:
            line = line.strip()
            if line:
                data = line.split()
                distances.append(float(data[0]))
                elevations.append(float(data[1]))

    return distances, elevations


def write_cross_river_sections_data(filename, results):
    lines = []

    h_elev = "Elevation"
    h_area = "Area"
    h_width = "Width"
    line = f"{h_elev:>10}\t{h_area:>10}\t{h_width:>10}\n"
    lines.append(line)

    for res in results:
        line = f"{res[0]:10.2f}\t{res[1]:10.2f}\t{res[2]:10.2f}\n"
        lines.append(line)

    with open(filename, 'w') as file:
        file.writelines(lines)


def read_parameters(filename, default_target_elevation_count):
    parameters = {}

    if not os.path.exists(filename):
        return parameters

    with open(filename, 'r') as file:
        next(file)  # Skip the header line
        for line in file:
            line = line.strip()
            if line:
                data = line.split()
                if len(data) == 4:
                    crs_id = data[0]
                    count = int(data[1])
                    min_elevation = float(data[2])
                    max_elevation = float(data[3])
                    if min_elevation >= max_elevation:
                        print(f"Error: {crs_id} min_target_elevation >= max_target_elevation")
                    parameters[crs_id] = {
                        "crs_id": crs_id,
                        "min_elevation": min_elevation,
                        "max_elevation": max_elevation,
                        "count": count
                    }
                elif len(data) == 2:
                    crs_id = data[0]
                    count = int(data[1])
                    parameters[crs_id] = {
                        "crs_id": crs_id,
                        "count": count
                    }
                else:
                    continue
    parameters["0"] = {
        "crs_id": "0",
        "count": default_target_elevation_count
    }
    return parameters


# help and test functions
def init_data():
    # Cross river section data
    distances = [
        0.00, 29.80, 59.61, 89.41, 119.21, 149.01, 178.82, 208.62, 238.42, 268.23,
        298.03, 327.83, 357.64, 387.44, 417.24, 447.04, 476.85, 506.65, 536.45, 566.26,
        596.06, 625.86, 655.67, 685.47, 715.27, 745.07, 774.88, 804.68, 834.48, 864.29, 894.09
    ]
    elevations = [
        1040.66, 1040.70, 1041.15, 1041.35, 1039.90, 1040.76, 1040.95, 1040.89, 1040.60, 1040.10,
        1040.19, 1040.19, 1040.15, 1040.22, 1039.76, 1039.54, 1039.55, 1039.61, 1039.89, 1040.03,
        1040.19, 1041.48, 1042.46, 1042.42, 1042.66, 1041.77, 1041.32, 1041.48, 1041.96, 1041.71,
        1042.32
    ]
    return distances, elevations


def init_parameters():
    min_target_elevation = 1039.6
    max_target_elevation = 1043
    elevation_count = 10

    return min_target_elevation, max_target_elevation, elevation_count


def test():
    # distances, elevations = init_data()
    distances, elevations = read_cross_river_data("data/crs002.txt")
    target_elevation = 1041
    distances, elevations, polygon_areas = calculate_polygon_area_with_target_elevation(distances, elevations, target_elevation)

    # Plotting the cross river section and the polygons
    plt.figure(figsize=(10, 6))
    plt.plot(distances, elevations, '-o', label='Cross River Section')
    target_elevations = [1039.60, 1039.98, 1040.36, 1040.73, 1041.11, 1041.49, 1041.87,  1042.24, 1042.62, 1043.00]
    for target_elevation in target_elevations:
        plt.axhline(y=target_elevation, color='r', linestyle='--', label='Elevation 1041')

    target_elevation = 1041
    # Display polygon areas as text annotations
    for i, area in enumerate(polygon_areas):
        plt.annotate(f'{area:.1f}', xy=(distances[i], target_elevation), xytext=(10, 10), textcoords='offset points', ha='center')

    plt.xlabel('Distance')
    plt.ylabel('Elevation')

    print(polygon_areas)


def test3():
    parameters = read_parameters("parameters.txt")
    for k, v in parameters.items():
        print(k, v)


def demo():
    # ------------------------------------------------------
    # cross_river_section_id = "crs001"
    input_dir = "data"
    output_dir = "results"
    parameters_filename = "parameters.txt"
    default_target_elevation_count = 5

    # sample_data_filename = f"{input_dir}/{cross_river_section_id}.txt"
    # ------------------------------------------------------
    parameters = read_parameters(parameters_filename, default_target_elevation_count)

    for filename in os.listdir(input_dir):
        print("filename: ", filename)
        sample_data_filename = os.path.join(input_dir, filename)
        if not os.path.isfile(sample_data_filename):
            continue

        cross_river_section_id = filename.split(".")[0]
        distances, elevations = read_cross_river_data(sample_data_filename)

        # min_target_elevation, max_target_elevation, elevation_count =  init_parameters()

        elevation_areas = calculate_cross_section_area_elevations(cross_river_section_id, distances, elevations, parameters)
        out_file = f"{output_dir}/ea_{cross_river_section_id}.txt"
        write_cross_river_sections_data(out_file, elevation_areas)


if __name__ == "__main__":
    demo()
    # test()
