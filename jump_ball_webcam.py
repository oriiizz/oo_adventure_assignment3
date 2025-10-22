import pygame
import sys
import random
import cv2
import mediapipe as mp
import numpy as np
from threading import Thread
import time

# 初始化
pygame.init()
pygame.mixer.init()  # 初始化音频系统
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mouth Control Platformer - 张嘴跳跃!")
clock = pygame.time.Clock()

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (150, 150, 150)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 250)  # 天空蓝
CLOUD_WHITE = (255, 255, 255)  # 云朵白
PLATFORM_BROWN = (139, 90, 43)  # 平台棕色
PLATFORM_GREEN = (34, 139, 34)  # 平台草绿色

class SoundGenerator:
    """音效生成器 - 用代码生成简单音效"""
    def __init__(self):
        self.sample_rate = 22050
        self.jump_sound = None
        self.game_over_sound = None
        self.background_music_playing = False
        self.music_volume = 0.3
        self.sfx_volume = 0.5
        
    def generate_jump_sound(self):
        """生成跳跃音效（上升音调）"""
        duration = 0.1
        frequency_start = 400
        frequency_end = 600
        
        samples = int(self.sample_rate * duration)
        wave = np.zeros(samples)
        
        for i in range(samples):
            t = i / self.sample_rate
            # 频率从低到高
            freq = frequency_start + (frequency_end - frequency_start) * (i / samples)
            wave[i] = np.sin(2 * np.pi * freq * t)
        
        # 添加淡出效果
        fade = np.linspace(1, 0, samples)
        wave = wave * fade
        
        # 转换为pygame可用的格式
        wave = np.int16(wave * 32767 * self.sfx_volume)
        stereo_wave = np.column_stack((wave, wave))
        
        self.jump_sound = pygame.sndarray.make_sound(stereo_wave)
        
    def generate_game_over_sound(self):
        """生成游戏结束音效（下降音调）"""
        duration = 0.5
        frequency_start = 400
        frequency_end = 200
        
        samples = int(self.sample_rate * duration)
        wave = np.zeros(samples)
        
        for i in range(samples):
            t = i / self.sample_rate
            # 频率从高到低
            freq = frequency_start + (frequency_end - frequency_start) * (i / samples)
            wave[i] = np.sin(2 * np.pi * freq * t)
        
        # 添加淡出效果
        fade = np.linspace(1, 0, samples)
        wave = wave * fade
        
        wave = np.int16(wave * 32767 * self.sfx_volume)
        stereo_wave = np.column_stack((wave, wave))
        
        self.game_over_sound = pygame.sndarray.make_sound(stereo_wave)
    
    def generate_background_music(self):
        """生成简单的背景音乐（循环旋律）"""
        duration = 2.0  # 2秒循环
        
        # 简单的旋律音符（频率）- 欢快的音阶
        melody = [
            (523, 0.25),  # C5
            (587, 0.25),  # D5
            (659, 0.25),  # E5
            (784, 0.25),  # G5
            (659, 0.25),  # E5
            (587, 0.25),  # D5
            (523, 0.5),   # C5
        ]
        
        samples = int(self.sample_rate * duration)
        wave = np.zeros(samples)
        
        current_sample = 0
        for freq, note_duration in melody:
            note_samples = int(self.sample_rate * note_duration)
            for i in range(note_samples):
                if current_sample < samples:
                    t = i / self.sample_rate
                    wave[current_sample] = np.sin(2 * np.pi * freq * t)
                    current_sample += 1
        
        wave = np.int16(wave * 32767 * self.music_volume)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def init_sounds(self):
        """初始化所有音效"""
        try:
            self.generate_jump_sound()
            self.generate_game_over_sound()
            print("✅ 音效生成成功！")
        except Exception as e:
            print(f"⚠️ 音效生成失败: {e}")
    
    def play_jump(self):
        """播放跳跃音效"""
        if self.jump_sound:
            self.jump_sound.play()
    
    def play_game_over(self):
        """播放游戏结束音效"""
        if self.game_over_sound:
            self.game_over_sound.play()
    
    def start_background_music(self):
        """开始播放背景音乐"""
        if not self.background_music_playing:
            try:
                music = self.generate_background_music()
                # 使用音乐通道循环播放
                pygame.mixer.Channel(0).play(music, loops=-1)
                self.background_music_playing = True
                print("🎵 背景音乐开始播放！")
            except Exception as e:
                print(f"⚠️ 背景音乐播放失败: {e}")
    
    def stop_background_music(self):
        """停止背景音乐"""
        pygame.mixer.Channel(0).stop()
        self.background_music_playing = False

