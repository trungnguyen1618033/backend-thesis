import pickle
import numpy as np
import csv
import argparse
from ArcfaceRetina import FacialRecognition
import os
import cv2
import faiss
from matplotlib import pyplot as plt
from skimage import io
import random
from util import base64_to_pil, np_to_base64
from multiprocessing.dummy import Pool as ThreadPool


def read_data_train(path):
    f = open(path, "rb")
    dict_ = pickle.load(f)
    X = []
    Y = []
    db_img_paths = []
    for x in dict_:
        _class = x["class"]
        Y.append(_class)
        X.append(np.array(x["features"]))
        db_img_paths.append(x["imgfile"])
    X = np.array(X)
    Y = np.array(Y)
    f.close()
    return X, Y, db_img_paths


class FaceRecognition:
    def __init__(
        self,
        arcface_model="./model/model-r100-ii/model,0",
        retina_detector="./model/R50",
        gpu_index=0,
    ):

        self.model = FacialRecognition(
            arcface_model=arcface_model,
            retina_model=retina_detector,
            gpu_index=gpu_index,
        )
        self.train_embedding_file = "Model-v1"
        self.threshold = 1.2

        self.X_train, self.Y_train, self.db_path = read_data_train(
            self.train_embedding_file
        )
        self.d = 512
        self.search_model = faiss.IndexFlatL2(self.d)
        self.search_model.add(self.X_train)

    def handle_recognize_face(self, bounded_face, k):
        D, I = self.search_model.search(bounded_face, k)
        predictions = []
        for k in range(len(I[0])):
            la = self.Y_train[I[0][k]]
            dis = D[0][k]
            if dis > self.threshold and "unknown" not in predictions:
                predictions.append("unknown")
            predictions.append(la)
        return None if not len(predictions) else predictions[0]

    def predict_2(self, img):
        k = 15
        features, bboxes = self.model.detect_face_and_get_embedding_test_2(img)
        list_label = []
        if not features:
            return None, None
        param_pools = []
        for feature in features:
            bounded_face = np.array([feature])

            param_pools.append((bounded_face, k))

        pool = ThreadPool()
        pool_results = pool.starmap(self.handle_recognize_face, param_pools)
        pool.close()
        pool.join()

        for result in pool_results:
            if result:
                list_label.append(result)

        return list_label, bboxes

    def predict(self, img):
        features, bboxes = model.detect_face_and_get_embedding_test_2(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #   GET PREDICTIONS
        k = 15
        predicts = []
        bboxes_results = []
        if features is None:
            return None
        if features is not None:
            for i, feature in enumerate(features):
                D, I = search_model.sreach(np.array([feature]), k)
                predictions = []
                la = Y_train[I[0][0]]
                dis = D[0][0]
                if dis > threshold:
                    predictions.append("unknow")
                predictions.append(la)
                if len(predictions) != 0:
                    predicts.append(predictions[0])
                    bboxes_results.append(bboxes[i])
            return predicts

    def GetLabel(self, image, path_folder):
        img = cv2.imread(image)
        labels, faces = self.predict_2(img)
        dict_base64 = []
        if labels is None:
            return None, None, None
        if faces is not None:
            bboxes = np.asarray(faces, dtype=np.int)
            # print('bboxes', bboxes, type(bboxes))
            for j, i in enumerate(bboxes):
                # print(i, type(i), i[0], i[1], i[2], i[3])
                cropped = img[int(i[1]) : int(i[3]), int(i[0]) : int(i[2])]
                link_path = "./detected"
                temp = "x" + str(j) + ".jpg"
                name = path_folder.replace(".jpg", temp)
                filename = os.path.join(link_path, name)
                cv2.imwrite(filename, cropped)
                # img_read = cv2.imread(filename)
                img_crop = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                image_data = np.array(img_crop)
                image_base64 = np_to_base64(image_data)
                dict_base64.append(image_base64)
        return labels, bboxes, dict_base64

    def SearchCeleb(self, path_folder, index):
        path = os.listdir(path_folder)
        my_image = []
        dict_base64 = []
        for i, image in enumerate(path):
            path_img = os.path.join(path_folder, image)
            labels, faces, base64 = self.GetLabel(path_img, image)
            if labels is None:
                continue
            for i, label in enumerate(labels):
                if label == index:
                    my_image.append(image)
                    dict_base64.append(base64)
        return my_image, dict_base64

    def DetectFace(self, path_folder, name):
        path = os.listdir(path_folder)
        errors = {}
        success = True
        dicts = []
        wr = open("Model-v1", "ab+")

        for image in path:
            dict = {}
            path_img = os.path.join(path_folder, image)
            img = cv2.imread(path_img)
            bboxes, embedding, nimg = self.model.detect_face_and_get_embedding_new(img)
            if len(bboxes) > 1:
                errors["message"] = "Nhieu khuon mat trong hinh" + image
                return errors
            # cropped = img[
            #     int(bboxes[0][1]) : int(bboxes[0][3]),
            #     int(bboxes[0][0]) : int(bboxes[0][2]),
            # ]
            # link_path = "./detected"
            # filename = os.path.join(link_path, image)
            # cv2.imwrite(filename, cropped)
            # # img_read = cv2.imread(filename)
            # img_crop = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            if embedding is not None:
                if len(embedding.shape) == 1:
                    dict["class"] = name
                    dict["features"] = embedding
                    dict["imgfile"] = image
                    # print(dict)
                    dicts.append(dict)
        if not dicts:
            errors["message"] = "Empty dicts" + image
            return errors
        else:
            pickle.dump(dicts, wr)
        wr.close()
        return success
