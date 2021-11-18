# License for this file:
#
#    Among Ys Rewrite
#    Copyright (C) 2021  Milenakos
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import random, math, os, pygame, requests, sys, logging, socket, threading, json, ast, traceback
import tkinter as tk

def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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
    def __init__(self, name, is_sus):
        if is_sus:
            color = 0
        else:
            color = 255
        self.name = name
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(get_path("arlrdbd.ttf"), 35)
        self.textSurf = self.font.render(name, 5, (255, color, color))
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
        self.image = pygame.image.load(get_path("img/crew/" + colors + ".png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (74, 99))
        self.rect = self.image.get_rect()
        self.rect.center = (640, 360)
        self.x = 640
        self.y = 360

        self.color = colors
        self.nickname = name
        self.name = Name(name, True)

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
        self.image = pygame.image.load(get_path("img/crew/" + random.choice(colors) + ".png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (74, 99))
        self.rect = self.image.get_rect()
        self.rect.center = (640, 360)
        self.moves = ast.literal_eval(open(get_path("moves\\file" + str(idd) + ".txt"), "r").read())
        self.my_name = random.choice(names)
        self.name = Name(self.my_name, False)
        names.remove(self.my_name)
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

def ping_pong(do_ping_pong, new_x, new_y, change):
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
    v = "v2.3.0"

    logging.info("Loading pygame...")
    
    pygame.init()
    pygame.font.init()

    logging.info("Loading variables...")
    
    client, walls_mask, hitbox_mask, chat_opened, kill_btn, counter, back, crew, message_done, message_text, log_text = 0, 0, 0, 0, 0, 0, 0, 0, "", "", "" # to fix "Referenced before assigment" errors
    
    do_kill, do_write, do_ping_pong, kill_possible, running, loading = False, False, False, True, True, False
    
    ticks, FPS, x, y, change, old_super, kill_save = 0, 120, -2800, -450, 12, -1, -120
    
    orient = "Left"
    
    names = ["Xiaoness191", "Milenakos", "SOKE®", "RubiK", "=/", "^ Frinkifail ^", "m(._.)m", "hezigonic",
             "Andrew Meep", "atomicgrape908", "suffix.", "CatRBLX", "Deltaonetrooper", "drealy", "Drewskibob",
             "Euro2555", "nclazrfpyt", "finched also poppi alpha", "FloppityLopp", "GentleToonMan", "GentleToonMan",
             "J'zargo", "lucyy", "m(._.)mV2", "Mr. snowmanfan20_YT", "normal", "exotic", "Stoned", "Allleeeeeccccccc",
             "ThisIsMyUsername", "tiddcunt", "Vana_Ungkap", "WarNoodleZ", "Wut", "Yuuta Togashi", "Zatrex", "FedeGamer"]
    
    colors = ["Red", "Blue", "Green", "Pink", "Orange", "Yellow", "Black", "White", "Purple", "Brown", "Cyan", "Lime",
             "Maroon", "Rose", "Banana", "Gray", "Tan", "Coral", "Olive", "Fortegreen"]
    
    moves, bots, players, loading2 = [], [], [], []

    logging.info("Creating game window...")
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Among Ys Rewrite")
    clock = pygame.time.Clock()

    logging.info("Rendering first frame...")
    font = pygame.font.Font(get_path("arlrdbd.ttf"), 30)
    font1 = pygame.font.Font(get_path("arlrdbd.ttf"), 35)
    loading = font.render("Loading images...", 5, (255, 255, 255))

    screen.fill((0, 0, 0))
    
    screen.blit(loading, (5, 680))
    
    pygame.display.flip()

    while running:
        clock.tick(FPS)
        ticks += 1
        
        do_kill, running, message_text, message_done, do_ping_pong, chat_opened = check_for_input(is_multiplayer, kill_btn, running, chat_opened, message_text, message_done, do_ping_pong)

        if ticks != 1:
            if do_kill and kill_possible and not is_multiplayer:
                x, y, kill_possible, counter = kill_bot(bots, ticks, kill_save, font, kill_possible, x, y, counter)

            do_ping_pong, orient, x, y, message_done, log_text = move_player(do_ping_pong, change, ticks, is_multiplayer, orient, x, y, client, player_name, player_color, players, do_write, moves, walls_mask, hitbox_mask, chat_opened, message_done, log_text)

        if ticks == 1:
            logging.info("Loading images...")
            walls = pygame.image.load(get_path("img/layout.png"))
            walls_mask = pygame.mask.from_surface(walls)

            hitbox = pygame.image.load(get_path("img/hitbox.png"))
            hitbox_mask = pygame.mask.from_surface(hitbox)

            kill = pygame.image.load(get_path("img/kill.png"))
            kill_btn = kill.get_rect()
            kill_btn.center = (1200, 640)
            logging.info("Checking for updates...")
            loading = [font.render("Checking for updates...", 5, (255, 255, 255))]
        elif ticks == 2:
            try:
                latest = requests.get("https://api.github.com/repos/milena-kos/Among-Ys-Rewrite/releases/latest").text
                version = json.loads(latest)["name"]
            except Exception as e:
                logging.warning("Failed to check version.")
                version = None
            logging.info("Loading map...")
            loading = [font.render("Loading map...", 5, (255, 255, 255))]
        elif ticks == 3:
            back = pygame.image.load(get_path('img/skeld.png'))
            crew = Crew(player_color, player_name)
            if is_multiplayer:
                logging.info("Connecting to server...")
                loading = [font.render("Connecting to server...", 5, (255, 255, 255))]
            else:
                logging.info("Loading bots...")
                loading = [font.render("Loading bots...", 5, (255, 255, 255))]
        elif ticks == 4 and not is_multiplayer:
            if not do_write:
                for i in range(0, len(os.listdir(get_path("moves")))):
                    bot = Bot(i, colors, names, ticks)
                    bots.append(bot)
            logging.info("Loading text...")
            loading = [font.render("Loading text...", 5, (255, 255, 255))]
        elif ticks == 4:
            HOST, PORT = is_multiplayer.split(":")

            client = Client(HOST, int(PORT))
            logging.info("Loading text...")
            loading = [font.render("Loading text...", 5, (255, 255, 255))]
        elif ticks == 5 and not is_multiplayer:
            logging.info("Rendering counter...")
            textSurf = font1.render("People left: " + str(len(bots) + 1), 5, (255, 255, 255))
            counter = pygame.Surface((1280, 720))
            counter.blit(textSurf, [0, 0])
            counter.set_colorkey((0,0,0))
        if ticks == 5:
            log_text = ""
            if d == True:
                log_text += "Failed to start logging.\n"
            elif version and version != v and getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                logging.warning("Using old version of Among Ys Rewrite.")
                log_text += "New version of Among Ys Rewrite is available. Please upgrade your game.\n"
        
        if ticks > 5:
            loading = []
            loading2 = []
            for i in log_text.splitlines()[::-1]:
                loading.append(font.render(i, 5, (255, 255, 255)))
                loading2.append(font.render(i, 5, (0, 0, 0)))

        render_screen(screen, ticks, back, x, y, bots, orient, players, is_multiplayer, counter, kill_possible, kill, kill_btn, crew, walls, loading, loading2, chat_opened, message_text, font)

    if do_write:
        file = open("moves\\file.txt", "w")
        file.write(str(moves))
        file.close()

    if is_multiplayer:
        client.close()

    logging.info("Quitting pygame...")
    pygame.quit()

def render_screen(screen, ticks, back, x, y, bots, orient, players, is_multiplayer, counter, kill_possible, kill, kill_btn, crew, walls, loading, loading2, chat_opened, message_text, font):
    screen.fill((0, 0, 0))
    chat_offset = 0

    if ticks > 4:
        screen.blit(back, (x, y))
        for i in bots:
            i.update(x, y, screen, orient)
        for i in players:
            i.draw(screen, x, y)
        if not is_multiplayer:
            screen.blit(counter, (0, 0))
            if kill_possible:
                screen.blit(kill, kill_btn)
        crew.update(orient)
        crew.draw(screen)
        walls.get_rect().center = (x, y)
    if ticks > 4 and chat_opened:
        pygame.draw.rect(screen, (255,255,255), (10, 660, 500, 50))
        pygame.draw.rect(screen, (0,0,0), (10, 660, 500, 50), 5)
        textSurf = font.render(str(message_text) + "|", 5, (0, 0, 0))
        message = pygame.Surface((1280, 720))
        message.fill((255,255,255))
        message.blit(textSurf, [0, 0])
        message.set_colorkey((255,255,255))
        screen.blit(message, (20, 660))
        chat_offset += 70
    if loading:
        for num, i in enumerate(loading2):
            x = 5
            y = 680 - chat_offset - (num * 35)
            screen.blit(i, (x + 2, y + 2))
            screen.blit(i, (x + 2, y - 2))
            screen.blit(i, (x - 2, y + 2))
            screen.blit(i, (x - 2, y - 2))
            screen.blit(i, (x, y + 2))
            screen.blit(i, (x, y - 2))
            screen.blit(i, (x - 2, y))
            screen.blit(i, (x + 2, y))
        for num, i in enumerate(loading):
            screen.blit(i, (5, 680 - chat_offset - (num * 35)))

    pygame.display.flip()

def move_player(do_ping_pong, change, ticks, is_multiplayer, orient, x, y, client, player_name, player_color, players, do_write, moves, walls_mask, hitbox_mask, chat_opened, message_done, log_text):
    do_ping_pong, new_x, new_y, orient = do_movement(do_ping_pong, change, ticks, is_multiplayer, orient, chat_opened)

    x_save, y_save = x, y

    x += new_x
    y += new_y

    if ticks > 4 and is_multiplayer:
        message_done, log_text = update_multiplayer(client, player_name, player_color, players, x, y, orient, message_done, log_text)

    if do_write and not is_multiplayer:
        moves.append([x, y, orient])

    x, y, do_ping_pong = collision_check(walls_mask, hitbox_mask, x, y, x_save, y_save, do_ping_pong)
    return do_ping_pong, orient, x, y, message_done, log_text

def update_multiplayer(client, player_name, player_color, players, x, y, orient, message_done, log_text):
    info = client.get()
    if info != None:
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
            if info[5] != "":
                line = info[0] + ": " + info[5] + "\n"
                log_text += line
    client.write([player_name, x, y, orient, player_color, message_done])
    if message_done != "":
        line = player_name + ": " + message_done + "\n"
        log_text += line
    return "", log_text

def collision_check(walls_mask, hitbox_mask, x, y, x_save, y_save, do_ping_pong):
    if walls_mask.overlap(hitbox_mask, (-x, -y)):
        x, y = x_save, y_save
        if do_ping_pong:
            old_super = do_ping_pong
            while do_ping_pong == old_super:
                do_ping_pong = random.randint(1, 8)
            logging.info("New ping pong direction, %s.", do_ping_pong)
    return x, y, do_ping_pong

def do_movement(do_ping_pong, change, ticks, is_multiplayer, orient, chat_opened):
    keys = pygame.key.get_pressed()

    new_x = new_y = 0

    new_x, new_y = calcluate_coordinates_change(do_ping_pong, keys, change, new_x, new_y, chat_opened)

    if new_x > 0:
        orient = "Left"
    elif new_x < 0:
        orient = "Right"
    return do_ping_pong, new_x, new_y, orient

def calcluate_coordinates_change(do_ping_pong, keys, change, new_x, new_y, chat_opened):
    if do_ping_pong:
        new_x, new_y = ping_pong(do_ping_pong, new_x, new_y, change)
    elif not chat_opened:
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_x += change
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_x -= change

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_y += change
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_y -= change
    return new_x, new_y

def check_for_input(is_multiplayer, kill_btn, running, chat_opened, message_text, message_done, do_ping_pong):
    do_kill = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            logging.info("Got exit signal.")
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not is_multiplayer:
            if event.button == 1 and kill_btn.collidepoint(event.pos) and not chat_opened:
                logging.info("Got mouse press signal.")
                do_kill = True
        elif event.type == pygame.KEYDOWN:
            do_ping_pong, message_text, chat_opened, do_kill, message_done = keydown_functions(event, is_multiplayer, chat_opened, do_ping_pong, message_text, do_kill, message_done)
    return do_kill, running, message_text, message_done, do_ping_pong, chat_opened

def keydown_functions(event, is_multiplayer, chat_opened, do_ping_pong, message_text, do_kill, message_done):
    if event.key == pygame.K_q and not is_multiplayer:
        if not chat_opened:
            logging.info("Got Q press signal.")
            do_kill = True
    if event.key == pygame.K_p and not is_multiplayer and not chat_opened:
        logging.info("Ping pong state was %s, now vice-versa.", str(do_ping_pong))
        if do_ping_pong:
            do_ping_pong = False
        else:
            do_ping_pong = True
    if chat_opened:
        if event.key == pygame.K_RETURN:
            logging.info(f"{message_text} was sent by me!")
            message_done = message_text
            message_text = ''
        elif event.key == pygame.K_BACKSPACE:
            message_text = message_text[:-1]
        else:
            message_text = str(message_text) + event.unicode
    if event.key == pygame.K_RETURN and is_multiplayer:
        if chat_opened:
            chat_opened = False
        else:
            chat_opened = True
    return do_ping_pong, message_text, chat_opened, do_kill, message_done

def kill_bot(bots, ticks, kill_save, font, kill_possible, x, y, counter):
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
        textSurf = font.render("People left: " + str(len(bots) + 1), 5, (255, 255, 255))
        counter = pygame.Surface((1280, 720))
        counter.blit(textSurf, [0, 0])
        counter.set_colorkey((0,0,0))
    else:
        logging.info("No bots in kill distance or kill cooldown is active.")
    do_kill = False
    if len(bots) == 0:
        logging.info("All bots killed.")
        kill_possible = False
    return x, y, kill_possible, counter

def character_limit(nickname):
    if len(nickname.get()) > 15:
        logging.info("Over 15 characters, limiting...")
        nickname.set(nickname.get()[:15])

def settings():
    if not os.path.exists(os.getenv('LOCALAPPDATA') + "\\Milenakos\\AmongYsRewrite"):
        os.makedirs(os.getenv('LOCALAPPDATA') + "\\Milenakos\\AmongYsRewrite")
    try:
        pref = json.load(open(os.getenv('LOCALAPPDATA') + "\\Milenakos\\AmongYsRewrite\\settings.json", "r"))
    except Exception:
        logging.warning('Failed to load settings.json!')
        pref = False


    master = tk.Tk()
    master.title("Settings")
    logging.info('Loaded! Adding buttons...')
    tk.Label(master, text="Among Ys Settings").grid(row=0)
    tk.Label(master, text="Your name").grid(row=1, column=0)
    tk.Label(master, text="Your color").grid(row=2, column=0)
    tk.Label(master, text="Multiplayer IP").grid(row=3, column=0)
    
    color = tk.StringVar()
    nickname = tk.StringVar()
    ip = tk.StringVar()

    color.set("Red")
    if pref:
        ip.set(pref["ip"])
        nickname.set(pref["nickname"])
        color.set(pref["color"])

    e1 = tk.Entry(master, textvariable = nickname)
    e2 = tk.OptionMenu(master, color, "Red", "Blue", "Green", "Pink", "Orange", "Yellow", "Black", "White", "Purple", "Brown", "Cyan", "Lime", "Maroon", "Rose", "Banana", "Gray",
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
    nickname.trace("w", lambda *args: character_limit(nickname))
    tk.mainloop()
    logging.info('Got input! Closing settings...')

    try:
        json.dump({"ip": ip.get(), "nickname": nickname.get(), "color": color.get()}, open(os.getenv('LOCALAPPDATA') + "\\Milenakos\\AmongYsRewrite\\settings.json", "w"))
    except Exception:
       logging.warning('Failed to save settings.json!')

    return master, nickname.get(), color.get(), ip.get()

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
        if c == "l":
            c = "127.0.0.1:9090"
        main(a, b, c, d)
    except Exception as e:
        logging.warning('Got error! Analysing...')
        if e == "can't invoke \"destroy\" command: application has been destroyed":
            logging.info("Aplication exit by user, no errors.")
        else:
            logging.fatal(str(traceback.format_exc()))
            pygame.quit()