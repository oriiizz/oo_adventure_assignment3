import pygame
import sys
import random

# 初始化
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Infinite Ball Platformer - Easy Mode")
clock = pygame.time.Clock()

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (150, 150, 150)
RED = (255, 0, 0)

class Player:
    def __init__(self):
        self.radius = 15
        self.reset()
        
    def reset(self):
        self.x = 100
        self.y = HEIGHT - 100
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.speed = 5
        self.jump_power = -10  # 降低跳跃力度，更容易控制
        self.double_jump_available = True
        self.jump_count = 0
        self.dash_power = 12  # 降低冲刺力量
        self.dash_available = True
        self.dash_direction = 0
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.alive = True
        self.invincible = 0  # 无敌时间（防止连续掉落）
        
    def update(self, platforms, keys):
        if not self.alive:
            return
            
        # 无敌时间倒计时
        if self.invincible > 0:
            self.invincible -= 1
            
        # 处理冲刺
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
            
        if self.dash_timer > 0:
            self.dash_timer -= 1
            self.vel_x = self.dash_direction * self.dash_power
            # 冲刺期间忽略左右输入
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                pass
        else:
            # 正常移动
            self.vel_x = 0
            if keys[pygame.K_LEFT]:
                self.vel_x = -self.speed
            if keys[pygame.K_RIGHT]:
                self.vel_x = self.speed
        
        # 处理跳跃 - 添加按键缓冲，更容易触发
        if keys[pygame.K_UP]:
            # 一段跳：在地面上
            if self.on_ground and self.jump_count == 0:
                self.vel_y = self.jump_power
                self.on_ground = False
                self.jump_count = 1
                self.double_jump_available = True
            # 二段跳：在空中且二段跳可用
            elif not self.on_ground and self.double_jump_available and self.jump_count == 1:
                self.vel_y = self.jump_power * 0.9  # 二段跳稍弱
                self.double_jump_available = False
                self.jump_count = 2
        
        # 处理冲刺（Shift键）
        if keys[pygame.K_LSHIFT] and self.dash_available and self.dash_cooldown == 0:
            self.dash_available = False
            self.dash_cooldown = 80  # 增加冷却时间，降低冲刺频率
            self.dash_timer = 8  # 缩短冲刺持续时间
            # 根据移动方向决定冲刺方向
            if keys[pygame.K_LEFT]:
                self.dash_direction = -1
            elif keys[pygame.K_RIGHT]:
                self.dash_direction = 1
            else:
                # 如果没有水平移动，冲刺方向与角色朝向一致
                self.dash_direction = 1 if self.vel_x >= 0 else -1
        
        # 释放冲刺键后重置冲刺可用性
        if not keys[pygame.K_LSHIFT]:
            self.dash_available = True
        
        # 重力 - 降低重力，让玩家有更多时间控制
        self.vel_y += 0.4
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
                # 落地后重置跳跃状态
                self.jump_count = 0
                self.double_jump_available = True
        
        # 检查是否掉出屏幕底部
        if self.y > HEIGHT + self.radius and self.invincible == 0:
            self.alive = False
            
        # 防止走出左边界
        if self.x < self.radius:
            self.x = self.radius
    
    def draw(self, screen, camera_x):
        if not self.alive:
            return
            
        # 计算屏幕上的位置
        screen_x = self.x - camera_x
        
        # 绘制小球 - 无敌时间闪烁效果
        if self.invincible > 0 and self.invincible % 10 < 5:
            color = LIGHT_GRAY  # 闪烁效果
        else:
            color = WHITE
            
        pygame.draw.circle(screen, color, (int(screen_x), int(self.y)), self.radius)
        
        # 绘制跳跃状态指示器
        if not self.on_ground:
            if self.double_jump_available and self.jump_count == 1:
                # 一段跳后，二段跳可用 - 显示一个圆环
                pygame.draw.circle(screen, LIGHT_GRAY, (int(screen_x), int(self.y)), self.radius + 5, 1)
            elif not self.double_jump_available:
                # 二段跳已使用 - 显示一个X
                pygame.draw.line(screen, LIGHT_GRAY, 
                                (screen_x - 5, self.y - 5), 
                                (screen_x + 5, self.y + 5), 1)
                pygame.draw.line(screen, LIGHT_GRAY, 
                                (screen_x + 5, self.y - 5), 
                                (screen_x - 5, self.y + 5), 1)
        
        # 绘制冲刺状态
        if self.dash_cooldown > 0:
            # 冷却中 - 显示一个部分填充的圆弧
            angle = 360 * (1 - self.dash_cooldown / 80)
            pygame.draw.arc(screen, LIGHT_GRAY, 
                           (screen_x - self.radius - 8, self.y - self.radius - 8, 
                            (self.radius + 8) * 2, (self.radius + 8) * 2),
                           0, angle * 3.14159 / 180, 2)
        
        # 绘制方向指示器
        if self.vel_x > 0:
            # 向右移动时显示向右箭头
            pygame.draw.polygon(screen, WHITE, [
                (screen_x + self.radius + 5, self.y),
                (screen_x + self.radius + 15, self.y),
                (screen_x + self.radius + 10, self.y - 8)
            ])
        elif self.vel_x < 0:
            # 向左移动时显示向左箭头
            pygame.draw.polygon(screen, WHITE, [
                (screen_x - self.radius - 5, self.y),
                (screen_x - self.radius - 15, self.y),
                (screen_x - self.radius - 10, self.y - 8)
            ])

