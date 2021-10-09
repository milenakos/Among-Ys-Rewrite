import random, math, os, pygame, requests, sys, logging, socket, threading, json, ast
import tkinter as tk

class Client:
    def __init__(self, host, port):
        self.info = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def receive(self):
        while True:
            message = self.sock.recv(4096)
            if message:
                try:
                    self.info = json.loads(message)
                except Exception as e:
                    print(e)

    def write(self, data):
        self.sock.send(json.dumps(data).encode('utf-8'))

    def close(self):
        self.sock.close()

    def get(self):
        return self.info

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
        logging.info("Class Name: Returning %s...", self.name)
        return self.name

class Crew(pygame.sprite.Sprite):
    def __init__(self, colors, name):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/crew/" + colors + ".png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (74, 99))
        self.rect = self.image.get_rect()
        self.rect.center = (640, 360)
        self.x = 640
        self.y = 360

        self.color = colors
        self.nickname = name
        self.name = Name(name)

    def update(self, orient, *args):
        self.orient = orient
        if args:
            self.x = args[0]
            self.y = args[1]

    def draw(self, screen, *args):
        if args:
            self.rect.center = (args[0] - self.x + 640, args[1] - self.y + 360)
        self.name.update(self.rect.center, screen)
        if self.orient == "Right":
            screen.blit(self.image, self.rect)
        elif self.orient == "Left":
            screen.blit(pygame.transform.flip(self.image, True, False), self.rect)

class Bot(pygame.sprite.Sprite):
    def __init__(self, idd, colors, names, ticks):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/crew/" + random.choice(colors) + ".png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (74, 99))
        self.rect = self.image.get_rect()
        self.rect.center = (640, 360)
        self.moves = ast.literal_eval(open("moves\\file" + str(idd) + ".txt", "r").read())
        self.future_name = random.randint(0, len(names) - 1)
        self.my_name = names[self.future_name]
        self.name = Name(self.my_name)
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

def ping_pong(do_ping_pong):
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
    return new_x, new_y

