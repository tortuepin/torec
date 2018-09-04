#!/usr/bin/env python
import subprocess
import os
import sys
import datetime
import glob
import fire
from time import sleep
import tty
import termios

class Torec:

    def __init__(self):
        self.type = 'mp3'
        self.save_dir = self.__get_save_dir()
        #self.save_dir = '/Users/tortuepin/develop/torec/'

    def __start_rec(self, filename):
        # 録音をスタート
        p = subprocess.Popen(("rec", filename))
        return p

    def __stop(self, process):
        # プロセスを終了する
        process.terminate()
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()

    def __start_play(self, filename):
        # filenameを再生する
        p = subprocess.Popen(("play", filename), stdin = subprocess.PIPE)
        return p

    def __get_save_dir(self):
        save_dir = os.getenv('TOREC_SAVE_DIR', None)
        if save_dir is None:
            print("ERROR: $TOREC_SAVE_DIR is not set")
            sys.exit()
        print("save on", save_dir)
        return save_dir

    def __gen_name(self, practice_name):
        # 日付を取得
        today = datetime.date.today().strftime("%y%m%d")

        # 同じ名前がないか調査
        tmp_filename = today + '_' + practice_name
        cmd = self.save_dir + tmp_filename + '*'
        # 同じ名前を探して番号順に並べている
        last = sorted(glob.glob(cmd), reverse=True, key=
                lambda x:int(os.path.basename(x).split('_')[-1].split('.')[0])
                )
        l = len(last)
        if len(last) > 0:
            num = int(self.__split_name(os.path.basename(last[0]))[-1]) + 1
        else:
            num = 1

        # ファイル名をかえす
        return self.save_dir + tmp_filename + '_' + str(num) + '.' + self.type

    def __split_name(self, fname):
        # ファイル名を分割する
        # return[0]:日付
        # return[1]:名前
        # return[2]:番号
        ret_list = []
        t = fname.split("_")
        ret_list.append(t[0])
        ret_list.append(t[1])
        ret_list.append(t[2].split(".")[0])

        return ret_list

    def __print_choices(self):
        print("continue your recording : <Enter>")
        print("replay : Type 'r' key")
        print("delete : Type 'd' key")
        print("finish : Type 'c' key")
        print("If you Type <Space>, alternate recording and play")
    
    def __call_rec(self, practice_name):
        filename = self.__gen_name(practice_name)
        print("\n------recording-------")
        print("stop recording <Enter>")
        p = self.__start_rec(filename)
        sys.stdin.read(1)
        self.__stop(p)
        print("-------stop recording-------")
        self.__print_choices()
        return filename

    def __call_play(self, filename):
        print("\n------playing------")
        print("stop playing <Enter>")
        p = self.__start_play(filename)
        sys.stdin.read(1)
        self.__stop(p)
        print("-------stop playing-------")
        self.__print_choices()

    def __call_del(self, filename):
        print("Delete", os.path.basename(filename))
        print("OK?(y/n)")
        i = sys.stdin.read(1)
        if i in ['y', 'Y']:
            os.remove(filename)
            print("Deleted", os.path.basename(filename))
            return True
        else:
            print("Canceled")
            return False

    def start(self, practice_name):
        play_flag = 0
        print("Type <Enter> to start recording")

        while(True):
            i = sys.stdin.read(1)
            if 'f' in locals() and i == 'r':
                self.__call_play(f)
                play_flag = 1
                continue
            elif 'f' in locals() and i == 'd':
                if self.__call_del(f):
                    del f
                    print("continue your recording : <Enter>")
                else:
                    self.__print_choices()
                continue
            elif 'f' in locals() and i == ' ':
                # スペースが入力されたときはplayとrecを交互に
                if play_flag == 0:
                    self.__call_play(f)
                    play_flag = 1
            elif i == 'c':
                sys.exit()

            f = self.__call_rec(practice_name)
            play_flag = 0



if __name__ == '__main__':
    #標準入力のファイルディスクプリタを取得
    fd = sys.stdin.fileno()

    #fdの端末属性をゲットする
    old = termios.tcgetattr(fd)
    tty.setcbreak(sys.stdin.fileno())

    torec = Torec()
    fire.Fire(torec.start)

    termios.tcsetattr(fd, termios.TCSANOW, old)
