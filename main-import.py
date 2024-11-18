import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QFileDialog, QPushButton, QHBoxLayout
from qdarktheme import load_stylesheet

# VTK
from QtOrthoViewer import *
from QtSegmentationViewer import QtSegmentationViewer
from VtkBase import VtkBase
from ViewersConnection import ViewersConnection

# Main Window
class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MPR Viewer")
        self.setWindowIcon(QtGui.QIcon("icon.ico"))
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        
        # Create a central widget and layout
        central_widget = QtWidgets.QWidget()
        central_layout = QtWidgets.QVBoxLayout()
        
        # Create a frame with background color
        self.background_frame = QtWidgets.QFrame()
        self.background_frame.setStyleSheet("background-color: lightgray;")
        self.background_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.background_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Create viewers and connections
        self.vtkBaseClass = VtkBase()
        self.QtSagittalOrthoViewer = QtOrthoViewer(self.vtkBaseClass, SLICE_ORIENTATION_YZ, "Sagittal Plane - YZ")
        self.QtCoronalOrthoViewer = QtOrthoViewer(self.vtkBaseClass, SLICE_ORIENTATION_XZ, "Coronal Plane - XZ")
        self.QtAxialOrthoViewer = QtOrthoViewer(self.vtkBaseClass, SLICE_ORIENTATION_XY, "Axial Plane - XY")
        self.QtSegmentationViewer = QtSegmentationViewer(self.vtkBaseClass, label="3D Viewer")
        
        self.ViewersConnection = ViewersConnection(self.vtkBaseClass)
        self.ViewersConnection.add_orthogonal_viewer(self.QtSagittalOrthoViewer.get_viewer())
        self.ViewersConnection.add_orthogonal_viewer(self.QtCoronalOrthoViewer.get_viewer())
        self.ViewersConnection.add_orthogonal_viewer(self.QtAxialOrthoViewer.get_viewer())
        self.ViewersConnection.add_segmentation_viewer(self.QtSegmentationViewer.get_viewer())

        # Set up the main layout
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        left_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        left_splitter.addWidget(self.QtAxialOrthoViewer)
        left_splitter.addWidget(self.QtSegmentationViewer)
        
        right_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        right_splitter.addWidget(self.QtCoronalOrthoViewer)
        right_splitter.addWidget(self.QtSagittalOrthoViewer)

        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_splitter)

        # Set the central widget
        central_layout.addWidget(self.background_frame)
        central_layout.addWidget(main_splitter)
        central_widget.setLayout(central_layout)

        # Custom title bar
        self.title_bar = QtWidgets.QFrame()
        self.title_bar.setStyleSheet("background-color: rgb(105, 61, 253); border: 2px solid black; border-radius: 10px;")
        title_layout = QHBoxLayout(self.title_bar)
        self.maximize_button = QPushButton("🗖")
        self.maximize_button.clicked.connect(self.toggle_maximize)
        self.close_button = QPushButton("✖")
        self.close_button.clicked.connect(self.close)
        title_layout.addWidget(self.maximize_button)
        title_layout.addWidget(self.close_button)
        title_layout.setAlignment(QtCore.Qt.AlignRight)

        # Create menu bar
        self.create_menu()

        # Set the main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.menuBar())
        main_layout.addWidget(central_widget)
        main_widget = QtWidgets.QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Style the central widget
        self.centralWidget().setStyleSheet("""
            background-color:qlineargradient(spread:pad, x0:1, y1:0, x2:1, y2:0, stop:0 rgb(47, 37, 181), stop:1 rgba(0, 0, 128, 255)); 
            border-radius: 15px;
            padding: 10px;
        """)
    
    def mousePressEvent(self, evt):
        self.oldPos = evt.globalPos()

    def mouseMoveEvent(self, evt):
        delta = evt.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = evt.globalPos() 

    def connect(self):
        pass

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        open_action = QtWidgets.QAction("Open Image", self)
        open_action.setShortcut("Ctrl+o")
        open_action.triggered.connect(self.open_data)
        file_menu.addAction(open_action)

    def open_data(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Image Files (*.mhd)")
        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
            if filenames:
                try:
                    self.load_data(filenames[0])
                    self.render_data()
                except Exception as e:
                    print(e)
                    QtWidgets.QMessageBox.critical(self, "Error", "Unable to open the image file.")

    def load_data(self, filename):
        self.vtkBaseClass.connect_on_data(filename)
        self.QtAxialOrthoViewer.connect_on_data(filename)
        self.QtCoronalOrthoViewer.connect_on_data(filename)
        self.QtSagittalOrthoViewer.connect_on_data(filename)
        self.QtSegmentationViewer.connect_on_data(filename)
        self.ViewersConnection.connect_on_data()
    
    def render_data(self):
        self.QtAxialOrthoViewer.render()
        self.QtCoronalOrthoViewer.render()
        self.QtSagittalOrthoViewer.render()
        self.QtSegmentationViewer.render()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.QtAxialOrthoViewer.close()
        self.QtCoronalOrthoViewer.close()
        self.QtSagittalOrthoViewer.close()
        self.QtSegmentationViewer.close()
    
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

def main():
    """Main function for the application."""
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
