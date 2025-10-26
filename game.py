import pygame
import sys
import random
import cv2
import mediapipe as mp
import numpy as np
import os
import librosa

# 跳跃音效文件路径
JUMP_SOUND_FILE = "bubblepop-254773.mp3"

# 初始化
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flower Hop - 音乐节奏跳跃游戏")
clock = pygame.time.Clock()
import pygame
import sys
import random
import cv2
import mediapipe as mp
import numpy as np
import os
import librosa

# 跳跃音效文件路径
JUMP_SOUND_FILE = "bubblepop-254773.mp3"

# 初始化
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flower Hop - 音乐节奏跳跃游戏")
clock = pygame.time.Clock()

# 酸性设计美学色彩系统 - 赛博朋克风格
class ColorScheme:
    # 深色背景（纯黑基调）
    BG_TOP = (10, 0, 20)           # 深紫黑
    BG_BOTTOM = (0, 5, 15)         # 深蓝黑
    
    # 霓虹色彩（高饱和度对比色）
    NEON_PINK = (255, 20, 147)     # 霓虹粉
    NEON_CYAN = (0, 255, 255)      # 电光蓝
    NEON_GREEN = (57, 255, 20)     # 荧光绿
    NEON_PURPLE = (191, 0, 255)    # 荧光紫
    NEON_YELLOW = (255, 255, 0)    # 荧光黄
    NEON_ORANGE = (255, 100, 0)    # 荧光橙
    
    # 平台颜色（金属质感渐变）
    PLATFORM_PRIMARY = (255, 20, 147)   # 霓虹粉
    PLATFORM_ACCENT = (0, 255, 255)     # 电光蓝
    PLATFORM_GLOW = (57, 255, 20)       # 荧光绿光晕
    
    # UI元素（高对比度）
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (0, 255, 255)      # 电光蓝文字
    ACCENT = (255, 20, 147)             # 霓虹粉强调
    SUCCESS = (57, 255, 20)             # 荧光绿
    WARNING = (255, 255, 0)             # 荧光黄
    ERROR = (255, 0, 100)               # 霓虹红
    
    # 粒子效果（赛博朋克色彩爆炸）
    PARTICLE_COLORS = [
        (255, 20, 147),   # 霓虹粉
        (0, 255, 255),    # 电光蓝
        (57, 255, 20),    # 荧光绿
        (191, 0, 255),    # 荧光紫
        (255, 255, 0),    # 荧光黄
        (255, 100, 0)     # 荧光橙
    ]
    
    # 故障艺术色彩
    GLITCH_RED = (255, 0, 100)
    GLITCH_CYAN = (0, 255, 200)
    GLITCH_GREEN = (100, 255, 0)

# 传统颜色兼容
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 音乐文件路径
MUSIC_FILE = "find_yourself.mp3"

# 全局变量
music_playing = False
beats = []
current_beat_index = 0

# 加载音乐和节奏
def load_music_and_beats():
    global music_playing, beats
    
    if not os.path.exists(MUSIC_FILE):
        print(f"❌ 音乐文件 '{MUSIC_FILE}' 不存在！")
        print("请将陶喆的《找自己》音乐文件命名为 'find_yourself.mp3' 并放在游戏目录下。")
        music_playing = False
        return
    
    try:
        # 加载音乐到 pygame
        print("🎵 正在加载音乐到 pygame...")
        pygame.mixer.music.load(MUSIC_FILE)
        print("✅ pygame 音乐加载成功！")
        
        # 使用 librosa 分析音乐节奏
        print("🎵 正在使用 librosa 分析音乐节奏（可能需要几秒钟）...")
        
        try:
            y, sr = librosa.load(MUSIC_FILE, sr=None)
            print(f"✅ librosa 加载成功！采样率: {sr} Hz")
            
            # 检测节拍
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)
            
            beats = list(beat_times)
            print(f"✅ 检测到 {len(beats)} 个节拍，BPM: {tempo:.1f}")
            
        except Exception as librosa_error:
            print(f"⚠️ librosa 节奏分析失败: {librosa_error}")
            print("⚠️ 可能需要安装 ffmpeg 或 audioread")
            print("💡 将使用固定节奏生成平台...")
            
            # 备用方案：使用固定BPM生成节拍
            BPM = 98  # 陶喆《找自己》的大约BPM
            BEAT_INTERVAL = 60.0 / BPM
            SONG_LENGTH = 240  # 假设4分钟
            beats = [i * BEAT_INTERVAL for i in range(int(SONG_LENGTH / BEAT_INTERVAL))]
            print(f"✅ 使用固定节奏，BPM: {BPM}，生成 {len(beats)} 个节拍")
        
        music_playing = True
        
    except Exception as e:
        print(f"❌ 加载音乐失败: {e}")
        print("💡 游戏将在没有音乐的情况下运行")
        music_playing = False

