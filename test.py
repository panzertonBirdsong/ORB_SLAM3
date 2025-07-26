import cv2
img = cv2.imread('/home/pzt/Documents/Research/SLAM/EuRoc/MH_03_medium/mav0/cam0/data/1403637143438319104.png')
print("Loaded:", img is not None, "Shape:", None if img is None else img.shape)

