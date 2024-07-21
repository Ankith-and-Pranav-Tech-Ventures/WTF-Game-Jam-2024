import random
import time
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
app = Ursina()
textures = {
    "grass": load_texture("Assets/Textures/Grass_Block.png"),
    "stone": load_texture("Assets/Textures/Stone_Block.png"),
    "brick": load_texture("Assets/Textures/Brick_Block.png"),
    "dirt": load_texture("Assets/Textures/Dirt_Block.png"),
    "wood": load_texture("Assets/Textures/Wood_Block.png"),
    "sky": load_texture("Assets/Textures/Skybox.png"),
    "arm": load_texture("Assets/Textures/Arm_Texture.png"),
    "health_boost": load_texture("Assets/Textures/Health_Boost.png"),
    "skeleton": load_texture("Assets/Textures/minecraft-skeleton.png"),
}
punch_sound = Audio("Assets/SFX/Punch_Sound.wav", loop=False, autoplay=False)
disappear_sound = Audio("Assets/SFX/nakime-biwa-sound-effect-made-with-Voicemod.mp3", loop=False, autoplay=False)
start_game_sound = Audio("Assets/SFX/17215597590081w5abxam-voicemaker.in-speech.mp3", loop=False, autoplay=False)
block_pick = 1
player_health = 100
player_speed = 1
player_score = 0
blocks = []
block_timer = time.time()
power_up_timer = time.time()
health_decrease_timer = time.time()
platform_offset = 0
moving_blocks = []
moving_health_blocks = []
treasury_blocks = []
def update():
    global block_pick, player_health, block_timer, power_up_timer, player_speed, health_decrease_timer, player_score, platform_offset
    if held_keys["left mouse"] or held_keys["right mouse"]:
        hand.active()
    else:
        hand.passive()
    if held_keys["1"]: block_pick = 1
    if held_keys["2"]: block_pick = 2
    if held_keys["3"]: block_pick = 3
    if held_keys["4"]: block_pick = 4
    if held_keys["5"]: block_pick = 5
    current_time = time.time()
    if current_time - health_decrease_timer >= 1:
        player_health -= 1
        health_decrease_timer = current_time
    if player_health <= 0:
        print("Game Over!")
        application.quit()
    if current_time - block_timer >= 5:
        block_timer = current_time
        update_blocks()
    if current_time - power_up_timer >= 10:
        power_up_timer = current_time
        update_power_ups()
    for block in moving_blocks:
        block.position += Vec3(block.direction[0] * player_speed * time.dt, 0, block.direction[1] * player_speed * time.dt)
        if block.position.x > 9 or block.position.x < -9:
            block.direction = (-block.direction[0], block.direction[1])
        if block.position.z > 9 or block.position.z < -9:
            block.direction = (block.direction[0], -block.direction[1])
    for block in moving_health_blocks:
        block.position += Vec3(block.direction[0] * player_speed * time.dt, 0, block.direction[1] * player_speed * time.dt)
        if block.position.x > 9 or block.position.x < -9:
            block.direction = (-block.direction[0], block.direction[1])
        if block.position.z > 9 or block.position.z < -9:
            block.direction = (block.direction[0], -block.direction[1])
    for block in treasury_blocks:
        if block.hovered and held_keys["right mouse down"]:
            punch_sound.play()
            destroy(block)
            print("Game Completed!")
            application.quit()
            if block in treasury_blocks:
                treasury_blocks.remove(block)
    health_text.text = f'Health: {player_health}'
    score_text.text = f'Score: {player_score}'
    if player.position.y > platform_offset - 5:
        platform_offset += 5
        create_platform(platform_offset)
def update_blocks():
    global moving_blocks, moving_health_blocks
    for voxel in blocks:
        if random.random() < 0.1:
            invoke(voxel.blink_and_disappear, delay=0)
    for platform_start in range(0, platform_offset + 1, 10):
        while len([block for block in moving_blocks if platform_start <= block.position.y < platform_start + 10]) < 10:
            x = random.randint(-9, 9)
            y = random.randint(platform_start, platform_start + 9)
            z = random.randint(-9, 9)
            if random.random() < 0.2:
                texture = textures["skeleton"]
                direction = (random.uniform(-1, 1), random.uniform(-1, 1))
            else:
                texture = random.choice(list(textures.values())[:5])
                direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            moving_block = MovingBlock(position=(x, y, z), texture=texture, direction=direction)
            moving_blocks.append(moving_block)
    for platform_start in range(0, platform_offset + 1, 10):
        while len([block for block in moving_health_blocks if platform_start <= block.position.y < platform_start + 10]) < 3:
            x = random.randint(-9, 9)
            y = random.randint(platform_start, platform_start + 9)
            z = random.randint(-9, 9)
            direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            health_block = HealthBlock(position=(x, y, z), texture=textures["health_boost"], direction=direction)
            moving_health_blocks.append(health_block)
