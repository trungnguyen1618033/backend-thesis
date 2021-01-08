# coding=utf-8
import mxnet as mx
import numpy as np
from Arcface import ArcfaceModel
from face_preprocess import preprocess
import cv2
from retinaface import RetinaFace


class FacialRecognition:
    def __init__(
        self,
        gpu_index=-1,
        arcface_model="model-r100-ii/model,0",
        image_size="112,112",
        retina_model="/model/R50",
    ):
        if gpu_index >= 0:
            retina_ctx = mx.gpu(gpu_index)
        else:
            retina_ctx = mx.cpu()
        self.face_detector = RetinaFace(prefix=retina_model, epoch=0, ctx_id=gpu_index)
        self.face_recognition = ArcfaceModel(
            gpu=gpu_index, model=arcface_model, image_size=image_size
        )

    def get_scales(self, img):
        scales = [1024, 1980]
        im_shape = img.shape
        target_size = scales[0]
        max_size = scales[1]
        im_size_min = np.min(im_shape[0:2])
        im_size_max = np.max(im_shape[0:2])
        # im_scale = 1.0
        # if im_size_min>target_size or im_size_max>max_size:
        im_scale = float(target_size) / float(im_size_min)
        # prevent bigger axis from being more than max_size:
        if np.round(im_scale * im_size_max) > max_size:
            im_scale = float(max_size) / float(im_size_max)
        scales = [im_scale]
        # print('im_scale', im_scale)
        # im_shape = img.shape
        # TEST_SCALES = [100, 200, 300, 400]
        # target_size = 400
        # max_size = 1200
        # im_size_min = np.min(im_shape[0:2])
        # im_size_max = np.max(im_shape[0:2])
        # im_scale = float(target_size) / float(im_size_min)
        # # prevent bigger axis from being more than max_size:
        # if np.round(im_scale * im_size_max) > max_size:
        #     im_scale = float(max_size) / float(im_size_max)
        # scales = [float(scale) / target_size * im_scale for scale in TEST_SCALES]
        return scales

    def detect_face_and_get_embedding(self, img):
        thresh = 0.8
        flip = False
        scales = self.get_scales(img)
        bboxes, rs = self.face_detector.detect(img, thresh, scales=scales, do_flip=flip)
        # print('bbox:', bboxes)
        if len(bboxes) <= 0:
            return None, None
        # print('landmark:', rs)
        if rs is not None:
            points = rs.astype(np.int32)
            # point = points[0, :].reshape((2, 5)).T
            nimg = preprocess(img, bboxes[0], points[0], image_size="112,112")
            #             nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
            x = np.transpose(nimg, (2, 0, 1))
            embeddings = self.face_recognition.get_feature(x)
            return embeddings, nimg
        return None, None

    def detect_face_and_get_embedding_new(self, img):
        thresh = 0.8
        flip = False
        scales = self.get_scales(img)
        bboxes, rs = self.face_detector.detect(img, thresh, scales=scales, do_flip=flip)
        # print('bbox:', bboxes)
        if len(bboxes) <= 0:
            return None, None, None
        # print('landmark:', rs)
        if rs is not None:
            points = rs.astype(np.int32)
            # point = points[0, :].reshape((2, 5)).T
            nimg = preprocess(img, bboxes[0], points[0], image_size="112,112")
            #             nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
            x = np.transpose(nimg, (2, 0, 1))
            embeddings = self.face_recognition.get_feature(x)
            return bboxes, embeddings, nimg
        return None, None, None

    def detect_face_and_get_embedding_test(self, img):
        thresh = 0.8
        flip = False
        scales = self.get_scales(img)
        bboxes, rs = self.face_detector.detect(img, thresh, scales=scales, do_flip=flip)
        if len(bboxes) <= 0:
            return None
        print("len bboxes: ", len(bboxes))
        embeddings = []
        if rs is not None:
            bboxes, points = rs
            #             print('len total bboxes: ',len(bboxes))
            for i, bbox in enumerate(bboxes):
                #                 print('bbox: ', bbox)
                point = points[i, :].reshape((2, 5)).T
                #                 print('point: ', point)
                nimg = preprocess(img, bbox, point, image_size="112,112")
                #                 nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
                x = np.transpose(nimg, (2, 0, 1))
                embedding = self.face_recognition.get_feature(x)
                embeddings.append(embedding)
                cv2.rectangle(
                    img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2
                )
            return embeddings
        return None

    def detect_face_and_get_embedding_test_2(self, img):
        thresh = 0.8
        flip = False
        scales = self.get_scales(img)
        bboxes, rs = self.face_detector.detect(img, thresh, scales=scales, do_flip=flip)
        if len(bboxes) <= 0:
            return None, None
        embeddings = []
        bbox_list = []
        if rs is not None:
            points = rs.astype(np.int32)
            for i, bbox in enumerate(bboxes):
                # point = points[i, :].reshape((2, 5)).T
                nimg = preprocess(img, bbox, points[i], image_size="112,112")
                nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
                x = np.transpose(nimg, (2, 0, 1))
                embedding = self.face_recognition.get_feature(x)
                embeddings.append(embedding)
                bbox_list.append(bbox)
            return embeddings, bbox_list
        return None, None

    def get_embedding(self, img):
        nimg = cv2.resize(img, (112, 112))
        #         nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
        x = np.transpose(nimg, (2, 0, 1))
        embeddings = self.face_recognition.get_feature(x)
        return embeddings

    def detect_face(self, img):
        thresh = 0.8
        flip = False
        scales = self.get_scales(img)
        bboxes, rs = self.face_detector.detect(img, thresh, scales=scales, do_flip=flip)
        bbox_list = []
        embeddings = []
        if not bboxes:
            return None
        else:
            points = rs.astype(np.int32)
            for i, bbox in enumerate(bboxes):
                # point = points[i, :].reshape((2, 5)).T
                nimg = preprocess(img, bbox, points[i], image_size="112,112")
                nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
                x = np.transpose(nimg, (2, 0, 1))
                embedding = self.face_recognition.get_feature(x)
                embeddings.append(embedding)
                bbox_list.append(bbox)
            return embeddings, bbox_list
        return None, None
