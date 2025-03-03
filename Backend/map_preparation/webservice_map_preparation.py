import os
import shutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import cv2
import numpy as np

from Backend.map_preparation.FileUploaded import FileUploaded
from Backend.map_preparation.service_map_preparation import cut_image_path, image_path, logger, UPLOAD_DIR, FILENAME

app = FastAPI()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

@app.post('/save')
async def save_file(b: bytes, name: str) -> JSONResponse:
    """sets the image path and saves the image to uploaded_files

    Args:
        b (bytes): bytes of the uploaded image
        name (str): name of the uploaded image

    Returns:
        JSONResponse: FileUploaded with success message and bool
    """
    global image_path
    image_path = os.path.join(UPLOAD_DIR, name)
    logger.info(f'image path set to {image_path}')

    # Iterate over the files and directories in the specified directory
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove the directory and all its contents
        except Exception as e:
            return JSONResponse(content=FileUploaded(success=False,
                                   message=f'Failed to delete {file_path}. Reason: {e}'))
            
    with open(image_path, "wb") as buffer:
        buffer.write(b)

    response_body = FileUploaded(filename=FILENAME,
                           location=image_path,
                           success=True,
                           message=f'Upload of {FILENAME} in {image_path} successful')
    return JSONResponse(content=response_body.model_dump()) 

@app.post('/pencil_point')
async def addPoint(x: float, y: float, thickness: int) -> JSONResponse:
    """modifies the image by drawing a circle at the specified point.
    Uses the cv2.circle algorithm

    Args:
        x (float): x-coordinate of the point
        y (float): y-coordinate of the point
        thickness (int): Thickness of the circle

    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    x = int(x)
    y = int(y)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Modify the image based on click (e.g., draw a circle at the clicked position)
    cv2.circle(image, (x, y), thickness, BLACK, -1)  # black circle
        
    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully"})

@app.post('/pencil_line')
async def addLine(start_point: tuple, end_point: tuple, thickness: int) -> JSONResponse:
    """Modifying the image by drawing a line between the two points. 
    Uses the cv2.line function

    Args:
        start_point (tuple): x- and y coordinate of the start point
        end_point (tuple): x- and y coordinate of the end point
        thickness (int): thickness of the line

    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    logger.info(f'startpoint is {start_point}, endpoint is {end_point}')
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Convert points to integers
    start_point = (int(start_point[0]), int(start_point[1]))
    end_point = (int(end_point[0]), int(end_point[1]))
    
    cv2.line(image, start_point, end_point, BLACK, thickness=thickness)
    
    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully"})

@app.post('/draw_square')
async def drawSquare(start_point: tuple, end_point: tuple) -> JSONResponse:
    """Modifies the image by drawing a square between the two points.
    Uses the cv2.rectangle function.

    Args:
        start_point (tuple): x- and y coordinate of the start point
        end_point (tuple): x- and y coordinate of the end point

    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    logger.info(f'startpoint is {start_point}, endpoint is {end_point}')
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Convert points to integers
    start_point = (int(start_point[0]), int(start_point[1]))
    end_point = (int(end_point[0]), int(end_point[1]))
    
    cv2.rectangle(image, start_point, end_point, BLACK, -1)

    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully"})

@app.post('/eraser_click')
async def erasePoint(x: float, y: float, thickness: int) -> JSONResponse:
    """modifies the image by erasing a circle at the specified point.
    Uses the cv2.circle algorithm. Draws a white circle essentially.

    Args:
        x (float): x-coordinate of the point
        y (float): y-coordinate of the point
        thickness (int): Thickness of the circle

    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    x = int(x)
    y = int(y)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Modify the image based on click (e.g., draw a circle at the clicked position)
    cv2.circle(image, (x, y), thickness, WHITE, -1)  # Red circle

    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully", "x": x, "y": y})

