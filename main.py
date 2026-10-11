import os
import random
import sys
import pygame

# 1. 基础配置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
FPS = 60

# 经典 Chrome 灰白配色 & 暗黑夜景配色
COLOR_BG_DAY = (247, 247, 247)
COLOR_BG_NIGHT = (32, 33, 36)

GROUND_Y = 320         # 地平面 Y 坐标
BASE_SPEED = 7.0       # 游戏初始基准滚动速度


def create_inverted_sheet(sheet):
    """生成夜间反色精灵图：将深灰图案映射为柔和高亮浅灰色"""
    inv = sheet.copy()
    w, h = inv.get_size()
    for x in range(w):
        for y in range(h):
            c = inv.get_at((x, y))
            if c.a > 0:
                inv.set_at((x, y), (255 - c.r, 255 - c.g, 255 - c.b, c.a))
    return inv


class Dino:
    """经典 Chrome 小恐龙：支持昼夜切换、奔跑动画、下蹲、跳跃与死亡定格"""

    def __init__(self, x, ground_y, sheet_day, sheet_night):
        self.x = x
        self.ground_y = ground_y

        # 日间与夜间贴图双模式缓存
        self.stand_imgs = {
            False: sheet_day.subsurface((848, 2, 44, 47)),
            True: sheet_night.subsurface((848, 2, 44, 47)),
        }
        self.run_imgs = {
            False: [sheet_day.subsurface((936, 2, 44, 47)), sheet_day.subsurface((980, 2, 44, 47))],
            True: [sheet_night.subsurface((936, 2, 44, 47)), sheet_night.subsurface((980, 2, 44, 47))],
        }
        self.duck_imgs = {
            False: [sheet_day.subsurface((1112, 19, 59, 30)), sheet_day.subsurface((1171, 19, 59, 30))],
            True: [sheet_night.subsurface((1112, 19, 59, 30)), sheet_night.subsurface((1171, 19, 59, 30))],
        }
        self.dead_imgs = {
            False: sheet_day.subsurface((1024, 2, 44, 47)),
            True: sheet_night.subsurface((1024, 2, 44, 47)),
        }

        self.stand_y = ground_y - self.stand_imgs[False].get_height()
        self.duck_y = ground_y - self.duck_imgs[False][0].get_height()
        self.y = self.stand_y

        # 物理参数
        self.jump_velocity = -14.0
        self.gravity = 0.8
        self.velocity_y = 0.0

        # 状态机
        self.is_jumping = False
        self.is_ducking = False
        self.is_dead = False
        self.step_index = 0

    def reset(self):
        self.y = self.stand_y
        self.velocity_y = 0.0
        self.is_jumping = False
        self.is_ducking = False
        self.is_dead = False
        self.step_index = 0

    def jump(self):
        if not self.is_jumping and not self.is_ducking and not self.is_dead:
            self.velocity_y = self.jump_velocity
            self.is_jumping = True

    def duck(self, is_down):
        if not self.is_dead:
            self.is_ducking = is_down
            if self.is_jumping and is_down:
                self.velocity_y += 3.0

    def update(self):
        if self.is_dead:
            return

        self.step_index += 1

        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y += self.velocity_y

            if self.y >= self.stand_y:
                self.y = self.stand_y
                self.velocity_y = 0.0
                self.is_jumping = False
        else:
            self.y = self.duck_y if self.is_ducking else self.stand_y

    def get_hitbox(self):
        if self.is_dead:
            img = self.dead_imgs[False]
        elif self.is_jumping:
            img = self.stand_imgs[False]
        elif self.is_ducking:
            img = self.duck_imgs[False][0]
        else:
            img = self.run_imgs[False][0]

        rect = pygame.Rect(int(self.x), int(self.y), img.get_width(), img.get_height())
        return rect.inflate(-10, -8)

    def draw(self, screen, is_night, is_running=True):
        if self.is_dead:
            current_img = self.dead_imgs[is_night]
        elif self.is_jumping or not is_running:
            current_img = self.stand_imgs[is_night]
        else:
            anim_imgs = self.duck_imgs[is_night] if self.is_ducking else self.run_imgs[is_night]
            frame = (self.step_index // 6) % len(anim_imgs)
            current_img = anim_imgs[frame]

        screen.blit(current_img, (int(self.x), int(self.y)))





class Cactus:
    """仙人掌障碍物：多株形态组合与昼夜支持"""

    def __init__(self, ground_y, sheet_day, sheet_night):
        cactus_rects = [
            (228, 2, 17, 35),
            (245, 2, 34, 35),
            (228, 2, 51, 35),
            (332, 2, 25, 50),
            (332, 2, 50, 50),
        ]
        choice = random.choice(cactus_rects)
        self.imgs = {
            False: sheet_day.subsurface(choice),
            True: sheet_night.subsurface(choice),
        }
        self.width = self.imgs[False].get_width()
        self.height = self.imgs[False].get_height()

        self.x = WINDOW_WIDTH + random.randint(20, 80)
        self.y = ground_y - self.height + 2

    def update(self, speed):
        self.x -= speed

    def get_hitbox(self):
        rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        return rect.inflate(-6, -6)

    def draw(self, screen, is_night):
        screen.blit(self.imgs[is_night], (int(self.x), int(self.y)))


class Pterodactyl:
    """翼龙障碍物：煽翅飞行动画与三种空层"""

    def __init__(self, ground_y, sheet_day, sheet_night):
        self.frames = {
            False: [sheet_day.subsurface((134, 2, 46, 40)), sheet_day.subsurface((180, 2, 46, 40))],
            True: [sheet_night.subsurface((134, 2, 46, 40)), sheet_night.subsurface((180, 2, 46, 40))],
        }
        self.width = self.frames[False][0].get_width()
        self.height = self.frames[False][0].get_height()
        self.step_index = 0

        self.x = WINDOW_WIDTH + random.randint(20, 80)
        flight_heights = [
            ground_y - 45,  # 低空：必须下蹲钻过！
            ground_y - 70,  # 中空：起跳跨越
            ground_y - 95,  # 高空：直接穿过
        ]
        self.y = random.choice(flight_heights)

    def update(self, speed):
        self.x -= speed + 1.2
        self.step_index += 1

    def get_hitbox(self):
        rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        return rect.inflate(-8, -8)

    def draw(self, screen, is_night):
        frame = (self.step_index // 8) % 2
        screen.blit(self.frames[is_night][frame], (int(self.x), int(self.y)))


class Ground:
    def __init__(self, ground_y, sheet_day, sheet_night):
        self.ground_y = ground_y
        self.imgs = {
            False: sheet_day.subsurface((2, 58, 1200, 9)),
            True: sheet_night.subsurface((2, 58, 1200, 9)),
        }
        self.width = self.imgs[False].get_width()
        self.positions = [0, self.width]

    def update(self, speed):
        for i in range(2):
            self.positions[i] -= speed

        if self.positions[0] <= -self.width:
            self.positions[0] = self.positions[1] + self.width
        elif self.positions[1] <= -self.width:
            self.positions[1] = self.positions[0] + self.width

    def draw(self, screen, is_night):
        img = self.imgs[is_night]
        for pos in self.positions:
            screen.blit(img, (int(pos), self.ground_y))


class Cloud:
    def __init__(self, sheet_day, sheet_night):
        self.imgs = {
            False: sheet_day.subsurface((86, 2, 46, 13)),
            True: sheet_night.subsurface((86, 2, 46, 13)),
        }
        self.width = self.imgs[False].get_width()
        self.reset()
        self.x = random.randint(50, WINDOW_WIDTH)

    def reset(self):
        self.x = WINDOW_WIDTH + random.randint(50, 250)
        self.y = random.randint(50, 150)
        self.speed = random.uniform(1.2, 2.0)

    def update(self):
        self.x -= self.speed
        if self.x <= -self.width:
            self.reset()

    def draw(self, screen, is_night):
        screen.blit(self.imgs[is_night], (int(self.x), int(self.y)))


class ScoreBoard:
    """计分系统：5位数复古字模、最高分持久化、整百闪烁彩蛋"""

    def __init__(self, sheet_day, sheet_night):
        # 0-9 官方数字与 HI 贴图
        self.digits = {
            False: [sheet_day.subsurface((655 + i * 10, 2, 10, 12)) for i in range(10)],
            True: [sheet_night.subsurface((655 + i * 10, 2, 10, 12)) for i in range(10)],
        }
        self.hi_img = {
            False: sheet_day.subsurface((755, 2, 20, 12)),
            True: sheet_night.subsurface((755, 2, 20, 12)),
        }

        self.score = 0
        self.high_score = 0
        self.score_float = 0.0

        # 整百闪烁特效相关
        self.blink_timer = 0
        self.blink_score = 0

    def reset(self):
        self.score = 0
        self.score_float = 0.0
        self.blink_timer = 0

    def update(self, speed):
        # 分数按奔跑速度平滑增长 (约每 0.1 秒涨 1 分)
        self.score_float += speed * 0.025
        prev_score = self.score
        self.score = int(self.score_float)

        if self.score > self.high_score:
            self.high_score = self.score

        # 触发每 100 分闪烁特效
        if self.score // 100 > prev_score // 100 and self.score > 0:
            self.blink_timer = 60  # 闪烁 1 秒 (60 帧)
            self.blink_score = (self.score // 100) * 100

        if self.blink_timer > 0:
            self.blink_timer -= 1

    def draw(self, screen, is_night):
        digits = self.digits[is_night]
        hi_icon = self.hi_img[is_night]

        # 从右上角对齐绘制
        base_x = WINDOW_WIDTH - 20

        # 1. 绘制当前分数 (如果在闪烁中，每隔 8 帧闪一次)
        show_current = True
        display_score = self.score
        if self.blink_timer > 0:
            show_current = (self.blink_timer // 8) % 2 == 0
            display_score = self.blink_score

        if show_current:
            score_str = f"{display_score:05d}"
            for i, ch in enumerate(reversed(score_str)):
                digit_img = digits[int(ch)]
                screen.blit(digit_img, (base_x - (i + 1) * 10, 20))

        # 2. 绘制最高分 HI
        if self.high_score > 0:
            hi_base_x = base_x - 75
            hi_score_str = f"{self.high_score:05d}"
            for i, ch in enumerate(reversed(hi_score_str)):
                digit_img = digits[int(ch)]
                screen.blit(digit_img, (hi_base_x - (i + 1) * 10, 20))

            screen.blit(hi_icon, (hi_base_x - 50 - hi_icon.get_width() - 4, 20))


def get_resource_path(relative_path):
    """获取资源绝对路径，兼容普通开发环境与 PyInstaller 打包单文件环境"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


def main():
    pygame.init()
    pygame.display.set_caption("Chrome Dino Runner")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # 1. 加载精灵图并预生成夜间反色图 (兼容打包环境)
    sprite_path = get_resource_path("sprite.png")
    sheet_day = pygame.image.load(sprite_path).convert_alpha()
    sheet_night = create_inverted_sheet(sheet_day)

    # 2. UI 贴图（GAME OVER 艺术字与左下角第 3 个起的一整套旋转重玩图标）
    game_over_imgs = {
        False: sheet_day.subsurface((655, 15, 191, 11)),
        True: sheet_night.subsurface((655, 15, 191, 11)),
    }
    restart_frames = {
        False: [
            sheet_day.subsurface((77, 72, 29, 25)),
            sheet_day.subsurface((111, 70, 34, 28)),
            sheet_day.subsurface((147, 70, 34, 28)),
            sheet_day.subsurface((183, 70, 35, 28)),
            sheet_day.subsurface((219, 70, 34, 28)),
            sheet_day.subsurface((255, 70, 34, 28)),
        ],
        True: [
            sheet_night.subsurface((77, 72, 29, 25)),
            sheet_night.subsurface((111, 70, 34, 28)),
            sheet_night.subsurface((147, 70, 34, 28)),
            sheet_night.subsurface((183, 70, 35, 28)),
            sheet_night.subsurface((219, 70, 34, 28)),
            sheet_night.subsurface((255, 70, 34, 28)),
        ],
    }
    restart_anim_tick = 0

    # 居中 UI 坐标与按钮判定区
    go_x = (WINDOW_WIDTH - game_over_imgs[False].get_width()) // 2
    go_y = 135
    res_x = (WINDOW_WIDTH - restart_frames[False][0].get_width()) // 2
    res_y = 175
    restart_rect = pygame.Rect(res_x - 10, res_y - 10, restart_frames[False][0].get_width() + 20, restart_frames[False][0].get_height() + 20)

    # 3. 实体初始化
    dino = Dino(x=60, ground_y=GROUND_Y, sheet_day=sheet_day, sheet_night=sheet_night)
    ground = Ground(ground_y=GROUND_Y, sheet_day=sheet_day, sheet_night=sheet_night)
    clouds = [Cloud(sheet_day, sheet_night) for _ in range(3)]
    scoreboard = ScoreBoard(sheet_day, sheet_night)
    obstacles = []

    game_speed = BASE_SPEED
    game_started = False
    game_over = False

    def restart_game():
        nonlocal game_started, game_over, game_speed, restart_anim_tick
        dino.reset()
        scoreboard.reset()
        obstacles.clear()
        game_speed = BASE_SPEED
        restart_anim_tick = 0
        game_started = True
        game_over = False
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    running = True
    while running:
        # 死亡时，鼠标悬停重玩按钮变小手光标并播放旋转动效
        is_hover_restart = game_over and restart_rect.collidepoint(pygame.mouse.get_pos())
        if is_hover_restart:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            restart_anim_tick += 1
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            restart_anim_tick = 0

        # --- 1. 处理输入事件 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_SPACE, pygame.K_UP):
                    if not game_started:
                        game_started = True
                        dino.jump()
                    elif game_over:
                        restart_game()
                    else:
                        dino.jump()
                elif event.key == pygame.K_DOWN:
                    if game_started and not game_over:
                        dino.duck(True)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    dino.duck(False)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not game_started:
                        game_started = True
                        dino.jump()
                    elif game_over:
                        restart_game()
                    elif not dino.is_jumping:
                        dino.jump()

        # --- 2. 状态更新 ---
        # 昼夜判定：每 1000 分中，700~900 分为宁静黑夜，其余为阳光白昼
        is_night = 700 <= (scoreboard.score % 1000) < 900

        if game_started and not game_over:
            # 动态难度递增：每过 100 分速度提升 +0.3，最高飙至 14.0
            game_speed = min(14.0, BASE_SPEED + (scoreboard.score // 100) * 0.3)

            dino.update()
            scoreboard.update(game_speed)
            ground.update(game_speed)
            for cloud in clouds:
                cloud.update()

            # 障碍物刷新生成：间距随速度动态调整
            min_gap = int(280 + game_speed * 15)
            max_gap = int(480 + game_speed * 20)
            if len(obstacles) == 0:
                spawn = True
            else:
                last_obs = obstacles[-1]
                spawn = last_obs.x < WINDOW_WIDTH - random.randint(min_gap, max_gap)

            if spawn:
                # 得分超过 300 以后才开始引入翼龙
                if scoreboard.score > 300 and random.random() < 0.35:
                    obstacles.append(Pterodactyl(GROUND_Y, sheet_day, sheet_night))
                else:
                    obstacles.append(Cactus(GROUND_Y, sheet_day, sheet_night))

            # 碰撞检测
            dino_box = dino.get_hitbox()
            for obs in obstacles[:]:
                obs.update(game_speed)
                if dino_box.colliderect(obs.get_hitbox()):
                    game_over = True
                    dino.is_dead = True

                if obs.x < -100:
                    obstacles.remove(obs)
        else:
            # 未开始或游戏结束：云朵依然可以悠闲飘过
            for cloud in clouds:
                cloud.update()

        # --- 3. 画面渲染 ---
        bg_color = COLOR_BG_NIGHT if is_night else COLOR_BG_DAY
        screen.fill(bg_color)

        for cloud in clouds:
            cloud.draw(screen, is_night)
        ground.draw(screen, is_night)

        for obs in obstacles:
            obs.draw(screen, is_night)

        dino.draw(screen, is_night, is_running=game_started)
        scoreboard.draw(screen, is_night)

        # 游戏结束 UI 渲染
        if game_over:
            screen.blit(game_over_imgs[is_night], (go_x, go_y))
            if is_hover_restart:
                frame_idx = 1 + (restart_anim_tick // 4) % (len(restart_frames[is_night]) - 1)
                active_btn = restart_frames[is_night][frame_idx]
            else:
                active_btn = restart_frames[is_night][0]
            btn_x = (WINDOW_WIDTH - active_btn.get_width()) // 2
            btn_y = res_y
            screen.blit(active_btn, (btn_x, btn_y))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
