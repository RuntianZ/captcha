#coding:utf-8
import sys
sys.path.append('ml/')

import numpy as np
from cgen import gen_captcha_text_and_image, get_captcha_from_url
from cgen import number
from cgen import alphabet
from cgen import ALPHABET

import numpy as np
import tensorflow as tf

# The default batch size.
default_batch_size = 64

# The default model path.
default_input_model_path = ""
default_output_model_path = ""

# The default accurate check step number.
default_acc_check_step = 50


# Set the shape of a captcha image
IMAGE_HEIGHT = 60
IMAGE_WIDTH = 160
MAX_CAPTCHA = 0

# Convert the image to a grey-scale map. Color is useless in CNN.
def convert2gray(img):
    if len(img.shape) > 2:
        gray = np.mean(img, -1)
        return gray
    else:
        return img

# Genarate the character set that appears in captcha images.
char_set = number + alphabet + ALPHABET + ['_']
CHAR_SET_LEN = len(char_set)


# Transfer the text into a 62-dimension 0-1 vector, each dimension stands for the appearance of one character.
# Here, to simplify the accuracy calculation, there will be no duplicate characters in the captcha.
def t2v(text):
    text_len = len(text)
    if text_len > MAX_CAPTCHA:
        raise ValueError('Invalid length of captcha text')

    vector = np.zeros(MAX_CAPTCHA*CHAR_SET_LEN)
    def c2p(c):
        if c =='_':
            k = 62
            return k
        k = ord(c)-48 # Is number?
        if k > 9:
            k = ord(c) - 65 + 10 # Is upper characters?
            if k > 35:
                k = ord(c) - 97 + 36 # Is lower characters?
                if k > 61:
                    raise ValueError('Invalid character detected in text')
        return k
    for i, c in enumerate(text):
        idx = i * CHAR_SET_LEN + c2p(c)
        vector[idx] = 1
    return vector


# Restore the text from the vector
def v2t(vec):
    char_pos = vec.nonzero()[0]
    text=[]
    for i, c in enumerate(char_pos):
        char_idx = c % CHAR_SET_LEN
        if char_idx < 10:
            char_code = char_idx + ord('0')
        elif char_idx < 36:
            char_code = char_idx - 10 + ord('A')
        elif char_idx < 62:
            char_code = char_idx-  36 + ord('a')
        elif char_idx == 62:
            char_code = ord('_')
        else:
            raise ValueError('error')
        text.append(chr(char_code))
    return "".join(text)


# Genarate one training batch
# When the size of the batch is the nth power of 2, tensorflow perform better. But I don't know why. A dalao told me so.
def get_next_batch(batch_size, generator):
    
    # Initailize batch_x for the image, and batch_y for according text vector
    batch_x = np.zeros([batch_size, IMAGE_HEIGHT*IMAGE_WIDTH])
    batch_y = np.zeros([batch_size, MAX_CAPTCHA*CHAR_SET_LEN])


    def wrap_gen_captcha_text_and_image():
        while True:
            text, image = generator()
            if image.shape == (60, 160, 3):
                return text, image

    for i in range(batch_size):
        text, image = wrap_gen_captcha_text_and_image()
        image = convert2gray(image)
        
       # flatten the image as CNN input. Ignore structure information. 
        batch_x[i,:] = image.flatten() / 255 
        batch_y[i,:] = t2v(text)

    return batch_x, batch_y


X = 0
Y = 0
keep_prob = tf.placeholder(tf.float32) 