class Platform:
    def __init__(self, x, y, width, is_safe=False):
        self.x = x
        self.y = y
        self.width = width
        self.is_safe = is_safe  # 安全平台，更宽更容易跳跃
        
    def draw(self, screen, camera_x):
        # 计算屏幕上的位置
        screen_x = self.x - camera_x
        color = LIGHT_GRAY if self.is_safe else WHITE
        pygame.draw.rect(screen, color, (screen_x, self.y, self.width, 10))

class Game:
    def __init__(self):
        self.player = Player()
        self.platforms = []
        self.camera_x = 0
        self.score = 0
        self.last_platform_x = 0
        self.difficulty = 0  # 难度级别，随着距离增加
        self.generate_initial_platforms()
        
    def generate_initial_platforms(self):
        # 创建初始平台 - 更简单更密集
        self.platforms = [
            Platform(0, HEIGHT - 50, WIDTH, True),  # 地面，标记为安全平台
        ]
        
        # 添加初始简单平台
        self.last_platform_x = WIDTH
        for i in range(15):  # 生成更多初始平台
            self.add_easy_platform()
    
    def add_easy_platform(self):
        # 生成简单平台 - 更密集，更宽，高度变化更小
        gap = random.randint(30, 120)  # 更小的间隙
        width = random.randint(150, 300)  # 更宽的平台
        height = random.randint(30, 80)  # 更小的高度变化
        
        x = self.last_platform_x + gap
        y = HEIGHT - 50 - height
        
        # 确保平台不会太高
        if y < HEIGHT - 250:
            y = HEIGHT - 250
            
        # 前几个平台标记为安全平台
        is_safe = len(self.platforms) < 10
        
        self.platforms.append(Platform(x, y, width, is_safe))
        self.last_platform_x = x + width
    
    def add_normal_platform(self):
        # 中等难度平台
        gap = random.randint(50, 150)
        width = random.randint(100, 200)
        height = random.randint(50, 120)
        
        x = self.last_platform_x + gap
        y = HEIGHT - 50 - height
        
        if y < HEIGHT - 300:
            y = HEIGHT - 300
            
        self.platforms.append(Platform(x, y, width))
        self.last_platform_x = x + width
    
    def add_hard_platform(self):
        # 困难平台
        gap = random.randint(80, 200)
        width = random.randint(80, 150)
        height = random.randint(80, 150)
        
        x = self.last_platform_x + gap
        y = HEIGHT - 50 - height
        
        if y < HEIGHT - 350:
            y = HEIGHT - 350
            
        self.platforms.append(Platform(x, y, width))
        self.last_platform_x = x + width
    
    def update(self, keys):
        # 更新玩家
        self.player.update(self.platforms, keys)
        
        # 如果玩家死亡，不更新其他内容
        if not self.player.alive:
            return
            
        # 更新相机位置 - 跟随玩家，但保持玩家在屏幕中央
        target_x = self.player.x - WIDTH // 2
        self.camera_x = target_x
        
        # 更新分数和难度
        if self.player.x > self.score:
            self.score = self.player.x
            
        # 根据距离调整难度
        self.difficulty = min(self.score / 1000, 2)  # 难度上限为2
        
        # 生成新平台
        while self.last_platform_x < self.player.x + WIDTH * 1.5:
            # 根据难度选择平台类型
            rand = random.random()
            if self.difficulty < 0.5:  # 前500距离都是简单平台
                self.add_easy_platform()
            elif self.difficulty < 1.0:  # 500-1000距离，80%简单，20%中等
                if rand < 0.8:
                    self.add_easy_platform()
                else:
                    self.add_normal_platform()
            elif self.difficulty < 1.5:  # 1000-1500距离，50%简单，30%中等，20%困难
                if rand < 0.5:
                    self.add_easy_platform()
                elif rand < 0.8:
                    self.add_normal_platform()
                else:
                    self.add_hard_platform()
            else:  # 1500+距离，30%简单，40%中等，30%困难
                if rand < 0.3:
                    self.add_easy_platform()
                elif rand < 0.7:
                    self.add_normal_platform()
                else:
                    self.add_hard_platform()
            
        # 移除视野外的平台以节省内存
        self.platforms = [p for p in self.platforms if p.x + p.width > self.camera_x - 100]
    
    def draw(self, screen):
        # 绘制背景
        screen.fill(BLACK)
        
        # 绘制平台
        for platform in self.platforms:
            platform.draw(screen, self.camera_x)
        
        # 绘制玩家
        self.player.draw(screen, self.camera_x)
        
        # 绘制UI
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        score_text = font.render(f"Distance: {int(self.score)}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        # 难度指示
        difficulty_text = small_font.render(f"Difficulty: {self.difficulty:.1f}", True, WHITE)
        screen.blit(difficulty_text, (20, 90))
        
        # 跳跃状态指示
        if self.player.alive:
            jump_status = "Jump: Ready"
            if not self.player.on_ground:
                if self.player.double_jump_available and self.jump_count == 1:
                    jump_status = "Jump: Double Available"
                elif not self.double_jump_available:
                    jump_status = "Jump: Used"
            
            jump_text = small_font.render(jump_status, True, WHITE)
            screen.blit(jump_text, (20, 50))
            
            # 冲刺状态指示
            dash_status = "Dash: Ready" if self.player.dash_cooldown == 0 else f"Dash: Cooldown {self.player.dash_cooldown//10}"
            dash_text = small_font.render(dash_status, True, WHITE)
            screen.blit(dash_text, (20, 70))
        
        controls_text = font.render("Controls: Arrows + Shift(Dash)", True, GRAY)
        screen.blit(controls_text, (WIDTH//2 - 180, 20))
        
        # 新手提示
        if self.score < 500:
            tip_text = small_font.render("Tip: Use UP arrow to jump, SHIFT to dash", True, LIGHT_GRAY)
            screen.blit(tip_text, (WIDTH//2 - 180, HEIGHT - 30))
        
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
        self.__init__()

    def run(self):
        running = True
        
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if (not self.player.alive or event.key == pygame.K_r) and event.key == pygame.K_r:
                        # 重新开始游戏
                        self.reset()
            
            # 获取按键状态
            keys = pygame.key.get_pressed()
            
            # 更新游戏状态
            self.update(keys)
            
            # 绘制
            self.draw(screen)
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

# 运行游戏
if __name__ == "__main__":
    game = Game()
    game.run()