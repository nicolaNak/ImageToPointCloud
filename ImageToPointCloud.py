import os.path
import numpy as np
import scipy.misc
from PIL import Image
'''
creates a point cloud .ply file from any given image that can be processed by PIL, and is created in the same folder as the image
if the image is black and white can set the black sections to be transparent, otherwise pick n
point spacing needs to be made bigger the larger the image is from testing results, 0.5 probably the minimum
TODO: option to convert ply file into binary
'''

class CreatePlyFile():

	def __init__(self):
		self.path = ""
		self.depthPath = ""
		self.fileName = ""
		self.startHeader = "ply\nformat ascii 1.0\ncomment point cloud of image\nelement vertex"
		self.properties = "property float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nproperty uchar alpha\n"
		self.endHeader = "element face 0\nproperty list uchar int vertex_indices\nend_header\n"
		self.separationValue = 0.5
		#make second array of only 5k  points by changing w to 71 or 50k points with 225
		#calculate value 71^2 = 5041 // 225^2 = 50625
		#does not give this exact amount, usually over due to height but close enough
		self.widthValue = 71
		#for B&W images, the point where points under this value will not be added to the point cloud
		self.cutoffThreshold = 100
		self.receiveImage()	
	
	def receiveImage(self):
		self.path = input("Image file: ")
		if os.path.exists(self.path):
			print("Image is being processed")
			iArray = np.asarray(Image.open(self.path))
			self.receiveDepthImage(iArray)
		else:
			print("Image not found, please check file path and name")
			self.receiveImage()
			
	def receiveDepthImage(self, imageArray):
		depthConfirmation = input("Add depth to point cloud with depth image? y/n: ")
		if depthConfirmation == "y":
			self.depthPath = input("Depth Image file: ")
			if os.path.exists(self.depthPath):
				print("Depth image is being processed")
				dArray = np.asarray(Image.open(self.depthPath))
				self.processImageAndDepth(imageArray, dArray)
			else:
				print("Image not found, please check file path and name")
				self.receiveDepthImage()
		else:
			self.processArray(imageArray, True)
		
	def processImageAndDepth(self, imageArray, depthArray):
		resizedImageArray, checkBW, w, h = self.processArray(imageArray, False)
		resizedDepthArray = self.processDepthArray(depthArray, w, h) 
		self.createPly(resizedImageArray, resizedDepthArray, resizedImageArray.shape[0], resizedImageArray.shape[1], checkBW)
	
	#creates array of X by Y pixels by 3 where 3 are RGB values from 0 to 255 - done for image and depth in case not the same size
	def processArray(self, aArray, check):
		tupleLength = len(aArray.shape)
		checkBW = False
		#make first array of original image size
		x = aArray.shape[0]
		y = aArray.shape[1] 
		if tupleLength > 2:
			z = aArray.shape[2]
			aArray.resize((x,y,z))
		else:
			aArray.resize((x,y))
			checkBW = True
		decrease = (x*y)/(self.widthValue*self.widthValue) 
		#get h value
		ratio = x/y
		h = int(self.widthValue*ratio)
		resizedArray = scipy.misc.imresize(aArray,(h, self.widthValue))
		if check == True:
			self.createPly(resizedArray, None, resizedArray.shape[0], resizedArray.shape[1], checkBW)
		else:
			return resizedArray, checkBW, w, h
	
	def processDepthArray(self, depthArray, width, height):
		resizedDepthArray = scipy.misc.imresize(depthArray,(height,width))
		return resizedDepthArray
	
	def checkPath(self):
		plyPath, name = os.path.split(self.path)
		self.path = plyPath
		self.fileName, fileType = name.split('.')	#don't need the file type		
	
	def createPly(self, imageArray, depthArray, x, y, mono):
		vertCounter = 0 #for if chose to turn black to alpha need to recalc vertices
		self.checkPath()
		plyFileName = self.fileName + ".ply"
		print("ply file is being created")
		if self.path != "":
			filaPath = os.path.join(self.path,plyFileName)
		else:
			filePath = plyFileName
		if mono:
			alphaConfirmation = input("convert B&W image to transparent&W (y/n): ")
			if alphaConfirmation == "y":
				blackToAlpha = True
		else:
			blackToAlpha = False
		vertList = []
		for i in range(0,x):
				for j in range(0,y):
					posX = i * self.separationValue
					posY = ((y - 1) * self.separationValue) - (j * self.separationValue) #stops point cloud being inverted
					if depthArray.size: #depth image amount fed in here, between 0 and 10 in value
						posZ = depthArray[i][j][0]
						if posZ > 0:
							posZ = (posZ / 255) * 10
					else:
						posZ = 0.0 
					r=g=b = 0
					a = 255
					if blackToAlpha:
						r = imageArray[i][j]
						g = imageArray[i][j]
						b = imageArray[i][j]
						if r < self.cutoffThreshold:
							a = 0 
					else:
						r = imageArray[i][j][0]
						g = imageArray[i][j][1]
						b = imageArray[i][j][2]						
					if a > 0: #no point to a point you cant see!
						vertLine = str(posX) + " " + str(posY) + " " + str(posZ) + " " + str(r) + " " + str(g) + " " + str(b) + " " + str(a) + "\n"
						vertList.append(vertLine)
						vertCounter += 1
						
		fullStartHeader = self.startHeader + " " + str(vertCounter) + "\n"
		
		with open(filePath, "w") as file:
			file.write(fullStartHeader)
			file.write(self.properties)
			file.write(self.endHeader)
			for l in vertList:
				file.write(l) 
		print("%s created with %i vertices" % (plyFileName,vertCounter))
		
if __name__ == '__main__':
	plyFile = CreatePlyFile()
	