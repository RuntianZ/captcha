/**
 * captchatest.h - The unit test for captcha.h
 * Created by: Runtian Zhai
 */

#ifndef SRC_CAPTCHATEST_H
#define SRC_CAPTCHATEST_H

/**
 * test_error_function       Testing the error function.
 * @param func               The function to be tested.
 * @return                   An evaluation message.
 */
char *test_error_function(double (*func)(char*, char*));


#endif //SRC_CAPTCHATEST_H
