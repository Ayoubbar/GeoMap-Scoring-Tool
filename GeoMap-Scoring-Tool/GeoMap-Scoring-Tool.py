import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget,
    QHBoxLayout, QLineEdit, QCheckBox, QMessageBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MapScoreCalculator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Map Score Calculator')

        # Main layout
        main_layout = QHBoxLayout()

        # Legend input layout
        legend_layout = QVBoxLayout()
        self.legend_button = QPushButton('Upload Legend')
        self.legend_button.clicked.connect(self.upload_legend)
        self.legend_score_min_label = QLabel('Min Score:')
        self.legend_score_min_input = QLineEdit('0')
        self.legend_score_max_label = QLabel('Max Score:')
        self.legend_score_max_input = QLineEdit('1')
        self.legend_segments_label = QLabel('Number of Segments:')
        self.legend_segments_input = QLineEdit('10')

        legend_layout.addWidget(self.legend_button)
        legend_layout.addWidget(self.legend_score_min_label)
        legend_layout.addWidget(self.legend_score_min_input)
        legend_layout.addWidget(self.legend_score_max_label)
        legend_layout.addWidget(self.legend_score_max_input)
        legend_layout.addWidget(self.legend_segments_label)
        legend_layout.addWidget(self.legend_segments_input)

        # Legend display layout
        self.legend_display = QLabel()
        self.legend_display.setFixedSize(200, 400)
        legend_display_layout = QVBoxLayout()
        legend_display_layout.addWidget(self.legend_display)

        # Map input layout
        map_layout = QVBoxLayout()
        self.map_button = QPushButton('Upload Map')
        self.map_button.clicked.connect(self.upload_map)
        self.black_white_checkbox = QCheckBox('The map is in black and white')
        self.black_white_checkbox.setChecked(False)
        map_layout.addWidget(self.map_button)
        map_layout.addWidget(self.black_white_checkbox)

        # Interactive map layout
        self.canvas = FigureCanvas(plt.figure())
        map_layout.addWidget(self.canvas)

        # Result layout
        self.result_display = QLabel()
        self.result_display.setFixedSize(400, 400)
        self.average_score_label = QLabel('Average Score of the Map: ')
        result_layout = QVBoxLayout()
        result_layout.addWidget(self.result_display)
        result_layout.addWidget(self.average_score_label)

        # Add layouts to main layout
        main_layout.addLayout(legend_layout)
        main_layout.addLayout(legend_display_layout)
        main_layout.addLayout(map_layout)
        main_layout.addLayout(result_layout)

        # Set main widget and layout
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.legend_image = None
        self.map_image = None
        self.unique_colors = []
        self.scores = []

    def upload_legend(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Upload Legend", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if fileName:
            self.legend_image = cv2.imread(fileName)
            self.legend_image = cv2.cvtColor(self.legend_image, cv2.COLOR_BGR2RGB)
            self.process_legend()
            self.display_image(self.legend_image, self.legend_display)

    def upload_map(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Upload Map", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if fileName:
            self.map_image = cv2.imread(fileName)
            self.map_image = cv2.cvtColor(self.map_image, cv2.COLOR_BGR2RGB)
            if not self.black_white_checkbox.isChecked():
                self.map_image = self.remove_greyish_pixels(self.map_image)
            self.process_map()
            self.display_interactive_map(self.map_image)

    def display_image(self, image, display_label):
        qformat = QImage.Format_RGB888
        img = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        img = img.scaled(display_label.width(), display_label.height(), Qt.KeepAspectRatio)
        display_label.setPixmap(QPixmap.fromImage(img))

    def display_interactive_map(self, image):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        ax.imshow(image)
        ax.axis('off')

        def on_move(event):
            if event.inaxes:
                x, y = int(event.xdata), int(event.ydata)
                if x < 0 or y < 0 or x >= image.shape[1] or y >= image.shape[0]:
                    return

                pixel_color = image[y, x]
                score = self.find_score(pixel_color)
                ax.set_title(f'Score: {score:.1f}')
                self.canvas.draw()

        self.canvas.mpl_connect('motion_notify_event', on_move)
        self.canvas.draw()

    def find_score(self, pixel_color):
        index = self.find_nearest_color(pixel_color, self.unique_colors, self.scores)
        return self.scores[index]

    def process_legend(self):
        try:
            min_score = float(self.legend_score_min_input.text())
            max_score = float(self.legend_score_max_input.text())
            num_segments = int(self.legend_segments_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numerical values for scores and segments.")
            return

        legend_height = self.legend_image.shape[0]
        section_height = legend_height // num_segments
        self.unique_colors = []

        for i in range(num_segments):
            section = self.legend_image[i * section_height:(i + 1) * section_height, :]
            section_pixels = section.reshape(-1, 3)
            average_color = np.mean(section_pixels[~np.apply_along_axis(self.is_white, 1, section_pixels)], axis=0)
            self.unique_colors.append(average_color.astype(int))

        self.unique_colors = np.array(self.unique_colors)
        self.scores = np.linspace(min_score, max_score, num_segments)

        # Display the segmented legend
        legend_img = np.zeros((legend_height, 100, 3), dtype=np.uint8)
        for i, color in enumerate(self.unique_colors):
            legend_img[i * section_height:(i + 1) * section_height, :] = color
        self.display_image(legend_img, self.legend_display)

    def process_map(self):
        if self.legend_image is None or self.map_image is None:
            QMessageBox.warning(self, "Missing Data", "Please upload both legend and map images.")
            return

        found_colors, processed_image, score_map, average_score = self.check_colors_in_image(self.map_image, self.unique_colors, self.scores, self.black_white_checkbox.isChecked())

        self.display_image(processed_image, self.result_display)
        self.average_score_label.setText(f'Average Score of the Map: {average_score:.2f}')

    def remove_greyish_pixels(self, image):
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                r, g, b = image[i, j]
                if abs(int(r) - int(g)) <= 20 and abs(int(r) - int(b)) <= 20 and abs(int(g) - int(b)) <= 20:
                    image[i, j] = [255, 255, 255]
        return image

    def is_white(self, pixel):
        return np.all(pixel >= 250)

    def find_nearest_color(self, pixel, colors, scores):
        distances = np.sqrt(np.sum((colors - pixel) ** 2, axis=1))
        min_index = np.argmin(distances)

        # Check if the color is exactly the same
        if np.array_equal(pixel, colors[min_index]):
            return min_index

        # If not exactly the same, choose the lower score of the two segments it lies in between
        for i in range(len(colors) - 1):
            if (colors[i][0] <= pixel[0] <= colors[i + 1][0] or colors[i][0] >= pixel[0] >= colors[i + 1][0]):
                if (colors[i][1] <= pixel[1] <= colors[i + 1][1] or colors[i][1] >= pixel[1] >= colors[i + 1][1]):
                    if (colors[i][2] <= pixel[2] <= colors[i + 1][2] or colors[i][2] >= pixel[2] >= colors[i + 1][2]):
                        return i if scores[i] < scores[i + 1] else i + 1
        return min_index

    def check_colors_in_image(self, image, legend_colors, legend_scores, black_in_legend):
        # Check if black is in the legend colors
        def is_black(pixel):
            return np.all(pixel <= [15, 15, 15])

        if not black_in_legend:
            black_pixels = np.all(image <= [15, 15, 15], axis=-1)
            image[black_pixels] = [255, 255, 255]
        
        found_colors = set()
        total_score = 0
        total_pixels = 0
        score_map = np.zeros((image.shape[0], image.shape[1]))
        
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                pixel_color = image[i, j]
                if not self.is_white(pixel_color):
                    nearest_color_index = self.find_nearest_color(pixel_color, legend_colors, legend_scores)
                    found_colors.add(tuple(legend_colors[nearest_color_index]))
                    score = legend_scores[nearest_color_index]
                    score_map[i, j] = score
                    total_score += score
                    total_pixels += 1
        
        average_score = total_score / total_pixels if total_pixels > 0 else 0
        return found_colors, image, score_map, average_score

def main():
    app = QApplication(sys.argv)
    ex = MapScoreCalculator()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
