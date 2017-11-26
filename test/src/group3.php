<?php
/**
 * Test group 1
 * Simple captcha with 5 characters little dotted noise
 */

/* The characters to choose from */
$chars = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789';
$minn = 6;
$maxn = 9;
$maximg = 10000;
$maxdot = 200;
$maxwidth = 180;
$maxheight = 30;
$ans = '';

for ($t = 0; $t < $maximg; $t++) {
    $n = rand($minn, $maxn);
    $string = '';
    for ($i = 0; $i < $n; $i++) {
        $rand = rand(0, strlen($chars) - 1);
        $string .= substr($chars, $rand, 1);
    }
    $ans .= $string."\r\n";
    $_SESSION['string'] = $string;
    $im = imagecreatetruecolor($maxwidth, $maxheight);
    $backcolor = imagecolorallocate($im, rand(220, 255), rand(220, 255), rand(220, 255));
    imagefilledrectangle($im, 0, 0, $maxwidth, $maxheight, $backcolor);

    /* Set dots */
    for ($i = 0; $i < $maxdot; ++$i) {
        $dotcolor = imagecolorallocate($im, rand(0, 255), rand(0, 255), rand(0, 255));
        $x = rand(0, $maxwidth);
        $y = rand(0, $maxheight);
        imagesetpixel($im, $x, $y, $dotcolor);
    }

    for ($i = 0; $i < strlen($string); ++$i) {
        $frontcolor = imagecolorallocate($im, rand(0, 120), rand(0, 120), rand(0, 120));
        imagestring($im, 10, rand($maxwidth * $i / $n + 1, $maxwidth * $i / $n + 10), rand(0, 5),
            substr($string, $i, 1), $frontcolor);
    }

    /* Save the image */
    imagepng($im, 'E:/captcha/group3/'.$t.'.png');
    imagedestroy($im);
}

/* The answer file */
$ansfile = fopen('E:/captcha/answers/group3.txt', 'w') or die('error');
fwrite($ansfile, $ans);
fclose($ansfile);