def update_power_ups():
    pass
def create_platform(y_offset):
    for x in range(-10, 10):
        for z in range(-10, 10):
            block = Voxel(position=(x, y_offset, z), texture=random.choice(list(textures.values())[:5]))
            blocks.append(block)
    if random.random() < 0.1:
        x = random.randint(-9, 9)
        z = random.randint(-9, 9)
        treasury_block = TreasuryBlock(position=(x, y_offset, z))
        treasury_blocks.append(treasury_block)
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=textures["grass"]):
        super().__init__(
            parent=scene,
            position=position,
            model="Assets/Models/Block",
            origin_y=0.5,
            texture=texture,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            highlight_color=color.light_gray,
            scale=0.5
        )
    def input(self, key):
        if self.hovered:
            if key == "left mouse down":
                punch_sound.play()
                if block_pick == 1: voxel = Voxel(position=self.position + mouse.normal, texture=textures["grass"])
                elif block_pick == 2: voxel = Voxel(position=self.position + mouse.normal, texture=textures["stone"])
                elif block_pick == 3: voxel = Voxel(position=self.position + mouse.normal, texture=textures["brick"])
                elif block_pick == 4: voxel = Voxel(position=self.position + mouse.normal, texture=textures["dirt"])
                elif block_pick == 5: voxel = Voxel(position=self.position + mouse.normal, texture=textures["wood"])
            if key == "right mouse down":
                punch_sound.play()
                destroy(self)
                if self in blocks:
                    blocks.remove(self)
    def blink_and_disappear(self):
        self.color = color.red
        invoke(self.reset_color, delay=0.5)
        invoke(self.disappear, delay=5)
    def reset_color(self):
        self.color = color.color(0, 0, random.uniform(0.9, 1))
    def disappear(self):
        destroy(self)
        if self in blocks:
            blocks.remove(self)
        disappear_sound.play()
class MovingBlock(Button):
    def __init__(self, position=(0, 0, 0), texture=textures["grass"], direction=(1, 0)):
        super().__init__(
            parent=scene,
            position=position,
            model="Assets/Models/Block",
            origin_y=0.5,
            texture=texture,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            highlight_color=color.light_gray,
            scale=0.5
        )
        self.direction = direction
    def input(self, key):
        global player_score
        if self.hovered and key == "right mouse down" and self.texture == textures["skeleton"]:
            punch_sound.play()
            player_score += 50
            destroy(self)
            if self in moving_blocks:
                moving_blocks.remove(self)
class HealthBlock(Button):
    def __init__(self, position=(0, 0, 0), texture=textures["health_boost"], direction=(1, 0)):
        super().__init__(
            parent=scene,
            position=position,
            model="Assets/Models/Block",
            origin_y=0.5,
            texture=texture,
            color=color.color(0, 0, random.uniform(0.9, 1)),
            highlight_color=color.light_gray,
            scale=0.5
        )
        self.direction = direction
    def input(self, key):
        global player_health
        if self.hovered and key == "right mouse down":
            punch_sound.play()
            player_health = min(100, player_health + 20)
            destroy(self)
            if self in moving_health_blocks:
                moving_health_blocks.remove(self)
class TreasuryBlock(Button):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            parent=scene,
            position=position,
            model="Assets/Models/Block",
            origin_y=0.5,
            texture=None,  # No texture
            color=color.gold,  # Gold color
            highlight_color=color.light_gray,
            scale=1.0
        )
    def input(self, key):
        if self.hovered and key == "right mouse down":
            punch_sound.play()
            destroy(self)
            print("Game Completed!")
            application.quit()
            if self in treasury_blocks:
                treasury_blocks.remove(self)
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model="Assets/Models/Hand",
            texture=textures["arm"],
            scale=0.2,
            rotation=(150, -10, 0),
            position=(0.6, -0.6)
        )
    def active(self):
        self.enabled = True
    def passive(self):
        self.enabled = False
class Arm(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model="Assets/Models/Arm",
            texture=textures["arm"],
            scale=0.2,
            rotation=(150, -10, 0),
            position=(0.6, -0.6)
        )
player = FirstPersonController()
sky = Sky()
hand = Hand()
arm = Arm()
blocks = [Voxel(position=(x, 0, z), texture=random.choice(list(textures.values())[:5])) for x in range(-10, 10) for z in range(-10, 10)]
start_game_sound.play()
create_platform(0)
health_text = Text(text=f'Health: {player_health}', position=(-0.8, 0.4), scale=2)
score_text = Text(text=f'Score: {player_score}', position=(-0.8, 0.3), scale=2)
app.run()