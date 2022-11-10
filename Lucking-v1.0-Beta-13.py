import math
import os
import random
import sys
import tempfile
import time
import tkinter.filedialog
import zipfile

import pygame

try:
    from sys import _MEIPASS
    Resources = os.path.join(_MEIPASS, 'Resources')
except:
    Resources = 'Resources'

ver = 'v1.0 Beta 13'


class Button:
    # 按钮类
    def __init__(self, screen, img, rect):
        self.screen = screen
        self.img = img
        self.rect = rect
        self.screen.blit(self.img, self.rect)

    def click(self, pos):
        # 判断是否点击到了按钮
        return self.rect.collidepoint(pos)


class Note:
    # Note 类
    def __init__(self, pos, time):
        if pos:
            self.pos = abs(pos)-1
            self.type = pos < 0
        else:
            self.pos = random.randint(0, 8)
            self.type = 2
        self.time = time
        self.multi = False
        self.click = 0
        self.clicktime = 0
        self.direction = 1


if __name__ == '__main__':
    while True:
        # 读取全局设置
        try:
            global_offset, show_split_line = map(
                eval, open('config.txt').readlines())
        except:
            with open('config.txt', 'w') as f:
                f.write('0\nFalse')
            global_offset = 0
            show_split_line = False

        # 初始化游戏窗口
        pygame.init()
        screen = pygame.display.set_mode((1000, 600))
        pygame.display.set_caption(f'Lucking {ver}')
        pygame.display.set_icon(pygame.image.load(
            os.path.join(Resources, 'icon.png')))

        # 初始化文字
        font = pygame.font.Font(os.path.join(Resources, 'songhei.ttf'), 30)
        font_small = pygame.font.Font(
            os.path.join(Resources, 'songhei.ttf'), 15)
        font_big = pygame.font.Font(os.path.join(Resources, 'songhei.ttf'), 60)

        # 显示标题页面
        state = 0
        while state == 0:
            screen.blit(pygame.image.load(
                os.path.join(Resources, 'title.png')), (0, 0))
            img_logo_big = pygame.image.load(
                os.path.join(Resources, 'Lucking.png'))
            rect_logo_big = img_logo_big.get_rect()
            rect_logo_big.center = (
                500, 275-50*math.sin(time.time()*2 % math.pi))
            text_start = font.render('单击以开始', True, (0, 0, 0))
            rect_start = text_start.get_rect()
            rect_start.midbottom = (500, 500)
            text_ver_small = font_small.render(
                'Version: '+ver, True, (0, 0, 0))
            rect_ver_small = text_ver_small.get_rect()
            rect_ver_small.bottomleft = (0, 600)
            text_drag_small = font_small.render(
                '可将 ZIP 压缩包或文件夹直接拖拽到窗口中', True, (0, 0, 0))
            rect_drag_small = text_drag_small.get_rect()
            rect_drag_small.midbottom = (500, 600)
            text_author_small = font_small.render(
                'Author: 蔗蓝', True, (0, 0, 0))
            rect_author_small = text_author_small.get_rect()
            rect_author_small.bottomright = (1000, 600)
            screen.blit(img_logo_big, rect_logo_big)
            screen.blit(text_start, rect_start)
            screen.blit(text_ver_small, rect_ver_small)
            screen.blit(text_drag_small, rect_drag_small)
            screen.blit(text_author_small, rect_author_small)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    state = 1
                elif event.type == pygame.DROPFILE:
                    if os.path.isdir(event.file):
                        dir = event.file
                        state = 2
                    elif os.path.isfile(event.file) and event.file.endswith('.zip'):
                        dir = tempfile.mkdtemp(prefix='Lucking_')
                        zipfile.ZipFile(event.file).extractall(
                            os.path.expandvars(dir))
                        t = [i for i in os.listdir(
                            dir) if os.path.isdir(os.path.join(dir, i))]
                        if len(t) == 0:
                            state = 2
                        elif len(t) == 1:
                            dir = os.path.join(dir, t[0])
                            state = 2

        # 打开歌曲文件夹
        if state == 1:
            tk = tkinter.Tk()
            tk.withdraw()
            dir = tkinter.filedialog.askdirectory()
            tk.destroy()
            if not dir:
                continue

        # 读取歌曲信息
        info = [i.strip() for i in open(os.path.join(
            dir, 'info.txt'), encoding='utf-8').readlines()]
        song_name, song_composer, song_bpm, song_length, song_offset = map(
            eval, info)
        beat = 60/song_bpm  # 每拍长度/秒
        offset = song_offset+global_offset  # 谱面偏移/秒

        # 初始化音频系统
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(os.path.join(dir, 'music.mp3'))
            beat_sound_1 = pygame.mixer.Sound(
                os.path.join(Resources, 'beat1.mp3'))
            beat_sound_2 = pygame.mixer.Sound(
                os.path.join(Resources, 'beat2.mp3'))
            play_sound = (beat_sound_1.play, beat_sound_2.play,
                          lambda: (beat_sound_1.play(), beat_sound_2.play()))
            music_state = True
        except:
            play_sound = (print,)*3
            music_state = False

        # 初始化背景图片
        try:
            bgpic = pygame.transform.scale(pygame.image.load(
                os.path.join(dir, 'background.png')), (1000, 600))
            black = pygame.Surface((1000, 600), pygame.SRCALPHA)
            black.fill((0, 0, 0, 150))
            bgpic.blit(black, (0, 0))
            def show_bgpic(): screen.blit(bgpic, (0, 0))
        except:
            def show_bgpic(): screen.fill((0, 0, 0))

        # 显示难度选择界面
        state = 0
        autoplay = False
        while state == 0:
            show_bgpic()
            y = 50
            for i in song_name.split('\n'):
                text_name_big = font_big.render(i, True, (255, 255, 255))
                rect_name_big = text_name_big.get_rect()
                rect_name_big.topleft = (50, y)
                screen.blit(text_name_big, rect_name_big)
                y = rect_name_big.bottom+10
            text_composer = font.render(song_composer, True, (255, 255, 255))
            rect_composer = text_composer.get_rect()
            rect_composer.topleft = (50, rect_name_big.bottom+10)
            text_return = font.render('按 X 键返回', True, (255, 255, 255))
            rect_return = text_return.get_rect()
            rect_return.bottomleft = (50, 550)
            text_autoplay = font.render(
                '自动播放已打开 (按 A 键关闭)' if autoplay else '自动播放已关闭 (按 A 键打开)', True, (255, 255, 255))
            rect_autoplay = text_autoplay.get_rect()
            rect_autoplay.bottomleft = (50, rect_return.top-10)
            screen.blit(text_composer, rect_composer)
            screen.blit(text_return, rect_return)
            screen.blit(text_autoplay, rect_autoplay)
            buttons = {}
            button_rect = pygame.Rect(710, 50, 240, 120)
            for i in ('Simple', 'Medium', 'Difficult', 'King'):
                if os.path.isfile(os.path.join(dir, i+'.txt')):
                    buttons[i] = Button(screen, pygame.image.load(
                        os.path.join(Resources, i+'.png')), pygame.Rect(button_rect))
                    button_rect.centery += 130
            img_logo = pygame.transform.scale(img_logo_big, (100, 50))
            rect_logo = img_logo.get_rect()
            rect_logo.bottomright = (990, 590)
            screen.blit(img_logo, rect_logo)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        state = 2
                    elif event.key == pygame.K_a:
                        autoplay = not autoplay
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i in buttons.keys():
                        if buttons[i].click(event.pos):
                            diff = i
                            state = 1
        if state == 2:
            continue

        def game():
            # 正式游戏
            global music_state

            # 显示加载页面
            load_time = time.time()
            show_bgpic()
            text_loading_big = font_big.render('正在加载谱面', True, (255, 255, 255))
            rect_loading_big = text_loading_big.get_rect()
            rect_loading_big.center = (500, 300)
            screen.blit(text_loading_big, rect_loading_big)
            pygame.display.update()

            # 设置文字
            text_diff = font.render(diff, True, (255, 255, 255))
            rect_diff = text_diff.get_rect()
            rect_diff.bottomright = (1000, 600)
            text_replay = font.render('按 R 键重新开始', True, (255, 255, 255))
            rect_replay = text_replay.get_rect()
            text_pause_big = font_big.render('已暂停', True, (255, 255, 255))
            rect_pause_big = text_pause_big.get_rect()
            rect_pause_big.midbottom = (500, 295)
            text_continue = font.render('单击以继续', True, (255, 255, 255))
            rect_continue = text_continue.get_rect()
            rect_continue.midtop = (500, 305)

            # 解析谱面
            notes = []
            times = set()  # 每个节拍的音符数量
            multi = set()  # 存在多个音符的节拍
            linemotion = {0: 0}  # 判定线位置
            speedchange = {0: 1}  # 谱面流速变化
            flip = {0: False}  # 谱面左右翻转
            flag_f = False
            reverse = {0: False}  # 谱面上下翻转
            flag_r = False
            repeat_times = 1  # 反复次数
            repeat_interval = 0  # 反复间隔
            repeat_multiline = False  # 多行反复
            g0 = g1 = g2 = g3 = 0  # 节拍偏移量

            def add_note(pos, time):
                # 添加 Note
                notes.append(Note(pos, time))
                if time in times:
                    multi.add(time)  # 该节拍已存在音符，加入多押列表
                else:
                    times.add(time)  # 记录该节拍

            with open(os.path.join(dir, diff+'.txt'), encoding='utf-8') as f:
                for i in f.readlines():
                    line = i.strip()
                    if line.startswith('-'):  # 分割线，忽略
                        continue
                    elif line.startswith('%'):  # 反复
                        tmp = line[1:].split()
                        g0 = float(tmp[0])
                        repeat_interval, repeat_times = map(
                            float, tmp[1].strip('(').split('*'))
                        repeat_multiline = tmp[1].endswith('(')
                    elif line.startswith(')'):  # 多行反复结束
                        g0 = 0
                        repeat_times = 1
                        repeat_interval = 0
                        repeat_multiline = False
                    else:
                        x = 0
                        for f in range(int(repeat_times)):
                            if line.startswith('#'):  # 谱面特效
                                tmp = line[1:].split()
                                t = g3+g2+g1+g0+x+float(tmp[1])
                                if tmp[0] == 'f':  # 左右翻转
                                    flag_f = not flag_f
                                    flip[t] = flag_f
                                elif tmp[0] == 'l':  # 判定线移动
                                    linemotion[t] = float(tmp[2])
                                elif tmp[0] == 'r':  # 下落方向
                                    flag_r = not flag_r
                                    reverse[t] = flag_r
                                elif tmp[0] == 's':  # 谱面流速
                                    speedchange[t] = float(tmp[2])
                            elif line.startswith('$'):  # 批量输入
                                tmp = line[1:].split()
                                t = g3+g2+g1+g0+x+float(tmp[0])
                                g = tmp[1].split('*')
                                step = float(g[0])
                                flag = -1 if step < 0 else 1
                                for h in range(int(g[1] if len(g) == 2 else 1)):
                                    for j in tmp[2].split(','):
                                        k = j.split('*')
                                        for l in range(int(k[1]) if len(k) == 2 else 1):
                                            if k[0]:
                                                for m in k[0].split('/'):
                                                    add_note(float(m)*flag, t)
                                            t += abs(step)
                            elif line.startswith('***'):  # 三级偏移
                                g3 = float(line[3:])
                            elif line.startswith('**'):  # 二级偏移
                                g2 = float(line[2:])
                            elif line.startswith('*'):  # 一级偏移
                                g1 = float(line[1:])
                            elif line.strip():  # note
                                l = list(map(float, line.strip().split()))
                                t = g3+g2+g1+g0+x+l[0]  # 计算节拍
                                if len(l) == 1:
                                    add_note(0, t)
                                else:
                                    for j in range(1, len(l)):
                                        add_note(l[j], t)
                            x += repeat_interval
                        if not repeat_multiline:
                            g0 = 0
                            repeat_times = 1
                            repeat_interval = 0
            notes.sort(key=lambda x: x.time)  # 按节拍排序

            def getlinepos(time):
                # 获取判定线位置
                before = after = 0
                for i in sorted(linemotion):
                    if i <= time:
                        before = i
                    else:
                        after = i
                        break
                if not after:
                    return 500+linemotion[before]
                else:
                    progress = (time-before)/(after-before)
                    extent = linemotion[after]-linemotion[before]
                    return 500+linemotion[before]+extent*(math.sin((progress-0.5)*math.pi)+1)/2

            def getspeed(time):
                # 获取谱面流速/(像素/拍)
                defaultspeed = {'Simple': 150, 'Medium': 300, 'Difficult': 450,
                                'King': 600}[diff]*beat  # 默认流速
                before = after = 0
                for i in sorted(speedchange):
                    if i <= time:
                        before = i
                    else:
                        after = i
                        break
                if not after:
                    return defaultspeed*speedchange[before]
                else:
                    progress = (time-before)/(after-before)
                    extent = speedchange[after]-speedchange[before]
                    return defaultspeed*(speedchange[before]+extent*progress)

            def getflip(time):
                # 获取谱面是否左右反转
                before = 0
                for i in sorted(flip):
                    if i <= time:
                        before = i
                    else:
                        break
                return flip[before]

            def getreverse(time):
                # 获取谱面是否上下反转
                before = 0
                for i in sorted(reverse):
                    if i <= time:
                        before = i
                    else:
                        break
                return reverse[before]

            for note in notes:
                if note.time in multi:  # 多押
                    note.multi = True
                if getflip(note.time):
                    note.flip()
                if getreverse(note.time):
                    note.reverse()

            c1 = c2 = c3 = c4 = score = combo = total_delta = 0  # 四种判定个数、得分、连击数、打击总偏差
            colors = {1: (0, 255, 0), 2: (0, 255, 255),
                      -1: (255, 0, 0), -2: (255, 0, 255)}  # 打击特效及判定线颜色
            combo_his = {0: (255, 0, 255)}  # 连击数历史记录

            # 加载界面至少显示 0.5 秒
            while time.time()-load_time < 0.5:
                pass

            music_started = False  # 已经开始播放音乐
            start_time = time.time()  # 游戏开始时间
            while True:
                now_time = time.time()-start_time-2  # （开始前等待2秒）
                now_beat = (now_time-offset)/beat  # 当前节拍

                if now_time > song_length+1:
                    break  # 歌曲结束

                if music_state and not music_started and now_time > 0:
                    pygame.mixer.music.play()  # 开始播放歌曲
                    music_started = True

                if now_time > 0:
                    # 以颜色形式保存连击数历史
                    combo_prog = combo/len(notes)
                    if combo_prog < 0.5:
                        k = 1-(1-combo_prog*2)**2
                        t = int(k*255)
                        combo_his[int(1000*now_time/song_length)
                                  ] = (255-t, t, 255-t)  # 紫-绿
                    else:
                        k = combo_prog*2-1
                        t1 = int(k*255)
                        t2 = int(k*40)
                        combo_his[int(1000*now_time/song_length)
                                  ] = (t1, 255-t2, 0)  # 绿-金

                # Miss 判定和 Autoplay
                for note in notes:
                    if autoplay and now_beat > note.time and not note.click:
                        note.clicktime = note.time
                        play_sound[note.type]()
                        note.click = 1
                        c1 += 1
                        combo += 1
                        score += 10000 / len(notes)
                    elif (now_beat-note.time)*beat > 0.35 and not note.click:
                        note.click = -2
                        c4 += 1
                        combo = 0

                def show():
                    # 显示谱面
                    show_bgpic()
                    for note in notes:
                        if -20 < getlinepos(now_beat)-10-(note.time-now_beat)*note.direction*getspeed(now_beat) < 600:
                            if not note.click:
                                # 显示 Note
                                rect = pygame.Rect(
                                    110*note.pos+10, getlinepos(now_beat)-10-(note.time-now_beat)*note.direction*getspeed(now_beat), 100, 20)
                                if note.multi:
                                    # 显示多押提示
                                    rect2 = pygame.Rect(
                                        rect.left-2, rect.top-2, 104, 24)
                                    pygame.draw.rect(screen, (255, 255, 200),
                                                     rect2, border_radius=5)
                                pygame.draw.rect(screen, ((100, 150, 200), (200, 150, 100),
                                                          (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))[note.type],
                                                 rect, border_radius=5)
                                # 显示数字提示
                                text_num = font.render(
                                    str(int(note.pos+1)), True, (255, 255, 0))
                                rect_num = text_num.get_rect()
                                rect_num.center = rect.center
                                screen.blit(text_num, rect_num)
                        if now_beat-note.clicktime < 0.5 and note.click in (-1, 1, 2):
                            # 显示打击特效
                            size = (
                                max(0, now_beat-note.clicktime)/0.5)**0.5*100
                            rect = pygame.Rect(0, 0, size, size)
                            rect.center = (110*note.pos+60,
                                           getlinepos(now_beat))
                            pygame.draw.rect(
                                screen, colors[note.click], rect, 5)

                    # 显示分割线
                    if show_split_line:
                        for i in range(10):
                            pygame.draw.line(
                                screen, (100, 100, 100), (i*110+5, 0), (i*110+5, 600), 3)

                    # 显示判定线
                    if c2+c3+c4 == 0:
                        linecolor = 1
                    elif c3+c4 == 0:
                        linecolor = 2
                    else:
                        linecolor = -1
                    pygame.draw.line(
                        screen, colors[linecolor], (0, getlinepos(now_beat)), (1000, getlinepos(now_beat)), 5)

                    # 显示进度条
                    for i in range(list(combo_his.keys())[-1]+1):
                        if i not in combo_his:
                            combo_his[i] = combo_his[i-1]
                        pygame.draw.line(
                            screen, combo_his[i], (i, 0), (i, 5), 1)

                    # 显示文字
                    y = 600
                    for i in reversed(song_name.split('\n')):
                        text_name = font.render(i, True, (255, 255, 255))
                        rect_name = text_name.get_rect()
                        rect_name.bottomleft = (0, y)
                        screen.blit(text_name, rect_name)
                        y -= 30
                    text_score = font.render(
                        f'{str(round(score)).zfill(5)} | Combo: {combo}'+' (Autoplay)'*autoplay, True, (255, 255, 255))
                    rect_score = text_score.get_rect()
                    rect_score.midbottom = (500, 600)
                    screen.blit(text_score, rect_score)
                    screen.blit(text_diff, rect_diff)

                def pause():
                    # 暂停
                    if music_state:
                        pygame.mixer.music.pause()
                    rect_replay.midtop = (500, rect_continue.bottom+10)
                    rect_return.midtop = (500, rect_replay.bottom+10)
                    screen.blit(text_pause_big, rect_pause_big)
                    screen.blit(text_continue, rect_continue)
                    screen.blit(text_replay, rect_replay)
                    screen.blit(text_return, rect_return)
                    pygame.display.update()
                    clicked = False
                    while not clicked:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_x:
                                    return 1
                                elif event.key == pygame.K_r:
                                    return 2
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                clicked = True
                    for i in range(3, 0, -1):
                        show()
                        text_num_big = font_big.render(
                            str(i), True, (255, 255, 255))
                        rect_num_big = text_num_big.get_rect()
                        rect_num_big.center = (500, 300)
                        screen.blit(text_num_big, rect_num_big)
                        pygame.display.update()
                        time.sleep(1)
                    if music_started:
                        pygame.mixer.music.unpause()

                # 刷新谱面
                show()
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        # 关闭窗口，退出游戏
                        sys.exit()
                    elif event.type == pygame.WINDOWFOCUSLOST and not autoplay or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        # 窗口丢失焦点，暂停游戏
                        t = pause()
                        if t == 1:  # 返回标题界面
                            return
                        elif t == 2:  # 重玩
                            return game()
                        else:
                            start_time = time.time()-now_time-2
                    elif event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_9:
                        # 按下数字键，打击音符
                        if not autoplay:
                            key = event.key-pygame.K_1
                            for note in notes:
                                delta = abs(now_beat-note.time)*beat  # 打击误差/秒
                                if delta <= 0.35 and not note.click and note.pos == key:
                                    # 有效打击
                                    note.clicktime = now_beat
                                    total_delta += now_beat-note.time
                                    play_sound[note.type]()
                                    if delta <= 0.08:
                                        # Perfect 判定
                                        note.click = 1
                                        c1 += 1
                                        combo += 1
                                        score += 10000 / len(notes) * \
                                            (0.7+math.log(combo+1, c1+c2+c3+c4+1)*0.3)
                                    elif delta <= 0.2:
                                        # Good 判定
                                        note.click = 2
                                        c2 += 1
                                        combo += 1
                                        score += 10000 / len(notes)*(0.7 +
                                                                     math.log(combo+1, c1 + c2+c3+c4+1)*0.3)*(0.9-(delta-0.08)/0.12*0.3)
                                    else:
                                        # Bad 判定
                                        note.click = -1
                                        c3 += 1
                                        combo = 0
                                    break

            # 评级
            if len(notes) == c1:
                letter = 'AP'
            elif c3+c4 == 0:
                letter = 'FC'
            elif score >= 9000:
                letter = 'S'
            elif score >= 8000:
                letter = 'A'
            elif score >= 7000:
                letter = 'B'
            elif score >= 6000:
                letter = 'C'
            else:
                letter = 'Fail'

            # 显示结算界面
            show_bgpic()
            y = 50
            for i in song_name.split('\n'):
                text_name_big = font_big.render(i, True, (255, 255, 255))
                rect_name_big = text_name_big.get_rect()
                rect_name_big.topleft = (50, y)
                screen.blit(text_name_big, rect_name_big)
                y = rect_name_big.bottom+10
            text_composer = font.render(song_composer, True, (255, 255, 255))
            rect_composer = text_composer.get_rect()
            rect_composer.topleft = (50, rect_name_big.bottom+10)
            text_diff = font.render(
                diff+' (Autoplay)'*autoplay, True, (255, 255, 255))
            rect_diff = text_diff.get_rect()
            rect_diff.topleft = (50, rect_composer.bottom+10)
            rect_return.bottomleft = (50, 550)
            rect_replay.bottomleft = (50, rect_return.top-10)
            screen.blit(text_name_big, rect_name_big)
            screen.blit(text_composer, rect_composer)
            screen.blit(text_diff, rect_diff)
            screen.blit(text_return, rect_return)
            screen.blit(text_replay, rect_replay)
            img_letter = pygame.image.load(
                os.path.join(Resources, letter+'.png'))
            rect_letter = img_letter.get_rect()
            rect_letter.midtop = (865, 50)
            text_score_big = font_big.render(
                str(round(score)).zfill(5), True, (255, 255, 255))
            rect_score_big = text_score_big.get_rect()
            rect_score_big.midtop = (865, rect_letter.bottom)
            screen.blit(img_letter, rect_letter)
            screen.blit(text_score_big, rect_score_big)
            for line in range(len(combo_his)//4):
                pygame.draw.line(
                    screen, combo_his[line*4], (line+740, rect_score_big.bottom+10), (line+740, rect_score_big.bottom+25), 1)
            text_perfect = font.render(f'Perfect: {c1}', True, colors[1])
            rect_perfect = text_perfect.get_rect()
            rect_perfect.midtop = (865, rect_score_big.bottom+35)
            text_good = font.render(f'Good: {c2}', True, colors[2])
            rect_good = text_good.get_rect()
            rect_good.midtop = (865, rect_perfect.bottom+10)
            text_bad = font.render(f'Bad: {c3}', True, colors[-1])
            rect_bad = text_bad.get_rect()
            rect_bad.midtop = (865, rect_good.bottom+10)
            text_miss = font.render(f'Miss: {c4}', True, colors[-2])
            rect_miss = text_miss.get_rect()
            rect_miss.midtop = (865, rect_bad.bottom+10)
            text_total = font.render(
                f'Total: {len(notes)}', True, (255, 255, 255))
            rect_total = text_total.get_rect()
            rect_total.midtop = (865, rect_miss.bottom+10)
            text_delta = font.render(
                f'Delta: {round(total_delta/(c1+c2+c3)*1000) if c1+c2+c3 else 0}ms', True, (255, 255, 255))
            rect_delta = text_delta.get_rect()
            rect_delta.midtop = (865, rect_total.bottom+10)
            screen.blit(text_perfect, rect_perfect)
            screen.blit(text_good, rect_good)
            screen.blit(text_bad, rect_bad)
            screen.blit(text_miss, rect_miss)
            screen.blit(text_total, rect_total)
            screen.blit(text_delta, rect_delta)
            screen.blit(img_logo, rect_logo)
            pygame.display.update()

            # 等待用户操作
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_x:
                            return
                        elif event.key == pygame.K_r:
                            return game()

        game()
