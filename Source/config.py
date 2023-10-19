import os
import warnings
import tensorflow as tf


def setup_environment():
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)


def setup_warnings():
    warnings.filterwarnings("ignore")
