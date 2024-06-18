import cv2
import numpy as np
import itertools
import os
from google.cloud import vision
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.path.dirname(__file__), 'google_lens.json')


# Function to check if two rectangles overlap
def rectangles_overlap(rect1, rect2):
  left1, top1, right1, bottom1 = rect1
  left2, top2, right2, bottom2 = rect2
  return not (right1 < left2 or right2 < left1 or bottom1 < top2 or bottom2 < top1)


# Function to merge two rectangles
def merge_rectangles(rect1, rect2):
  left1, top1, right1, bottom1 = rect1
  left2, top2, right2, bottom2 = rect2
  left = min(left1, left2)
  top = min(top1, top2)
  right = max(right1, right2)
  bottom = max(bottom1, bottom2)
  return (left, top, right, bottom)


# Function to perform OCR
def detect_text(image_content):
  client = vision.ImageAnnotatorClient()
  image = vision.Image(content=image_content)
  response = client.document_text_detection(image=image)
  detected_texts = []
  if response.full_text_annotation:
    for page in response.full_text_annotation.pages:
      for block in page.blocks:
        for paragraph in block.paragraphs:
          for word in paragraph.words:
            word_text = "".join([symbol.text for symbol in word.symbols])
            filtered_text = ''.join([char.upper() for char in word_text if char.isdigit() or 'A' <= char.upper() <= 'Z'])
            detected_texts.append(filtered_text)

  if response.error.message:
    raise Exception(
      f"{response.error.message}"
    )

  return "".join(detected_texts)


