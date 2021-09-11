import random, math, os, pygame, requests, json, time

class Name(pygame.sprite.Sprite):
    def __init__(self, name):
        self.name = name
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font("arlrdbd.ttf", 35)
        self.textSurf = self.font.render(name, 1, (255, 255, 255))
        self.image = pygame.Surface((1280, 720))
        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.image.blit(self.textSurf, [640 - W/2, 280 - H/2])
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()

    def update(self, where, screen):
        self.rect.center = where
        screen.blit(self.image, self.rect)

    def get_name(self):
        return self.name

class Crew(pygame.sprite.Sprite):
    def __init__(self, colors):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/crew/" + random.choice(colors) + ".png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (74, 99))
        self.rect = self.image.get_rect()
        self.rect.center = (640, 360)

        self.name = Name("Player")

    def update(self, x, y, screen, orient):
        self.name.update(self.rect.center, screen)
        if orient == "Right":
            screen.blit(self.image, self.rect)
        elif orient == "Left":
            screen.blit(pygame.transform.flip(self.image, True, False), self.rect)

class Bot(pygame.sprite.Sprite):
    def __init__(self, idd, colors, names, ticks):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/crew/" + random.choice(colors) + ".png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (74, 99))
        self.rect = self.image.get_rect()
        self.rect.center = (640, 360)
        self.moves = eval(open("moves\\file" + str(idd) + ".txt", "r").read())
        self.future_name = random.randint(0, len(names) - 1)
        self.name = Name(names[self.future_name])
        names.pop(self.future_name)
        self.ticks = ticks

    def update(self, x, y, screen, orient):
        self.ticks += 1
        try:
            self.rect.center = (x - self.moves[self.ticks][0] + 640, y - self.moves[self.ticks][1] + 360)
            self.name.update(self.rect.center, screen)
            if self.moves[self.ticks][2] == "Right":
                screen.blit(self.image, self.rect)
            else:
                screen.blit(pygame.transform.flip(self.image, True, False), self.rect)
        except IndexError:
            self.ticks = 0

    def distance_from_center(self): # sorry i wont put centre because why
        return math.hypot(640 - self.rect.x, 360 - self.rect.y)

    def get_coords(self):
        return self.moves[self.ticks][0], self.moves[self.ticks][1]

