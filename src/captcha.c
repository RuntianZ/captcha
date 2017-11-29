/**
 * Implementing captcha.h
 * Created by: Runtian Zhai
 */

#include "captcha.h"
#include <string.h>
#include <stdlib.h>

char *captcha_recognize(char *png_file)
{
    return "";
}

/* 改进过的Levenshtein算法(即计算编辑距离)
 * 将删除字符和加入字符的代价赋为100
 * 替换的代价视字符的相似程度而定：一致则为0，完全不相似则为1
 */
double error_function(char *recognize_result, char *answer)
{
#define min(a, b) (((a) < (b)) ? (a) : (b))
#define max(a, b) (((a) > (b)) ? (a) : (b))
#define del_penalty 100
#define level1 80
#define level2 50
#define level3 20
	int trans[256][256];
	int l1 = strlen(recognize_result), l2 = strlen(answer);
	if (l1 == 0 || l2 == 0)
	{
		if (l1 == 0 && l2 == 0)
			return 1;
		return 0;
	}
	// int l = l1 > l2 ? l1 : l2;
	int **dp = (int **)malloc((l1 + 1) * sizeof(int *));
	for (int i = 0; i <= l1; ++i)
		dp[i] = (int *)malloc((l2 + 1) * sizeof(int));
	for (int i = 0; i < 256; ++i)
		for (int j = 0; j < 256; ++j)
		{
			if (i == j)
				trans[i][j] = 0;
			else
				trans[i][j] = 100;
		}
	/* level 1 */
	trans['a']['o'] = trans['o']['a'] = level1;
	trans['a']['0'] = trans['0']['a'] = level1;
	trans['b']['q'] = trans['q']['b'] = level1;
	trans['b']['d'] = trans['d']['b'] = level1;
	trans['b']['D'] = trans['D']['b'] = level1;
	trans['b']['0'] = trans['0']['b'] = level1;
	trans['c']['s'] = trans['s']['c'] = level1;
	trans['c']['S'] = trans['S']['c'] = level1;
	trans['d']['o'] = trans['o']['d'] = level1;
	trans['g']['o'] = trans['o']['g'] = level1;
	trans['g']['0'] = trans['0']['g'] = level1;
	trans['a']['2'] = trans['2']['a'] = level1;
	trans['h']['H'] = trans['H']['h'] = level1;
	trans['i']['I'] = trans['I']['i'] = level1;
	trans['j']['l'] = trans['l']['j'] = level1;
	trans['k']['x'] = trans['x']['k'] = level1;
	trans['k']['X'] = trans['X']['k'] = level1;
	trans['l']['J'] = trans['J']['l'] = level1;
	trans['n']['N'] = trans['N']['n'] = level1;
	trans['o']['p'] = trans['p']['o'] = level1;
	trans['o']['q'] = trans['q']['o'] = level1;
	trans['o']['D'] = trans['D']['o'] = level1;
	trans['o']['P'] = trans['P']['o'] = level1;
	trans['u']['y'] = trans['y']['u'] = level1;
	trans['u']['V'] = trans['V']['u'] = level1;
	trans['v']['w'] = trans['w']['v'] = level1;
	trans['x']['K'] = trans['K']['x'] = level1;
	trans['y']['Y'] = trans['Y']['y'] = level1;
	trans['z']['7'] = trans['7']['z'] = level1;
	trans['B']['D'] = trans['D']['B'] = level1;
	trans['B']['6'] = trans['6']['B'] = level1;
	trans['I']['J'] = trans['J']['I'] = level1;
	trans['I']['L'] = trans['L']['I'] = level1;
	trans['J']['T'] = trans['T']['J'] = level1;
	trans['K']['X'] = trans['X']['K'] = level1;
	trans['L']['1'] = trans['1']['L'] = level1;
	trans['Q']['0'] = trans['0']['Q'] = level1;
	trans['T']['1'] = trans['1']['T'] = level1;
	trans['V']['W'] = trans['W']['V'] = level1;
	trans['1']['K'] = trans['K']['1'] = level1;

	/* level 2 */
	trans['a']['q'] = trans['q']['a'] = level2;
	trans['b']['o'] = trans['o']['b'] = level2;
	trans['c']['e'] = trans['e']['c'] = level2;
	trans['c']['G'] = trans['G']['c'] = level2;
	trans['i']['1'] = trans['1']['i'] = level2;
	trans['i']['l'] = trans['l']['i'] = level2;
	trans['i']['j'] = trans['j']['i'] = level2;
	trans['j']['J'] = trans['J']['j'] = level2;
	trans['l']['L'] = trans['L']['l'] = level2;
	trans['o']['Q'] = trans['Q']['o'] = level2;
	trans['o']['6'] = trans['6']['o'] = level2;
	trans['o']['9'] = trans['9']['o'] = level2;
	trans['u']['v'] = trans['v']['u'] = level2;
	trans['v']['y'] = trans['y']['v'] = level2;
	trans['v']['Y'] = trans['Y']['v'] = level2;
	trans['y']['V'] = trans['V']['y'] = level2;
	trans['B']['3'] = trans['3']['B'] = level2;
	trans['P']['B'] = trans['B']['P'] = level2;
	trans['B']['R'] = trans['R']['B'] = level2;
	trans['E']['F'] = trans['F']['E'] = level2;
	trans['O']['Q'] = trans['Q']['O'] = level2;
	trans['U']['V'] = trans['V']['U'] = level2;
	trans['6']['8'] = trans['8']['6'] = level2;

	/* level 3 */
	trans['b']['6'] = trans['6']['b'] = level3;
	trans['c']['C'] = trans['C']['c'] = level3;
	trans['g']['q'] = trans['q']['g'] = level3;
	trans['k']['K'] = trans['K']['k'] = level3;
	trans['l']['I'] = trans['I']['l'] = level3;
	trans['l']['1'] = trans['1']['l'] = level3;
	trans['m']['n'] = trans['n']['m'] = level3;
	trans['m']['M'] = trans['M']['m'] = level3;
	trans['o']['O'] = trans['O']['o'] = level3;
	trans['o']['0'] = trans['0']['o'] = level3;
	trans['p']['P'] = trans['P']['p'] = level3;
	trans['q']['9'] = trans['q']['9'] = level3;
	trans['s']['S'] = trans['S']['s'] = level3;
	trans['u']['U'] = trans['U']['u'] = level3;
	trans['v']['V'] = trans['V']['v'] = level3;
	trans['w']['W'] = trans['W']['w'] = level3;
	trans['x']['X'] = trans['X']['x'] = level3;
	trans['z']['Z'] = trans['Z']['z'] = level3;
	trans['z']['2'] = trans['2']['z'] = level3;
	trans['O']['0'] = trans['0']['O'] = level3;
	trans['S']['5'] = trans['5']['S'] = level3;
	trans['Z']['2'] = trans['2']['Z'] = level3;
	trans['s']['5'] = trans['5']['s'] = level3;

	for (int i = 0; i <= l1; ++i)
		dp[i][0] = 100 * i;
	for (int i = 0; i <= l2; ++i)
		dp[0][i] = 100 * i;
	for (int i = 1; i <= l1; ++i)
		for (int j = 1; j <= l2; ++j)
			dp[i][j] = min(trans[recognize_result[i - 1]][answer[j - 1]] + dp[i - 1][j - 1], min(dp[i - 1][j] + del_penalty, dp[i][j - 1] + del_penalty));
	double fullmark = max(l1, l2) * 100;
	double res = (fullmark - dp[l1][l2]) / fullmark;
	for (int i = 0; i < l1; ++i)
		free(dp[i]);
	free(dp);
	return res;
}

struct captcha *generate_sample(int group_id, int n)
{
    return NULL;
}