def crack_captcha_cnn(w_alpha=0.01, b_alpha=0.1):
    
    x = tf.reshape(X, shape=[-1, IMAGE_HEIGHT, IMAGE_WIDTH, 1])

   # The first convolutional layer, 3x3 convolution, 32 kernels
    w_c1 = tf.Variable(w_alpha*tf.random_normal([3, 3, 1, 32]))
    b_c1 = tf.Variable(b_alpha*tf.random_normal([32]))
    conv1 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(x, w_c1, strides=[1, 1, 1, 1], padding='SAME'), b_c1))
    conv1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv1 = tf.nn.dropout(conv1, keep_prob)
    
    # The second convolutional layer, 64 kernels
    w_c2 = tf.Variable(w_alpha*tf.random_normal([3, 3, 32, 64]))
    b_c2 = tf.Variable(b_alpha*tf.random_normal([64]))
    conv2 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv1, w_c2, strides=[1, 1, 1, 1], padding='SAME'), b_c2))
    conv2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv2 = tf.nn.dropout(conv2, keep_prob)
    
    # The third convolutional layer, 64 kernels
    w_c3 = tf.Variable(w_alpha*tf.random_normal([3, 3, 64, 64]))
    b_c3 = tf.Variable(b_alpha*tf.random_normal([64]))
    conv3 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv2, w_c3, strides=[1, 1, 1, 1], padding='SAME'), b_c3))
    conv3 = tf.nn.max_pool(conv3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv3 = tf.nn.dropout(conv3, keep_prob)
    
   # Full connected layer
    w_d = tf.Variable(w_alpha*tf.random_normal([8*20*64, 1024]))
    b_d = tf.Variable(b_alpha*tf.random_normal([1024]))
    dense = tf.reshape(conv3, [-1, w_d.get_shape().as_list()[0]])
    dense = tf.nn.relu(tf.add(tf.matmul(dense, w_d), b_d))
    dense = tf.nn.dropout(dense, keep_prob)
    
    
   # Output layer
    w_out = tf.Variable(w_alpha*tf.random_normal([1024, MAX_CAPTCHA*CHAR_SET_LEN]))
    b_out = tf.Variable(b_alpha*tf.random_normal([MAX_CAPTCHA*CHAR_SET_LEN]))
    out = tf.add(tf.matmul(dense, w_out), b_out)

    return out


def train_crack_captcha_cnn(acc_limit, step_limit, generator, cache_frequency):
    if acc_limit < 0 or step_limit < 0:
        raise ValueError('Neither limit can be negative.')
    if acc_limit == 0 and step_limit == 0:
        raise ValueError('At least one limit is needed.')

    output = crack_captcha_cnn()
    
    # Genarate loss function. I use the simple sigmoid_cross_entropy algorithm. Here logits is the output of CNN and labels is the correct answer
    loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=output, labels=Y))
    
    # Use AdamOptimaizer, maybe other optimizer will perform better? I don't know...Sorry.
    optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)
    
    # Calculate accuracy, just simply count how many characters are correctly predicted
    # TO DO replace tf.eaual with our error_function
    predict = tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN])
    max_idx_p = tf.argmax(predict, 2)
    max_idx_l = tf.argmax(tf.reshape(Y, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
    correct_pred = tf.equal(max_idx_p, max_idx_l)
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
    
    # Begin training...finally
    saver = tf.train.Saver()
    global default_batch_size, default_input_model_path, default_output_model_path, default_acc_check_step
    with tf.Session() as sess:
        if default_input_model_path != "":
            saver.restore(sess, default_input_model_path)
        else:
            sess.run(tf.global_variables_initializer())

        step = 0
        while True:
            batch_x, batch_y = get_next_batch(default_batch_size, generator)
            _, loss_ = sess.run([optimizer, loss], feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.75})
            print(step, loss_)


            if (step_limit != 0) and (step >= step_limit):
                # Perform leaving accuracy check.
                batch_x_test, batch_y_test = get_next_batch(100, generator)
                acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keep_prob: 1.})
                print('****',step, acc)
                saver.save(sess, default_output_model_path)
                break

            if (acc_limit != 0) and (step % default_acc_check_step == 0):
                batch_x_test, batch_y_test = get_next_batch(100, generator)
                acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keep_prob: 1.})
                print('****',step, acc)
                if acc >= acc_limit:
                    saver.save(sess, default_output_model_path)
                    break

            # Cache the model.
            if (cache_frequency != 0) and (step % cache_frequency == cache_frequency - 1):
                print('Model cached.')
                saver.save(sess, default_output_model_path)
            step += 1


# In this function, given a captcha image it will return the text prediction
# There is still bugs in restoring the model
# TO DO I never test this function
def crack_captcha(captcha_image):
    '''
    crack_captcha -        Recognize a captcha image.
    :param captcha_image:  A 160*60 image object.
    :return:               A string. Recognition result.
    '''
    output = crack_captcha_cnn()

    global default_input_model_path
    saver = tf.train.Saver()
    with tf.Session() as sess:
        saver.restore(sess, default_input_model_path)

        predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
        text_list = sess.run(predict, feed_dict={X: [captcha_image], keep_prob: 1})

        text = text_list[0].tolist()
        vector = np.zeros(MAX_CAPTCHA*CHAR_SET_LEN)
        i = 0
        for n in text:
                vector[i*CHAR_SET_LEN + n] = 1
                i += 1
        return v2t(vector)