# MediaPipe 人脸检测
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# 摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ 无法打开摄像头！")
    sys.exit(1)

# 粒子系统

class Player:
    def __init__(self):
        self.size = 70  # 缩小嘴巴显示尺寸
        self.x = WIDTH // 2 - 100  # 偏向中间偏左的位置
        self.y = HEIGHT // 2  # 垂直居中
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -12
        self.alive = True
        self.on_ground = False
        self.mouth_open = False
        self.mouth_image = None
        self.camera_x = 0  # 摄像机X坐标，用于横向滚动
        self.last_mouth_open = False
        self.rotation = 0  # 旋转角度
        self.scale_pulse = 1.0  # 缩放脉冲
    
    def update(self, platforms):
        if not self.alive:
            return
        
        # 自动向右移动
        self.camera_x += self.speed
        
        # 滞空时间控制
        if hasattr(self, 'air_timer'):
            self.air_timer += 1
        
        # 应用重力
        if self.mouth_open:
            gravity = 1.1  # 张嘴下落更快
        else:
            # 张嘴弹跳后，闭嘴时滞空时间短，快速下落
            if hasattr(self, 'air_timer') and self.air_timer < 10:
                gravity = 1.1  # 前10帧仍然快速下落
            else:
                gravity = 0.6  # 闭嘴下落也更快
        self.vel_y += gravity
        self.y += self.vel_y
        
        # 动画效果
        self.rotation = (self.rotation + 2) % 360  # 持续旋转
        self.scale_pulse = 1.0 + 0.1 * abs(np.sin(pygame.time.get_ticks() / 500))  # 脉冲效果
        
        # 平台碰撞
        self.on_ground = False
        for platform in platforms:
            platform_screen_x = platform.x - self.camera_x
            
            # 计算玩家的底部中心点
            player_bottom = self.y + self.size // 2
            player_left = self.x - self.size // 2
            player_right = self.x + self.size // 2
            player_center_x = self.x
            
            # 检测碰撞：玩家底部接触平台顶部
            if (self.vel_y >= 0 and 
                player_bottom >= platform.y and 
                player_bottom <= platform.y + 20 and
                player_right > platform_screen_x and 
                player_left < platform_screen_x + platform.width):
                
                # 检查是否落在缺口上
                if platform.has_gap:
                    gap_start = platform_screen_x + platform.width // 2 - platform.gap_width // 2
                    gap_end = gap_start + platform.gap_width
                    # 使用玩家中心点判断是否在缺口内
                    if player_center_x > gap_start and player_center_x < gap_end:
                        continue  # 穿过缺口
                
                # 站在平台上
                self.y = platform.y - self.size // 2
                self.vel_y = 0
                self.on_ground = True
                break
        
        # 检查掉落
        if self.y > HEIGHT + 100:
            self.alive = False
    
    def jump(self):
        """跳跃方法，张嘴和闭嘴弹跳高度不同"""
        if self.on_ground:
            if self.mouth_open:
                self.jump_power = -16  # 张嘴弹跳更高
                self.vel_y = self.jump_power
                self.on_ground = False
                self.air_timer = 0  # 新增滞空计时器
            else:
                self.jump_power = -10  # 闭嘴弹跳较低
                self.vel_y = self.jump_power
                self.on_ground = False
                self.air_timer = 0

    def draw_mouth(self, screen, mouth_image):
        """绘制嘴巴图像（酸性设计+霓虹光效）"""
        center_x = int(self.x)
        center_y = int(self.y)
        display_size = int(self.size * self.scale_pulse)
        if mouth_image is not None:
            mouth_surface = pygame.transform.scale(mouth_image, (display_size, display_size))
            mouth_surface = pygame.transform.rotate(mouth_surface, self.rotation)
            glow_radius = display_size // 2 + 20
            glow_colors = [
                ColorScheme.NEON_PINK,
                ColorScheme.NEON_CYAN,
                ColorScheme.NEON_GREEN,
                ColorScheme.NEON_PURPLE
            ]
            for i, base_color in enumerate(glow_colors):
                radius = glow_radius + i * 15
                alpha = 120 - i * 25
                glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*base_color, alpha), (radius, radius), radius)
                glitch_x = random.randint(-3, 3) if random.random() < 0.1 else 0
                glitch_y = random.randint(-3, 3) if random.random() < 0.1 else 0
                screen.blit(glow_surf, (center_x - radius + glitch_x, center_y - radius + glitch_y))
            rect = mouth_surface.get_rect(center=(center_x, center_y))
            screen.blit(mouth_surface, rect)
            ring_colors = [
                (ColorScheme.NEON_PINK, 5),
                (ColorScheme.NEON_CYAN, 4),
                (ColorScheme.NEON_GREEN, 3)
            ]
            for color, width in ring_colors:
                pygame.draw.circle(screen, color, (center_x, center_y), display_size // 2 + 8, width)
                if self.mouth_open and random.random() < 0.3:
                    offset = random.randint(2, 5)
                    pygame.draw.circle(screen, ColorScheme.GLITCH_RED, (center_x + offset, center_y), display_size // 2 + 8, 2)
                    pygame.draw.circle(screen, ColorScheme.GLITCH_CYAN, (center_x - offset, center_y), display_size // 2 + 8, 2)
            if self.mouth_open:
                for angle in range(0, 360, 45):
                    rad = np.radians(angle + self.rotation)
                    star_x = center_x + int((display_size // 2 + 25) * np.cos(rad))
                    star_y = center_y + int((display_size // 2 + 25) * np.sin(rad))
                    star_color = random.choice([ColorScheme.NEON_YELLOW, ColorScheme.NEON_GREEN, ColorScheme.NEON_CYAN])
                    pygame.draw.circle(screen, star_color, (star_x, star_y), 4)
                    pygame.draw.circle(screen, (255, 255, 255), (star_x, star_y), 2)
        else:
            # 默认占位符（霓虹圆形）
            pygame.draw.circle(screen, ColorScheme.NEON_PINK, (center_x, center_y), display_size // 2)
            pygame.draw.circle(screen, ColorScheme.NEON_CYAN, (center_x, center_y), display_size // 2, 5)

class Platform:
    def __init__(self, x, y, width, has_gap=False):
        self.x = x
        self.y = y
        self.width = width
        self.has_gap = has_gap
        self.gap_width = 80 if has_gap else 0
        self.height = 25  # 稍微增加高度
        self.corner_radius = 12  # 圆角半径
    
    def draw_platform_segment(self, screen, x, y, width):
        """绘制单个平台段（金属质感+霓虹边缘）"""
        surf = pygame.Surface((width, self.height), pygame.SRCALPHA)
        for i in range(self.height):
            ratio = i / self.height
            r = int(ColorScheme.PLATFORM_PRIMARY[0] * (1 - ratio) + ColorScheme.PLATFORM_ACCENT[0] * ratio)
            g = int(ColorScheme.PLATFORM_PRIMARY[1] * (1 - ratio) + ColorScheme.PLATFORM_ACCENT[1] * ratio)
            b = int(ColorScheme.PLATFORM_PRIMARY[2] * (1 - ratio) + ColorScheme.PLATFORM_ACCENT[2] * ratio)
            pygame.draw.line(surf, (r, g, b, 220), (self.corner_radius, i), (width - self.corner_radius, i))
        screen.blit(surf, (x, y))

    def draw(self, screen):
        """平台主绘制方法，支持缺口和完整平台"""
        if self.has_gap and self.gap_width > 0:
            left_width = self.width // 2 - self.gap_width // 2
            right_width = self.width - left_width - self.gap_width
            # 左侧平台段
            self.draw_platform_segment(screen, self.x, self.y, left_width)
            # 右侧平台段
            self.draw_platform_segment(screen, self.x + left_width + self.gap_width, self.y, right_width)
        else:
            self.draw_platform_segment(screen, self.x, self.y, self.width)

class Game:
    def __init__(self):
        self.player = Player()
        self.platforms = []
        self.score = 0
        self.game_over = False
        self.music_start_time = 0
        # oh～文本动画列表，每个元素为 dict: {x, y, alpha, life, font_size}
        self.oh_texts = []

        # 加载跳跃音效
        self.jump_sound = None
        if os.path.exists(JUMP_SOUND_FILE):
            try:
                self.jump_sound = pygame.mixer.Sound(JUMP_SOUND_FILE)
            except Exception as e:
                print(f"❌ 跳跃音效加载失败: {e}")
        else:
            print(f"⚠️ 跳跃音效文件 {JUMP_SOUND_FILE} 不存在")

        # 创建初始平台
        self.create_initial_platforms()

        # 立即开始播放音乐
        if music_playing:
            pygame.mixer.music.play()
            self.music_start_time = pygame.time.get_ticks()
    
    
    
    def create_initial_platforms(self):
        """创建初始平台，增加平台数量让玩家有更多准备时间"""
        platforms = []
        # 地面平台 - 延长到屏幕外更远的位置
        platforms.append(Platform(-WIDTH, HEIGHT - 110, WIDTH * 4, False))
        # 初始平台更多，确保玩家有足够时间适应
        x = WIDTH // 2
        for i in range(15):  # 增加到15个初始平台
            has_gap = i >= 12
            width = random.randint(220, 320)
            y = HEIGHT - 110 - random.randint(0, 15)
            platforms.append(Platform(x, y, width, has_gap))
            if i < 10:
                x += random.randint(140, 170)
            elif i < 12:
                x += random.randint(160, 190)
            else:
                x += random.randint(180, 230)
        return platforms
    
    def update_platforms(self):
        """根据音乐节奏生成平台"""
        global current_beat_index
        
        # 获取最右侧平台的X坐标
        if len(self.platforms) > 0:
            rightmost_x = max(p.x + p.width for p in self.platforms)
        else:
            rightmost_x = 0
        
        # 根据游戏进度调整难度
        game_progress = self.player.camera_x
        is_easy_phase = game_progress < 3000  # 前3000像素为简单阶段
        
        # 确保始终有足够的平台在右侧
        while rightmost_x < self.player.camera_x + WIDTH * 1.5:
            if music_playing and len(beats) > 0:
                current_time = (pygame.time.get_ticks() - self.music_start_time) / 1000.0
                
                # 检查是否到达节拍点
                if current_beat_index < len(beats) and current_time >= beats[current_beat_index]:
                    # 在节拍点创建有缺口的平台
                    if is_easy_phase:
                        # 简单阶段：间隔小，很少缺口
                        gap = random.randint(100, 140)
                        width = random.randint(200, 300)
                        y = HEIGHT - 110 - random.randint(0, 30)
                        has_gap = random.random() < 0.2  # 只有20%概率有缺口
                    else:
                        # 正常难度
                        gap = random.randint(120, 180)
                        width = random.randint(180, 280)
                        y = HEIGHT - 110 - random.randint(0, 60)
                        has_gap = True
                    
                    x = rightmost_x + gap
                    self.platforms.append(Platform(x, y, width, has_gap))
                    
                    current_beat_index += 1
                    if current_beat_index % 10 == 0:
                        print(f"🎵 节拍 {current_beat_index}/{len(beats)}")
                    
                    rightmost_x = x + width
                else:
                    # 非节拍时生成普通平台
                    if is_easy_phase:
                        gap = random.randint(80, 130)
                        width = random.randint(200, 300)
                        y = HEIGHT - 110 - random.randint(0, 20)
                    else:
                        gap = random.randint(100, 160)
                        width = random.randint(180, 280)
                        y = HEIGHT - 110 - random.randint(0, 40)
                    
                    x = rightmost_x + gap
                    self.platforms.append(Platform(x, y, width, False))
                    rightmost_x = x + width
            else:
                # 没有音乐时的随机生成
                gap = random.randint(100, 160)
                width = random.randint(180, 280)
                y = HEIGHT - 110 - random.randint(0, 40)
                x = rightmost_x + gap
                has_gap = random.random() < 0.3
                
                self.platforms.append(Platform(x, y, width, has_gap))
                rightmost_x = x + width
        
        # 平台离开屏幕后不移除，保持存在
        # 注释掉原来的移除逻辑
        # self.platforms = [p for p in self.platforms if p.x + p.width > self.player.camera_x - 100]
    
    def draw_gradient_background(self):
        """绘制赛博朋克酸性渐变背景"""
        for y in range(HEIGHT):
            # 从深紫黑到深蓝黑的渐变
            ratio = y / HEIGHT
            r = int(ColorScheme.BG_TOP[0] + (ColorScheme.BG_BOTTOM[0] - ColorScheme.BG_TOP[0]) * ratio)
            g = int(ColorScheme.BG_TOP[1] + (ColorScheme.BG_BOTTOM[1] - ColorScheme.BG_TOP[1]) * ratio)
            b = int(ColorScheme.BG_TOP[2] + (ColorScheme.BG_BOTTOM[2] - ColorScheme.BG_TOP[2]) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
        
        # 添加随机故障扫描线效果
        if random.random() < 0.05:  # 5%概率出现故障线
            glitch_y = random.randint(0, HEIGHT)
            glitch_color = random.choice([ColorScheme.GLITCH_RED, ColorScheme.GLITCH_CYAN, ColorScheme.GLITCH_GREEN])
            for i in range(3):
                y = glitch_y + i - 1
                if 0 <= y < HEIGHT:
                    alpha_surf = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
                    alpha_surf.fill((*glitch_color, 80))
                    screen.blit(alpha_surf, (0, y))
    
    def draw_music_lines(self):
        """绘制霓虹音乐波纹效果（赛博朋克风格）"""
        if not music_playing or len(beats) == 0:
            return
        
        current_time = (pygame.time.get_ticks() - self.music_start_time) / 1000.0
        
        # 计算当前是否接近节拍点
        beat_intensity = 0
        for beat_time in beats:
            time_diff = abs(current_time - beat_time)
            if time_diff < 0.15:
                beat_intensity = max(beat_intensity, 1.0 - time_diff / 0.15)
        
        # 绘制多层霓虹波纹
        if beat_intensity > 0.3:
            num_waves = 12  # 增加波纹数量
            for i in range(num_waves):
                # 随机选择霓虹色
                colors = [ColorScheme.NEON_PINK, ColorScheme.NEON_CYAN, ColorScheme.NEON_GREEN, 
                         ColorScheme.NEON_PURPLE, ColorScheme.NEON_YELLOW]
                wave_color = colors[i % len(colors)]
                
                # 计算波纹位置（带故障偏移）
                base_x = (WIDTH // num_waves) * i + (WIDTH // (num_waves * 2))
                glitch_offset = random.randint(-int(beat_intensity * 30), int(beat_intensity * 30))
                x = base_x + glitch_offset
                
                # 波纹高度随节奏剧烈变化
                line_height = int(HEIGHT * (0.4 + beat_intensity * 0.6))
                y_start = (HEIGHT - line_height) // 2
                
                # 绘制霓虹线条（带发光效果）
                line_width = int(3 + beat_intensity * 6)
                
                # 外层光晕
                for glow_level in range(3, 0, -1):
                    glow_width = line_width + glow_level * 4
                    alpha = int(80 * beat_intensity / glow_level)
                    for dy in range(line_height):
                        ratio = dy / line_height
                        # 波纹内渐变（从一种霓虹色到另一种）
                        next_color = colors[(i + 1) % len(colors)]
                        r = int(wave_color[0] * (1 - ratio) + next_color[0] * ratio)
                        g = int(wave_color[1] * (1 - ratio) + next_color[1] * ratio)
                        b = int(wave_color[2] * (1 - ratio) + next_color[2] * ratio)
                        
                        surf = pygame.Surface((glow_width, 1), pygame.SRCALPHA)
                        surf.fill((r, g, b, alpha))
                        screen.blit(surf, (x - glow_width // 2, y_start + dy))
                
                # 核心亮线
                for dy in range(line_height):
                    ratio = dy / line_height
                    next_color = colors[(i + 1) % len(colors)]
                    r = int(wave_color[0] * (1 - ratio) + next_color[0] * ratio)
                    g = int(wave_color[1] * (1 - ratio) + next_color[1] * ratio)
                    b = int(wave_color[2] * (1 - ratio) + next_color[2] * ratio)
                    
                    surf = pygame.Surface((line_width, 1), pygame.SRCALPHA)
                    surf.fill((r, g, b, int(255 * beat_intensity)))
                    screen.blit(surf, (x - line_width // 2, y_start + dy))
    
    def draw_macos_ui(self):
        """绘制赛博朋克UI（霓虹边框+故障效果）"""
        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 28)

        # 面板参数
        panel_x = 20
        panel_y = 20
        panel_w = 320

        # 创建霓虹面板
        panel_surf = pygame.Surface((panel_w, 170), pygame.SRCALPHA)
        # 深色半透明背景
        pygame.draw.rect(panel_surf, (5, 0, 15, 200), (0, 0, panel_w, 170), border_radius=8)

        # 多层霓虹边框
        pygame.draw.rect(panel_surf, (*ColorScheme.NEON_PINK, 255), (0, 0, panel_w, 170), 3, border_radius=8)
        pygame.draw.rect(panel_surf, (*ColorScheme.NEON_CYAN, 180), (3, 3, panel_w-6, 164), 2, border_radius=6)

        # 故障边框（随机出现）
        if random.random() < 0.15:
            glitch_offset = random.randint(-3, 3)
            pygame.draw.rect(panel_surf, (*ColorScheme.GLITCH_RED, 150), 
                           (glitch_offset, 0, panel_w, 170), 2, border_radius=8)

        screen.blit(panel_surf, (panel_x, panel_y))

        # 统一行间距设置
        line_spacing = 44  # 每行间距
        extra_distance_gap = 18  # 距离与提示之间额外间距
        base_y = 48  # 顶部留白加大，原28改为48

        # 居中计算
        def center_x(text_surf):
            return panel_x + (panel_w - text_surf.get_width()) // 2

        # 距离居中
        distance_text = font.render(f"{int(self.player.camera_x)}m", True, ColorScheme.NEON_CYAN)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_text = font.render(f"{int(self.player.camera_x)}m", True, (*ColorScheme.NEON_PINK, 100))
            screen.blit(glow_text, (center_x(glow_text) + offset[0], base_y + offset[1]))
        screen.blit(distance_text, (center_x(distance_text), base_y))

        # 提示居中
        label_text = small_font.render("OPEN MOUTH >> JUMP", True, ColorScheme.NEON_YELLOW)
        screen.blit(label_text, (center_x(label_text), base_y + line_spacing + extra_distance_gap))

        # 节拍进度居中，使用与提示一致的字体大小
        if music_playing and len(beats) > 0:
            beat_text = font.render(f"{current_beat_index}/{len(beats)}", True, ColorScheme.NEON_PURPLE)
            screen.blit(beat_text, (center_x(beat_text), base_y + line_spacing * 2 + extra_distance_gap))
        
        # 底部霓虹提示条
        hint_surf = pygame.Surface((WIDTH - 40, 60), pygame.SRCALPHA)
        pygame.draw.rect(hint_surf, (0, 0, 0, 180), (0, 0, WIDTH - 40, 60), border_radius=10)
        pygame.draw.rect(hint_surf, (*ColorScheme.NEON_CYAN, 255), (0, 0, WIDTH - 40, 60), 2, border_radius=10)
        pygame.draw.rect(hint_surf, (*ColorScheme.NEON_PINK, 150), (2, 2, WIDTH - 44, 56), 1, border_radius=8)
        screen.blit(hint_surf, (20, HEIGHT - 80))
        
        hint_text = small_font.render("[ R ] RESTART  |  [ ESC ] EXIT", True, ColorScheme.NEON_GREEN)
        hint_rect = hint_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(hint_text, hint_rect)
    
    def draw_game_over(self):
        """绘制游戏结束界面（酸性故障艺术风格）"""
        # 深色半透明遮罩
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        # 游戏结束面板
        panel_w, panel_h = 600, 350
        panel_x = (WIDTH - panel_w) // 2
        panel_y = (HEIGHT - panel_h) // 2
        
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        # 深色背景
        pygame.draw.rect(panel_surf, (10, 0, 20, 250), (0, 0, panel_w, panel_h), border_radius=15)
        
        # 多层霓虹边框
        pygame.draw.rect(panel_surf, (*ColorScheme.NEON_PINK, 255), (0, 0, panel_w, panel_h), 4, border_radius=15)
        pygame.draw.rect(panel_surf, (*ColorScheme.NEON_CYAN, 200), (4, 4, panel_w-8, panel_h-8), 3, border_radius=12)
        pygame.draw.rect(panel_surf, (*ColorScheme.NEON_GREEN, 150), (8, 8, panel_w-16, panel_h-16), 2, border_radius=10)
        
        # 随机故障边框
        if random.random() < 0.5:
            glitch_x = random.randint(-5, 5)
            glitch_y = random.randint(-3, 3)
            pygame.draw.rect(panel_surf, (*ColorScheme.GLITCH_RED, 180), 
                           (glitch_x, glitch_y, panel_w, panel_h), 3, border_radius=15)
        
        screen.blit(panel_surf, (panel_x, panel_y))
        
        # 文字
        title_font = pygame.font.Font(None, 92)
        text_font = pygame.font.Font(None, 54)
        hint_font = pygame.font.Font(None, 38)
        
        # "GAME OVER" 标题（故障分离效果）
        title_text = "GAME OVER"
        
        # RGB分离故障效果
        title_r = title_font.render(title_text, True, ColorScheme.GLITCH_RED)
        title_g = title_font.render(title_text, True, ColorScheme.NEON_GREEN)
        title_b = title_font.render(title_text, True, ColorScheme.NEON_CYAN)
        title_main = title_font.render(title_text, True, ColorScheme.NEON_PINK)
        
        title_rect = title_main.get_rect(center=(WIDTH // 2, panel_y + 90))
        
        # 绘制分离图层
        screen.blit(title_r, (title_rect.x - 4, title_rect.y + 2))
        screen.blit(title_b, (title_rect.x + 4, title_rect.y - 2))
        screen.blit(title_g, (title_rect.x + 2, title_rect.y + 3))
        screen.blit(title_main, title_rect)
        
        # 距离显示（霓虹数字）
        distance_text = f"DISTANCE: {int(self.player.camera_x)}m"
        distance = text_font.render(distance_text, True, ColorScheme.NEON_CYAN)
        
        # 添加发光效果
        for angle in range(0, 360, 45):
            offset_x = int(3 * np.cos(np.radians(angle)))
            offset_y = int(3 * np.sin(np.radians(angle)))
            glow = text_font.render(distance_text, True, (*ColorScheme.NEON_PINK, 80))
            screen.blit(glow, (WIDTH // 2 - distance.get_width() // 2 + offset_x, panel_y + 180 + offset_y))
        
        distance_rect = distance.get_rect(center=(WIDTH // 2, panel_y + 180))
        screen.blit(distance, distance_rect)
        
        # 重启提示（脉冲动画）
        hint_text = "[ R ] RESTART"
        hint = hint_font.render(hint_text, True, ColorScheme.NEON_GREEN)
        
        # 脉冲动画
        pulse = 1.0 + 0.3 * abs(np.sin(pygame.time.get_ticks() / 250))
        hint_scaled = pygame.transform.scale(hint, (int(hint.get_width() * pulse), int(hint.get_height() * pulse)))
        hint_scaled_rect = hint_scaled.get_rect(center=(WIDTH // 2, panel_y + 270))
        
        # 绘制光晕
        glow_size = int(hint.get_width() * pulse * 1.2)
        glow_surf = pygame.Surface((glow_size, int(hint.get_height() * pulse * 1.5)), pygame.SRCALPHA)
        for i in range(5):
            alpha = 60 - i * 10
            color = ColorScheme.NEON_YELLOW if i % 2 == 0 else ColorScheme.NEON_GREEN
            pygame.draw.ellipse(glow_surf, (*color, alpha), glow_surf.get_rect())
        screen.blit(glow_surf, (hint_scaled_rect.x - (glow_size - hint_scaled_rect.width) // 2, 
                                hint_scaled_rect.y - 10))
        
        screen.blit(hint_scaled, hint_scaled_rect)
    
    def detect_mouth(self, frame):
        """检测嘴部并提取图像"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            h, w = frame.shape[:2]
            
            # 嘴唇关键点
            upper_lip = [face_landmarks.landmark[i] for i in [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]]
            lower_lip = [face_landmarks.landmark[i] for i in [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]]
            
            # 计算嘴巴张开程度
            upper_center = np.mean([[p.x * w, p.y * h] for p in upper_lip], axis=0)
            lower_center = np.mean([[p.x * w, p.y * h] for p in lower_lip], axis=0)
            vertical_distance = np.linalg.norm(upper_center - lower_center)
            
            mouth_left = face_landmarks.landmark[61]
            mouth_right = face_landmarks.landmark[291]
            horizontal_distance = np.linalg.norm([
                (mouth_left.x - mouth_right.x) * w,
                (mouth_left.y - mouth_right.y) * h
            ])
            
            ratio = vertical_distance / horizontal_distance if horizontal_distance > 0 else 0
            self.player.mouth_open = ratio > 0.35
            
            # 提取嘴部区域
            mouth_points = []
            for idx in [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 146, 91, 181, 84, 17, 314, 405, 321, 375]:
                point = face_landmarks.landmark[idx]
                mouth_points.append([int(point.x * w), int(point.y * h)])
            
            mouth_points = np.array(mouth_points)
            x, y, w_mouth, h_mouth = cv2.boundingRect(mouth_points)
            
            # 扩展边界
            margin = 15
            x = max(0, x - margin)
            y = max(0, y - margin)
            w_mouth = min(w - x, w_mouth + 2 * margin)
            h_mouth = min(h - y, h_mouth + 2 * margin)
            
            if w_mouth > 0 and h_mouth > 0:
                mouth_roi = frame[y:y+h_mouth, x:x+w_mouth]
                mouth_roi = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2RGB)
                mouth_roi = np.rot90(mouth_roi)
                self.player.mouth_image = pygame.surfarray.make_surface(mouth_roi)
            else:
                self.player.mouth_image = None
        else:
            self.player.mouth_open = False
            self.player.mouth_image = None
    
    def update(self):
        if self.game_over:
            return
        
        # 读取摄像头
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            self.detect_mouth(frame)
        
        # 记录之前的状态
        was_on_ground = self.player.on_ground
        
        # 嘴巴控制跳跃 - 只在嘴巴从闭到开时跳跃
        if self.player.mouth_open and not self.player.last_mouth_open:
            if self.player.on_ground:
                self.player.jump()
                # 播放跳跃音效
                if self.jump_sound:
                    self.jump_sound.play()
                # 添加oh～文本动画
                oh_x = int(self.player.x)
                oh_y = int(self.player.y - self.player.size // 2)
                self.oh_texts.append({
                    "x": oh_x,
                    "y": oh_y,
                    "alpha": 255,
                    "life": 0,
                    "font_size": random.randint(38, 52)
                })
        
        # 更新 last_mouth_open 状态
        self.player.last_mouth_open = self.player.mouth_open
        
        # 更新玩家
        self.player.update(self.platforms)
        # 更新oh~文本动画（更明显、更好看，飘向顶部边框）
        for oh in self.oh_texts:
            # 计算目标点（顶部边框中心）
            target_x = WIDTH // 2
            target_y = 48  # 与UI顶部文字对齐
            # 当前点到目标点的插值
            progress = min(1.0, oh["life"] / 40)
            oh["x"] = int(oh["x"] * (1 - progress) + target_x * progress)
            oh["y"] = int(oh["y"] * (1 - progress) + target_y * progress)
            oh["life"] += 1
            oh["alpha"] = max(0, 255 - oh["life"] * 6)  # 逐渐透明
        # 移除消失的文本（完全出框或透明）
        self.oh_texts = [oh for oh in self.oh_texts if oh["alpha"] > 0 and oh["y"] > 0]
        
        # 检测落地（无粒子效果）
        
        # 删除粒子相关更新
        
        # 更新平台
        self.update_platforms()
        
        # 更新分数
        if self.player.alive:
            self.score += 1
        else:
            self.game_over = True
    
    def draw(self):
        # 渐变背景
        self.draw_gradient_background()
        
        # 绘制随音乐抖动的背景线条
        self.draw_music_lines()
        
        # 删除粒子绘制
        
        # 绘制平台（相对于摄像机，使用新的绘制方法）
        for platform in self.platforms:
            platform_screen_x = platform.x - self.player.camera_x
            if -100 < platform_screen_x < WIDTH + 100:  # 只绘制可见的平台
                # 临时创建一个screen_platform用于绘制
                screen_platform = Platform(platform_screen_x, platform.y, platform.width, platform.has_gap)
                screen_platform.gap_width = platform.gap_width
                screen_platform.draw(screen)
        
        # 绘制玩家（嘴巴）
        if self.player.alive:
            self.player.draw_mouth(screen, self.player.mouth_image)
        # 绘制oh~文本动画（更明显、更好看，带发光、加粗、飘向顶部）
        for oh in self.oh_texts:
            # 更大更粗字体
            font_size = max(oh["font_size"], 60)
            font = pygame.font.Font(None, font_size)
            text = "oh~"
            # 发光层
            for glow in range(6, 0, -1):
                glow_font = pygame.font.Font(None, font_size + glow * 6)
                glow_surf = glow_font.render(text, True, ColorScheme.NEON_PINK)
                glow_surf.set_alpha(int(oh["alpha"] * 0.12 * glow))
                screen.blit(glow_surf, (oh["x"] - glow_surf.get_width() // 2, oh["y"] - glow_surf.get_height() // 2))
            # 主文字（荧光粉加粗）
            text_surf = font.render(text, True, ColorScheme.NEON_PINK)
            text_surf.set_alpha(oh["alpha"])
            screen.blit(text_surf, (oh["x"] - text_surf.get_width() // 2, oh["y"] - text_surf.get_height() // 2))
        
        # UI - macOS风格毛玻璃效果
        self.draw_macos_ui()

        # 右上角显示摄像头人脸识别影像（原始帧）
        # 只在摄像头帧可用时显示
        try:
            ret, frame = cap.read()
            if ret:
                # 翻转并缩放
                frame = cv2.flip(frame, 1)
                # 缩小比例，底部与左边边框齐平
                cam_w, cam_h = 220, 140
                small_frame = cv2.resize(frame, (cam_w, cam_h))
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                cam_surf = pygame.surfarray.make_surface(np.rot90(rgb_frame))
                # 右上角坐标（左边和底部与边框对齐）
                cam_x = WIDTH - cam_w - 20
                cam_y = 20
                # 霓虹边框
                border_surf = pygame.Surface((cam_w + 8, cam_h + 8), pygame.SRCALPHA)
                pygame.draw.rect(border_surf, ColorScheme.NEON_CYAN, (0, 0, cam_w + 8, cam_h + 8), 6, border_radius=18)
                pygame.draw.rect(border_surf, ColorScheme.NEON_PINK, (4, 4, cam_w, cam_h), 3, border_radius=14)
                screen.blit(border_surf, (cam_x - 4, cam_y - 4))
                screen.blit(cam_surf, (cam_x, cam_y))
        except Exception:
            pass
        
        # 游戏结束
        if self.game_over:
            self.draw_game_over()
    
    def reset(self):
        """重置游戏状态"""
        global current_beat_index
        
        # 重置玩家
        self.player.x = WIDTH // 2 - 100
        self.player.y = HEIGHT // 2
        self.player.vel_y = 0
        self.player.alive = True
        self.player.on_ground = False
        self.player.camera_x = 0
        self.player.last_mouth_open = False
        
        # 重置游戏状态
        self.score = 0
        self.game_over = False
        current_beat_index = 0
    # 删除清空粒子
        
        # 重新创建平台
        self.platforms = []
        self.platforms = self.create_initial_platforms()
        
        # 重新开始音乐
        if music_playing:
            pygame.mixer.music.stop()
            pygame.mixer.music.play()
            self.music_start_time = pygame.time.get_ticks()

def main():
    print("\n🌸 Flower Hop - Rhythm Jump Game")
    print("=" * 50)
    
    # 加载音乐和节奏
    load_music_and_beats()
    
    print("\n📹 Opening camera...")
    print("👄 Open your mouth to JUMP!")
    print("⌨️  Press R to Restart | Press ESC to Exit\n")
    
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
        
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    # 清理
    cap.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception as e:
        print("\n========== GAME CRASHED ==========")
        print(f"❌ Error: {e}")
        traceback.print_exc()
        print("========== END TRACEBACK ==========")
