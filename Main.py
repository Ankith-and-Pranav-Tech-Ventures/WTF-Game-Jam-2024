import random
import time
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()
xyz=load_texture('Assets/Models/Grass_Block.png')

# Load textures
grass_texture = load_texture("Assets/Textures/Grass_Block.png")
stone_texture = load_texture("Assets/Textures/Stone_Block.png")
brick_texture = load_texture("Assets/Textures/Brick_Block.png")
dirt_texture = load_texture("Assets/Textures/Dirt_Block.png")
wood_texture = load_texture("Assets/Textures/Wood_Block.png")
sky_texture = load_texture("Assets/Textures/Skybox.png")
arm_texture = load_texture("Assets/Textures/Arm_Texture.png")
punch_sound = Audio("Assets/SFX/Punch_Sound.wav", loop=False, autoplay=False)
speed_boost_texture = load_texture("Assets/Textures/Speed_Boost.png")
health_boost_texture = load_texture("Assets/Textures/Health_Boost.png")
hunger_boost_texture = load_texture("Assets/Textures/Hunger_Boost.png")

window.exit_button.visible = False
block_pick = 1
player_health = 100
player_hunger = 100
player_speed = 1

# Timer for block management and power-ups
block_timer = 0
power_up_timer = 0
block_interval = 5  # Time interval for block updates in seconds
power_up_interval = 10  # Time interval for power-up updates in seconds

moving_blocks = []
invisible_blocks = []
block_speed = 1
active_power_ups = []

# Textures for moving blocks (available assets)
moving_block_textures = [grass_texture, stone_texture, brick_texture, dirt_texture, wood_texture]

def update():
    global block_pick, player_health, player_hunger, block_timer, power_up_timer, player_speed

    if held_keys["left mouse"] or held_keys["right mouse"]:
        hand.active()
    else:
        hand.passive()

    if held_keys["1"]: block_pick = 1
    if held_keys["2"]: block_pick = 2
    if held_keys["3"]: block_pick = 3
    if held_keys["4"]: block_pick = 4
    if held_keys["5"]: block_pick = 5

    # Decrease hunger and health over time
    player_hunger -= 0.1
    if player_hunger <= 0:
        player_health -= 0.1
        player_hunger = 0
    if player_health <= 0:
        print("Game Over!")
        exit()  # Exit the game if health reaches 0

    # Update block appearance and disappearance
    current_time = time.time()
    if current_time - block_timer >= block_interval:
        block_timer = current_time
        update_blocks()

    # Update power-ups
    if current_time - power_up_timer >= power_up_interval:
        power_up_timer = current_time
        update_power_ups()

    # Move and update moving blocks
    for block in moving_blocks:
        block.position += Vec3(block.direction[0] * block_speed * time.dt, block.direction[1] * block_speed * time.dt, 0)

        # Ensure the block stays within the platform boundaries
        if block.position.x > 19 or block.position.x < 0:
            block.direction = (-block.direction[0], block.direction[1])
        if block.position.z > 19 or block.position.z < 0:
            block.direction = (block.direction[0], -block.direction[1])

        if random.random() < 0.02:  # Randomly make the block invisible
            block.visible = False
        else:
            block.visible = True

    # Check collision with power-ups
    for power_up in active_power_ups:
        if player.intersects(power_up).hit:
            apply_power_up(power_up)
            destroy(power_up)
            active_power_ups.remove(power_up)

def update_blocks():
    global blocks, moving_blocks, invisible_blocks

    # Randomly choose a block to appear or disappear
    for voxel in blocks:
        if random.random() < 0.1:  # Adjust the probability as needed
            voxel.appear()
            destroy(voxel, delay=1)  # Destroy the voxel after a delay
            blocks.remove(voxel)

    # Randomly place new blocks
    for _ in range(10):  # Adjust the number of new blocks as needed
        x = random.randint(0, 19)
        z = random.randint(0, 19)
        if not any(block.position == (x, 0, z) for block in blocks):
            texture = random.choice([grass_texture, stone_texture, brick_texture, dirt_texture, wood_texture])
            voxel = Voxel(position=(x, 0, z), texture=texture)
            blocks.append(voxel)
    
    # Add moving blocks with random textures
    while len(moving_blocks) < 15:  # Ensure at least 15 moving blocks
        x = random.randint(0, 19)
        z = random.randint(0, 19)
        texture = random.choice(moving_block_textures)
        direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        moving_block = MovingBlock(position=(x, 0, z), texture=texture, direction=direction)
        moving_blocks.append(moving_block)

