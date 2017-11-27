/**
 * Common header file for captcha project.
 * Created by Runtian Zhai
 */

#ifndef SRC_CAPTCHA_H
#define SRC_CAPTCHA_H

struct captcha {
    char *url; /* The URL of the captcha image */
    char *answer; /* The captcha string */
};

/**
 * captcha_recognize  To recognize a captcha image. The main function to implement.
 * @param png_file    The path of the file to be recognized.
 * @return            The recognized string.
 */
char *captcha_recognize(char *png_file);

/**
 * error_function            The error function that evaluates a recognition result.
 * @param recognize_result   The recognition result of an image.
 * @param answer             The real captcha of the same image.
 * @return                   A number in [0,1]. 0 means totally wrong, while 1 means correctly recognized.
 */
double error_function(char *recognize_result, char *answer);

/**
 * test_error_function       Testing the error function.
 * @param func               The function to be tested.
 * @return                   An evaluation message.
 */
char *test_error_function(double (*func)(char*, char*));


#define MAX_SAMPLE_NUM 500

/**
 * generate_sample   Generate n samples indicated by the group id.
 * @param group_id   The id of the group.
 * @param n          The number of samples. Required to be less than MAX_SAMPLE_NUM.
 * @return           An array containing generated captchas.
 */
struct captcha *generate_sample(int group_id, int n);


#endif //SRC_CAPTCHA_H
