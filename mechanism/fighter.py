import pygame


class Fighter:
    def __init__(self, x, y, flip, data, sprite_sheets, animation_steps):
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheets, animation_steps)
        self.action = (
            0  # 0: idle, 1: run, 2: jump, 3: attack_1, 4: attck_2, 5: hit, 6: death
        )
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 90, 180))
        self.vel_y = 0  # vertical position control
        self.runnning = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.hit = False
        self.health = 100
        self.rect_move = 0

    def load_images(self, sprite_sheets, animation_steps):
        # extract images from spritesheest
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheets.subsurface(
                    x * self.size, y * self.size, self.size, self.size
                )
                temp_img_list.append(
                    pygame.transform.scale(
                        temp_img, (self.size * self.image_scale, self.size * 1.5)
                    )
                )
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, jutsu_number):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.runnning = False
        self.attack_type = 0

        # get keypresses
        key = pygame.key.get_pressed()

        # can only performed other actions if not currently attacking
        if self.attacking == False:
            # movements
            if key[pygame.K_a]:
                dx = -SPEED
                self.runnning = True
            if key[pygame.K_d]:
                dx = SPEED
                self.runnning = True

            # jumping
            if key[pygame.K_w] and self.jump == False:
                self.vel_y = -30
                self.jump = True

            # attack
            if jutsu_number:
                self.attack_type = jutsu_number
                self.attack(surface, target)

        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # ensure players stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 20:
            self.vel_y = 0
            dy = screen_height - 20 - self.rect.bottom
            self.jump = False

        # ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # move when attacking
        if self.rect_move == 1:
            if self.flip == False:
                move_speed = self.attacking_rect.midright[0] - self.rect.x
                self.rect.x += move_speed - self.rect.width
            else:
                move_speed = self.rect.x - self.attacking_rect.midleft[0]
                self.rect.x -= move_speed + self.rect.width
            self.rect_move = 0

        # apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # update player position
        self.rect.x += dx
        self.rect.y += dy

    # handle animation updates
    def update(self):
        # check what action the player is performing
        if self.hit == True:
            self.update_action(5)
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)
            elif self.attack_type == 2:
                self.update_action(4)
        elif self.jump == True:
            self.update_action(2)
        elif self.runnning == True:
            self.update_action(1)
        else:
            self.update_action(0)

        animation_cooldown = 350
        # update image
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
            # for moving the rectangle setting update
            if self.frame_index == 9 and self.action == 3:
                self.rect_move = 1

        # check if the animation is finished
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
            # check if an attack is executed
            if self.action == 3 or self.action == 4:
                self.attacking = False
                self.attack_cooldown = 100
            # check if damage was taken
            if self.action == 5:
                self.hit = False
                # if the player was in the middle of the attack then the attack should stop
                self.attacking = False
                self.attack_cooldown = 100

    def attack(self, surface, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attacking_rect = pygame.Rect(
                self.rect.centerx - (4 * self.rect.width * self.flip),
                self.rect.y,
                4 * self.rect.width,
                self.rect.height,
            )
            if self.attacking_rect.colliderect(target.rect):
                target.health -= 10
                # target.hit = True

            pygame.draw.rect(surface, (0, 255, 0), self.attacking_rect)

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation setting
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(
            img,
            (
                self.rect.x - (self.offset[0] * self.image_scale),
                self.rect.y - (self.offset[1] * self.image_scale),
            ),
        )
