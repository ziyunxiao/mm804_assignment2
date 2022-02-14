from matplotlib.pyplot import plot_date
import numpy as np
import vtk
from vtk.util.colors import brown_ochre, tomato, banana
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera

# 1. Read model
reader = vtk.vtkSTLReader()
reader.SetFileName("dolphin.stl")
reader.Update()
poly_data = reader.GetOutput()


normals = vtk.vtkPolyDataNormals()
# normals.SetInputConnection(reader.GetOutputPort())
normals.AddInputData(poly_data)

# 2. set Plane center to model center
center = poly_data.GetCenter()

plane = vtk.vtkPlane()
# plane.SetOrigin(0, 0, 0)
plane.SetOrigin(center)
plane.SetNormal(-1, 0, 0)


clipper = vtk.vtkClipPolyData()
clipper.SetInputConnection(normals.GetOutputPort())
clipper.SetClipFunction(plane)
clipper.GenerateClipScalarsOn()
clipper.GenerateClippedOutputOn()

# 3. set clipper value
clipper.SetValue(0)
clipMapper = vtk.vtkPolyDataMapper()
clip_data = clipper.GetOutput()
clipMapper.SetInputData(clip_data)
clipMapper.SetInputConnection(clipper.GetOutputPort())
clipMapper.ScalarVisibilityOff()
backProp = vtk.vtkProperty()
backProp.SetDiffuseColor(tomato)
clipActor = vtk.vtkActor()
clipActor.SetMapper(clipMapper)
clipActor.GetProperty().SetColor(brown_ochre)
clipActor.SetBackfaceProperty(backProp)

# 4 cutter
cutEdges = vtk.vtkCutter()
cutEdges.SetInputConnection(normals.GetOutputPort())
cutEdges.SetCutFunction(plane)
cutEdges.GenerateCutScalarsOn()
cutEdges.SetValue(0, 0)
cutStrips = vtk.vtkStripper()
cutStrips.SetInputConnection(cutEdges.GetOutputPort())
cutStrips.Update()
cutPoly = vtk.vtkPolyData()
cutPoly.SetPoints(cutStrips.GetOutput().GetPoints())
cutPoly.SetPolys(cutStrips.GetOutput().GetLines())

cutTriangles = vtk.vtkTriangleFilter()
cutTriangles.SetInputData(cutPoly)
cutMapper = vtk.vtkPolyDataMapper()
cutMapper.SetInputData(cutPoly)
cutMapper.SetInputConnection(cutTriangles.GetOutputPort())
cutActor = vtk.vtkActor()
cutActor.SetMapper(cutMapper)
cutActor.GetProperty().SetColor(banana)
cutActor.VisibilityOn()

# 
restMapper = vtk.vtkPolyDataMapper()
rest_data = clipper.GetClippedOutput()
# restMapper.SetInputData(rest_data)
restMapper.SetInputData(clipper.GetClippedOutput())
restMapper.ScalarVisibilityOff()
restActor = vtk.vtkActor()
restActor.SetMapper(restMapper)
restActor.GetProperty().SetRepresentationToWireframe()


    
#create renderers and add actors of plane and cube


ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(800, 600)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

style = vtkInteractorStyleTrackballCamera()
iren.SetInteractorStyle(style)

# 5. display plane
#Sample the plane
sampler = vtk.vtkSampleFunction()
sampler.SetImplicitFunction(plane)

#Set the bounds to be slightly larger
meshBounds = poly_data.GetBounds()
planeBounds = [0, 0, 0, 0, 0, 0]
for i in range(0,3):
    length = 1.2*(meshBounds[2*i+1] - center[i])
    planeBounds[2*i] = center[i] - length
    planeBounds[2*i+1] = center[i] + length

sampler.SetModelBounds(planeBounds)
sampler.ComputeNormalsOff()
sampler.Update()

#Extract the isosurface at 0
contour = vtk.vtkContourFilter()
contour.SetInputData(sampler.GetOutput())
contour.SetValue(0,0.)
contour.Update()

planeMapper = vtk.vtkPolyDataMapper()
planeMapper.SetInputConnection(contour.GetOutputPort())
planeActor = vtk.vtkActor()
planeActor.SetMapper(planeMapper)
planeActor.GetProperty().SetColor(banana)
planeActor.VisibilityOn()


# display data
ren.AddActor(clipActor)
ren.AddActor(cutActor)
ren.AddActor(restActor)
ren.AddActor(planeActor)

iren.Initialize()
renWin.Render()

# output data
n1 = poly_data.GetNumberOfCells()
n2 = poly_data.GetNumberOfPoints()
print(f"Original Data: Nubmer of Cells:{n1} Number of Points {n2}")

n3 = clip_data.GetNumberOfCells()
n4 = clip_data.GetNumberOfPoints()
print(f"clipped data: Nubmer of Cells:{n3} Number of Points {n4}")

n5 = rest_data.GetNumberOfCells()
n6 = rest_data.GetNumberOfPoints()
print(f"Rest Data: Nubmer of Cells:{n5} Number of Points {n6}")

iren.Start()


