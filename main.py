import json
import pygame as pg
import pytmx
pg.init()

screen_width = 900
screen_height = 600
fps = 80
tile_scale = 1.5

font = pg.font.Font(None, 36)

class Portal(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.load_animations()
        self.image = self.images[0]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y

        self.current_image = 0
        self.interval = 100
        self.timer = pg.time.get_ticks()

    def load_animations(self):
        tile_size = 64
        tile_scale = 4
        self.images  = []

        num_images = 8
        spritesheet = pg.image.load('sprites/Green Portal Sprite Sheet.png')

        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            image = pg.transform.flip(image, False, True)
            self.images.append(image)
    def update(self):
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.images):
                self.current_image = 0
            self.image = self.images[self.current_image]
            self.timer = pg.time.get_ticks()
class Ball(pg.sprite.Sprite):
    def __init__(self, player_rect, direction):
        super().__init__()
        self.direction = direction
        self.speed = 10
        self.image = pg.image.load('sprites/ball.png')
        self.image = pg.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()

        if self.direction == 'right':
            self.rect.x = player_rect.right
        else:
            self.rect.x = player_rect.left
        self.rect.y = player_rect.centery
    def update(self):
        if self.direction == 'right':
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

class Coin(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.load_animations()
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.current_image = 0
        self.interval = 200
        self.timer = pg.time.get_ticks()
    def load_animations(self):
        tile_size = 16
        tile_scale = 4
        self.images= []
        num_images = 5
        spritesheet = pg.image.load('sprites/Coin_Gems/MonedaD.png')
        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.images.append(image)
    def update(self):
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.images):
                self.current_image = 0
            self.image = self.images[self.current_image]
            self.timer = pg.time.get_ticks()
        

        