def update_power_ups():
    global active_power_ups

    # Randomly place new power-ups
    for _ in range(3):  # Adjust the number of new power-ups as needed
        x = random.randint(0, 19)
        z = random.randint(0, 19)
        if not any(power_up.position == (x, 0, z) for power_up in active_power_ups):
            texture = random.choice([speed_boost_texture, health_boost_texture, hunger_boost_texture])
            power_up = PowerUp(position=(x, 0, z), texture=texture)
            active_power_ups.append(power_up)

def apply_power_up(power_up):
    global player_health, player_hunger, player_speed

    if power_up.texture == speed_boost_texture:
        player_speed *= 2  # Double the player's speed
        invoke(reset_speed, delay=5)  # Reset speed after 5 seconds
    elif power_up.texture == health_boost_texture:
        player_health = min(100, player_health + 20)  # Restore health by 20 points
    elif power_up.texture == hunger_boost_texture:
        player_hunger = min(100, player_hunger + 20)  # Restore hunger by 20 points

def reset_speed():
    global player_speed
    player_speed = 1  # Reset player speed to normal

# Voxel (block) properties
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture = grass_texture):
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
        self.original_color = self.color  # Save the original color

    def input(self, key):
        global player_hunger
        
        if self.hovered:
            if key == "left mouse down":
                punch_sound.play()
                if block_pick == 1: 
                    voxel = Voxel(position=self.position + mouse.normal, texture=grass_texture)
                elif block_pick == 2: 
                    voxel = Voxel(position=self.position + mouse.normal, texture=stone_texture)
                elif block_pick == 3: 
                    voxel = Voxel(position=self.position + mouse.normal, texture=brick_texture)
                elif block_pick == 4: 
                    voxel = Voxel(position=self.position + mouse.normal, texture=dirt_texture)
                elif block_pick == 5: 
                    voxel = Voxel(position=self.position + mouse.normal, texture=wood_texture)
                
                # Increase hunger when gathering resources
                player_hunger -= 0.5

            if key == "right mouse down":
                punch_sound.play()
                destroy(self)
                if self in blocks:
                    blocks.remove(self)

    def appear(self):
        # Make the voxel appear in red
        self.color = color.red
        # Optionally, you can add a method to revert the color back to the original after some time

# Moving block properties
class MovingBlock(Button):
    def __init__(self, position=(0, 0, 0), texture=grass_texture, direction=(1, 0)):
        super().__init__(
            parent=scene,
            position=position,
            model="Assets/Models/Block",
            origin_y=0.5,
            texture=texture,  # Ensure texture is passed here
            color=color.color(0, 0, random.uniform(0.9, 1)),
            highlight_color=color.light_gray,
            scale=0.5
        )
        self.direction = direction

class PowerUp(Button):
    def __init__(self, position=(0, 0, 0), texture=speed_boost_texture):
        super().__init__(
            parent=scene,
            position=position,
            model="Assets/Models/PowerUp",
            origin_y=0.5,
            texture=texture,  # Ensure texture is passed here
            color=color.white,
            highlight_color=color.light_gray,
            scale=0.5
        )

class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model="cube",
            color=color.white,
            scale=(0.2, 0.2, 0.2),
            rotation=(90, 0, 0),
            position=(0.05, -0.4)
        )
        self.active()

    def active(self):
        self.visible = True

    def passive(self):
        self.visible = False

class HUD(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model="quad",
            texture=sky_texture,
            scale=(0.2, 0.1),
            color=color.black,
            position=(0.05, -0.4)
        )
        self.health_text = Text(text=f"Health: {int(player_health)}", color=color.white, scale=2, position=(0, 0))
        self.hunger_text = Text(text=f"Hunger: {int(player_hunger)}", color=color.white, scale=2, position=(0, -0.05))

    def update(self):
        self.health_text.text = f"Health: {int(player_health)}"
        self.hunger_text.text = f"Hunger: {int(player_hunger)}"

# List to keep track of existing blocks and power-ups
blocks = []
moving_blocks = []
active_power_ups = []

# Create initial world
for z in range(20):
    for x in range(20):
        texture = random.choice([grass_texture, stone_texture, brick_texture, dirt_texture, wood_texture])
        voxel = Voxel(position=(x, 0, z), texture=texture)
        blocks.append(voxel)

player = FirstPersonController()
hand = Hand()
sky = Sky()
hud = HUD()

# Run the game
app.run()