# Function to detect squares and read text in it
def mark_square_questions(img_path, square_ranges, squares_count):
  padding = 30
  extra_width = 20
  img = cv2.imread(img_path, cv2.IMREAD_COLOR)
  grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  image_height, image_width = grayscale.shape
  _, threshold = cv2.threshold(grayscale, 155, 255, cv2.THRESH_BINARY)
  contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  contours = sorted(contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))

  squares_list = []
  for contour in contours:
    approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
    if len(approx) == 4:
      area = cv2.contourArea(contour)
      x, y, w, h = cv2.boundingRect(approx)
      aspect_ratio = float(w) / h
      if 10000 <= area <= 14000 and 0.8 <= aspect_ratio <= 1.2:
        squares_list.append((x, y, w, h))

  # Add padding to each row of squares and store rectangles
  rectangles = []
  for _, group in itertools.groupby(squares_list, key=lambda x: x[1] // (2 * padding)):
    squares_sorted_horizontally = sorted(group, key=lambda x: x[0])

    leftmost_x, rightmost_x = float('inf'), float('-inf')

    # Find leftmost and rightmost square edges
    for square in squares_sorted_horizontally:
      leftmost_x = min(leftmost_x, square[0])
      rightmost_x = max(rightmost_x, square[0] + square[2])

    # Calculate rectangle left and right coordinates with padding and extra width
    left = int(leftmost_x - padding - extra_width / 2)
    right = int(rightmost_x + padding + extra_width / 2)

    top_y_square = min(squares_sorted_horizontally, key=lambda x: x[1])[1]
    bottom_y_square = max(squares_sorted_horizontally, key=lambda x: x[1])[1]
    height_squares = bottom_y_square - top_y_square
    center_y = int((top_y_square + bottom_y_square) / 2)

    top = center_y - int(height_squares / 2)
    bottom = center_y + int(height_squares / 2)
    rectangles.append((0, top, image_width-1, bottom+50))

  # Merge overlapping rectangles
  merged_rectangles = []
  for rect in rectangles:
    if not merged_rectangles:
      merged_rectangles.append(rect)
    else:
      merged = False
      for i in range(len(merged_rectangles)):
        if rectangles_overlap(merged_rectangles[i], rect):
          merged_rectangles[i] = merge_rectangles(merged_rectangles[i], rect)
          merged = True
          break
      if not merged:
        merged_rectangles.append(rect)

  # Re-index squares within merged rectangles
  sorted_squares, new_index = [], 0
  for (left, top, right, bottom) in merged_rectangles:
    cv2.rectangle(img, (left, top), (right, bottom), (255, 0, 0), 2)
    squares_in_rectangle = []

    for (x, y, w, h) in squares_list:
      if left <= x <= right and top <= y <= bottom:
        squares_in_rectangle.append((x, y, w, h))

    # Sort squares in the rectangle by x-coordinate
    squares_in_rectangle_sorted = sorted(squares_in_rectangle, key=lambda x: x[0])

    # Re-index the squares and draw the new indices
    for (x, y, w, h) in squares_in_rectangle_sorted:
      sorted_squares.append((x, y, w, h))
      new_index += 1

  def merge_squares_into_rectangle(indices):
    if not indices:
      return None

    # Extract coordinates of squares to be merged
    squares_to_merge = [sorted_squares[i] for i in indices]
    
    # Calculate the bounding box of the merged squares
    x_coords = [x for x, _, _, _ in squares_to_merge]
    y_coords = [y for _, y, _, _ in squares_to_merge]
    w_coords = [x + w for x, _, w, _ in squares_to_merge]
    h_coords = [y + h for _, y, _, h in squares_to_merge]

    left = min(x_coords)
    top = min(y_coords)
    right = max(w_coords)
    bottom = max(h_coords)

    return left, top, right, bottom

  # Define a function to process each range of squares
  def process_square_range(start, end):
    indices = list(range(start, end+1))
    merged_rect = merge_squares_into_rectangle(indices)

    extracted_text = ""
    if merged_rect:
      left, top, right, bottom = merged_rect

      # Extract the region inside the merged rectangle
      merged_image = threshold[top:bottom, left:right]
      success, encoded_image = cv2.imencode('.png', merged_image)
      if success:
        image_content = encoded_image.tobytes()
        extracted_text = detect_text(image_content)
    return extracted_text

  words_list = []
  if len(squares_list) == squares_count:
    for item in square_ranges:
      first_idx, last_idx = map(int, item.split('-'))
      word_detected = process_square_range(first_idx, last_idx)
      words_list.append(word_detected)

  return len(squares_list), words_list


# Function to detect circles & shaded circles
def mark_circle_questions(img_path):
  img = cv2.imread(img_path, cv2.IMREAD_COLOR)
  grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  image_height, image_width = grayscale.shape
  _, binary_img = cv2.threshold(grayscale, 67, 255, cv2.THRESH_BINARY)
  blur_image = cv2.blur(grayscale, (3, 3))

  # Initialize lists to store shaded circles and their indices
  shaded_circles, shaded_circles_index = [], []

  # Parameters
  padding = 20
  extra_width = 15
  detected_circles = cv2.HoughCircles(blur_image, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=40, maxRadius=50)

  if detected_circles is not None:
    detected_circles = np.uint16(np.around(detected_circles))
    detected_circles_sorted = detected_circles[0, :][detected_circles[0, :, 1].argsort()]
    row_padding = []

    for _, group in itertools.groupby(detected_circles_sorted, key=lambda x: (x[1] // (2 * padding))):
      circles_sorted_horizontally = sorted(group, key=lambda x: x[0])
      row_padding.append(circles_sorted_horizontally)

    # List to store rectangles
    rectangles = []
    for row in row_padding:
      top = min(row, key=lambda x: x[1])[1] - padding
      bottom = max(row, key=lambda x: x[1])[1] + padding
      left = min(row, key=lambda x: x[0])[0] - padding - extra_width
      right = max(row, key=lambda x: x[0])[0] + padding + extra_width

      # Store rectangle
      rectangles.append((0, top, image_width-1, bottom))

      for index, point in enumerate(row):
        x, y, r = point[0], point[1], point[2]

        # Find and mark shaded circles
        zero_pixel_count = 0
        for i in range(max(0, y - r), min(binary_img.shape[0], y + r + 1)):
          for j in range(max(0, x - r), min(binary_img.shape[1], x + r + 1)):
            if ((i - y) ** 2 + (j - x) ** 2) <= r ** 2:
              if binary_img[i, j] == 0:
                zero_pixel_count += 1
        
        if zero_pixel_count > 999:
          shaded_circles.append((x, y, r))


    # Merge overlapping rectangles
    merged_rectangles = []
    for rect in rectangles:
      if not merged_rectangles:
        merged_rectangles.append(rect)
      else:
        merged = False
        for i in range(len(merged_rectangles)):
          if rectangles_overlap(merged_rectangles[i], rect):
            merged_rectangles[i] = merge_rectangles(merged_rectangles[i], rect)
            merged = True
            break
        if not merged:
          merged_rectangles.append(rect)

    # List to store final circle indices
    all_circles = []

    # Re-index circles within merged rectangles
    new_index = 0
    for (left, top, right, bottom) in merged_rectangles:
      circles_in_rectangle = []
      for row in row_padding:
        for point in row:
          x, y, r = point[0], point[1], point[2]
          if left <= x <= right and top <= y <= bottom:
            circles_in_rectangle.append((x, y, r))

      # Sort circles in the rectangle by x-coordinate
      circles_in_rectangle_sorted = sorted(circles_in_rectangle, key=lambda x: x[0])

      # Re-index the circles and draw the new indices
      for (x, y, r) in circles_in_rectangle_sorted:
        all_circles.append((x, y, r, new_index))
        if (x, y, r) in shaded_circles:
          shaded_circles_index.append(new_index)
        new_index += 1

    return len(detected_circles_sorted), shaded_circles_index
  return 0, []