def main():
    v = "v2.2.0"
    new_ver = False

    pygame.init()
    pygame.font.init()

    do_kill = False
    do_write = False
    do_ping_pong = False
    kill_possible = True
    ticks = 0
    FPS = 120
    x = -2800
    y = -450
    change = 12
    old_super = -1
    orient = "Left"
    names = ["Xiaoness191", "Milenakos", "SOKE®", "RubiK", "=/", "^ Frinkifail ^", "m(._.)m",
             "Andrew Meep", "atomicgrape908", "suffix.", "CatRBLX", "Deltaonetrooper", "drealy", "Drewskibob",
             "Euro2555", "nclazrfpyt", "finched also poppi alpha", "FloppityLopp", "GentleToonMan", "GentleToonMan",
             "J'zargo", "lucyy", "m(._.)mV2", "Mr. snowmanfan20_YT", "normal", "exotic", "Stoned", "That_One_Amogus_Person",
             "ThisIsMyUsername", "tiddcunt", "Vana_Ungkap", "WarNoodleZ", "Wut", "Yuuta Togashi", "Zatrex", "FedeGamer", "hezigonic"]
    colors = ["Red", "Blue", "Green", "Pink", "Orange", "Yellow", "Black", "White", "Purple", "Brown", "Cyan", "Lime", "Maroon", "Rose", "Banana", "Gray",
              "Tan", "Coral", "Olive", "Fortegreen"]
    moves = []
    bots = []

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Among Ys Rewrite Beta")
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()

    back = pygame.image.load('img/loadings/loading.png')

    walls = pygame.image.load("img/layout.png")
    walls_mask = pygame.mask.from_surface(walls)

    hitbox = pygame.image.load("img/hitbox.png")
    hitbox_mask = pygame.mask.from_surface(hitbox)

    kill = pygame.image.load("img/kill.png")
    kill_btn = kill.get_rect()
    kill_btn.center = (1200, 640)

    screen.blit(back, (0, 0))

    running = True

    while running:
        clock.tick(FPS)
        ticks += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and kill_btn.collidepoint(event.pos):
                    do_kill = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    do_kill = True

        if do_kill and kill_possible:
            dists = []
            for i in bots:
                dists.append(i.distance_from_center())
            if min(dists) <= 270:
                enemy_ind = dists.index(min(dists))
                enemy = bots[enemy_ind]
                x, y = enemy.get_coords()
                bots.pop(enemy_ind)
                textSurf = font.render("People left: " + str(len(bots) + 1), 1, (255, 255, 255))
                image = pygame.Surface((1280, 720))
                image.blit(textSurf, [0, 0])
                image.set_colorkey((0,0,0))
            do_kill = False
            if len(bots) == 0:
                kill_possible = False

        keys = pygame.key.get_pressed()

        x_save, y_save = x, y
           
        new_x = new_y = 0

        if do_ping_pong:
            if do_ping_pong == True:
                do_ping_pong = random.randint(1, 8)
            if do_ping_pong == 1:
                new_x += change
            elif do_ping_pong == 2:
                new_x -= change
            elif do_ping_pong == 3:
                new_y += change
            elif do_ping_pong == 4:
                new_y -= change
            elif do_ping_pong == 5:
                new_y -= change
                new_x -= change
            elif do_ping_pong == 6:
                new_y -= change
                new_x += change
            elif do_ping_pong == 7:
                new_y += change
                new_x -= change
            elif do_ping_pong == 8:
                new_y += change
                new_x += change

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_x += change
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_x -= change

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_y += change
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_y -= change

        if new_x > 0:
            orient = "Left"
        elif new_x < 0:
            orient = "Right"

        x += new_x
        y += new_y

        if do_write:
            moves.append([x, y, orient])

        if walls_mask.overlap(hitbox_mask, (-x, -y)):
            x, y = x_save, y_save
            if do_ping_pong:
                old_super = do_ping_pong
                while do_ping_pong == old_super:
                    do_ping_pong = random.randint(1, 8)

        if ticks == 2:
            latest = requests.get("https://api.github.com/repos/milena-kos/Among-Ys-Rewrite/releases/latest").text
            version = json.loads(latest)["name"]
            if version != v:
                font = pygame.font.Font("arlrdbd.ttf", 30)
                new_ver = font.render("New version of Among Ys Rewrite is available. Please upgrade your game.", 1, (255, 255, 255))
            back = pygame.image.load('img/skeld.png')
            crew = Crew(colors)
            if not do_write:
                for i in range(0, len(os.listdir(".\\moves"))):
                    bot = Bot(i, colors, names, ticks)
                    bots.append(bot)
            all_sprites.add(crew)

            font = pygame.font.Font("arlrdbd.ttf", 35)
            textSurf = font.render("People left: " + str(len(bots) + 1), 1, (255, 255, 255))
            image = pygame.Surface((1280, 720))
            image.blit(textSurf, [0, 0])
            image.set_colorkey((0,0,0))

        screen.fill((0, 0, 0))
        
        if ticks > 1:
            screen.blit(back, (x, y))
            for i in bots:
                i.update(x, y, screen, orient)
            screen.blit(image, (0, 0))
            if kill_possible:
                screen.blit(kill, kill_btn)
            walls.get_rect().center = (x, y)
            if new_ver:
                screen.blit(new_ver, (0, 680))
        else:
            screen.blit(back, (0, 0))
        
        all_sprites.update(x, y, screen, orient)
        pygame.display.flip()

    if do_write:
        file = open("moves\\file.txt", "w")
        file.write(str(moves))
        file.close()

    pygame.quit()

if __name__ == "__main__":
    main()