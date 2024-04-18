import cv2
import numpy as np
import subprocess

# step 1
def convert_image_to_grayscale(self):
    self.grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

def threshold_image(self):
    self.thresholded_image = cv2.threshold(self.grayscale_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def invert_image(self):
    self.inverted_image = cv2.bitwise_not(self.thresholded_image)

def dilate_image(self):
    self.dilated_image = cv2.dilate(self.inverted_image, None, iterations=5)



# step 2
def find_contours(self):
    self.contours, self.hierarchy = cv2.findContours(self.dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # self.image_with_all_contours = self.image.copy()
    # cv2.drawContours(self.image_with_all_contours, self.contours, -1, (0, 255, 0), 3)

def filter_contours_and_leave_only_rectangles(self):
    self.rectangular_contours = []
    for contour in self.contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            self.rectangular_contours.append(approx)
    # self.image_with_only_rectangular_contours = self.image.copy()
    # cv2.drawContours(self.image_with_only_rectangular_contours, self.rectangular_contours, -1, (0, 255, 0), 3)

def find_largest_contour_by_area(self):
    max_area = 0
    self.contour_with_max_area = None
    for contour in self.rectangular_contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            self.contour_with_max_area = contour
    self.image_with_contour_with_max_area = self.image.copy()
    cv2.drawContours(self.image_with_contour_with_max_area, [self.contour_with_max_area], -1, (0, 255, 0), 3)



# step 3
def order_points_in_the_contour_with_max_area(self):
    self.contour_with_max_area_ordered = self.order_points(self.contour_with_max_area)
    # The code below is to plot the points on the image but not required for the perspective transform
    self.image_with_points_plotted = self.image.copy()
    for point in self.contour_with_max_area_ordered:
        point_coordinates = (int(point[0]), int(point[1]))
        self.image_with_points_plotted = cv2.circle(self.image_with_points_plotted, point_coordinates, 10, (0, 0, 255), -1)

def calculate_new_width_and_height_of_image(self):
    existing_image_width = self.image.shape[1]
    existing_image_width_reduced_by_10_percent = int(existing_image_width * 0.9)
    
    distance_between_top_left_and_top_right = self.calculateDistanceBetween2Points(self.contour_with_max_area_ordered[0], self.contour_with_max_area_ordered[1])
    distance_between_top_left_and_bottom_left = self.calculateDistanceBetween2Points(self.contour_with_max_area_ordered[0], self.contour_with_max_area_ordered[3])

    aspect_ratio = distance_between_top_left_and_bottom_left / distance_between_top_left_and_top_right

    self.new_image_width = existing_image_width_reduced_by_10_percent
    self.new_image_height = int(self.new_image_width * aspect_ratio)

def apply_perspective_transform(self):
    pts1 = np.float32(self.contour_with_max_area_ordered)
    pts2 = np.float32([[0, 0], [self.new_image_width, 0], [self.new_image_width, self.new_image_height], [0, self.new_image_height]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    self.perspective_corrected_image = cv2.warpPerspective(self.image, matrix, (self.new_image_width, self.new_image_height))

# Below are helper functions
def calculateDistanceBetween2Points(self, p1, p2):
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    return dis

def order_points(self, pts):
    pts = pts.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect

def add_10_percent_padding(self):
    image_height = self.image.shape[0]
    padding = int(image_height * 0.1)
    self.perspective_corrected_image_with_padding = cv2.copyMakeBorder(self.perspective_corrected_image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=[255, 255, 255])



# step 4
def grayscale_image(self):
    self.grey = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

def threshold_image(self):
    self.thresholded_image = cv2.threshold(self.grey, 127, 255, cv2.THRESH_BINARY)[1]

def invert_image(self):
    self.inverted_image = cv2.bitwise_not(self.thresholded_image)


# step 5
def erode_vertical_lines(self):
    hor = np.array([[1,1,1,1,1,1]])
    self.vertical_lines_eroded_image = cv2.erode(self.inverted_image, hor, iterations=10)
    self.vertical_lines_eroded_image = cv2.dilate(self.vertical_lines_eroded_image, hor, iterations=10)

def erode_horizontal_lines(self):
    ver = np.array([[1],
            [1],
            [1],
            [1],
            [1],
            [1],
            [1]])
    self.horizontal_lines_eroded_image = cv2.erode(self.inverted_image, ver, iterations=10)
    self.horizontal_lines_eroded_image = cv2.dilate(self.horizontal_lines_eroded_image, ver, iterations=10)

def combine_eroded_images(self):
    self.combined_image = cv2.add(self.vertical_lines_eroded_image, self.horizontal_lines_eroded_image)

def dilate_combined_image_to_make_lines_thicker(self):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    self.combined_image_dilated = cv2.dilate(self.combined_image, kernel, iterations=5)



# step 6
def subtract_combined_and_dilated_image_from_original_image(self):
    self.image_without_lines = cv2.subtract(self.inverted_image, self.combined_image_dilated)

def remove_noise_with_erode_and_dilate(self):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    self.image_without_lines_noise_removed = cv2.erode(self.image_without_lines, kernel, iterations=1)
    self.image_without_lines_noise_removed = cv2.dilate(self.image_without_lines_noise_removed, kernel, iterations=1)




# step 7: Finding the cells
def dilate_image(self):
    kernel_to_remove_gaps_between_words = np.array([
            [1,1,1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1,1,1]
    ])
    self.dilated_image = cv2.dilate(self.thresholded_image, kernel_to_remove_gaps_between_words, iterations=5)
    simple_kernel = np.ones((5,5), np.uint8)
    self.dilated_image = cv2.dilate(self.dilated_image, simple_kernel, iterations=2)

def find_contours(self):
    result = cv2.findContours(self.dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    self.contours = result[0]
    # The code below is for visualization purposes only but not necessary for the OCR to work.
    self.image_with_contours_drawn = self.original_image.copy()
    cv2.drawContours(self.image_with_contours_drawn, self.contours, -1, (0, 255, 0), 3)

def convert_contours_to_bounding_boxes(self):
    self.bounding_boxes = []
    self.image_with_all_bounding_boxes = self.original_image.copy()
    for contour in self.contours:
        x, y, w, h = cv2.boundingRect(contour)
        self.bounding_boxes.append((x, y, w, h))
        # This line below draws a rectangle on the image with the shape of the bounding box
        self.image_with_all_bounding_boxes = cv2.rectangle(self.image_with_all_bounding_boxes, (x, y), (x + w, y + h), (0, 255, 0), 5)



# step 8: Sorting The Bounding Boxes By X And Y Coordinates To Make Rows And Columns
def get_mean_height_of_bounding_boxes(self):
    heights = []
    for bounding_box in self.bounding_boxes:
        x, y, w, h = bounding_box
        heights.append(h)
    return np.mean(heights)

def sort_bounding_boxes_by_y_coordinate(self):
    self.bounding_boxes = sorted(self.bounding_boxes, key=lambda x: x[1])

def club_all_bounding_boxes_by_similar_y_coordinates_into_rows(self):
    self.rows = []
    half_of_mean_height = self.mean_height / 2
    current_row = [ self.bounding_boxes[0] ]
    for bounding_box in self.bounding_boxes[1:]:
        current_bounding_box_y = bounding_box[1]
        previous_bounding_box_y = current_row[-1][1]
        distance_between_bounding_boxes = abs(current_bounding_box_y - previous_bounding_box_y)
        if distance_between_bounding_boxes <= half_of_mean_height:
            current_row.append(bounding_box)
        else:
            self.rows.append(current_row)
            current_row = [ bounding_box ]
    self.rows.append(current_row)

def sort_all_rows_by_x_coordinate(self):
    for row in self.rows:
        row.sort(key=lambda x: x[0])



# step 9: Extracting The Text From The Bounding Boxes Using OCR
def crop_each_bounding_box_and_ocr(self):
    self.table = []
    current_row = []
    image_number = 0
    for row in self.rows:
        for bounding_box in row:
            x, y, w, h = bounding_box
            y = y - 5
            cropped_image = self.original_image[y:y+h, x:x+w]
            image_slice_path = "./ocr_slices/img_" + str(image_number) + ".jpg"
            cv2.imwrite(image_slice_path, cropped_image)
            results_from_ocr = self.get_result_from_tersseract(image_slice_path)
            current_row.append(results_from_ocr)
            image_number += 1
        self.table.append(current_row)
        current_row = []

def get_result_from_tersseract(self, image_path):
    output = subprocess.getoutput('tesseract ' + image_path + ' - -l eng --oem 3 --psm 7 --dpi 72 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789().calmg* "')
    output = output.strip()
    return output