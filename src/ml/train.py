#coding:utf-8
from gen_captcha import gen_captcha_text_and_image
from gen_captcha import number
from gen_captcha import alphabet
from gen_captcha import ALPHABET

import numpy as np
import tensorflow as tf

# Test whether captcha genaration works.
text, image = gen_captcha_text_and_image() 

# Set the shape of a captcha image
IMAGE_HEIGHT = 60
IMAGE_WIDTH = 160
MAX_CAPTCHA = len(text)

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
def get_next_batch(batch_size=128):
    
    # Initailize batch_x for the image, and batch_y for according text vector
	batch_x = np.zeros([batch_size, IMAGE_HEIGHT*IMAGE_WIDTH])
	batch_y = np.zeros([batch_size, MAX_CAPTCHA*CHAR_SET_LEN])


	def wrap_gen_captcha_text_and_image():
		while True:
			text, image = gen_captcha_text_and_image()
			if image.shape == (60, 160, 3):
				return text, image

	for i in range(batch_size):
		text, image = wrap_gen_captcha_text_and_image()
		image = convert2gray(image)
        
       # flatten the image as CNN input. Ignore structure information. 
		batch_x[i,:] = image.flatten() / 255 
		batch_y[i,:] = t2v(text)

	return batch_x, batch_y


# Initialize the input x and input y
X = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT*IMAGE_WIDTH])
Y = tf.placeholder(tf.float32, [None, MAX_CAPTCHA*CHAR_SET_LEN])
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


def train_crack_captcha_cnn():
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
    
    # Begin tarining...finally
	saver = tf.train.Saver()
	with tf.Session() as sess:
		sess.run(tf.global_variables_initializer())

		step = 0
		while True:
			batch_x, batch_y = get_next_batch(64)
			_, loss_ = sess.run([optimizer, loss], feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.75})
			print(step, loss_)


			if step % 100 == 0:
				batch_x_test, batch_y_test = get_next_batch(100)
				acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keep_prob: 1.})
				print('****',step, acc)
				if acc > 0.9:
					saver.save(sess, "/tmp/crack_capcha.ckpt")
					break
			step += 1

# In this function, given a captcha image it will return the text prediction
# There is still bugs in restoring the model
# TO DO I never test this function
def crack_captcha(captcha_image):
	output = crack_captcha_cnn()

	saver = tf.train.Saver()
	with tf.Session() as sess:
		saver.restore(sess, "/tmp/crack_capcha.ckpt")

		predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
		text_list = sess.run(predict, feed_dict={X: [captcha_image], keep_prob: 1})

		text = text_list[0].tolist()
		vector = np.zeros(MAX_CAPTCHA*CHAR_SET_LEN)
		i = 0
		for n in text:
				vector[i*CHAR_SET_LEN + n] = 1
				i += 1
		return v2t(vector)

#train_crack_captcha_cnn()
