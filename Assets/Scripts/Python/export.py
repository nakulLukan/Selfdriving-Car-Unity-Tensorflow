import tensorflow as tf 
from tensorflow.keras import backend as K

net = tf.keras.models.load_model('models/RollerBall/AdamMse4x8x4.ckpt')
modelPathIn = 'export_model'
tf.saved_model.save(net, modelPathIn)

graph_def = tf.compat.v2.GraphDef()
with open(modelPathIn, 'rb') as f:
    graph_def.ParseFromString(f.read())

with tf.Graph().as_default() as graph:
    tf.import_graph_def(graph_def, name='')


# optimize and save to ONNX
# Note: tf appends :0 to layer names
inputs[:] = [i+":0" for i in inputs]
outputs[:] = [o+":0" for o in outputs]

# optional step, but helpful to facilitate readability and import to Barracuda
newGraphModel_Optimized = tf2onnx.tfonnx.tf_optimize(inputs, outputs, graph_def)

# saving the model
tf.compat.v1.reset_default_graph()
tf.import_graph_def(newGraphModel_Optimized, name='')

with tf.compat.v1.Session() as sess:
    # inputs_as_nchw are optional, but with ONNX in NCHW and Tensorflow in NHWC format, it is best to add this option
    g = tf2onnx.tfonnx.process_tf_graph(sess.graph,input_names=inputs, output_names=outputs, inputs_as_nchw=inputs)

    model_proto = g.make_model(modelPathOut)
    checker = onnx.checker.check_model(model_proto)

    tf2onnx.utils.save_onnx_model("./", "saved_model", feed_dict={}, model_proto=model_proto)


# validate onnxruntime
if(args.validate_onnx_runtime):
    print("validating onnx runtime")
    import onnxruntime as rt
    sess = rt.InferenceSession("saved_model.onnx")