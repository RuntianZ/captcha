<?php
/**
 * Test group 6
 * Captcha with 5 rotated characters and little dot and line noise
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
    $maxwidth = ($maxheight - $smallpixel) * $maxn;
    $im = imagecreatetruecolor($maxwidth, $maxheight);
    for ($i = 0; $i < $maxn; $i++) {
        $indvim = imagecreatefrompng('E:/captchatest/temp/'.$i.'.png');
        imagecolorallocate($im, $back_r, $back_g, $back_b);
        imagecopy($im, $indvim, ($maxheight - $smallpixel) * $i, 0, 0, 0, $maxheight, $maxheight);
    }

    /* Set dots */
    for ($i = 0; $i < $maxdot; ++$i) {
        $dotcolor = imagecolorallocate($im, rand(0, 255), rand(0, 255), rand(0, 255));
        $x = rand(0, $maxwidth);
        $y = rand(0, $maxheight);
        imagesetpixel($im, $x, $y, $dotcolor);
    }

    /* Set lines */
    for ($i = 0; $i < $maxline; ++$i) {
        $linecolor = imagecolorallocate($im, rand(0, 255), rand(0, 255), rand(0, 255));
        $x1 = rand(0, $maxwidth);
        $y1 = rand(0, $maxheight);
        $x2 = rand(0, $maxwidth);
        $y2 = rand(0, $maxheight);
        imageline($im, $x1, $y1, $x2, $y2, $linecolor);
    }

    /* Save captcha image */
    imagepng($im, 'E:/captchatest/group6/'.$t.'.png');
    imagedestroy($im);

}

/* Generate answer file */
$ansfile = fopen('E:/captchatest/answers/group6.txt', 'w') or die('error');
fwrite($ansfile, $ans);
fclose($ansfile);

