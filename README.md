# ImageToPointCloud
A short python script that converts an image into a point cloud

Written quickly as a customized tool for an interactive museum piece using scanned dataset images as point clouds 

The script runs in command prompt, it will ask you for an image and depth image, and if the image is black and white if you would like to remove points below the cut off color threshold, then it creates a ASCII .ply point cloud in the same folder the image is in

self.separationValue affects how far apart the points are, if you increase widthValue increase this as well
self.widthValue affects how many points are created
self.cutoffThreshold affects where B&W images points are not added to the point cloud
 