class Player(pg.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super(Player, self).__init__()
        self.load_animations()
        self.current_animation = self.idle_animation_right
        self.image = self.current_animation[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.center = (200, 100)

        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = map_width * tile_scale
        self.map_height = map_height * tile_scale

        self.timer = pg.time.get_ticks()
        self.interval = 200

        self.hp = 10
        self.damage_timer = pg.time.get_ticks()
        self.damage_interval = 1000

        self.direction = 'right'

    def load_animations(self):
        tile_size = 32
        tile_scale = 4
        self.idle_animation_right = []
        num_images = 5
        spritesheet = pg.image.load('sprites/Sprite Pack 3/2 - Twiggy/Idle (32 x 32).png')
        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.idle_animation_right.append(image)
            self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]
        self.move_animation_right = []

        num_images = 5
        spritesheet = pg.image.load('sprites/Sprite Pack 3/2 - Twiggy/Running (32 x 32).png')

        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.move_animation_right.append(image)

        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

    def update(self, platforms):
        # Список нажатых клавишь
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and not self.is_jumping:
            self.jump()
        if keys[pg.K_a]:
            self.direction = 'left'
            if self.current_animation != self.move_animation_left:
                self.current_animation = self.move_animation_left
            self.velocity_x = -10
        elif keys[pg.K_d]:
            self.direction = 'right'
            if self.current_animation != self.move_animation_right:
                self.current_animation = self.move_animation_right
            self.velocity_x = 10
        
        else:
            if self.current_animation == self.move_animation_right:
                self.current_animation = self.idle_animation_right
                self.current_image = 0
            elif self.current_animation == self.move_animation_left:
                self.current_animation = self.idle_animation_left
                self.current_image = 0
            self.velocity_x = 0
        
        
        new_x = self.rect.x + self.velocity_x

        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Столкновение с платформами
        for platform in platforms:
            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0 
                self.is_jumping = False
            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0
            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right
            
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()

    def jump(self):
        self.velocity_y = -45
        self.is_jumping = True

    def get_damage(self):
        if pg.time.get_ticks() - self.damage_timer > self.damage_interval:
            self.hp -= 1
            self.damage_timer = pg.time.get_ticks()
             

    
            

    

    
class Platform(pg.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super().__init__()


        self.image = pg.transform.scale(image, (width * tile_scale, height * tile_scale))
        self.rect = self.image.get_rect()
        self.rect.x = x * tile_scale
        self.rect.y = y * tile_scale
class Crab(pg.sprite.Sprite):
    def __init__(self, map_width, map_height, start_pos, final_pos):
        super().__init__()

        self.load_animations()
        self.current_animation = self.animation
        self.image = self.current_animation[0]
        self.current_image = 0
        
        self.rect = self.image.get_rect()
        self.rect.bottomleft = start_pos
        self.left_edge = start_pos[0]
        self.right_edge = final_pos[0] + self.image.get_width()

        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.map_width = map_width * tile_scale
        self.map_height = map_height * tile_scale

        self.timer = pg.time.get_ticks()
        self.interval = 300

        self.direction = 'right'
    
    def load_animations(self):
        tile_scale = 4
        tile_size = 32

        self.animation = []

        image = pg.image.load('sprites/Sprite Pack 2/9 - Snip Snap Crab/Movement_(Flip_image_back_and_forth) (32 x 32).png')
        image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
        self.animation.append(image)
        self.animation.append(pg.transform.flip(image, True, False))

    def update(self, platforms):
        if self.direction == 'right':
            self.velocity_x = 5
            if self.rect.right >= self.right_edge:
                self.direction = 'left'
        elif self.direction == 'left':
            self.velocity_x = -5
            if self.rect.left <= self.left_edge:
                self.direction = 'right'
        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        for platform in platforms:
            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0 
                self.is_jumping = False
            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0
            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right
# Класс Игры
class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((screen_width, screen_height))
        pg.display.set_caption('Платформер')
        self.level = 1
        self.setup()
    def setup(self):
        self.mode = 'game'
        self.clock = pg.time.Clock()
        self.is_running = False
        self.background = pg.image.load('background.png')
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.balls = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.portals = pg.sprite.Group()
        self.tmx_map = pytmx.load_pygame(f'maps/level{self.level}.tmx')
        self.map_pixel_width = self.tmx_map.width * self.tmx_map.tilewidth * tile_scale
        self.map_pixel_height = self.tmx_map.height * self.tmx_map.tileheight * tile_scale

        self.player = Player(self.map_pixel_width, self.map_pixel_height)
        self.all_sprites.add(self.player)
        with open(f'maps/level{self.level}_enemies.json', 'r') as json_file:
            data = json.load(json_file)
        for enemy in data['enemies']:
            if enemy['name'] == 'Crab':
                x1 = enemy['start_pos'][0] * tile_scale * self.tmx_map.tilewidth
                y1 = enemy['start_pos'][1] * tile_scale * self.tmx_map.tilewidth

                x2 = enemy['final_pos'][0] * tile_scale * self.tmx_map.tilewidth
                y2 = enemy['final_pos'][1] * tile_scale * self.tmx_map.tilewidth

                crab = Crab(self.map_pixel_width, self.map_pixel_height, [x1, y1], [x2, y2])
                self.enemies.add(crab)
                self.all_sprites.add(crab)
        for layer in self.tmx_map:
            if layer.name == 'platforms':
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        platform = Platform(tile, x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight,
                                            self.tmx_map.tilewidth,
                                            self.tmx_map.tileheight)
                        self.all_sprites.add(platform)
                        self.platforms.add(platform)
            elif layer.name == 'coins':
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)
                    if tile:
                        coin = Coin(x * self.tmx_map.tilewidth * tile_scale, y * self.tmx_map.tileheight * tile_scale)
                        self.all_sprites.add(coin)
                        self.coins.add(coin)
            elif layer.name == 'portal':
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)

                    if tile:
                        portal = Portal(x * self.tmx_map.tilewidth * tile_scale, y * self.tmx_map.tileheight * tile_scale)
                        self.all_sprites.add(portal)
                        self.portals.add(portal)
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 4
        
        self.collected_coins = 0
        self.run()

    def run(self):
        # Запуск игрового цикла
        self.is_running = True
        while self.is_running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(fps)
            pg.display.flip()
        pg.quit()
        quit()
    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    ball = Ball(self.player.rect, self.player.direction)
                    self.balls.add(ball)
                    self.all_sprites.add(ball)
    def update(self):
        

        if self.player.hp <= 0:
            self.mode = 'game over'
            return

        for enemy in self.enemies.sprites():
            if pg.sprite.collide_mask(self.player, enemy):
                self.player.get_damage()

        self.player.update(self.platforms)
        for enemy in self.enemies.sprites():
            enemy.update(self.platforms)
        self.balls.update()
        self.coins.update()
        self.portals.update()
        pg.sprite.groupcollide(self.balls, self.enemies, True, True)
        pg.sprite.groupcollide(self.balls, self.platforms, True, False)

        hits = pg.sprite.spritecollide(self.player, self.coins, True)
        for hit in hits:
            self.collected_coins += 1
        self.camera_x = self.player.rect.x - screen_width // 2
        self.camera_y = self.player.rect.y - screen_height // 2

        hits = pg.sprite.spritecollide(self.player, self.portals, False, pg.sprite.collide_mask)

        for hit in hits:
            self.level += 1
            if self.level == 3:
                quit()
            self.setup()
        
        
        

        self.camera_x = max(0, min(self.camera_x, self.map_pixel_width - screen_width))
        self.camera_y = max(0, min(self.camera_y, self.map_pixel_height - screen_height))
        
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, -self.camera_y))
        # Полоска здоровья
        pg.draw.rect(self.screen, pg.Color('red'), (10, 10, self.player.hp * 10, 10))
        pg.draw.rect(self.screen, pg.Color('black'), (10, 10, 100, 10), 1)

        text = font.render('Монеты: ' + str(self.collected_coins), True, pg.Color('black'))
        text_rect = text.get_rect(topleft=(10, 30))
        self.screen.blit(text, text_rect)
        
        if self.mode == 'game over':
            text = font.render("Вы проиграли", True, (255, 0, 0))
            text_rect = text.get_rect(center=(screen_width//2, screen_height//2))
            self.screen.blit(text, text_rect)
if __name__ == '__main__':
    game = Game()
    

        
        