def main(player_name, player_color, is_multiplayer, d):
    v = "v2.2.0"
    loading = False

    logging.info("Loading pygame...")
    
    pygame.init()
    pygame.font.init()

    logging.info("Loading variables...")
    client, walls_mask, hitbox_mask, kill_btn = 0, 0, 0, 0
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
    ping = -100
    kill_save = -120
    orient = "Left"
    names = ["Xiaoness191", "Milenakos", "SOKE®", "RubiK", "=/", "^ Frinkifail ^", "m(._.)m",
             "Andrew Meep", "atomicgrape908", "suffix.", "CatRBLX", "Deltaonetrooper", "drealy", "Drewskibob",
             "Euro2555", "nclazrfpyt", "finched also poppi alpha", "FloppityLopp", "GentleToonMan", "GentleToonMan",
             "J'zargo", "lucyy", "m(._.)mV2", "Mr. snowmanfan20_YT", "normal", "exotic", "Stoned", "Allleeeeeccccccc",
             "ThisIsMyUsername", "tiddcunt", "Vana_Ungkap", "WarNoodleZ", "Wut", "Yuuta Togashi", "Zatrex", "FedeGamer", "hezigonic"]
    colors = ["Red", "Blue", "Green", "Pink", "Orange", "Yellow", "Black", "White", "Purple", "Brown", "Cyan", "Lime", "Maroon", "Rose", "Banana", "Gray",
              "Tan", "Coral", "Olive", "Fortegreen"]
    moves = []
    bots = []
    players = []

    logging.info("Creating game window...")
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Among Ys Rewrite")
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()

    running = True

    logging.info("Rendering first frame...")
    font = pygame.font.Font("arlrdbd.ttf", 30)
    loading = font.render("Loading images...", 1, (255, 255, 255))

    screen.fill((0, 0, 0))
    
    screen.blit(loading, (0, 680))
    
    all_sprites.update(x, y, screen, orient)
    pygame.display.flip()

    while running:
        clock.tick(FPS)
        ticks += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Got exit signal.")
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not is_multiplayer:
                if event.button == 1 and kill_btn.collidepoint(event.pos):
                    logging.info("Got mouse press signal.")
                    do_kill = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and not is_multiplayer:
                    logging.info("Got Q press signal.")
                    do_kill = True

        if ticks != 1:
            if do_kill and kill_possible and not is_multiplayer:
                logging.info("Killing...")
                dists = []
                for i in bots:
                    dists.append(i.distance_from_center())
                if min(dists) <= 270 and ticks - kill_save > 120:
                    enemy_ind = dists.index(min(dists))
                    enemy = bots[enemy_ind]
                    x, y = enemy.get_coords()
                    logging.info("Bot %s was killed, with name %s.", enemy_ind, enemy.my_name)
                    bots.pop(enemy_ind)
                    kill_save = ticks
                    logging.info("%s people left, rendering counter.", str(len(bots) + 1))
                    textSurf = font.render("People left: " + str(len(bots) + 1), 1, (255, 255, 255))
                    image = pygame.Surface((1280, 720))
                    image.blit(textSurf, [0, 0])
                    image.set_colorkey((0,0,0))
                else:
                    logging.info("No bots in kill distance or kill cooldown is active.")
                do_kill = False
                if len(bots) == 0:
                    logging.info("All bots killed.")
                    kill_possible = False

            keys = pygame.key.get_pressed()

            x_save, y_save = x, y
               
            new_x = new_y = 0

            if do_ping_pong:
                new_x, new_y = ping_pong(do_ping_pong)
            else:
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    new_x += change
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    new_x -= change

                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    new_y += change
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    new_y -= change

            if keys[pygame.K_p] and ticks - ping > 100 and not is_multiplayer:
                logging.info("Ping pong state was %s, now vice-versa.", str(do_ping_pong))
                ping = ticks
                if do_ping_pong:
                    do_ping_pong = False
                else:
                    do_ping_pong = True

            if new_x > 0:
                orient = "Left"
            elif new_x < 0:
                orient = "Right"

            x += new_x
            y += new_y
            
            if ticks > 4 and is_multiplayer:
                info = client.get()
                if info != None:
                    print(info)
                    if isinstance(info, list) and info[0] != player_name and info[4] != player_color:
                        found = False
                        for j in players:
                            if info[0] == j.nickname and info[4] == j.color:
                                j.update(info[3], info[1], info[2])
                                found = True
                                break
                        if not found:
                            new = Crew(info[4], info[0])
                            players.append(new)
                            new.update(info[3], info[1], info[2])
                client.write([player_name, x, y, orient, player_color])

            if do_write and not is_multiplayer:
                moves.append([x, y, orient])

            if walls_mask.overlap(hitbox_mask, (-x, -y)):
                x, y = x_save, y_save
                if do_ping_pong:
                    old_super = do_ping_pong
                    while do_ping_pong == old_super:
                        do_ping_pong = random.randint(1, 8)
                    logging.info("New ping pong direction, %s.", do_ping_pong)

        if ticks == 1:
            logging.info("Loading images...")
            walls = pygame.image.load("img/layout.png")
            walls_mask = pygame.mask.from_surface(walls)

            hitbox = pygame.image.load("img/hitbox.png")
            hitbox_mask = pygame.mask.from_surface(hitbox)

            kill = pygame.image.load("img/kill.png")
            kill_btn = kill.get_rect()
            kill_btn.center = (1200, 640)
            logging.info("Checking for updates...")
            loading = font.render("Checking for updates...", 1, (255, 255, 255))
        if ticks == 2:
            try:
                latest = requests.get("https://api.github.com/repos/milena-kos/Among-Ys-Rewrite/releases/latest").text
                version = json.loads(latest)["name"]
            except Exception as e:
                logging.warning("Failed to check version.")
                version = None
            logging.info("Loading map...")
            loading = font.render("Loading map...", 1, (255, 255, 255))
        elif ticks == 3:
            back = pygame.image.load('img/skeld.png')
            crew = Crew(player_color, player_name)
            if is_multiplayer:
                logging.info("Connecting to server...")
                loading = font.render("Connecting to server...", 1, (255, 255, 255))
            else:
                logging.info("Loading bots...")
                loading = font.render("Loading bots...", 1, (255, 255, 255))
        elif ticks == 4 and not is_multiplayer:
            if not do_write:
                for i in range(0, len(os.listdir(".\\moves"))):
                    bot = Bot(i, colors, names, ticks)
                    bots.append(bot)
            logging.info("Loading text...")
            loading = font.render("Loading text...", 1, (255, 255, 255))
        elif ticks == 4:
            HOST, PORT = is_multiplayer.split(":")

            client = Client(HOST, int(PORT))
        elif ticks == 5 and not is_multiplayer:
            logging.info("Rendering counter...")
            font1 = pygame.font.Font("arlrdbd.ttf", 35)
            textSurf = font1.render("People left: " + str(len(bots) + 1), 1, (255, 255, 255))
            image = pygame.Surface((1280, 720))
            image.blit(textSurf, [0, 0])
            image.set_colorkey((0,0,0))
        if ticks == 5:
            log_text = ""
            if d == True:
                log_text += "Failed to start logging.\n"
            elif version and version != v and getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                logging.warning("Using old version of Among Ys Rewrite.")
                log_text += "New version of Among Ys Rewrite is available. Please upgrade your game."
            loading = font.render(log_text, 1, (255, 255, 255))

        screen.fill((0, 0, 0))
        
        if ticks > 4:
            screen.blit(back, (x, y))
            for i in bots:
                i.update(x, y, screen, orient)
            for i in players:
                i.draw(screen, x, y)
            if not is_multiplayer:
                screen.blit(image, (0, 0))
                if kill_possible:
                    screen.blit(kill, kill_btn)
            crew.update(orient)
            crew.draw(screen)
            walls.get_rect().center = (x, y)
        if loading:
            screen.blit(loading, (0, 680))
        
        all_sprites.update(x, y, screen, orient)
        pygame.display.flip()

    if do_write:
        file = open("moves\\file.txt", "w")
        file.write(str(moves))
        file.close()

    logging.info("Quitting pygame...")
    pygame.quit()
    if is_multiplayer:
        client.close()