@app.post('/eraser_line')
async def eraseLine(start_point: tuple, end_point: tuple, thickness: int) -> JSONResponse:
    """Modifying the image by erasing a line between the two points. 
    Uses the cv2.line function. Draws a while line essentially.

    Args:
        start_point (tuple): x- and y coordinate of the start point
        end_point (tuple): x- and y coordinate of the end point
        thickness (int): thickness of the line

    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    logger.info(f'startpoint is {start_point}, endpoint is {end_point}')
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Convert points to integers
    start_point = (int(start_point[0]), int(start_point[1]))
    end_point = (int(end_point[0]), int(end_point[1]))
    
    cv2.line(image, start_point, end_point, WHITE, thickness=thickness)
    
    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully"})

@app.post('/eraser_square')
async def eraseSquare(start_point: tuple, end_point: tuple) -> JSONResponse:
    """Modifies the image by erasing a square between the two points.
    Uses the cv2.rectangle function. Draws a white square essentially. 

    Args:
        start_point (tuple): x- and y coordinate of the start point
        end_point (tuple): x- and y coordinate of the end point

    Raises:
        HTTPException: 404 if image is not found

    Returns:
        JSONResponse: message if successful
    """
    logger.info(f'startpoint is {start_point}, endpoint is {end_point}')
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)

    # Convert points to integers
    start_point = (int(start_point[0]), int(start_point[1]))
    end_point = (int(end_point[0]), int(end_point[1]))
    
    cv2.rectangle(image, start_point, end_point, WHITE, -1)

    # Save the modified image
    cv2.imwrite(image_path, image)

    return JSONResponse(content={"message": "Image modified successfully"})

@app.post('/cut_out')
async def cutOut(start_point: tuple, end_point: tuple) -> JSONResponse:
    """Cuts the image defined by start- and end point

    Args:
        start_point (tuple): x- and y coordinate of the start point
        end_point (tuple): x- and y coordinate of the end point

    Raises:
        HTTPException: 404 if image is not found
        HTTPEXception: 400 if coordinates are invalid

    Returns:
        JSONResponse: message if modified successfully
    """
    global cut_image_path
    logger.info(f'startpoint is {start_point}, endpoint is {end_point}')
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Load the image
    image = cv2.imread(image_path)


    # Convert points to integers
    start_point = (int(start_point[0]), int(start_point[1]))
    end_point = (int(end_point[0]), int(end_point[1]))

    # Calculate the center and size of the rectangle
    center_x = (start_point[0] + end_point[0]) / 2
    center_y = (start_point[1] + end_point[1]) / 2
    width = abs(end_point[0] - start_point[0])
    height = abs(end_point[1] - start_point[1])

    # Ensure the coordinates are within the image bounds
    height_img, width_img = image.shape[:2]
    center_x = max(0, min(width_img, center_x))
    center_y = max(0, min(height_img, center_y))
    width = max(0, min(width_img, width))
    height = max(0, min(height_img, height))

    logger.info(f'center_x = {center_x}')
    logger.info(f'center_y = {center_y}')
    logger.info(f'width = {width}')
    logger.info(f'height = {height}')
    
    if width == 0 or height == 0:
        raise HTTPException(status_code=400, detail="Invalid coordinates: width or height cannot be zero.")

    # Extract the rectangle region
    cut_image = cv2.getRectSubPix(image, (int(width), int(height)), (center_x, center_y))

    # Save the modified image
    cut_image_path = os.path.join(UPLOAD_DIR, 'cut_image.jpg')
    cv2.imwrite(cut_image_path, cut_image)
        
    return JSONResponse(content={"message": "Image modified successfully"})

        
@app.post('/fillArea')
async def fillArea(x: float, y: float) -> JSONResponse:
    """Creates an image where the area defined by the point is filled with red color.
    Uses the floodfill algorithm of cv2

    Args:
        x (float): x-coordinate of the point
        y (float): y-coordinate of the point

    Raises:
        HTTPException: 404 if image is not found or not properly loaded

    Returns:
        JSONResponse: success message if successful with image path  
    """
    x = int(x)
    y = int(y)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise HTTPException(status_code=404, detail="Failed to load image")

    # Flood fill
    # gets the image size in height and width. 
    # Channels of the picture are not necessary, hence the slicing
    h, w = image.shape[:2]
    # flood fill requires a mask which is two pixels bigger in h and w dimension
    mask = np.zeros((h+2, w+2), np.uint8)
    flood_fill_color = (0, 0, 255)  # Fill color (red)
    seed_point = (x, y)
    lo_diff = (10, 10, 10)  # Lower brightness/color difference
    up_diff = (10, 10, 10)  # Upper brightness/color difference
    
    cv2.floodFill(image, mask, seed_point, flood_fill_color, lo_diff, up_diff)

    # Save the modified image
    _, extension = os.path.splitext(image_path)
    filled_image_path = os.path.join(UPLOAD_DIR, 'filled_image' + extension)
    cv2.imwrite(filled_image_path, image)

    return JSONResponse(content={"message": "Image modified successfully", "image_path": filled_image_path})

@app.post('/copyCutImage')
def copyCutImage() -> None:
    """If it exists, writes the cutted image to the image path to overwrite the original image with the cutted one
    """
    if os.path.exists(cut_image_path):
        image = cv2.imread(cut_image_path)
        cv2.imwrite(image_path, image)