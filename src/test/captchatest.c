#include "captchatest.h"
#include <stdio.h>

char *test_error_function(double (*func)(char*, char*))
{
#define TASSERT(s) if (!(s)) break
    /* Test requirements that must be met */
    int flag = 0, cnt = 1;
    while (!flag) {

        /* 1. Must return a value between 0 and 1 */
        TASSERT(func("k", "l") >= 0 && func("k", "l") <= 1);
        TASSERT(func("", "uv123") >= 0 && func("", "uv123") <= 1);
        TASSERT(func("03f12", "") >= 0 && func("03f12", "") <= 1);
        TASSERT(func("p2vAB", "DC2fd") >= 0 && func("p2vAB", "DC2fd") <= 1);
        TASSERT(func("A77s9dQp", "ame0il") >= 0 && func("A77s9dQp", "ame0il") <= 1);
        TASSERT(func("s01WTdE", "1vxZ33p7W") >= 0 && func("s01WTdE", "1vxZ33p7W") <= 1);
        cnt = 2;

        /* 2. Must return 1 if strings are identical */
        TASSERT(func("", "") == 1);
        TASSERT(func("a", "a") == 1);
        TASSERT(func("1a2b", "1a2b") == 1);
        TASSERT(func("zzz", "zzz") == 1);
        cnt = 3;

        /* 3. Must not return 1 if not identical */
        TASSERT(func("a", "A") < 1);
        TASSERT(func("x", "X") < 1);
        TASSERT(func("0", "O") < 1);
        TASSERT(func("2Z", "22") < 1);
        TASSERT(func("aaa", "aaaa") < 1);
        TASSERT(func("i1i1", "I1i1") < 1);
        cnt = 4;

        /* 4. Must return 0 if totally wrong */
        TASSERT(func("", "a") == 0);
        TASSERT(func("", "a0b1") == 0);
        TASSERT(func("a", "T") == 0);
        TASSERT(func("a", "") == 0);
        TASSERT(func("5", "v") == 0);
        TASSERT(func("a", "psl1") == 0);
        TASSERT(func("ab", "r") == 0);
        TASSERT(func("ee", "vv") == 0);
        TASSERT(func("pqr", "") == 0);
        TASSERT(func("1sl", "p") == 0);
        TASSERT(func("spvd", "iml") == 0);
        TASSERT(func("mpdb5", "cc012") == 0);
        flag = 1;
    }

    if (!flag) {
        switch (cnt) {
            case 1:
                return "0.00\nMust return a value between 0 and 1.";

            case 2:
                return "0.00\nMust return 1 if strings are identical.";

            case 3:
                return "0.00\nMust not return 1 if not identical.";

            case 4:
                return "0.00\nMust return 0 if totally wrong.";

        }
    }

    /* Unit test */
    double ans = 0;
#define TTEST(s1, t1, s2, t2) if (func(s1, t1) > func(s2, t2)) ans += 0.05
    TTEST("Z", "2", "a", "2");
    TTEST("1", "l", "o", "0");
    TTEST("aaa", "aaaa", "aa", "aaaa");
    TTEST("12345", "12435", "135", "12345");
    TTEST("uvw", "vvw", "uuw", "vvw");
    TTEST("u", "v", "U", "v");
    TTEST("y", "v", "B", "v");
    TTEST("p13", "p123", "p24", "p123");
    TTEST("ZzZzzZ", "zZzZzZ", "zZzZ", "zZzZzZ");
    TTEST("xvz", "xyz", "xzv", "xyz");
    TTEST("AbcDe", "Abcde", "AbCde", "Abcde");
    TTEST("000", "vvv", "123", "vvv");
    TTEST("111", "1l1", "111", "Ili");
    TTEST("MMP", "MmP", "NnP", "MmP");
    TTEST("vbQrt", "vb2rt", "vb5nt", "vb2rt");
    TTEST("ruRu", "rvRv", "rqcu", "rvRv");
    TTEST("hh1h", "hhh", "h", "hhh");
    TTEST("Q3", "QB", "Qt", "QB");
    TTEST("spmf", "spm1f", "spmKf", "spm1f");
    TTEST("Fg93m", "Fg93n", "F993M", "Fg93n");

    /* Return result */
    static char res[50];
    sprintf(res, "%.2f\nPassed general tests.", ans);
    return res;
}
