from __future__ import division
import cv2
import numpy

from naoqi import ALProxy

class Video(object):

    def __init__(self):
        IP = 'bobby.local'
        PORT = 9559

        self.camera = ALProxy("ALVideoDevice", IP, PORT)

        # set nao camera values
        cam_num = 0
        resolution = 2
        colorspace = 13
        fps = 10
        
        # set brightness to default
        self.camera.setCameraParameterToDefault("python_client", 0)

        # subscribe to camera
        self.video_client = self.camera.subscribeCamera("python_client", cam_num, resolution, colorspace, fps)

        # load haar cascades for face and eye detection
        self.face_cascade = cv2.CascadeClassifier('haar_cascades/haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('haar_cascades/haarcascade_eye.xml')

        # set face detection tuning arguments
        self.scale_factor = 1.1
        self.min_neighbors = 6

    def resize(self, img, new_width = 500):
        """ Resizes either grayscale or color image to specified width. """

        if(len(img.shape) > 2):
            h, w, c = img.shape
        else:
            h, w = img.shape
        r = new_width / w
        dim = (new_width, int(h * r))
        img = cv2.resize(img, dim, interpolation = cv2.INTER_LINEAR)
        return img

    def gray(self, img):
        """ Returns grayscale version of image. """

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return gray

    def show(self, width = 500, detect_faces = False):
        """ Gets NAO image, converts to Numpy array, and shows with OpenCV. Has option of detecting and indicating faces in image. """

        nao_image = self.camera.getImageRemote(self.video_client)

        # translate into one opencv can use
        img = (numpy.reshape(numpy.frombuffer(nao_image[6], dtype = '%iuint8' % nao_image[2]), (nao_image[1], nao_image[0], nao_image[2])))
        
        # resize image with opencv
        img = self.resize(img, width)

        # if detect_faces argument is set to True
        if detect_faces:

            # find faces
            faces = self.face_cascade.detectMultiScale(self.gray(img), self.scale_factor, self.min_neighbors)

            # for each face found
            for (x,y,w,h) in faces:
                # draw rectangle around face
                cv2.rectangle(img, (x,y), (x+w, y+h), (255, 0, 0), 1)
                
                # get crop of top half of face
                face = img[y:y+h/2, x:x+w]

                # detect eyes in that face
                eyes = self.eye_cascade.detectMultiScale(self.gray(face))
                
                # for each eye
                for (ex,ey,ew,eh) in eyes:
                    # draw rectangle around eye
                    cv2.rectangle(face, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 1)

        # display marked-up image
        cv2.imshow('img', img)

    def close(self):
        """ Unsubscribes from NAO camera and closes OpenCV windows. """

        self.camera.unsubscribe(self.video_client)
        cv2.destroyAllWindows()