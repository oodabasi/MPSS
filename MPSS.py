import cv2, time, imutils, config, os
import numpy as np
from stl import mesh

#Taking the all-black rows
ignore_row = []
          
#Takes an image in grayscale and transforms its values to binary
#Returns a resized and binary image(numpy_darray)
def import_image(image_name):

    image = cv2.imread(image_name,0)
    (thresh, image_binary) = cv2.threshold(image, 128, 1, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    image_binary = imutils.resize(image_binary,width=config.MAX_SIZE)

    global image_row , image_col
    image_row , image_col = image_binary.shape
    return image_binary

#Checks if the row has a white pixel. If it doesn't appends it to ignore_row
def check_row(image_binary):
    for row in range(len(image_binary)):
        if 1 not in image_binary[row]:
            ignore_row.append(row)

#Counting the files with png extension in current directory.
def png_counter():
    png_count = 0
    for f in os.listdir(str(os.getcwd())):
        if f.endswith('.png'):
            png_count += 1
    return png_count
    
#Takes the image numpy array and for each 1 value in the array it generates a point 
#Then it gives faces to the points
def define_faces(image_array , n_row, n_col, z_value):
    vertices = np.zeros((n_row, n_col, 3))
    #Generating vertices
    for row in range(0, n_row-config.VERTICE_DISTANCE):
        if row in ignore_row:
            continue
        for column in range(0, n_col-config.VERTICE_DISTANCE):
            if image_array[row][column]==0:
                continue
            #It takes the specified Distance value from config and generates points
            vertices[row][column] = (row,column,z_value)
            vertices[row][column+config.VERTICE_DISTANCE] = (row,column+config.VERTICE_DISTANCE,z_value)
            vertices[row+config.VERTICE_DISTANCE][column+config.VERTICE_DISTANCE] = (row+config.VERTICE_DISTANCE,column+config.VERTICE_DISTANCE,z_value)
            vertices[row+config.VERTICE_DISTANCE][column] = (row+config.VERTICE_DISTANCE,column,z_value)

    #Generating faces
    faces = []

    for row in range(0, n_row-config.VERTICE_DISTANCE ,config.VERTICE_DISTANCE):
        if row in ignore_row:
            continue
        for column in range(0, n_col-config.VERTICE_DISTANCE ,config.VERTICE_DISTANCE):

            if image_array[row][column] > config.PIXEL_COLOR_FILTER:
                #For the first triangle of a square
                vertice1 = vertices[row][column]
                vertice2 = vertices[row][column+config.VERTICE_DISTANCE]
                vertice3 = vertices[row+config.VERTICE_DISTANCE][column+config.VERTICE_DISTANCE]
                face1 = np.array([vertice1, vertice2, vertice3])
                #For the second triangle if a square
                vertice1 = vertices[row][column]
                vertice2 = vertices[row+config.VERTICE_DISTANCE][column]
                vertice3 = vertices[row+config.VERTICE_DISTANCE][column+config.VERTICE_DISTANCE]
                face2 = np.array([vertice1,vertice2,vertice3])

                faces.append(face1)
                faces.append(face2) 

    return faces

#Create the stl file from the faces
def create_mesh(faces_total, output_name):
    faces_numpy = np.array(faces_total)

    print("Creating Mesh.")
    surface = mesh.Mesh(np.zeros(faces_numpy.shape[0], dtype = mesh.Mesh.dtype))
    for i ,f in enumerate(faces_total):
        for j in range(3):
            surface.vectors[i][j] = faces_numpy[i][j]
            
    surface.save(output_name)
    print("Mesh created succesfully.")

if __name__ == '__main__':
    start_time = time.time()
    png_count = png_counter()
    faces_total1 = []

    for i in range(config.STARTING_LAYER,png_count,config.SKIP_AMOUNT):

        binary_image = import_image(f"{i}.png")
        check_row(binary_image)
        faces_total = define_faces(binary_image , image_row , image_col , i*config.HEIGHT)
        faces_total1.extend(faces_total)
        ignore_row = []

    create_mesh(faces_total1, config.OUTPUT_NAME)

    print("Time taken: ", time.time() - start_time)
    print("Output file: ", config.OUTPUT_NAME)
    print("Number of faces: ", len(faces_total1))
    print("Number of vertices: ", len(faces_total1)*3)
    print("Number of layers: ", png_count//config.SKIP_AMOUNT)