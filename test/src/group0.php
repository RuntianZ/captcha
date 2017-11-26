<?php
/**
 * Test group 1
 * Simple captcha with 5 characters little dotted noise
 */

/* The characters to choose from */
$chars = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789';
$maxn = 5;
$maximg = 10000;
$ans = '';

for ($t = 0; $t < $maximg; $t++) {
    $string = '';
    for ($i = 0; $i < $maxn; $i++) {
        $rand = rand(0, strlen($chars) - 1);
        $string .= substr($chars, $rand, 1);
    }
    $ans .= $string."\r\n";
    $_SESSION['string'] = $string;
    $im = imagecreatetruecolor(120, 30);
    $backcolor = imagecolorallocate($im, rand(220, 255), rand(220, 255), rand(220, 255));
    imagefilledrectangle($im, 0, 0, 120, 30, $backcolor);

    for ($i = 0; $i < strlen($string); ++$i) {
        $frontcolor = imagecolorallocate($im, rand(0, 120), rand(0, 120), rand(0, 120));
        imagestring($im, 10, rand(20 * $i + 1, 20 * $i + 10), rand(0, 5), substr($string, $i, 1), $frontcolor);
    }

    /* Save the image */
    imagepng($im, 'E:/captcha/group0/'.$t.'.png');
    imagedestroy($im);
}

/* The answer file */
$ansfile = fopen('E:/captcha/answers/group0.txt', 'w') or die('error');
fwrite($ansfile, $ans);
fclose($ansfile);
