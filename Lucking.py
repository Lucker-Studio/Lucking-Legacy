import math
import os
import random
import sys
import tempfile
import time
import zipfile

import easygui
import pygame

try:
    from sys import _MEIPASS
    Charts = os.path.join(_MEIPASS, 'Charts')
    Resources = os.path.join(_MEIPASS, 'Resources')
except:
    Charts = 'Charts'
    Resources = 'Resources'

ver = 'v1.0 Beta 22'


class Button:
    # 按钮类
    def __init__(self, screen, img, rect, window_size):
        self.screen = screen
        self.img = img
        self.rect = rect
        self.screen.blit(self.img, self.rect)
        a = window_size[0]/1000
        b = window_size[1]/600
        self.rect.left *= a
        self.rect.width *= a
        self.rect.top *= b
        self.rect.height *= b

    def click(self, pos):
        # 判断是否点击到了按钮
        return self.rect.collidepoint(pos)


class Note:
    # Note 类
    def __init__(self, type, pos, time):
        self.type = type
        self.pos = pos-1
        self.time = time
        self.speed = 0
        self.multi = False
        self.click = 0
        self.clicktime = 0
        self.clickpos = 0
        self.direction = 1
        self.extendto = self.time
        self.belongto = -1
        self.fail = False

    def getcolor(self):
        if self.fail:
            return (100, 100, 100)
        else:
            return ((100, 150, 200), (200, 150, 100),
                    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (255, 255, 0))[self.type]


class Player:
    # 音乐播放组件

    music_state = False
    loaded = False
    started = False
    paused = False

    def __init__(self):
        # 初始化
        try:
            pygame.mixer.init()
            self.music_state = True
        except:
            self.music_state = False

    def open(self, file):
        # 打开文件
        if self.music_state:
            pygame.mixer.music.load(file)
            self.loaded = True
            self.started = False

    def close(self):
        # 关闭正在播放的文件
        if self.music_state:
            pygame.mixer.music.unload()
            self.loaded = False
            self.started = False

    def play(self):
        # 播放
        if self.music_state and self.loaded:
            if self.started:
                if self.paused:
                    pygame.mixer.music.unpause()
                    self.paused = False
            else:
                pygame.mixer.music.play()
                self.started = True

    def pause(self):
        # 暂停
        if self.music_state and self.started:
            pygame.mixer.music.pause()
            self.paused = True

    def stop(self):
        # 停止
        if self.music_state and self.started:
            pygame.mixer.music.stop()
            self.started = False
            self.paused = False

    def set_pos(self, pos):
        # 设置播放位置 (单位:秒)
        if self.music_state and pos >= 0:
            if not self.started:
                self.play()
            pygame.mixer.music.set_pos(pos)