def character_limit(entry_text):
    if len(entry_text.get()) > 15:
        logging.info("Over 15 characters, limiting...")
        entry_text.set(entry_text.get()[:15])

def settings():
    master = tk.Tk()
    master.title("Settings")
    logging.info('Loaded! Adding buttons...')
    tk.Label(master, text="Among Ys Settings").grid(row=0)
    tk.Label(master, text="Your name").grid(row=1, column=0)
    tk.Label(master, text="Your color").grid(row=2, column=0)
    tk.Label(master, text="Multiplayer IP").grid(row=3, column=0)
    variable = tk.StringVar(master)
    variable.set("Red")
    entry_text = tk.StringVar()
    ip = tk.StringVar()
    mp = tk.IntVar()
    e1 = tk.Entry(master, textvariable = entry_text)
    e2 = tk.OptionMenu(master, variable, "Red", "Blue", "Green", "Pink", "Orange", "Yellow", "Black", "White", "Purple", "Brown", "Cyan", "Lime", "Maroon", "Rose", "Banana", "Gray",
              "Tan", "Coral", "Olive", "Fortegreen")
    e3 = tk.Entry(master, textvariable = ip)
    e1.grid(row=1, column=1)
    e2.grid(row=2, column=1)
    e3.grid(row=3, column=1)    
    tk.Button(master, 
          text='Start',
          width=15,
          command=master.quit).grid(row=4, column=1)
    tk.Button(master, 
          text='Quit',
          width=15,
          command=master.destroy).grid(row=4, column=0)
    logging.info('Done! Waiting for input...')
    entry_text.trace("w", lambda *args: character_limit(entry_text))
    tk.mainloop()
    logging.info('Got input! Closing settings...')
    return master, entry_text.get(), variable.get(), ip.get()

if __name__ == "__main__":
    d = False
    try:
        os.remove("log.txt")
        logging.basicConfig(filename='log.txt', level=logging.INFO)
    except FileNotFoundError:
        logging.basicConfig(filename='log.txt', level=logging.INFO)
        logging.warning('Failed to delete log file!')
    except PermissionError:
        d = True
    try:
        logging.info('Loading settings window...')
        master, a, b, c = settings()
        logging.info('Destorying window...')
        master.destroy()
        logging.info('Starting game...')
        main(a, b, c, d)
    except Exception as e:
        logging.warning('Got error! Analysing...')
        if e == "can't invoke \"destroy\" command: application has been destroyed":
            logging.info("Aplication exit by user, no errors.")
        else:
            logging.fatal(e)
            pygame.quit()