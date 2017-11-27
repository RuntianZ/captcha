<?php
/**
 * Test group 9
 * Complex captcha with random font
 */

/* The characters to choose from */
$chars = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789';
$maxn = 9;
$maximg = 10000;
$ans = '';
$maxwidth = 1080;
$maxheight = 150;
$maxdot = 5000;

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

    $fontfile = [
        'E:/captchatest/font/footlight.ttf',
        'E:/captchatest/font/lucida.ttf',
        'E:/captchatest/font/kristen.ttf',
        'E:/captchatest/font/freestyle.ttf',
        'E:/captchatest/font/imprisha.ttf',
    ];

    for ($i = 0; $i < strlen($string); ++$i) {
        $frontcolor = imagecolorallocate($im, rand(0, 120), rand(0, 120), rand(0, 120));
        $fonti = rand(0, count($fontfile) - 1);
        imagettftext($im, 75, 0, rand(20 * $i + 1, 20 * $i + 10) * 5,
            rand(100, 125), $frontcolor, $fontfile[$fonti], substr($string, $i, 1));
    }

    /* Set dots */
    for ($i = 0; $i < $maxdot; ++$i) {
        $dotcolor = imagecolorallocate($im, rand(0, 255), rand(0, 255), rand(0, 255));
        $x = rand(0, $maxwidth);
        $y = rand(0, $maxheight);
        imagesetpixel($im, $x, $y, $dotcolor);
    }

    /* Save the image */
    imagepng($im, 'E:/captchatest/group9/'.$t.'.png');
    imagedestroy($im);
    echo $t;
    echo "\n";
}

/* The answer file */
$ansfile = fopen('E:/captchatest/answers/group9.txt', 'w') or die('error');
fwrite($ansfile, $ans);
fclose($ansfile);
