import vtk
from pathlib import Path
from tkinter import CENTER
from vtkmodules.vtkIOGeometry import (
    vtkBYUReader,
    vtkOBJReader,
    vtkSTLReader
)
from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkIOPLY import vtkPLYReader
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from pprint import pprint
from vtkmodules.vtkIOImage import (
    vtkBMPWriter,
    vtkJPEGWriter,
    vtkPNGWriter,
    vtkPNMWriter,
    vtkPostScriptWriter,
    vtkTIFFWriter
)
from vtkmodules.vtkRenderingCore import vtkWindowToImageFilter

def makePlaneWidget(vtkObj,iren,plane,actor):
    """Make an interactive planeWidget"""

    # Callback function
    def movePlane(obj, events):
        obj.GetPlane(plane)
        actor.VisibilityOn()

    # Associate the line widget with the interactor
    planeWidget = vtk.vtkImplicitPlaneWidget()
    planeWidget.SetInteractor(iren)
    planeWidget.SetPlaceFactor(1.25)
    planeWidget.SetInputData(vtkObj)
    planeWidget.PlaceWidget()
    planeWidget.AddObserver("InteractionEvent", movePlane)
    planeWidget.SetScaleEnabled(0)
    planeWidget.SetEnabled(1)
    planeWidget.SetOutlineTranslation(0)
    planeWidget.GetPlaneProperty().SetOpacity(0.5)

    return planeWidget


def camera_modified_callback(caller, event):
    """
     Used to estimate positions similar to the book illustrations.
    :param caller:
    :param event:
    :return:
    Usage:
        renWin.Render()
        ren.GetActiveCamera().AddObserver('ModifiedEvent', camera_modified_callback)
    """
    print(caller.GetClassName(), "modified")
    # Print the interesting stuff.
    res = f'\tcamera = renderer.GetActiveCamera()\n'
    res += f'\tcamera.SetPosition({", ".join(map("{0:0.6f}".format, caller.GetPosition()))})\n'
    res += f'\tcamera.SetFocalPoint({", ".join(map("{0:0.6f}".format, caller.GetFocalPoint()))})\n'
    res += f'\tcamera.SetViewUp({", ".join(map("{0:0.6f}".format, caller.GetViewUp()))})\n'
    res += f'\tcamera.SetDistance({"{0:0.6f}".format(caller.GetDistance())})\n'
    res += f'\tcamera.SetClippingRange({", ".join(map("{0:0.6f}".format, caller.GetClippingRange()))})\n'
    print(res)

def get_program_parameters():
    import argparse
    description = 'What the program does.'
    epilogue = '''
        An expanded description of what the program does.
   '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue)
    parser.add_argument('filename', help='A required filename.')
    parser.add_argument('figure', default=0, type=int, nargs='?', help='An optional figure number.')
    args = parser.parse_args()
    return args.filename, args.figure


def write_image(file_name, ren_win, rgba=True):
    """
    Write the render window view to an image file.

    Image types supported are:
     BMP, JPEG, PNM, PNG, PostScript, TIFF.
    The default parameters are used for all writers, change as needed.

    :param file_name: The file name, if no extension then PNG is assumed.
    :param ren_win: The render window.
    :param rgba: Used to set the buffer type.
    :return:
    """

    if file_name:
        valid_suffixes = ['.bmp', '.jpg', '.png', '.pnm', '.ps', '.tiff']
        # Select the writer to use.
        parent = Path(file_name).resolve().parent
        path = Path(parent) / file_name
        if path.suffix:
            ext = path.suffix.lower()
        else:
            ext = '.png'
            path = Path(str(path)).with_suffix(ext)
        if path.suffix not in valid_suffixes:
            print(f'No writer for this file suffix: {ext}')
            return
        if ext == '.bmp':
            writer = vtkBMPWriter()
        elif ext == '.jpg':
            writer = vtkJPEGWriter()
        elif ext == '.pnm':
            writer = vtkPNMWriter()
        elif ext == '.ps':
            if rgba:
                rgba = False
            writer = vtkPostScriptWriter()
        elif ext == '.tiff':
            writer = vtkTIFFWriter()
        else:
            writer = vtkPNGWriter()

        windowto_image_filter = vtkWindowToImageFilter()
        windowto_image_filter.SetInput(ren_win)
        windowto_image_filter.SetScale(1)  # image quality
        if rgba:
            windowto_image_filter.SetInputBufferTypeToRGBA()
        else:
            windowto_image_filter.SetInputBufferTypeToRGB()
            # Read from the front buffer.
            windowto_image_filter.ReadFrontBufferOff()
            windowto_image_filter.Update()

        writer.SetFileName(path)
        writer.SetInputConnection(windowto_image_filter.GetOutputPort())
        writer.Write()
    else:
        raise RuntimeError('Need a filename.')


def ReadPolyData(file_name):
    valid_suffixes = ['.g', '.obj', '.stl', '.ply', '.vtk', '.vtp']
    path = Path(file_name)
    if path.suffix:
        ext = path.suffix.lower()
    if path.suffix not in valid_suffixes:
        print(f'No reader for this file suffix: {ext}')
        return None
    else:
        if ext == ".ply":
            reader = vtkPLYReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".vtp":
            reader = vtkXMLPolyDataReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".obj":
            reader = vtkOBJReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".stl":
            reader = vtkSTLReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".vtk":
            reader = vtkPolyDataReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        elif ext == ".g":
            reader = vtkBYUReader()
            reader.SetGeometryFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()

        return poly_data

if __name__ == "__main__":
    data = ReadPolyData("dolphin.stl")
    center = data.GetCenter()

    pprint(center)

