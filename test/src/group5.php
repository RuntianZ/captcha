<?php
/**
 * Test group 5
 * Captcha with 5 rotated characters and no noise
 */

/* The characters to choose from */
$chars = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789';
$maxn = 5;
$maximg = 10000;
$maxdot = 100;
$maxline = 3;
$maxheight = 30;
$maxangle = 30;
$smallpixel = 2;
$ans = '';

for ($t = 0; $t < $maximg; $t++) {
    $string = '';
    for ($i = 0; $i < $maxn; $i++) {
        $rand = rand(0, strlen($chars) - 1);
        $string .= substr($chars, $rand, 1);
    }
    $ans .= $string."\r\n";
    $back_r = rand(220, 255);
    $back_g = rand(220, 255);
    $back_b = rand(220, 255);

    /* Create individual character images */
    for ($i = 0; $i < $maxn; $i++) {
        $im = imagecreatetruecolor($maxheight, $maxheight);
        $backcolor = imagecolorallocate($im, $back_r, $back_g, $back_b);
        imagefilledrectangle($im, 0, 0, $maxheight, $maxheight, $backcolor);

        $frontcolor = imagecolorallocate($im, rand(0, 120), rand(0, 120), rand(0, 120));
        imagestring($im, 10, rand(5, 12), rand(0, 5), substr($string, $i, 1), $frontcolor);

        /* Rotate the image */
        $angle = rand(-$maxangle, $maxangle);
        $newim = imagerotate($im, $angle, $backcolor);
        imagedestroy($im);
        $im = $newim;

        /* Save the image */
        imagepng($im, 'E:/captchatest/temp/'.$i.'.png');
        imagedestroy($im);
    }

    /* Create the captcha image */
    $im = imagecreatetruecolor(($maxheight - $smallpixel) * $maxn, $maxheight);
    for ($i = 0; $i < $maxn; $i++) {
        $indvim = imagecreatefrompng('E:/captchatest/temp/'.$i.'.png');
        imagecolorallocate($im, $back_r, $back_g, $back_b);
        imagecopy($im, $indvim, ($maxheight - $smallpixel) * $i, 0, 0, 0, $maxheight, $maxheight);
    }

    /* Save captcha image */
    imagepng($im, 'E:/captchatest/group5/'.$t.'.png');
    imagedestroy($im);

}

/* Generate answer file */
$ansfile = fopen('E:/captchatest/answers/group5.txt', 'w') or die('error');
fwrite($ansfile, $ans);
fclose($ansfile);