# The above methods are not supposed to be called directly in other files.
######################################################################################
# The following methods can be used by importing the train module.


def start_train(acc_limit = 0, step_limit = 0, \
    generator = gen_captcha_text_and_image, cache_frequency = 10):
    '''
    start_train -             Start to train the model.
    :param acc_limit:         The model accuracy lower limit.
    :param step_limit:        The training step upper limit.
    :param generator:         A function that returns a new captcha image and its result every
                              time it is called.
    :param cache_frequency:   Whether the model should be cached while it is being trained.

    You must set one limit if you want to train the model. If the accuracy limit is set,
    the model will be trained until the accuracy is reached. If the step limit is set,
    the model will stop training once the model is trained that many times. The model
    will stop if any of the limits is reached.
    The generator is a function that returns (text, image) on calling, where image is a
    captcha image and text is its result. By default, this method uses the default
    generator, which generates a captcha with 4 characters and little noise every time.
    You need to change this if you want to train on a specific training set.
    The image is a numpy array of a pillow image object. For example, you can use the
    following code to create a captcha image:
    captcha_image = Image.open(captcha) 
    captcha_image = numpy.array(captcha_image)
    If cache_frequency = n > 0, the method will cache the model every n steps. If n = 0 then
    the model will not be cached. Cache the model so that you can resume training if 
    interrupted. A message will be printed every time the model is cached.
    This method reads the initial model from default model input path and writes the trained
    model to default model output path. Set these two paths using set_model_path(). If input
    path is set to an empty string, a new model will be created and used.

    Note:
    According to our experiments, caching is a rather slow operation. If you plan to keep
    this running for a long period of time (say, overnight), you should set cache_frequency
    to a large value. However, it is not a good practice to prohibit caching, as all your
    work will be lost in accidents such as power failure.

    Example:
    >>> start_train(step_limit = 4, cache_frequency = 2)
    0 0.0839923 
    1 0.0823886
    Model cached.
    2 0.0829402
    3 0.0838127
    Model cached.
    4 0.0870781
    **** 4 0.0175
    '''

    # Test whether generator works.
    text, image = generator()
    global MAX_CAPTCHA
    MAX_CAPTCHA = len(text)

    # Initialize X and Y.
    global X, Y
    X = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT*IMAGE_WIDTH])
    Y = tf.placeholder(tf.float32, [None, MAX_CAPTCHA*CHAR_SET_LEN])
    train_crack_captcha_cnn(acc_limit, step_limit, generator, cache_frequency)


def set_batch_size(new_size):
    '''
    set_batch_size -  Set the training batch size.
    :param new_size:  The new batch size.

    The batch size is the number of samples that will be used for training in one iteration.
    By default, the batch size is 64. It is recommended to set the batch size to a power of 2.
    '''
    global default_batch_size
    default_batch_size = new_size


def set_model_path(input_path = "", output_path = ""):
    '''
    set_model_path -     Set the default model paths.
    :param input_path:   The new model input path.
    :param output_path:  The new model output path.

    This method sets default input path and output path. The input path is used in initializing
    training model and performing recognition. The output path is used when saving trained
    model.
    '''
    global default_input_model_path, default_output_model_path
    default_input_model_path = input_path
    default_output_model_path = output_path


def recognize(url, local = False):
    '''
    recognize      Recognize a captcha image from its URL.
    :param url:    The URL of the captcha image.
    :param local:  True if this captcha image is a local file.
    :return:       A string. Recognition result.

    This method uses the model from the default model input path.

    Examples:
    >>> recognize('http://www.example.com/captcha.png')
    cAptChA
    >>> recognize('E:/captchas/captcha.png', True)
    hEllO
    '''
    global default_input_model_path
    if default_input_model_path == '':
        raise ValueError('Input path not set.')
    img = convert2gray(get_captcha_from_url(url, local))
    flat = img.flatten() / 255
    result = crack_captcha(flat)

    return result
