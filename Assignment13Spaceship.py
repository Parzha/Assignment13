
import random
import math
import threading
import sys
import os
import arcade

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = 0.3
SPRITE_SCALING_LASER = 0.8
COIN_COUNT = random.randint(1,4)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "SPACE CONQUEROR "

BULLET_SPEED = 10


PARTICLE_GRAVITY = 0.05
PARTICLE_FADE_RATE = 8
PARTICLE_MIN_SPEED = 2.5
PARTICLE_SPEED_RANGE = 2.5
PARTICLE_COUNT = 20
PARTICLE_RADIUS = 3
PARTICLE_COLORS = [arcade.color.ALIZARIN_CRIMSON,
                   arcade.color.COQUELICOT,
                   arcade.color.LAVA,
                   arcade.color.KU_CRIMSON,
                   arcade.color.DARK_TANGERINE]
PARTICLE_SPARKLE_CHANCE = 0.02
SMOKE_START_SCALE = 0.25
SMOKE_EXPANSION_RATE = 0.03
SMOKE_FADE_RATE = 7
SMOKE_RISE_RATE = 0.5
SMOKE_CHANCE = 0.25



class Coin(arcade.Sprite):

    def follow_sprite(self, player_sprite):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.change_y -= 0.09



class Smoke(arcade.SpriteCircle):
    def __init__(self, size):
        super().__init__(size, arcade.color.LIGHT_GRAY, soft=True)
        self.change_y = SMOKE_RISE_RATE
        self.scale = SMOKE_START_SCALE

    def update(self):
        if self.alpha <= PARTICLE_FADE_RATE:
            self.remove_from_sprite_lists()
        else:
            self.alpha -= SMOKE_FADE_RATE
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.scale += SMOKE_EXPANSION_RATE


class Particle(arcade.SpriteCircle):
    def __init__(self, my_list):
        color = random.choice(PARTICLE_COLORS)
        super().__init__(PARTICLE_RADIUS, color)
        self.normal_texture = self.texture
        self.my_list = my_list
        speed = random.random() * PARTICLE_SPEED_RANGE + PARTICLE_MIN_SPEED
        direction = random.randrange(360)
        self.change_x = math.sin(math.radians(direction)) * speed
        self.change_y = math.cos(math.radians(direction)) * speed
        self.my_alpha = 255
        self.my_list = my_list

    def update(self):

        if self.my_alpha <= PARTICLE_FADE_RATE:
            self.remove_from_sprite_lists()
        else:
            # Update
            self.my_alpha -= PARTICLE_FADE_RATE
            self.alpha = self.my_alpha
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.change_y -= PARTICLE_GRAVITY

            if random.random() <= PARTICLE_SPARKLE_CHANCE:
                self.alpha = 255
                self.texture = arcade.make_circle_texture(int(self.width),
                                                          arcade.color.WHITE)
            else:
                self.texture = self.normal_texture

            if random.random() <= SMOKE_CHANCE:
                smoke = Smoke(5)
                smoke.position = self.position
                self.my_list.append(smoke)



class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.player_list = None
        self.coin_list = None
        self.bullet_list = None
        self.explosions_list = None
        self.player_sprite = None
        self.coin_sprite = None
        self.score = 0
        self.lives = 3
        self.set_mouse_visible(False)

        self.gun_sound = arcade.sound.load_sound(":resources:sounds/laser2.wav")
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/explosion2.wav")


        try:
            self.enemyThread = threading.Thread(target=self.spawnememies_seq())
            self.enemyThread.start()
        except:
            sys.exit()


        arcade.set_background_color(arcade.color.BLACK)
        self.background_image = arcade.load_texture(":resources:images/backgrounds/stars.png")


    def setup(self):
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.score = 0
        self.player_sprite = arcade.Sprite(":resources:images/space_shooter/playerShip2_orange.png",
                                           SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 70
        self.player_list.append(self.player_sprite)

    def spawnememies_seq(self):
        arcade.schedule(self.spawnenmies, 2)

    def follow_sprite(self, coin_sprite):
        self.center_y += self.change_y

    def spawnenmies(self,_):
        self.coin_sprite = Coin(":resources:images/space_shooter/playerShip1_green.png",
                                 SPRITE_SCALING_COIN)
        self.coin_sprite.angle = 180
        self.coin_sprite.center_x = random.randrange(SCREEN_WIDTH)
        self.coin_sprite.center_y = SCREEN_HEIGHT
        self.coin_sprite.change_y = 5
        self.coin_list.append(self.coin_sprite)



    def on_draw(self):

        arcade.start_render()
        self.coin_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()
        self.explosions_list.draw()
        arcade.draw_lrwh_rectangle_textured(0,0,SCREEN_WIDTH,SCREEN_HEIGHT,self.background_image)

        arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)
        if self.lives == 3:
            arcade.draw_text(f"♥", 750, 20, arcade.color.RED, 35)
            arcade.draw_text(f"♥", 700, 20, arcade.color.RED, 35)
            arcade.draw_text(f"♥", 650, 20, arcade.color.RED, 35)
        elif self.lives == 2:
            arcade.draw_text(f"♥", 700, 20, arcade.color.RED, 35)
            arcade.draw_text(f"♥", 650, 20, arcade.color.RED, 35)
        elif self.lives == 1:
            arcade.draw_text(f"♥", 650, 20, arcade.color.RED, 35)


        if self.lives == 0 :
            arcade.draw_text("GAME OVER!", 0, SCREEN_HEIGHT / 2, arcade.color.WHITE_SMOKE, 60, width=SCREEN_WIDTH,
                             align="center")
            arcade.exit()




    def on_mouse_motion(self, x, y, dx, dy):

        self.player_sprite.center_x = x

    def on_mouse_press(self, x, y, button, modifiers):

        arcade.sound.play_sound(self.gun_sound)
        bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_LASER)
        bullet.angle = 90
        bullet.change_y = BULLET_SPEED
        bullet.center_x = self.player_sprite.center_x
        bullet.bottom = self.player_sprite.top
        self.bullet_list.append(bullet)

    def on_update(self, delta_time):

        self.bullet_list.update()
        self.explosions_list.update()

        for coin in self.coin_list:
            if coin.position[1] > 0:
                coin.follow_sprite(self.coin_sprite)
            else:
                coin.remove_from_sprite_lists()

        for player in self.player_list:
            crash_list = arcade.check_for_collision_with_list(player, self.coin_list)
            for enemy in crash_list:
                self.lives-=1
                enemy.remove_from_sprite_lists()




        for bullet in self.bullet_list:

            hit_list = arcade.check_for_collision_with_list(bullet, self.coin_list)

            if len(hit_list) > 0:

                bullet.remove_from_sprite_lists()

            for coin in hit_list:
                for i in range(PARTICLE_COUNT):
                    particle = Particle(self.explosions_list)
                    particle.position = coin.position
                    self.explosions_list.append(particle)

                smoke = Smoke(50)
                smoke.position = coin.position
                self.explosions_list.append(smoke)

                coin.remove_from_sprite_lists()
                self.score += 1

                arcade.sound.play_sound(self.hit_sound)

            if bullet.bottom > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()


def main():
    window = MyGame()
    window.center_window()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()