if __name__ == '__main__':
    # 读取全局设置
    try:
        global_offset, show_split_line, show_edge_line, show_hit_line, window_size, key_map = eval(
            open('Lucking-config.txt').read())
    except:
        global_offset = 0
        show_split_line = True
        show_edge_line = False
        show_hit_line = False
        window_size = (1000, 600)
        key_map = '123456789'
        with open('Lucking-config.txt', 'w') as f:
            print((global_offset, show_split_line, show_edge_line,
                  show_hit_line, window_size, key_map), file=f)

    # 初始化游戏
    pygame.init()
    window = pygame.display.set_mode(window_size)
    screen = pygame.Surface((1000, 600))
    title = pygame.image.load(
        os.path.join(Resources, 'title.png'))
    img_logo_big = pygame.image.load(
        os.path.join(Resources, 'Lucking.png'))
    rect_logo_big = img_logo_big.get_rect()
    img_logo = pygame.transform.scale(img_logo_big, (100, 50))
    rect_logo = img_logo.get_rect()
    rect_logo.bottomright = (990, 590)
    pygame.display.set_caption(f'Lucking {ver}')
    pygame.display.set_icon(pygame.image.load(
        os.path.join(Resources, 'icon.png')))
    player = Player()

    def update_window():
        window.blit(pygame.transform.scale(screen, window_size), (0, 0))
        pygame.display.update()

    # 初始化文字
    font = pygame.font.Font(os.path.join(Resources, 'songhei.ttf'), 30)
    font_small = pygame.font.Font(
        os.path.join(Resources, 'songhei.ttf'), 15)
    font_big = pygame.font.Font(os.path.join(Resources, 'songhei.ttf'), 60)

    back_from_song = False
    while True:
        # 显示标题页面
        in_song = False
        if not back_from_song:
            choice_i = choice_j = 1
            state = 0
            while state == 0:
                screen.blit(title, (0, 0))
                rect_logo_big.center = (
                    500, 275-50*math.sin(time.time()*2 % math.pi))
                text_start = font.render('单击或回车以开始', True, (0, 0, 0))
                rect_start = text_start.get_rect()
                rect_start.midbottom = (500, 500)
                text_ver_small = font_small.render(
                    'Version: '+ver, True, (0, 0, 0))
                rect_ver_small = text_ver_small.get_rect()
                rect_ver_small.bottomleft = (0, 600)
                text_drag_small = font_small.render(
                    '可拖拽自制谱到窗口中', True, (0, 0, 0))
                rect_drag_small = text_drag_small.get_rect()
                rect_drag_small.midbottom = (500, 600)
                text_settings_small = font_small.render(
                    '按 S 键打开设置', True, (0, 0, 0))
                rect_settings_small = text_settings_small.get_rect()
                rect_settings_small.midbottom = (500, rect_drag_small.top)
                text_author_small = font_small.render(
                    'Author: 蔗蓝', True, (0, 0, 0))
                rect_author_small = text_author_small.get_rect()
                rect_author_small.bottomright = (1000, 600)
                screen.blit(img_logo_big, rect_logo_big)
                screen.blit(text_start, rect_start)
                screen.blit(text_ver_small, rect_ver_small)
                screen.blit(text_drag_small, rect_drag_small)
                screen.blit(text_settings_small, rect_settings_small)
                screen.blit(text_author_small, rect_author_small)
                update_window()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        in_song = True
                        state = 1
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                        items = ['谱面延迟', '显示分隔线', '显示判定边界', '显示打击线',
                                 '窗口大小', '自定义键位', '恢复默认设置']
                        while True:
                            changed = False
                            setting_item = easygui.choicebox(
                                '请选择设置项', 'Lucking 设置', items)
                            if not setting_item:
                                break
                            elif setting_item == '谱面延迟':
                                t = easygui.enterbox(
                                    '请输入谱面延迟（单位：ms）', 'Lucking 设置', str(int(global_offset*1000)))
                                if t != None:
                                    if t.strip('-').isdigit():
                                        global_offset = int(t)/1000
                                        changed = True
                                    else:
                                        easygui.msgbox('请输入整数', 'Lucking 设置')
                            elif setting_item == '显示分隔线':
                                t = easygui.boolbox(
                                    f'是否显示分隔线（当前设置：{("隐藏","显示")[show_split_line]}）', 'Lucking 设置', ('显示', '隐藏'))
                                if t != None:
                                    show_split_line = t
                                    changed = True
                            elif setting_item == '显示判定边界':
                                t = easygui.boolbox(
                                    f'是否显示判定边界（当前设置：{("隐藏","显示")[show_edge_line]}）', 'Lucking 设置', ('显示', '隐藏'))
                                if t != None:
                                    show_edge_line = t
                                    changed = True
                            elif setting_item == '显示打击线':
                                t = easygui.boolbox(
                                    f'是否显示打击线（当前设置：{("隐藏","显示")[show_hit_line]}）', 'Lucking 设置', ('显示', '隐藏'))
                                if t != None:
                                    show_hit_line = t
                                    changed = True
                            elif setting_item == '窗口大小':
                                t = easygui.enterbox(
                                    f'请输入窗口大小', 'Lucking 设置', f'{window_size[0]}x{window_size[1]}')
                                if t != None:
                                    if len(t.split('x')) != 2 or sum(map(str.isdigit, t.split('x'))) < 2:
                                        easygui.msgbox(
                                            '请输入正确的窗口大小（格式：宽x高）', 'Lucking 设置')
                                    else:
                                        window_size = tuple(
                                            map(int, t.split('x')))
                                        window = pygame.display.set_mode(
                                            window_size)
                                        update_window()
                                        changed = True
                            elif setting_item == '自定义键位':
                                t = easygui.enterbox(
                                    '请输入自定义键位', 'Lucking 设置', key_map)
                                if t != None:
                                    if len(t) != 9:
                                        easygui.msgbox(
                                            '请输入长度为9的字符串', 'Lucking 设置')
                                    else:
                                        key_map = t.lower()
                                        changed = True
                            elif setting_item == '恢复默认设置':
                                if easygui.ynbox('确定要恢复默认设置吗？', 'Lucking 设置', ('是', '否')):
                                    global_offset = 0
                                    show_split_line = True
                                    show_edge_line = False
                                    show_hit_line = False
                                    window_size = (1000, 600)
                                    key_map = '123456789'
                                    window = pygame.display.set_mode(
                                        window_size)
                                    update_window()
                                    changed = True
                            if changed:
                                with open('Lucking-config.txt', 'w') as f:
                                    print((global_offset, show_split_line, show_edge_line,
                                          show_hit_line, window_size, key_map), file=f)
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
        else:
            back_from_song = False
            state = 1

        # 选择歌曲
        if state == 1:
            packs = {int(i[0]): i[1] for i in map(
                lambda x: x.split(' ', 1), os.listdir(Charts))}
            songs = {int(i[0]): i[1] for i in map(
                lambda x: x.split(' ', 1), os.listdir(os.path.join(Charts, f'{choice_i} {packs[choice_i]}')))}
            state = 0
            while state == 0:
                screen.blit(title, (0, 0))
                screen.blit(img_logo, rect_logo)
                text_pack_big = font_big.render(
                    f'曲包:{packs[choice_i]}({choice_i}/{len(packs)})', True, (0, 0, 0))
                rect_pack_big = text_pack_big.get_rect()
                rect_pack_big.midtop = (500, 50)
                screen.blit(text_pack_big, rect_pack_big)
                y = rect_pack_big.bottom+10
                for k in songs:
                    text_song = font.render(
                        songs[k], True, (255, 0, 0) if k == choice_j else (0, 0, 0))
                    rect_song = text_song.get_rect()
                    rect_song.midtop = (500, y)
                    screen.blit(text_song, rect_song)
                    y = rect_song.bottom+10
                text_move_small = font_small.render(
                    '按方向键选择曲包/歌曲，按回车键确认，按 X 键返回', True, (0, 0, 0))
                rect_move_small = text_move_small.get_rect()
                rect_move_small.midbottom = (500, rect_drag_small.top)
                screen.blit(text_drag_small, rect_drag_small)
                screen.blit(text_move_small, rect_move_small)
                update_window()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            choice_j = (choice_j-2) % len(songs)+1
                        elif event.key == pygame.K_DOWN:
                            choice_j = choice_j % len(songs)+1
                        elif event.key == pygame.K_LEFT:
                            choice_i = (choice_i-2) % len(packs)+1
                            choice_j = 1
                            songs = {int(i[0]): i[1] for i in map(
                                lambda x: x.split(' ', 1), os.listdir(os.path.join(Charts, f'{choice_i} {packs[choice_i]}')))}
                        elif event.key == pygame.K_RIGHT:
                            choice_i = choice_i % len(packs)+1
                            choice_j = 1
                            songs = {int(i[0]): i[1] for i in map(
                                lambda x: x.split(' ', 1), os.listdir(os.path.join(Charts, f'{choice_i} {packs[choice_i]}')))}
                        elif event.key == pygame.K_RETURN:
                            state = 1
                        elif event.key == pygame.K_x:
                            state = 3
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
            if state == 1:
                dir = os.path.join(
                    Charts, f'{choice_i} {packs[choice_i]}', f'{choice_j} {songs[choice_j]}')
            elif state == 3:
                continue

        # 读取歌曲信息
        info = [i.strip() for i in open(os.path.join(
            dir, 'info.txt'), encoding='utf-8').readlines()]
        song_name, song_composer, song_bpm, song_length, song_offset = map(
            eval, info)
        beat = 60/song_bpm  # 每拍长度/秒
        offset = song_offset+global_offset  # 谱面偏移/秒

        # 初始化音频系统
        if player.music_state:
            player.open(os.path.join(dir, 'music.mp3'))
            beat_sound_1 = pygame.mixer.Sound(
                os.path.join(Resources, 'beat1.mp3'))
            beat_sound_2 = pygame.mixer.Sound(
                os.path.join(Resources, 'beat2.mp3'))
            beat_sound_3 = pygame.mixer.Sound(
                os.path.join(Resources, 'beat3.mp3'))
            play_sound = (beat_sound_1.play, beat_sound_2.play,
                          lambda: (beat_sound_1.play(), beat_sound_2.play()), beat_sound_3.play)
        else:
            play_sound = (lambda: None,)*4

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

        while True:
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
                text_composer = font.render(
                    song_composer, True, (255, 255, 255))
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
                            os.path.join(Resources, i+'.png')), pygame.Rect(button_rect), window_size)
                        button_rect.centery += 130
                screen.blit(img_logo, rect_logo)
                update_window()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_x:
                            back_from_song = in_song
                            player.close()
                            state = 2
                        elif event.key == pygame.K_a:
                            autoplay = not autoplay
                        else:
                            for i in buttons:
                                if event.key == ord(i[0].lower()):
                                    diff = i
                                    state = 1
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        for i in buttons:
                            if buttons[i].click(event.pos):
                                diff = i
                                state = 1
            if state == 2:
                break

            def game():
                # 显示加载页面
                load_time = time.time()
                show_bgpic()
                text_loading_big = font_big.render(
                    '正在加载谱面', True, (255, 255, 255))
                rect_loading_big = text_loading_big.get_rect()
                rect_loading_big.center = (500, 300)
                screen.blit(text_loading_big, rect_loading_big)
                update_window()

                # 设置文字
                text_diff = font.render(diff, True, (255, 255, 255))
                rect_diff = text_diff.get_rect()
                rect_diff.bottomright = (1000, 600)
                text_replay = font.render('按 R 键重新开始', True, (255, 255, 255))
                rect_replay = text_replay.get_rect()
                text_pause_big = font_big.render('已暂停', True, (255, 255, 255))
                rect_pause_big = text_pause_big.get_rect()
                rect_pause_big.midbottom = (500, 295)
                text_continue = font.render('单击或回车以继续', True, (255, 255, 255))
                rect_continue = text_continue.get_rect()
                rect_continue.midtop = (500, 305)

                # 解析谱面
                notes = []
                times = set()  # 每个节拍的音符数量
                multi = set()  # 存在多个音符的节拍
                last = {}  # 每一列的上一个音符
                linemotion = {0: 500}  # 判定线位置
                speed_flag = {0: 300}  # 下落速度标记
                flip_flag = {0: False}  # 左右翻转标记
                flip_now = False  # 左右翻转状态
                direction_flag = {0: False}  # 上下翻转标记
                direction_now = False  # 上下翻转状态
                repeat_start = 0  # 反复开始
                repeat_interval = 0  # 反复间隔
                repeat_times = 0  # 反复次数

                def add_note(type, pos, time):
                    # 添加 Note
                    notes.append(Note({'a': 0, 'b': 1, '?': 2, '+': 3}[type], random.randint(
                        1, 9) if type == '?' else pos, time))
                    if type != '+':
                        if time in times:
                            multi.add(time)  # 该节拍已存在音符，加入多押列表
                        else:
                            times.add(time)  # 记录该节拍

                with open(os.path.join(dir, diff+'.txt'), encoding='utf-8') as f:
                    for i in f.readlines():
                        repeat = i.startswith('\t')
                        line = i.strip()
                        if line.startswith('%'):  # 设置反复
                            tmp = line[1:].split()
                            repeat_start = float(tmp[0])
                            repeat_interval, repeat_times = map(
                                float, tmp[1].split('*'))
                        elif line:
                            tmp = line[1:].split()
                            if len(tmp) > 1:
                                t = repeat_start*repeat+float(tmp[1])
                            for f in range(int(repeat_times) if repeat else 1):
                                if line.startswith('#'):  # 谱面特效
                                    if tmp[0] == 'l':  # 判定线移动
                                        linemotion[t] = float(tmp[2])
                                    elif tmp[0] == 's':  # 下落速度
                                        speed_flag[t] = float(tmp[2])
                                    elif tmp[0] == 'f':  # 左右翻转
                                        flip_now = not flip_now
                                        flip_flag[t] = flip_now
                                    elif tmp[0] == 'd':  # 上下翻转
                                        direction_now = not direction_now
                                        direction_flag[t] = direction_now
                                elif line.startswith('$'):  # Note
                                    if len(tmp) > 3:
                                        g = tmp[2].split('*')
                                        step = float(g[0])
                                        x = 0
                                        for h in range(int(g[1] if len(g) == 2 else 1)):
                                            for j in tmp[3].split(','):
                                                k = j.split('*')
                                                o = k[0].count('-')
                                                if o == 1 and not k[0].endswith('-'):
                                                    o = int(k[0].split('-')[1])
                                                for l in range(int(k[1]) if len(k) == 2 else 1):
                                                    for m in k[0].split('-')[0]:
                                                        add_note(
                                                            tmp[0], int(m), t+x)
                                                        for p in range(o):
                                                            add_note(
                                                                '+', int(m), t+x+step*(p+1))
                                                    x += step*(o+1)
                                    elif len(tmp) == 3:
                                        for m in tmp[2]:
                                            add_note(tmp[0], int(m), t)
                                t += repeat_interval
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
                        return linemotion[before]
                    else:
                        progress = (time-before)/(after-before)
                        extent = linemotion[after]-linemotion[before]
                        return linemotion[before]+extent*(math.sin((progress-0.5)*math.pi)+1)/2

                def getflag(which, time):
                    # 获取音符属性
                    before = 0
                    for i in sorted(which):
                        if i <= time:
                            before = i
                        else:
                            break
                    return which[before]

                def culpos(note, time):
                    # 计算音符位置
                    return getlinepos(now_beat)-(time-now_beat)*note.speed*note.direction

                for i, note in enumerate(notes):
                    if note.type < 2:
                        last[note.pos] = i
                    elif note.type == 3:
                        note.belongto = last[note.pos]
                        notes[note.belongto].extendto = note.time
                    if note.time in multi:  # 多押
                        note.multi = True
                    if getflag(flip_flag, note.time):  # 左右翻转
                        note.pos = 8-note.pos
                    if getflag(direction_flag, note.time):  # 上下翻转
                        note.direction = -note.direction
                    note.speed = getflag(speed_flag, note.time)

                c1 = c2 = c3 = c4 = score = combo = total_error = 0  # 四种判定个数、得分、连击数、打击总偏差
                colors = {1: (0, 255, 0), 2: (0, 255, 255),
                          -1: (255, 0, 0), -2: (255, 0, 255)}  # 打击特效及判定线颜色
                combo_his = {0: (255, 0, 255)}  # 连击数历史记录

                # 加载界面至少显示 0.5 秒
                while time.time()-load_time < 0.5:
                    pass

                player.stop()
                start_time = time.time()  # 游戏开始时间
                while True:
                    now_time = time.time()-start_time-2  # （开始前等待2秒）
                    now_beat = (now_time-offset)/beat  # 当前节拍

                    if now_time > song_length:
                        break  # 歌曲结束

                    if now_time > 0 and not player.started:
                        player.play()  # 开始播放

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

                    for note in notes:
                        # Autoplay
                        if autoplay and now_beat > note.time and not note.click:
                            note.clicktime = note.time
                            play_sound[note.type]()
                            note.click = 1
                            c1 += 1
                            combo += 1
                            score += 10000 / len(notes)
                        # 延长键判定
                        elif note.type == 3 and now_beat > note.time and not note.click and notes[note.belongto].click > 0 and not notes[note.belongto].fail:
                            note.clicktime = note.time
                            play_sound[3]()
                            note.click = 1
                            c1 += 1
                            combo += 1
                            score += 10000 / len(notes) * \
                                (0.7+math.log(combo +
                                              1, c1+c2+c3+c4+1)*0.3)
                        # Miss 判定
                        elif (now_beat-note.time)*beat > 0.2 and not note.click:
                            note.click = -2
                            note.fail = True
                            c4 += 1
                            combo = 0

                    def show():
                        # 显示谱面
                        show_bgpic()

                        # 显示分割线
                        if show_split_line:
                            for i in range(10):
                                pygame.draw.line(
                                    screen, (100, 100, 100), (i*110+5, 0), (i*110+5, 600), 3)

                        # 显示判定边界
                        if show_edge_line:
                            for i in (1, -1):
                                t = i*getflag(speed_flag, now_beat)/beat
                                for j in range(72):
                                    pygame.draw.line(screen, colors[1], (j*14, getlinepos(
                                        now_beat)+0.08*t), (j*14+7, getlinepos(now_beat)+0.08*t), 1)
                                    pygame.draw.line(screen, colors[2], (j*14, getlinepos(
                                        now_beat)+0.2*t), (j*14+7, getlinepos(now_beat)+0.2*t), 1)

                        # 显示判定线
                        if c2+c3+c4 == 0:
                            linecolor = 1
                        elif c3+c4 == 0:
                            linecolor = 2
                        else:
                            linecolor = -1
                        pygame.draw.line(
                            screen, colors[linecolor], (0, getlinepos(now_beat)), (1000, getlinepos(now_beat)), 5)

                        for note in notes:
                            if note.extendto != note.time:
                                one = culpos(note, note.time)
                                another = culpos(note, note.extendto)
                                if -20 <= one <= 600 or -20 <= another <= 600 or one <= -20 and another >= 600 or another <= -20 and one >= 600:
                                    if one > another:
                                        a = another
                                        b = min(one, getlinepos(now_beat))
                                    else:
                                        a = one
                                        b = min(another, getlinepos(now_beat))
                                    pygame.draw.rect(
                                        screen, note.getcolor(), pygame.Rect(110*note.pos+10, a, 100, b-a))
                            if (note.type != 3 or now_beat < note.time and abs(culpos(note, note.time)-getlinepos(now_beat)) > 2.5 and not notes[note.belongto].fail) and -20 <= culpos(note, note.time) <= 600:
                                if note.click not in (-1, 1, 2):
                                    # 显示 Note
                                    width = 5 if note.type == 3 else 20
                                    rect = pygame.Rect(
                                        110*note.pos+10, culpos(note, note.time)-width/2, 100, width)
                                    if note.multi:
                                        # 显示多押提示
                                        rect2 = pygame.Rect(
                                            rect.left-2, rect.top-2, 104, 24)
                                        pygame.draw.rect(screen, (255, 255, 200),
                                                         rect2, border_radius=5)
                                    pygame.draw.rect(screen, note.getcolor(),
                                                     rect, border_radius=5)
                                    # 显示数字提示
                                    if note.type != 3:
                                        text_num = font.render(
                                            key_map[note.pos], True, (255, 255, 0))
                                        rect_num = text_num.get_rect()
                                        rect_num.center = rect.center
                                        screen.blit(text_num, rect_num)
                            if 0 < now_beat-note.clicktime <= 1 and note.click in (-1, 1, 2):
                                # 显示打击特效
                                size = (now_beat-note.clicktime)**0.5*100
                                alpha = min(
                                    1-(now_beat-note.clicktime), 0.5)/0.5*255
                                alphascr = pygame.Surface(
                                    (size, size), pygame.SRCALPHA)
                                rect = pygame.Rect(0, 0, size, size)
                                pygame.draw.rect(
                                    alphascr, (*colors[note.click], alpha), rect, 5, 5)
                                rect.center = (
                                    110*note.pos+60, getlinepos(now_beat)+note.clickpos)
                                screen.blit(alphascr, rect)
                                if show_hit_line:
                                    # 显示打击线
                                    size *= 10
                                    alphascr = pygame.Surface(
                                        (1000, 5), pygame.SRCALPHA)
                                    pygame.draw.rect(alphascr, (255, 255, 255, alpha), pygame.Rect(
                                        (1000-size)/2, 0, size, 5))
                                    screen.blit(
                                        alphascr, (0, getlinepos(now_beat)+note.clickpos-2.5))

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
                        player.pause()
                        rect_replay.midtop = (500, rect_continue.bottom+10)
                        rect_return.midtop = (500, rect_replay.bottom+10)
                        screen.blit(text_pause_big, rect_pause_big)
                        screen.blit(text_continue, rect_continue)
                        screen.blit(text_replay, rect_replay)
                        screen.blit(text_return, rect_return)
                        update_window()
                        clicked = False
                        while not clicked:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    sys.exit()
                                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                                    clicked = True
                                elif event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_x:
                                        return 1
                                    elif event.key == pygame.K_r:
                                        return 2
                        for i in range(3, 0, -1):
                            show()
                            text_num_big = font_big.render(
                                str(i), True, (255, 255, 255))
                            rect_num_big = text_num_big.get_rect()
                            rect_num_big.center = (500, 300)
                            screen.blit(text_num_big, rect_num_big)
                            update_window()
                            time.sleep(1)
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    sys.exit()
                        if player.started:
                            player.play()

                    # 刷新谱面
                    show()
                    update_window()

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
                        elif event.type == pygame.KEYDOWN:
                            # 按下数字键，打击音符
                            if not autoplay:
                                key = 0
                                while key < 9:
                                    try:
                                        if chr(event.key) == key_map[key]:
                                            break
                                        key += 1
                                    except:
                                        pass
                                if key < 9:
                                    for note in notes:
                                        error = (now_beat-note.time) * \
                                            beat  # 打击误差/秒
                                        if -0.25 <= error <= 0.2 and not note.click and note.pos == key:
                                            # 有效打击
                                            note.clicktime = now_beat
                                            total_error += now_beat-note.time
                                            play_sound[note.type]()
                                            if abs(error) <= 0.08:
                                                # Perfect 判定
                                                note.click = 1
                                                c1 += 1
                                                combo += 1
                                                score += 10000 / len(notes) * \
                                                    (0.7+math.log(combo +
                                                                  1, c1+c2+c3+c4+1)*0.3)
                                            elif abs(error) <= 0.2:
                                                # Good 判定
                                                note.click = 2
                                                c2 += 1
                                                combo += 1
                                                score += 10000 / len(notes)*(0.7 +
                                                                             math.log(combo+1, c1 + c2+c3+c4+1)*0.3)*(0.9-(error-0.08)/0.12*0.3)
                                            else:
                                                # Bad 判定
                                                note.click = -1
                                                c3 += 1
                                                combo = 0
                                            break
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            key = event.pos[0]*9//1001
                            for note in notes:
                                error = (now_beat-note.time) * \
                                    beat  # 打击误差/秒
                                if -0.25 <= error <= 0.2 and not note.click and note.pos == key:
                                    # 有效打击
                                    note.clicktime = now_beat
                                    total_error += now_beat-note.time
                                    play_sound[note.type]()
                                    if abs(error) <= 0.08:
                                        # Perfect 判定
                                        note.click = 1
                                        c1 += 1
                                        combo += 1
                                        score += 10000 / len(notes) * \
                                            (0.7+math.log(combo +
                                                          1, c1+c2+c3+c4+1)*0.3)
                                    elif abs(error) <= 0.2:
                                        # Good 判定
                                        note.click = 2
                                        c2 += 1
                                        combo += 1
                                        score += 10000 / len(notes)*(0.7 +
                                                                     math.log(combo+1, c1 + c2+c3+c4+1)*0.3)*(0.9-(error-0.08)/0.12*0.3)
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
                text_composer = font.render(
                    song_composer, True, (255, 255, 255))
                rect_composer = text_composer.get_rect()
                rect_composer.topleft = (50, rect_name_big.bottom+10)
                text_diff = font.render(
                    diff, True, (255, 255, 255))
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
                rect_letter.midtop = (790, 25 if autoplay else 50)
                if autoplay:
                    text_autoplayflag = font.render(
                        '(指 Autoplay)', True, (255, 255, 255))
                    rect_autoplayflag = text_autoplayflag.get_rect()
                    rect_autoplayflag.midtop = (790, rect_letter.bottom)
                text_score_big = font_big.render(
                    str(round(score)).zfill(5), True, (255, 255, 255))
                rect_score_big = text_score_big.get_rect()
                rect_score_big.midtop = (
                    790, rect_autoplayflag.bottom+10 if autoplay else rect_letter.bottom)
                screen.blit(img_letter, rect_letter)
                if autoplay:
                    screen.blit(text_autoplayflag, rect_autoplayflag)
                screen.blit(text_score_big, rect_score_big)
                for line in range(400):
                    pygame.draw.line(
                        screen, combo_his[line*1000//400], (line+590, rect_score_big.bottom+10), (line+590, rect_score_big.bottom+25), 1)
                text_perfect = font.render(f'Perfect: {c1}', True, colors[1])
                rect_perfect = text_perfect.get_rect()
                rect_perfect.midtop = (790, rect_score_big.bottom+35)
                text_good = font.render(f'Good: {c2}', True, colors[2])
                rect_good = text_good.get_rect()
                rect_good.midtop = (790, rect_perfect.bottom+10)
                text_bad = font.render(f'Bad: {c3}', True, colors[-1])
                rect_bad = text_bad.get_rect()
                rect_bad.midtop = (790, rect_good.bottom+10)
                text_miss = font.render(f'Miss: {c4}', True, colors[-2])
                rect_miss = text_miss.get_rect()
                rect_miss.midtop = (790, rect_bad.bottom+10)
                text_total = font.render(
                    f'Total: {len(notes)}', True, (255, 255, 255))
                rect_total = text_total.get_rect()
                rect_total.midtop = (790, rect_miss.bottom+10)
                text_average = font.render(
                    f'Average: {round(total_error/(c1+c2+c3)*1000) if c1+c2+c3 else 0:+}ms', True, (255, 255, 255))
                rect_average = text_average.get_rect()
                rect_average.midtop = (790, rect_total.bottom+10)
                screen.blit(text_perfect, rect_perfect)
                screen.blit(text_good, rect_good)
                screen.blit(text_bad, rect_bad)
                screen.blit(text_miss, rect_miss)
                screen.blit(text_total, rect_total)
                screen.blit(text_average, rect_average)
                screen.blit(img_logo, rect_logo)
                update_window()

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