class MouthDetector:
    """嘴巴检测器类"""
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.cap = None
        self.mouth_open = False
        self.mouth_ratio = 0.0
        self.running = True
        self.frame = None
        self.processed_frame = None
        self.face_image = None  # 存储裁剪的脸部图像
        self.face_rect = None  # 脸部矩形区域
        
        # 嘴巴关键点索引 (MediaPipe Face Mesh)
        self.UPPER_LIP = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
        self.LOWER_LIP = [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]
        self.MOUTH_LEFT = 61
        self.MOUTH_RIGHT = 291
        
        self.init_camera()
        
    def init_camera(self):
        """初始化摄像头"""
        try:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            print("✅ 摄像头初始化成功！")
        except Exception as e:
            print(f"❌ 摄像头初始化失败: {e}")
            
    def calculate_mouth_opening(self, landmarks, image_shape):
        """计算嘴巴张开程度"""
        h, w = image_shape[:2]
        
        # 获取上下嘴唇的关键点
        upper_lip_points = []
        lower_lip_points = []
        
        for idx in self.UPPER_LIP:
            point = landmarks[idx]
            upper_lip_points.append([point.x * w, point.y * h])
            
        for idx in self.LOWER_LIP:
            point = landmarks[idx]
            lower_lip_points.append([point.x * w, point.y * h])
        
        # 计算上下嘴唇中心点
        upper_center = np.mean(upper_lip_points, axis=0)
        lower_center = np.mean(lower_lip_points, axis=0)
        
        # 计算垂直距离
        vertical_distance = np.linalg.norm(upper_center - lower_center)
        
        # 获取嘴角距离（用于归一化）
        mouth_left = landmarks[self.MOUTH_LEFT]
        mouth_right = landmarks[self.MOUTH_RIGHT]
        horizontal_distance = np.linalg.norm([
            (mouth_left.x - mouth_right.x) * w,
            (mouth_left.y - mouth_right.y) * h
        ])
        
        # 计算比率 (垂直距离 / 水平距离)
        if horizontal_distance > 0:
            ratio = vertical_distance / horizontal_distance
        else:
            ratio = 0
            
        return ratio, upper_center, lower_center
    
    def process_frame(self):
        """处理摄像头帧"""
        if self.cap is None or not self.cap.isOpened():
            return
            
        ret, frame = self.cap.read()
        if not ret:
            return
            
        # 翻转图像（镜像效果）
        frame = cv2.flip(frame, 1)
        self.frame = frame.copy()
        
        # 转换为RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 检测人脸
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # 计算嘴巴张开程度
            ratio, upper_center, lower_center = self.calculate_mouth_opening(
                face_landmarks.landmark, frame.shape
            )
            
            self.mouth_ratio = ratio
            
            # 判断嘴巴是否张开 (阈值可调整)
            self.mouth_open = ratio > 0.35  # 降低阈值，更容易触发（原0.4）
            
            # 提取脸部区域
            self.extract_face(face_landmarks.landmark, frame)
            
            # 在图像上绘制嘴巴状态
            color = GREEN if self.mouth_open else RED
            cv2.circle(frame, tuple(upper_center.astype(int)), 5, color, -1)
            cv2.circle(frame, tuple(lower_center.astype(int)), 5, color, -1)
            cv2.line(frame, tuple(upper_center.astype(int)), 
                    tuple(lower_center.astype(int)), color, 2)
            
            # 显示比率
            cv2.putText(frame, f"Mouth: {ratio:.2f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, "JUMP!" if self.mouth_open else "Close", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        else:
            cv2.putText(frame, "No face detected", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)
            self.mouth_open = False
            self.face_image = None
            
        self.processed_frame = frame
    
    def extract_face(self, landmarks, frame):
        """提取并裁剪脸部图像"""
        h, w = frame.shape[:2]
        
        # 获取所有脸部关键点
        x_coords = [landmark.x * w for landmark in landmarks]
        y_coords = [landmark.y * h for landmark in landmarks]
        
        # 计算脸部边界框，并扩大一些边距
        margin = 0.3  # 30% 边距
        x_min = int(min(x_coords))
        x_max = int(max(x_coords))
        y_min = int(min(y_coords))
        y_max = int(max(y_coords))
        
        width = x_max - x_min
        height = y_max - y_min
        
        # 添加边距
        x_min = max(0, int(x_min - width * margin))
        x_max = min(w, int(x_max + width * margin))
        y_min = max(0, int(y_min - height * margin))
        y_max = min(h, int(y_max + height * margin))
        
        # 裁剪脸部
        try:
            face = frame[y_min:y_max, x_min:x_max]
            if face.size > 0:
                # 转换为RGBA（添加透明通道）
                face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                self.face_image = face_rgb
                self.face_rect = (x_min, y_min, x_max, y_max)
        except:
            self.face_image = None
    
    def update(self):
        """更新检测（在独立线程中运行）"""
        while self.running:
            self.process_frame()
            time.sleep(0.03)  # 约30fps
    
    def start(self):
        """启动检测线程"""
        thread = Thread(target=self.update, daemon=True)
        thread.start()
        
    def get_webcam_surface(self):
        """获取摄像头画面的pygame surface"""
        if self.processed_frame is None:
            return None
            
        frame = cv2.cvtColor(self.processed_frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        return frame
    
    def cleanup(self):
        """清理资源"""
        self.running = False
        if self.cap is not None:
            self.cap.release()

class Player:
    def __init__(self, sound_generator=None):
        self.radius = 30  # 增大显示区域以容纳脸部
        self.sound_generator = sound_generator
        self.reset()
        
    def reset(self):
        self.x = 100
        self.y = HEIGHT - 100
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.speed = 4  # 降低移动速度（原5）
        self.jump_power = -11  # 稍微降低跳跃力度（原-12）
        self.alive = True
        self.auto_move = True  # 自动前进
        self.last_jump_time = 0  # 记录上次跳跃时间
        
    def update(self, platforms, mouth_detector):
        if not self.alive:
            return
            
        # 自动前进
        if self.auto_move:
            self.vel_x = self.speed
        
        # 检测嘴巴张开来跳跃
        if mouth_detector.mouth_open and self.on_ground:
            current_time = pygame.time.get_ticks()
            # 防止跳跃音效过于频繁（至少间隔200ms）
            if current_time - self.last_jump_time > 200:
                self.vel_y = self.jump_power
                self.on_ground = False
                self.last_jump_time = current_time
                # 播放跳跃音效
                if self.sound_generator:
                    self.sound_generator.play_jump()
        
        # 重力
        self.vel_y += 0.45  # 稍微降低重力（原0.5），更容易控制
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 平台碰撞检测
        self.on_ground = False
        for platform in platforms:
            if (self.y + self.radius > platform.y and 
                self.y + self.radius < platform.y + 10 and
                self.x + self.radius > platform.x and 
                self.x - self.radius < platform.x + platform.width and
                self.vel_y > 0):
                self.y = platform.y - self.radius
                self.vel_y = 0
                self.on_ground = True
        
        # 检查是否掉出屏幕底部
        if self.y > HEIGHT + self.radius:
            if self.alive:  # 只在第一次死亡时播放音效
                if self.sound_generator:
                    self.sound_generator.play_game_over()
            self.alive = False
    
    def draw(self, screen, camera_x, mouth_detector):
        if not self.alive:
            return
            
        screen_x = self.x - camera_x
        
        # 绘制脸部或默认嘴巴形状的小球
        self.draw_face(screen, screen_x, self.y, mouth_detector)
    
    def draw_face(self, screen, x, y, mouth_detector):
        """绘制脸部（如果有）或默认小球"""
        
        # 如果有脸部图像，显示脸部
        if mouth_detector.face_image is not None:
            try:
                face_img = mouth_detector.face_image
                
                # 计算脸部大小（保持圆形）
                face_size = int(self.radius * 2)
                
                # 调整脸部图像大小
                face_resized = cv2.resize(face_img, (face_size, face_size))
                
                # 转换为pygame surface
                face_surface = pygame.surfarray.make_surface(np.rot90(face_resized))
                
                # 创建圆形遮罩（让脸部显示为圆形）
                mask_surface = pygame.Surface((face_size, face_size), pygame.SRCALPHA)
                pygame.draw.circle(mask_surface, (255, 255, 255, 255), 
                                 (face_size // 2, face_size // 2), self.radius)
                
                # 应用遮罩
                face_surface.set_colorkey((0, 0, 0))
                temp_surface = pygame.Surface((face_size, face_size), pygame.SRCALPHA)
                temp_surface.fill((0, 0, 0, 0))
                temp_surface.blit(face_surface, (0, 0))
                temp_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                
                # 绘制到屏幕
                face_rect = temp_surface.get_rect(center=(int(x), int(y)))
                screen.blit(temp_surface, face_rect)
                
                # 添加白色圆形边框
                pygame.draw.circle(screen, WHITE, (int(x), int(y)), self.radius, 3)
                
            except Exception as e:
                # 如果出错，绘制默认小球
                self.draw_default_ball(screen, x, y)
        else:
            # 没有检测到脸部，绘制默认小球
            self.draw_default_ball(screen, x, y)
    
    def draw_default_ball(self, screen, x, y):
        """绘制默认的嘴巴小球"""
        # 外圆
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), self.radius)
        
        # 绘制嘴巴
        mouth_y = y + 5
        if self.on_ground:
            # 闭嘴
            pygame.draw.arc(screen, BLACK, 
                          (x - self.radius//2, mouth_y - 5, self.radius, 10),
                          0, 3.14, 3)
        else:
            # 张嘴（跳跃中）
            pygame.draw.ellipse(screen, BLACK,
                              (x - self.radius//2, mouth_y - 5, self.radius, 10))
        
        # 绘制眼睛
        pygame.draw.circle(screen, BLACK, (int(x - 10), int(y - 8)), 4)
        pygame.draw.circle(screen, BLACK, (int(x + 10), int(y - 8)), 4)

class Platform:
    def __init__(self, x, y, width, is_safe=False):
        self.x = x
        self.y = y
        self.width = width
        self.is_safe = is_safe
        
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        
        # 马里奥风格的平台
        # 绘制草地顶部（绿色）
        grass_height = 8
        pygame.draw.rect(screen, PLATFORM_GREEN, (screen_x, self.y, self.width, grass_height))
        
        # 绘制土壤部分（棕色）
        soil_height = 15
        pygame.draw.rect(screen, PLATFORM_BROWN, (screen_x, self.y + grass_height, self.width, soil_height))
        
        # 添加草地纹理效果（小草）
        grass_spacing = 15
        for i in range(int(screen_x), int(screen_x + self.width), grass_spacing):
            # 绘制小草
            pygame.draw.line(screen, (0, 200, 0), (i, self.y), (i - 2, self.y - 3), 2)
            pygame.draw.line(screen, (0, 200, 0), (i, self.y), (i + 2, self.y - 3), 2)
        
        # 如果是安全平台，添加黄色边框（像马里奥的砖块）
        if self.is_safe:
            pygame.draw.rect(screen, (255, 215, 0), (screen_x, self.y, self.width, grass_height + soil_height), 2)

class Game:
    def __init__(self):
        self.sound_generator = SoundGenerator()
        self.sound_generator.init_sounds()
        self.player = Player(self.sound_generator)
        self.mouth_detector = MouthDetector()
        self.mouth_detector.start()
        self.platforms = []
        self.camera_x = 0
        self.score = 0
        self.last_platform_x = 0
        self.difficulty = 0
        self.show_webcam = True
        self.clouds = []  # 云朵列表
        self.music_enabled = True
        self.generate_clouds()
        self.generate_initial_platforms()
        # 启动背景音乐
        if self.music_enabled:
            self.sound_generator.start_background_music()
    
    def generate_clouds(self):
        """生成云朵"""
        for i in range(10):
            cloud = {
                'x': random.randint(0, WIDTH * 3),
                'y': random.randint(30, 150),
                'size': random.randint(40, 80),
                'speed': random.uniform(0.2, 0.5)
            }
            self.clouds.append(cloud)
        
    def generate_initial_platforms(self):
        self.platforms = [
            Platform(0, HEIGHT - 50, WIDTH * 3, True),  # 更长的地面平台
        ]
        
        self.last_platform_x = WIDTH
        for i in range(25):  # 更多初始平台（原20）
            self.add_easy_platform()
    
    def add_easy_platform(self):
        gap = random.randint(40, 120)  # 更小的间隙（原80-180）
        width = random.randint(200, 350)  # 更宽的平台（原150-300）
        height = random.randint(20, 60)  # 更小的高度变化（原30-100）
        
        x = self.last_platform_x + gap
        y = HEIGHT - 50 - height
        
        if y < HEIGHT - 180:  # 降低最大高度（原250）
            y = HEIGHT - 180
            
        is_safe = len(self.platforms) < 15  # 更多安全平台（原10）
        
        self.platforms.append(Platform(x, y, width, is_safe))
        self.last_platform_x = x + width
    
    def update(self):
        self.player.update(self.platforms, self.mouth_detector)
        
        if not self.player.alive:
            return
            
        # 更新相机
        target_x = self.player.x - WIDTH // 3
        self.camera_x = target_x
        
        # 更新云朵位置（视差滚动效果）
        for cloud in self.clouds:
            cloud['x'] += cloud['speed']
            # 如果云朵移出屏幕右侧，重新生成在左侧
            if cloud['x'] > self.camera_x + WIDTH + 100:
                cloud['x'] = self.camera_x - 100
                cloud['y'] = random.randint(30, 150)
                cloud['size'] = random.randint(40, 80)
        
        # 更新分数
        if self.player.x > self.score:
            self.score = self.player.x
            
        self.difficulty = min(self.score / 1000, 2)
        
        # 生成新平台
        while self.last_platform_x < self.player.x + WIDTH * 2:
            self.add_easy_platform()
            
        # 移除视野外的平台
        self.platforms = [p for p in self.platforms if p.x + p.width > self.camera_x - 100]
    
    def draw_cloud(self, screen, x, y, size):
        """绘制卡通云朵"""
        # 主圆
        pygame.draw.circle(screen, CLOUD_WHITE, (int(x), int(y)), int(size * 0.6))
        # 左侧圆
        pygame.draw.circle(screen, CLOUD_WHITE, (int(x - size * 0.5), int(y + size * 0.2)), int(size * 0.4))
        # 右侧圆
        pygame.draw.circle(screen, CLOUD_WHITE, (int(x + size * 0.5), int(y + size * 0.2)), int(size * 0.4))
        # 顶部圆
        pygame.draw.circle(screen, CLOUD_WHITE, (int(x - size * 0.2), int(y - size * 0.3)), int(size * 0.45))
        pygame.draw.circle(screen, CLOUD_WHITE, (int(x + size * 0.2), int(y - size * 0.3)), int(size * 0.45))
    
    def draw(self, screen):
        # 绘制天空背景
        screen.fill(SKY_BLUE)
        
        # 绘制云朵（带视差效果）
        for cloud in self.clouds:
            cloud_x = cloud['x'] - self.camera_x * 0.3  # 视差滚动（云朵移动更慢）
            if -100 < cloud_x < WIDTH + 100:  # 只绘制可见的云朵
                self.draw_cloud(screen, cloud_x, cloud['y'], cloud['size'])
        
        # 绘制平台
        for platform in self.platforms:
            platform.draw(screen, self.camera_x)
        
        # 绘制玩家
        self.player.draw(screen, self.camera_x, self.mouth_detector)
        
        # 绘制UI
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        score_text = font.render(f"Distance: {int(self.score)}", True, (255, 255, 0))
        screen.blit(score_text, (20, 20))
        
        # 显示嘴巴状态
        mouth_status = "MOUTH: OPEN!" if self.mouth_detector.mouth_open else "MOUTH: Closed"
        mouth_color = (255, 215, 0) if self.mouth_detector.mouth_open else (255, 100, 100)
        mouth_text = small_font.render(mouth_status, True, mouth_color)
        screen.blit(mouth_text, (20, 60))
        
        ratio_text = small_font.render(f"Ratio: {self.mouth_detector.mouth_ratio:.2f}", True, (255, 255, 0))
        screen.blit(ratio_text, (20, 90))
        
        # 提示信息
        tip_text = small_font.render("张大嘴巴来跳跃! (按 W 切换摄像头 | M 切换音乐)", True, (50, 50, 50))
        screen.blit(tip_text, (WIDTH//2 - 250, HEIGHT - 30))
        
        # 显示摄像头画面
        if self.show_webcam:
            webcam_surface = self.mouth_detector.get_webcam_surface()
            if webcam_surface is not None:
                # 缩小摄像头画面
                webcam_surface = pygame.transform.scale(webcam_surface, (160, 120))
                screen.blit(webcam_surface, (WIDTH - 170, 10))
        
        # 游戏结束画面
        if not self.player.alive:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            game_over_text = font.render("Game Over!", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - 80, HEIGHT//2 - 50))
            
            score_text = font.render(f"Final Distance: {int(self.score)}", True, WHITE)
            screen.blit(score_text, (WIDTH//2 - 120, HEIGHT//2))
            
            restart_text = font.render("Press R to play again", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - 120, HEIGHT//2 + 50))
    
    def reset(self):
        old_detector = self.mouth_detector
        old_sound = self.sound_generator
        self.__init__()
        self.mouth_detector = old_detector
        self.sound_generator = old_sound
        self.player.sound_generator = old_sound
    
    def cleanup(self):
        self.mouth_detector.cleanup()
        if self.sound_generator:
            self.sound_generator.stop_background_music()

    def run(self):
        running = True
        
        print("\n🎮 游戏开始!")
        print("📹 请确保摄像头能看到你的脸")
        print("👄 张大嘴巴来跳跃!")
        print("⌨️  按 W 切换摄像头显示")
        print("⌨️  按 M 切换背景音乐")
        print("⌨️  按 R 重新开始")
        print("⌨️  按 ESC 退出\n")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_w:
                        self.show_webcam = not self.show_webcam
                    elif event.key == pygame.K_m:
                        # 切换音乐
                        self.music_enabled = not self.music_enabled
                        if self.music_enabled:
                            self.sound_generator.start_background_music()
                        else:
                            self.sound_generator.stop_background_music()
            
            self.update()
            self.draw(screen)
            
            pygame.display.flip()
            clock.tick(60)
        
        self.cleanup()
        pygame.quit()
        sys.exit()

# 运行游戏
if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
