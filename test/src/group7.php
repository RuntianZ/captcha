<?php
/**
 * Test group 7
 * Captcha with 5 characters using imprisha.ttf
 */

/* The characters to choose from */
$chars = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789';
$maxn = 5;
$maximg = 10000;
$ans = '';
$maxwidth = 600;
$maxheight = 150;

for ($t = 0; $t < $maximg; $t++) {
    $string = '';
    for ($i = 0; $i < $maxn; $i++) {
        $rand = rand(0, strlen($chars) - 1);
        $string .= substr($chars, $rand, 1);
    }
    $ans .= $string."\r\n";
    $_SESSION['string'] = $string;
    $im = imagecreatetruecolor($maxwidth, $maxheight);
    $backcolor = imagecolorallocate($im, rand(220, 255), rand(220, 255), rand(220, 255));
    imagefilledrectangle($im, 0, 0, $maxwidth, $maxheight, $backcolor);

    $fontfile = 'E:/captchatest/font/imprisha.ttf';

    for ($i = 0; $i < strlen($string); ++$i) {
        $frontcolor = imagecolorallocate($im, rand(0, 120), rand(0, 120), rand(0, 120));
        imagettftext($im, 75, 0, rand(20 * $i + 1, 20 * $i + 10) * 5,
            rand(100, 125), $frontcolor, $fontfile, substr($string, $i, 1));
    }

    /* Save the image */
    imagepng($im, 'E:/captchatest/group7/'.$t.'.png');
    imagedestroy($im);
}

/* The answer file */
$ansfile = fopen('E:/captchatest/answers/group7.txt', 'w') or die('error');
fwrite($ansfile, $ans);
fclose($ansfile);
