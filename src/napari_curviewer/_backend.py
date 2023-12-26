""" Compute the direction cosines from a list of points
    The direction cosines are the vectors between each point
    and the next point in the list. The other two vectors are
    computed by cross product in a tricky way.
"""
import csv

import numpy as np
import vtk
from scipy.interpolate import splev, splprep
from vedo import utils


def create_direction_cosines_from_point_list(polyline):
    normals = []
    axiss0 = []
    axiss1 = []
    axiss2 = []
    N = len(polyline)
    for i in range(N - 1):
        p0 = polyline[i]
        p1 = polyline[i + 1]
        # Weird, but for radiological convention, the direction cosines are inverted
        normals.append([-p1[0] + p0[0], -p1[1] + p0[1], -p1[2] + p0[2]])

    # Compute the first orthogonal axis by choosing the axis that is the far away from normal
    normal = normals[0]
    axis2 = utils.versor(normal)
    axisTemp = [0, -1, 0] if np.abs(normal[1]) < 0.9999 else [-1, 0, 0]
    axis0 = utils.versor(np.cross(axisTemp, axis2))
    axis1 = utils.versor(np.cross(axis2, axis0))
    axiss0.append(axis0)
    axiss1.append(axis1)
    axiss2.append(axis2)

    # Compute iteratively the following orthogonal axis
    for i in range(1, N - 1):
        normal = normals[i]
        axis2 = utils.versor(normal)
        axis0Prev = axiss0[i - 1]
        axis1 = utils.versor(np.cross(axis2, axis0Prev))
        axis0 = utils.versor(np.cross(axis1, axis2))
        axiss0.append(axis0)
        axiss1.append(axis1)
        axiss2.append(axis2)

    return axiss0, axiss1, axiss2


def compute_slices_of_vtkImageData_along_curve(
    vtkImageData,
    curve,
    output_size=None,
    output_spacing=None,
    debug=False,
):
    if output_size is None:
        output_size = [300, 300]
    if output_spacing is None:
        output_spacing = [1, 1, 1]
    # Compute the direction cosines from the curve
    axiss0, axiss1, axiss2 = create_direction_cosines_from_point_list(curve)

    # Compute the slices
    slices = []
    for i in range(len(axiss0)):
        slic = vtk.vtkImageReslice()
        slic.SetInputData(vtkImageData)
        slic.SetResliceAxesDirectionCosines(
            axiss0[i][0],
            axiss0[i][1],
            axiss0[i][2],
            axiss1[i][0],
            axiss1[i][1],
            axiss1[i][2],
            axiss2[i][0],
            axiss2[i][1],
            axiss2[i][2],
        )
        slic.SetResliceAxesOrigin(curve[i])
        slic.SetOutputDimensionality(2)
        slic.SetInterpolationModeToLinear()
        slic.SetOutputSpacing(output_spacing)
        slic.SetOutputExtent(
            0, output_size[0] - 1, 0, output_size[1] - 1, 0, 1
        )
        slic.SetOutputOrigin(
            -(output_size[0] * 0.5 - 0.5) * output_spacing[0],
            -(output_size[1] * 0.5 - 0.5) * output_spacing[1],
            0,
        )
        slic.Update()
        slices.append(slic)
        if debug:
            print(
                "Slice "
                + str(i)
                + " Origin="
                + str(curve[i])
                + " DirectionCosines="
                + str(axiss0[i])
                + " | "
                + str(axiss1[i])
                + " | "
                + str(axiss2[i])
            )
    return slices


def get_curve(csv_file):
    # Load the curve from the csv file
    curve_points = []
    print(csv_file)
    with open(csv_file, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in reader:
            curve_points.append([float(row[0]), float(row[1]), float(row[2])])
    curve_points = resampleCurve(curve_points, 1)
    return curve_points


def resampleCurve(curve, spacing):
    # Convert the curve to a numpy array
    curve = np.array(curve)
    print("Curve shape=" + str(curve.shape))

    # Calculate the total length of the curve
    curve_length = np.sum(np.sqrt(np.sum(np.diff(curve, axis=0) ** 2, axis=1)))

    # Calculate the number of points needed to achieve the desired spacing
    num_points = int(np.ceil(curve_length / spacing))

    # Resample the curve using splines
    tck, u = splprep(curve.T, s=0, per=False)
    u_new = np.linspace(0, 1, num_points)
    curve_resampled = np.column_stack(splev(u_new, tck, der=0))

    return curve_resampled.tolist()


def reslice_tiff_image_along_curve(
    volume_path="/home/rfernandez/Bureau/Temp/TEST/raw.tif",
    csv_path="/home/rfernandez/Bureau/Temp/TEST/line.csv",
    output_path="/home/rfernandez/Bureau/Temp/TEST/output.tif",
):
    # Read the central line as a list of even spaced points (every pixel) from the list of xyz points stored in the csv
    curve_points = get_curve(csv_path)

    # Read the raw volume as a vtkImageData
    reader = vtk.vtkTIFFReader()
    reader.SetFileName(volume_path)
    reader.Update()
    vtkImageData = reader.GetOutput()

    # Compute the reslicing of the volume along the curve and combine the slices into a single volume
    slices = compute_slices_of_vtkImageData_along_curve(
        vtkImageData, curve_points, output_size=[50, 50]
    )
    append_filter = vtk.vtkImageAppend()
    append_filter.SetAppendAxis(2)  # Assuming Z-axis is the stacking direction
    for slic in slices:
        append_filter.AddInputData(slic.GetOutput())
    append_filter.Update()

    # Write slices, a tab of vtkResliceImage into a single multi slice tiff
    writer = vtk.vtkTIFFWriter()
    writer.SetFileName(output_path)
    writer.SetInputData(append_filter.GetOutput())
    writer.Write()


# reslice_tiff_image_along_curve()
