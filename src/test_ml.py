from ml import *
from server import *

train.set_model_path(input_path = "model/model.ckpt", output_path = "model/model.ckpt")
train.start_train(step_limit = 4, cache_frequency = 2)
