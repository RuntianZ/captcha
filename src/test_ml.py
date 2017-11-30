from ml import *
from server import *


gen = cgen.server_generator('user3', 'cptbtptp', 1)
train.start_train(times_limit = 10, generator = gen)
