<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class CaptchaController extends Controller {
    protected $usrinfo = [
        ['user1', 'yqqlmgsycl'],
        ['user2', 'hnczjtyrbl'],
        ['user3', 'cptbtptp'],
    ];

    protected $username, $password;

    protected $chars = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789';
    protected $maxgroupid = 9;

    public function get(Request $request) {
        if (!$request->has('groupid'))
            return 'Argument error.';
        $groupid = $request->input('groupid');
        $checkinfo = $this->parse_login_info($request);
        if ($checkinfo != 'Success')
            return $checkinfo;
        if ($groupid > $this->maxgroupid || $groupid < 0)
            return 'Group id error.';
        $username = $this->username;
        $password = $this->password;

        $url = 'storage/app/'.$username.'/captcha.png';
        $ansurl = 'storage/app/'.$username.'/ans.txt';
        $ans = $this->generate($groupid, $url, $username);
        $ansfile = fopen($ansurl, 'w') or die('error');
        fwrite($ansfile, $ans);
        fclose($ansfile);
        $msg = 'Success:http://vitas.runtianz.cn/storage/app/'.$username.'/captcha.png';
        return $msg;
    }

    public function attempt(Request $request) {
        $checkinfo = $this->parse_login_info($request);
        if ($checkinfo != 'Success')
            return $checkinfo;
        $username = $this->username;
        $password = $this->password;

        $ansurl = 'storage/app/'.$username.'/ans.txt';
        if (!file_exists($ansurl))
            return 'You should get before attempt.';
        $ans = file_get_contents($ansurl);
        $msg = 'Success:'.$ans;
        return $msg;
    }

    public function upload(Request $request) {
        $checkinfo = $this->parse_login_info($request);
        if ($checkinfo != 'Success')
            return $checkinfo;
        $username = $this->username;
        $password = $this->password;

        if (!$request->has('filename'))
            return 'Argument error.';
        $file = $request->file('file');
        if (!$file->isValid())
            return 'File is not valid.';
        $filename = $request->get('filename');
        $filepath = 'storage/app/'.$username.'/';
        $filename = $filename.'.tar.gz';
        $file->move($filepath, $filename);
        return 'Success:'.$filepath.$filename;
    }

    public function download(Request $request) {
        $checkinfo = $this->parse_login_info($request);
        if ($checkinfo != 'Success')
            return $checkinfo;
        $username = $this->username;
        $password = $this->password;

        if (!$request->has('filename'))
            return 'Argument error.';
        $filename = $request->get('filename');
        $filepath = $username.'/'.$filename.'.tar.gz';
        if (!Storage::disk('local')->exists($filepath))
            return 'No such file';
        $filepath = 'storage/app/'.$filepath;
        return 'Success:'.$filepath;
    }

    private function parse_login_info(Request $request) {
        if (!$request->has('username') || !$request->has('password'))
            return 'Argument error.';
        $username = $request->input('username');
        $password = $request->input('password');
        $useri = 0;
        while ($useri < count($this->usrinfo) &&
            ($username != $this->usrinfo[$useri][0] || $password != $this->usrinfo[$useri][1]))
            $useri++;
        if ($useri == count($this->usrinfo))
            return 'Password wrong.';
        $this->username = $username;
        $this->password = $password;
        return 'Success';
    }

    /* Captcha generator */
    private function generate($gid, $url, $username) {

        /* Generate string */
        switch ($gid) {
            case 0:
            case 1:
            case 4:
            case 5:
            case 6:
            case 7:
            case 8:
                $maxn = 5;
                break;

            case 2:
            case 9:
                $maxn = 9;
                break;

            case 3:
                $maxn = rand(6, 9);
        }

        $string = '';
        for ($i = 0; $i < $maxn; $i++) {
            $rand = rand(0, strlen($this->chars) - 1);
            $string .= substr($this->chars, $rand, 1);
        }

        $maxdot = 0;
        $maxwidth = 180;
        $maxheight = 30;
        $maxangle = 30;
        $smallpixel = 2;
        $fontpath = 'resources/font/edward.TTF';

        /* Generate image */
        switch ($gid) {
            case 0:
                $im = imagecreatetruecolor(120, 30);
                $backcolor = imagecolorallocate($im, rand(220, 255), rand(220, 255), rand(220, 255));
                imagefilledrectangle($im, 0, 0, 120, 30, $backcolor);

                for ($i = 0; $i < strlen($string); ++$i) {
                    $frontcolor = imagecolorallocate($im, rand(0, 120), rand(0, 120), rand(0, 120));
                    imagestring($im, 10, rand(20 * $i + 1, 20 * $i + 10), rand(0, 5), substr($string, $i, 1), $frontcolor);
                }
                break;

            case 1:
                $maxdot = 100;
                $maxwidth = 120;
            case 2:
                if ($maxdot == 0)
                    $maxdot = 900;
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
                    imagestring($im, 10, rand(20 * $i + 1, 20 * $i + 10), rand(0, 5), substr($string, $i, 1), $frontcolor);
                }
                break;

            case 3:
                $maxdot = 200;
                $maxwidth = 180;

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
                    imagestring($im, 10, rand($maxwidth * $i / $maxn + 1, $maxwidth * $i / $maxn + 10), rand(0, 5),
                        substr($string, $i, 1), $frontcolor);
                }
                break;

            case 4:
                $maxdot = 100;
                $maxline = 3;
                $maxwidth = 120;

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

                /* Set lines */
                for ($i = 0; $i < $maxline; ++$i) {
                    $linecolor = imagecolorallocate($im, rand(0, 255), rand(0, 255), rand(0, 255));
                    $x1 = rand(0, $maxwidth);
                    $y1 = rand(0, $maxheight);
                    $x2 = rand(0, $maxwidth);
                    $y2 = rand(0, $maxheight);
                    imageline($im, $x1, $y1, $x2, $y2, $linecolor);
                }

                for ($i = 0; $i < strlen($string); ++$i) {
                    $frontcolor = imagecolorallocate($im, rand(0, 120), rand(0, 120), rand(0, 120));
                    imagestring($im, 10, rand(20 * $i + 1, 20 * $i + 10), rand(0, 5), substr($string, $i, 1), $frontcolor);
                }
                break;

            case 5:
            case 6:
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
                    imagepng($im, 'storage/app/'.$username.'/'.$i.'.png');
                    imagedestroy($im);
                }

                /* Create the captcha image */
                $im = imagecreatetruecolor(($maxheight - $smallpixel) * $maxn, $maxheight);
                for ($i = 0; $i < $maxn; $i++) {
                    $indvim = imagecreatefrompng('storage/app/'.$username.'/'.$i.'.png');
                    imagecolorallocate($im, $back_r, $back_g, $back_b);
                    imagecopy($im, $indvim, ($maxheight - $smallpixel) * $i, 0, 0, 0, $maxheight, $maxheight);
                }

                if ($gid == 6) {
                    $maxdot = 100;
                    $maxline = 3;
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
                }
                break;

            case 7:
                $fontpath = 'resources/font/imprisha.TTF';
            case 8:
                $maxwidth = 600;
                $maxheight = 150;

                $im = imagecreatetruecolor($maxwidth, $maxheight);
                $backcolor = imagecolorallocate($im, rand(220, 255), rand(220, 255), rand(220, 255));
                imagefilledrectangle($im, 0, 0, $maxwidth, $maxheight, $backcolor);

                for ($i = 0; $i < strlen($string); ++$i) {
                    $frontcolor = imagecolorallocate($im, rand(0, 120), rand(0, 120), rand(0, 120));
                    imageTTFtext($im, 75, 0, rand(20 * $i + 1, 20 * $i + 10) * 5,
                        rand(100, 125), $frontcolor, $fontpath, substr($string, $i, 1));
                }
                break;

            case 9:
                $maxwidth = 1080;
                $maxheight = 150;
                $maxdot = 5000;

                $im = imagecreatetruecolor($maxwidth, $maxheight);
                $backcolor = imagecolorallocate($im, rand(220, 255), rand(220, 255), rand(220, 255));
                imagefilledrectangle($im, 0, 0, $maxwidth, $maxheight, $backcolor);

                $fontfile = [
                    'resources/font/footlight.TTF',
                    'resources/font/lucida.TTF',
                    'resources/font/kristen.TTF',
                    'resources/font/freestyle.TTF',
                    'resources/font/imprisha.TTF',
                ];

                for ($i = 0; $i < strlen($string); ++$i) {
                    $frontcolor = imagecolorallocate($im, rand(0, 120), rand(0, 120), rand(0, 120));
                    $fonti = rand(0, count($fontfile) - 1);
                    imageTTFtext($im, 75, 0, rand(20 * $i + 1, 20 * $i + 10) * 5,
                        rand(100, 125), $frontcolor, $fontfile[$fonti], substr($string, $i, 1));
                }

                /* Set dots */
                for ($i = 0; $i < $maxdot; ++$i) {
                    $dotcolor = imagecolorallocate($im, rand(0, 255), rand(0, 255), rand(0, 255));
                    $x = rand(0, $maxwidth);
                    $y = rand(0, $maxheight);
                    imagesetpixel($im, $x, $y, $dotcolor);
                }

        }

        /* Save image file */
        imagepng($im, $url);
        imagedestroy($im);
        return $string;
    }

}