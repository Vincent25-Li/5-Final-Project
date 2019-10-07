import numpy as np
import tensorflow as tf
import os, shutil


class Image_Classifier:
    def __init__(self, model_file, label_file, username, album, top_ranking=None):
        self.model_file = model_file
        self.label_file = label_file
        self.username = username
        self.album = album
        self.top_ranking = top_ranking

    def load_graph(self): # load model and weights
        graph = tf.Graph()
        graph_def = tf.GraphDef()

        with open(self.model_file, "rb") as f:
            graph_def.ParseFromString(f.read())
        with graph.as_default():
            tf.import_graph_def(graph_def)

        return graph

    # decode, resize, normalize, return normalized image
    def read_tensor_from_image_file(self, img_fp,
                                    input_height=299,
                                    input_width=299,
                                    input_mean=0,
                                    input_std=255):
        input_name = "file_reader"
        output_name = "normalized"
        file_reader = tf.read_file(img_fp, input_name)
        if img_fp.endswith(".png"):
            image_reader = tf.image.decode_png(
                file_reader, channels=3, name="png_reader")
        elif img_fp.endswith(".gif"):
            image_reader = tf.squeeze(
                tf.image.decode_gif(file_reader, name="gif_reader"))
        elif img_fp.endswith(".bmp"):
            image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
        else:
            image_reader = tf.image.decode_jpeg(
                file_reader, channels=3, name="jpeg_reader")
        float_caster = tf.cast(image_reader, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0)
        resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width]) # resize image
        normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std]) # squeeze pixel to 0 ~ 1
        sess = tf.compat.v1.Session()
        result = sess.run(normalized) # return normalized image

        return result


    def load_labels(self):
        label = []
    
        #'n' bytes of the file (or whole file) in bytes mode or 'n' bytes of the string if in string (regular) mode.
        proto_as_ascii_lines = tf.gfile.GFile(self.label_file).readlines() 
        for l in proto_as_ascii_lines:
            label.append(l.rstrip())
        return label


    def predict(self, img_fp):
        input_height = 224
        input_width = 224
        input_mean = 0
        input_std = 255
        input_layer = "Placeholder"
        output_layer = "final_result"

        graph = self.load_graph()
        t = self.read_tensor_from_image_file(
        img_fp,
        input_height=input_height,
        input_width=input_width,
        input_mean=input_mean,
        input_std=input_std)

        input_name = "import/" + input_layer
        output_name = "import/" + output_layer
        input_operation = graph.get_operation_by_name(input_name) # for tensorboard
        output_operation = graph.get_operation_by_name(output_name)  

        with tf.compat.v1.Session(graph=graph) as sess:
            results = sess.run(output_operation.outputs[0], {
            input_operation.outputs[0]: t
            })
            results = np.squeeze(results)

        top_k = results.argsort()[-5:][::-1]
        labels = self.load_labels()

        result_idx = results.argmax()

        return labels[result_idx]
        # for i in top_k:
        #     print(labels[i], results[i])

    def ensure_dir_exists(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def photo2category(self, img_fp, des):
        self.ensure_dir_exists(des)
        # print(f'img_fp: {img_fp}')
        img_name = img_fp.split('/')[-1]
        img_des = os.path.join(des, img_name)

        print(f'img_des: {img_des}')
        if not os.path.isfile(img_des):
            shutil.move(img_fp, des)
            print(f'img: {img_name} created')
        else:
            print(f'img: {img_name} already exists')
            return img_name

    