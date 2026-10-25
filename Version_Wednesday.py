import pygame
import math
import sys
import random

from pygame import K_SPACE


pygame.init()
width = 1920
height = 1080
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Godslayer")
pygame.font.init()

clock = pygame.time.Clock()

Helvetica = pygame.font.SysFont("Times New Roman",20)
Flask_Font = pygame.font.SysFont("Times New Roman",30,True)

def flask_display(amount,img,font,dest): #amount= healpot amount, img = images of flask list, font = font, dest = place where shown
    #choosing which image based on the number of flasks
    if amount > 5:
        screen.blit(img[0],dest)
    elif amount == 0:
        screen.blit(img[2],dest)
    elif amount <= 5:
        screen.blit(img[1],dest)
    #displaying the number of flasks
    text= font.render(str(amount),True,(255,255,255))
    screen.blit(text,dest)

def bg_floor(bossnr,bg,floor,rect):
    screen.blit(bg[bossnr-1],(0,0))
    screen.blit(floor[bossnr-1],(0,rect))

def player_animation(p,lr,imgs,pos):
    #finding correct animation frame
    if p == 9: #9 is the walking animation list
        walkp = frame_counter % 3
        if lr == "right":
            shownimg = pygame.transform.flip(imgs[p][walkp], True, False)
        else:
            shownimg = imgs[p][walkp]
    if lr == "right" and not p== 9:
        shownimg = pygame.transform.flip(imgs[p],True,False)
    elif not p == 9:
        shownimg = imgs[p]

    #shownig the player
    screen.blit(shownimg,pos)



#game state
game_status = "title_screen"

# enviroment
pygame.mixer.music.set_volume(0.2)

loading_time = 0
do_healing = False
healing = False
attacking_frame = False
gravity = 1
jump_height = height/54
screen_rect = screen.get_rect()
double_jump = False
double_jumping = False
attacking = False
attacking_time = 0
frame_counter = 0
damage_delay = 10
boss_number = 1
frame = 0
arrow_amount = int(width/77)
healing_frames = 0
spearspaces = 100 * 1.5
Music_playing = False
deadtime = 0
wintime = 0

#floor definition
height_floor = height-height/10.8

#stagel sis zügs
spearspaces_unten = random.randint(int(height * 0.4), int(height_floor - 50))
spearspaces_oben = spearspaces_unten - spearspaces

floor_rect = pygame.Rect(0,height_floor, width, height/10.8 + 20)
#schaden objekt
class Damage:
    def __init__(self):
        self.width = 30
        self.height = 80
        self.x = 0
        self.y = 0
        self.dealt_damage = 10
        self.rect = pygame.Rect(500,height_floor-self.height,self.width,self.height)
        self.already_damaged = False
        self.attacking_time = 0
#floor damage definition
floor_damage = Damage()
floor_damage.dealt_damage = 50
floor_damage.x = 11000
floor_damage.y = 10000
floor_damage.rect = pygame.Rect(floor_damage.x,floor_damage.y,floor_damage.width,height_floor)


#air arrows definition
air_arrow = Damage()
air_arrow.dealt_damage = 30
air_arrows_list = []

flying_spears = Damage()
flying_spears.dealt_damage = 40
tridents = Damage()
wave_spawn = Damage()
flying_spears_list = []
waves_list = []
tridents_list = []

#Wave
Poseidon_Wave = Damage()
Poseidon_Wave.width = width/9.6
Poseidon_Wave.height = height/3 - 10
Poseidon_Wave.rect =   (Poseidon_Wave.x,Poseidon_Wave.y,Poseidon_Wave.width,Poseidon_Wave.height)

#Waterfall
Waterfall = Damage()
Waterfall.width, Waterfall.height = width/ 5, height
Waterfall.rect = pygame.Rect(Waterfall.x,Waterfall.y,Waterfall.width,Waterfall.height)
Waterfall.dealt_damage = 80


#Ares Attacks
#Rage attack
ares_rage_1 = Damage()
ares_rage_1.width, ares_rage_1.height = width/4.5, width/4.5
ares_rage_1.dealt_damage = 40
ares_rage_1.rect = pygame.Rect(5000,0,ares_rage_1.width,ares_rage_1.height)

ares_rage_2 = Damage()
ares_rage_2.width, ares_rage_2.height = width/3, width/3
ares_rage_2.rect = pygame.Rect(5000,0,ares_rage_2.width,ares_rage_2.height)
ares_rage_2.dealt_damage = 60

#Dagger throw
dagger = Damage()
dagger_list = []


#bossklasse
class Boss:
    def __init__(self, name):
        self.width = width/9.6
        self.height = height/3
        self.y = height_floor-self.height
        self.x = width/2 - self.width/2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.health_max = 1000
        self.health = self.health_max
        self.combat_timer = 0
        self.attack_type = 1
        self.attacking = False
        self.attacking_time = 0
        self.attacking_site = "left"
        self.name = Helvetica.render(name,True,(255,255,255))
        self.animation_state = "Temporary"

athena = Boss("Athena, Goddess of Wisdom")

Poseidon = Boss("Poseidon, Lord of the Seven Seas")
Poseidon.x = width - (Poseidon.width + 10)

Ares = Boss("Ares, God of War")
Ares.width, Ares.height = width/6 * 0.85, width/6
Ares.rect = pygame.Rect(Ares.x, Ares.y, Ares.width, Ares.height)
Ares.y = height_floor - Ares.height

#player definition

class player:
    def __init__(self):
        self.x = 300
        self.y = height_floor-height/10.8
        self.height = height/10.8
        self.width = width/38.4
        self.velocity_x = width/274
        self.velocity_y = jump_height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.jumping = False
        self.falling = False
        self.crouched = False
        self.hit = False
        self.hit_timer = 10
        self.attack_direction = "left"
        self.health = 100
        self.health_max = 100
        self.alive = True
        self.animation = "temporary"
        self.moving = False
        self.healpot_amount = 10
        self.already_damaged = False

player = player()

#angriff klasse
class attack:
    def __init__(self):
        self.width = width/24
        self.height = height/13.5
        #angriff oben unten
        self.y_left_right = player.y + height/108
        self.y_up = player.y - self.height
        self.y_down = player.y + player.height
        #angriff links rechts
        self.x_right = player.x + player.width
        self.x_left = player.x - self.width
        self.x_up_down = player.x - (self.width - player.width)/2
        self.did_attack = False
        self.damage = 200
        self.rect = pygame.Rect(self.x_right,self.y_left_right,player.width,player.height)
light_attack = attack()



#healthbar
health_bar_background = pygame.Rect(width/96,height/54,width/3.76,height/27)
health_bar = pygame.Rect(width/76.8,height/43.2,player.health*((width/376-width/192)/100),height/36)

boss_bar_background = pygame.Rect(width/3 - 5,height_floor - height/192+10,width/3 + 10, 40)
boss_bar = pygame.Rect(width/3 ,height_floor - height/192 + 10,athena.health * 0.64, 30)

#Sounds
getting_hit_Sound = pygame.mixer.Sound("./Game_Main/Music and Sounds/normal.mp3")
pygame.mixer.Sound.set_volume(getting_hit_Sound,0.4)
hitting_sound = pygame.mixer.Sound("./Game_Main/Music and Sounds/crit.mp3")
pygame.mixer.Sound.set_volume(hitting_sound,0.4)
button_clicked_sound = pygame.mixer.Sound("./Game_Main/Music and Sounds/click_reverb.mp3")
pygame.mixer.Sound.set_volume(button_clicked_sound,0.4)



#Graphics
if True:
    #UI and background
    Game_Over = pygame.image.load("./Game_Main/UI/Game_Over.png")
    Game_Over = pygame.transform.scale(Game_Over,(width/2,Game_Over.get_height()/Game_Over.get_width()*width/2))
    Victory = pygame.transform.scale (pygame.image.load("./Game_Main/UI/Victory.png"),(width/2,Game_Over.get_height()/Game_Over.get_width()*width/2))
    Spacebar = pygame.image.load("./Game_Main/UI/Spacebar.png")
    Spacebar = pygame.transform.scale(Spacebar,(width / 4, Spacebar.get_height() / Spacebar.get_width() * width / 4))
    Thanks_Credit = pygame.image.load("./Game_Main/UI/Thank_You.png")
    Thanks_Credit = pygame.transform.scale(Thanks_Credit,(width/2* 1.5, Thanks_Credit.get_height() / Thanks_Credit.get_width() * width / 2 * 1.5))
    Names_Credit = pygame.image.load("./Game_Main/UI/Credits.png")
    Names_Credit = pygame.transform.scale(Names_Credit, (width / 2, Names_Credit.get_height() / Names_Credit.get_width() * width / 2))

    Flask_Assets = [
    pygame.transform.scale(pygame.image.load("./Game_Main/UI/Healing_Flask_Full.png"),(75,75)),
    pygame.transform.scale(pygame.image.load("./Game_Main/UI/Healing_Flask_Half.png"),(75,75)),
    pygame.transform.scale(pygame.image.load("./Game_Main/UI/Healing_Flask_empty.png"),(75,75))
    ]
    #Projectiles
    Gold_Arrow = pygame.transform.scale(pygame.image.load("./Game_Main/Projectiles/Gold Spear.png"),(air_arrow.width+20,air_arrow.height+20))
    Ground_Explosion = pygame.transform.scale(pygame.image.load("./Game_Main/Projectiles/Ground_Explosion.png"),(width, height/5 + 30))
    Ares_Daggers = pygame.transform.scale(pygame.image.load("./Game_Main/Projectiles/Dagger.png"),(30,50))
    Ares_Explosion_1 = pygame.transform.scale(pygame.image.load("./Game_Main/Projectiles/Explosion_1.png"),(width/4.5,width/4.5))
    Ares_Explosion_2 = pygame.transform.scale(pygame.image.load("./Game_Main/Projectiles/Explosion_2.png"),(width / 3, width / 3))
    Flying_Fish = pygame.transform.scale(pygame.image.load("./Game_Main/Projectiles/Fih_2.png"),(100,50))
    Wave = pygame.transform.scale(pygame.image.load("./Game_Main/Projectiles/Wave.png"),(Poseidon_Wave.width,Poseidon_Wave.height))
    Waterfall_image = pygame.transform.scale(pygame.image.load("Game_Main/Projectiles/Waterfall_2.png"), (player.width * 2, height))
    Waterfall_Warn = pygame.transform.scale(pygame.image.load("./Game_Main/Projectiles/Waterfall_Warn.png"),(player.width * 2, height))


    #Player
    Basic_Attack = pygame.transform.scale(pygame.transform.flip(pygame.image.load("./Game_Main/Player/Basic_Attack.png"),True,False),(light_attack.width,light_attack.height)) #possibly scale again
    Player_Assets= [
    pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Jump.png"),(player.width,player.height)),
    pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Attack.png"),(player.width,player.height)), #1 Player_Attack
    pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Dead.png"),(player.width,player.height)), #2 Player_Dead
    pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Heal_1.png"),(player.width,player.height)), #3 Player_Heal_1
    pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Heal_2.png"),(player.width,player.height)), #4 Player_Heal_2
    pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Hit.png"),(player.width,player.height)), #5 Player_Hit
    pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Idle.png"),(player.width,player.height)), #6 Player_Idle
    pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Rejump.png"),(player.width,player.height)), #7 Player_Rejump
    pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Victory.png"),(player.width,player.height)), #8 Player_Victory
    [pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Jump.png"),(player.width,player.height)), #9 List [running animations]
    pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Run_Mid.png"),(player.width,player.height)),
    pygame.transform.scale(pygame.image.load("./Game_Main/Player/Player_Run_Back.png"),(player.width,player.height))]
    ]
    #Athena
    Athena_Assets=[
    pygame.transform.scale(pygame.image.load("./Game_main/Athena/Athena_Idle.png"),(athena.width +20, athena.height + 20)),
    pygame.transform.scale(pygame.image.load("./Game_main/Athena/Athena_Summon.png"), (athena.width +20, athena.height + 20)),
    pygame.transform.scale(pygame.image.load("./Game_main/Athena/Athena_Airborne.png"), (athena.width +20, athena.height + 20)),
    pygame.transform.scale(pygame.image.load("./Game_main/Athena/Athena_Landing.png"), (athena.width*4/3 +20, athena.height +20)),
    pygame.transform.scale(pygame.image.load("./Game_main/Athena/Athena_Dash.png"),(athena.width + 20, athena.height + 20)),
    pygame.transform.flip(pygame.transform.scale(pygame.image.load("./Game_main/Athena/Athena_Dash.png"),(athena.width + 20, athena.height + 20)),True,False)
    ]

    #Poseidon
    Poseidon_Assets=[
    pygame.transform.scale(pygame.image.load("./Game_main/Poseidon/Poseidon_Idle.png"),(Poseidon.width+20,Poseidon.height + 20)),
    pygame.transform.scale(pygame.image.load("./Game_main/Poseidon/Poseidon_Summon_V1.png"),(Poseidon.width + 20, Poseidon.height + 20)),
    pygame.transform.scale(pygame.image.load("./Game_main/Poseidon/Poseidon_Summon_V2.png"),(Poseidon.width + 20, Poseidon.height + 20))
    ]

    Ares_Assets =[
    pygame.transform.scale(pygame.image.load("./Game_Main/Ares/Ares_Idle.png"),(Ares.width *1.2 ,Ares.height*1.2)),
    pygame.transform.scale(pygame.image.load("./Game_Main/Ares/Ares_Rage.png"), (Ares.width *1.2 ,Ares.height*1.2)),
    pygame.transform.scale(pygame.image.load("./Game_Main/Ares/Ares_Daggers.png"), (Ares.width *1.2 ,Ares.height*1.2)),
    pygame.transform.scale(pygame.image.load("./Game_Main/Ares/Ares_Teleport.png"), (Ares.width *1.2 ,Ares.height*1.2)),
    pygame.transform.scale(pygame.image.load("./Game_Main/Ares/Ares_Teleport_Warn.png"), (Ares.width *1.2 ,Ares.height*1.2))

    ]

    Backgrounds = [
    pygame.transform.scale(pygame.image.load("./Game_Main/Athena/Athena_Background.png"),(width, height)),
    pygame.transform.scale(pygame.image.load("./Game_Main/Poseidon/Poseidon_Background.png"), (width, height)),
    pygame.transform.scale(pygame.image.load("./Game_Main/Ares/Ares_Background.png"), (width, height)),
    ]

    Floors = [
    pygame.transform.scale(pygame.image.load("./Game_Main/Athena/Athena_Floor.png"), (width, height / 5)),
    pygame.transform.scale(pygame.image.load("./Game_Main/Poseidon/Poseidon_Floor.png"), (width, height / 5)),
    pygame.transform.scale(pygame.image.load("./Game_Main/Ares/Ares_Floor.png"), (width, height / 5))
    ]


#title screen definitions
if True:
    Title = "Godslayer"
    #Title Screen state
    Title_state = 1
    #Images
    TitleBG = pygame.image.load("Game_Main/Title_Screen_images/Title_BG.png")
    TitleBG = pygame.transform.scale(TitleBG,(width,height))

    #Fonts
    pygame.font.init() #initializes fonts which allows text to be displayed onscreen
    Titlefont = pygame.font.SysFont("Times new roman",150,True)
    Optionfont = pygame.font.SysFont("Times new roman",60,True)
    Infofont = pygame.font.SysFont("Times new roman",50,)

    #Music
    pygame.mixer.music.load("Game_Main/Title_Screen_images/Title_Theme.mp3")
    Title_Music_len = pygame.mixer.music.get_pos()



    #Text Boxes
    #State 1
    DisplayTitle = Titlefont.render(Title,True,(255,255,255))
    DisplayTitle = pygame.transform.scale(pygame.image.load("./Game_Main/Title_Screen_images/Title_Title_2.png"),(DisplayTitle.get_rect().width*2,DisplayTitle.get_rect().height*2))
    Start_Button = Optionfont.render("Start Game", True, (255, 255, 255))
    Controls_Button = Optionfont.render("Controls", True, (255, 255, 255))
    Boss_Select_Button = Optionfont.render("Quit Game", True, (255, 255, 255))
    #State 2
    Controls_Title = Optionfont.render("Controls",True,(255,255,255))
    Controls_1 = Infofont.render("          A D ← → - move left or right",True,(255,255,255))
    Controls_2 = Infofont.render("A D ← → - attack direction left or right",True,(255,255,255))
    Controls_3 = Infofont.render("Space  - Jump",True,(255,255,255))
    Controls_4 = Infofont.render(" ↑ - Attack",True,(255,255,255))
    Back_Button = Optionfont.render("Back",True,(255,255,255))


    #Mouse
    def cursor():
        pos = pygame.mouse.get_pos() #gets the position of the mouse
        #screen.blit(Cursor,mouse_pos) #activate if mouse is hidden, this line would show cursor
        pos = pygame.Rect(pos+(1,1))
        return pos

    #Debugging stuff
    Back_Button_rect = Back_Button.get_rect() #Defined here to fix it being undefined for 1 frame
    Wait_Bcuz_Else_Buggy = 0

    #bugfixing list because ke bock ka
    Bosses_for_Healthbar = ["Stragel",athena,Poseidon,Ares]

while True:
    while game_status == "alive":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # springen überprüfen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not player.falling and not do_healing:
                    if player.jumping:
                        double_jump= True
                    player.jumping = True
            # angreifen erkennen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and attacking_time <= 0  and not do_healing:
                    attacking = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN and not do_healing and not player.jumping and not player.falling and not attacking:
                    healing = True

        frame_counter += 1

        #draw boss arena
        bg_floor(boss_number,Backgrounds,Floors,floor_rect.y)

        #fallen
        if player.y+player.height < height_floor and player.jumping == False:
            player.falling = True
            player.jumping = False
            player.y += player.velocity_y
            player.velocity_y += gravity
        if player.y+player.height >= height_floor and player.jumping == False:
            player.falling = False
            player.y = height_floor-player.height
            jump_height = height/54
            player.velocity_y = jump_height
            double_jumping = False
            double_jump = False


        #bewegung rechts links
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_a] and not do_healing:
            player.moving = True
            player.x -= player.velocity_x
            player.attack_direction = "left"
            if not screen_rect.contains(player.rect) and player.rect.x < screen_rect.x:
                player.x += player.velocity_x
        if key_pressed[pygame.K_RIGHT] or key_pressed[pygame.K_d] and not do_healing:
            player.moving = True
            player.x += player.velocity_x
            player.attack_direction = "right"
            if not screen_rect.contains(player.rect) and player.rect.x > screen_rect.x:
                player.x -= player.velocity_x


        #springen
        if player.jumping and not player.falling:
            if double_jump and not double_jumping:
                double_jump = False
                double_jumping = True
                player.velocity_y = 0
                player.velocity_y = jump_height

            player.y -= player.velocity_y
            player.velocity_y -= gravity
            if player.velocity_y < -jump_height:
                player.velocity_y = 0
                player.jumping = False
                double_jumping = False
                player.velocity_y = jump_height
                jump_height = height/54


        #angriff vorbereiten
        athena.animation_state = 0
        if attacking:
            attacking_time = 30

            if attacking_time > 15:
                if player.attack_direction == "left":
                    attacking_site = "left"

                if player.attack_direction == "right":
                    attacking_site = "right"
                if player.attack_direction == "up":
                    attacking_site = "up"
                if player.attack_direction == "down":
                    attacking_site = "down"

            attacking = False
        else:
            light_attack.x_left_right = 11000
            light_attack.y_left_right = 11000
            light_attack.rect =  pygame.Rect(light_attack.x_left_right, light_attack.y_left_right, light_attack.width,light_attack.height)
        # angriff durchführen
        if attacking_time <= 15:
            attacking_frame = False
            light_attack.did_attack = False
            attacking = False
        if attacking_time > 15:
            if not light_attack.did_attack:
                attacking_frame = True
        if attacking_time > 15:

            if attacking_site == "left":
                light_attack.x_left = player.x - light_attack.width
                light_attack.y_left_right = player.y + height/108
                light_attack.rect = pygame.Rect(light_attack.x_left, light_attack.y_left_right, light_attack.width,light_attack.height)
            if attacking_site == "right":
                light_attack.y_left_right = player.y + height/108
                light_attack.x_right = player.x + player.width
                light_attack.rect = pygame.Rect(light_attack.x_right, light_attack.y_left_right, light_attack.width,light_attack.height)
            if attacking_site == "up":
                light_attack.y_up = player.y - light_attack.height
                light_attack.x_up_down = player.x - (light_attack.width - player.width)/2
                light_attack.rect = pygame.Rect(light_attack.x_up_down,light_attack.y_up,light_attack.width,light_attack.height)
            if attacking_site == "down":
                light_attack.y_down = player.y + player.height
                light_attack.x_up_down = player.x - (light_attack.width - player.width)/2
                light_attack.rect = pygame.Rect(light_attack.x_up_down,light_attack.y_down,light_attack.width,light_attack.height)
        attacking_time -= 1






        #bossfight
        if boss_number == 1:
            print(athena.health)
            #sieg erkennen
            if athena.health <=0:
                game_status = "victory"
            #player and boss collisiona d
            if athena.rect.colliderect(player.rect) and not player.already_damaged:
                player.health -= 30
                player.hit = True
                player.already_damaged = True
                if athena.attack_type == 2:
                    if athena.health < athena.health_max:
                        athena.health += 50
                        if athena.health > athena.health_max:
                            athena.health = athena.health_max


            if light_attack.rect.colliderect(athena.rect) and attacking_frame:
                pygame.mixer.Sound.play(hitting_sound)
                athena.health -= light_attack.damage
                light_attack.did_attack = True


            boss_bar = pygame.Rect(width / 3, height_floor - height / 192 + 15, athena.health * 0.64, 30)

            #initialize attack
            if athena.attacking == False and frame % 30 == 0 and frame !=0:

                athena.attacking = True
                athena.attack_type = random.randint(1,3)



            if athena.attack_type == 1 and athena.attacking:
                athena.animation_state = 1
                #pfeile definieren
                if athena.attacking_time == 0:
                    displacement = random.randint(5,20)* 3
                    for i in range(arrow_amount):
                        air_arrow.x = displacement + width/19 * i
                        air_arrow.y = 0
                        air_arrow.rect = pygame.Rect(air_arrow.x, air_arrow.y, air_arrow.width, air_arrow.height)
                        air_arrows_list.append(air_arrow.rect)

                #warnen
                elif athena.attacking_time < 10:
                    for i in range (len(air_arrows_list)):

                        pygame.draw.rect(screen, (255, 255, 255), air_arrows_list[i])
                elif athena.attacking_time >= 180:
                    athena.attacking_time = 0
                    athena.attacking = False
                    player.already_damaged = False

                #pfeile fallen
                elif athena.attacking_time >= 10:
                    for i in range (len(air_arrows_list)):
                        air_arrows_list[i].y += 15
                        if air_arrows_list[i].colliderect(player) and not player.already_damaged:
                            player.health -= air_arrow.dealt_damage
                            player.hit = True
                            player.already_damaged = True
                            if athena.health < athena.health_max:
                                athena.health += 30
                                if athena.health > athena.health_max:
                                    athena.health = athena.health_max

                        #pygame.draw.rect(screen,(255,255,255),air_arrows_list[i])
                        screen.blit(Gold_Arrow,(air_arrows_list[i].x-10,air_arrows_list[i].y-10))



            if athena.attack_type == 2 and athena.attacking:
                if athena.attacking_time == 0:
                    if player.x >= width/2:
                        athena.attacking_site = "left"
                    elif player.x < width/2:
                        athena.attacking_site = "right"
                elif athena.attacking_time < 20:
                    if athena.attacking_site == "left":
                        athena.x = 5
                        athena.rect = pygame.Rect(athena.x,athena.y,athena.width,athena.height)
                        athena.animation_state = 4
                    elif athena.attacking_site == "right":
                        athena.x = width-(athena.width + 5)
                        athena.rect = pygame.Rect(athena.x, athena.y, athena.width, athena.height)
                        athena.animation_state = 5
                elif athena.attacking_time <= 150:
                    if athena.attacking_site == "left":
                        athena.x +=     30
                        athena.rect = pygame.Rect(athena.x, athena.y, athena.width, athena.height)
                        athena.animation_state = 4
                    elif athena.attacking_site == "right":
                        athena.x -= 30
                        athena.rect = pygame.Rect(athena.x, athena.y, athena.width, athena.height)
                        athena.animation_state = 5
                elif athena.attacking_time >= 150:
                    athena.attacking_time = 0
                    athena.attacking = False
                    player.already_damaged = False
                    after_dash = random.randint(1,3)
                    if after_dash == 1:
                        location = 2
                    elif after_dash == 2:
                        location = 3
                    elif after_dash == 3:
                        location = 0.5
                    athena.x = width / location
                    if player.x >= athena.x-player.width and player.x <= athena.x+athena.width:
                        if player.x >= width / 2:
                            athena.x = 0
                        elif player.x < width / 2:
                            athena.x = width-(athena.width + 5)

                    athena.rect = pygame.Rect(athena.x, athena.y, athena.width, athena.height)


            if athena.attack_type == 3 and athena.attacking:
                player.already_damaged = False
                athena.animation_state = 2
                if athena.attacking_time == 0:
                    athena.y = - 20
                    athena.x = player.x - athena.width/2
                elif athena.attacking_time < 20:
                    athena.x = player.x - athena.width / 2
                    athena.rect = pygame.Rect(athena.x, athena.y, athena.width, athena.height)
                elif athena.attacking_time <= 90:
                    athena.y += 20
                    athena.rect = pygame.Rect(athena.x, athena.y, athena.width, athena.height)
                    if athena.y + athena.height >= height_floor:
                        athena.y = height_floor-athena.height
                        athena.attacking_time = 170
                elif athena.attacking_time >= 230:
                    athena.attacking_time = 0
                    athena.attacking = False
                    floor_damage.already_damaged = False
                    player.already_damaged = False
                elif athena.attacking_time >= 180:
                    athena.animation_state = 3
                    floor_damage.width = width
                    floor_damage.x = 0
                    floor_damage.y = height_floor - 30
                    floor_damage.rect = pygame.Rect(floor_damage.x, floor_damage.y, floor_damage.width, height_floor)
                    #pygame.draw.rect(screen, (255, 255, 255), floor_damage.rect)
                    screen.blit(Ground_Explosion,(floor_damage.rect.x,floor_damage.rect.y))
                    if player.rect.colliderect(floor_damage.rect) and not floor_damage.already_damaged:
                        floor_damage.already_damaged = True
                        player.health -= floor_damage.dealt_damage
                        player.hit = True


                elif athena.attacking_time >= 170:
                    athena.rect = pygame.Rect(athena.x, athena.y, athena.width, athena.height)





            if athena.attacking:
                athena.attacking_time += 1


        elif boss_number == 2:

            # check if defeated
            print(Poseidon.health)


            # set animation to default, will be put back to the correct one later on if he is not idle

            Poseidon.animation_state = 0

            # check if boss is damaged

            Poseidon.x = width - (Poseidon.width + 100)

            Poseidon.rect = pygame.Rect(Poseidon.x, Poseidon.y, Poseidon.width, Poseidon.height)
            if Poseidon.health <= 0:
                print("purple")
                game_status = "victory"


            if light_attack.rect.colliderect(Poseidon.rect) and attacking_frame:
                Poseidon.health -= light_attack.damage
                pygame.mixer.Sound.play(hitting_sound)
                if Poseidon.health <= 0:
                    game_status = "victory"
                light_attack.did_attack = True

            # controll if new attack needs to be started

            if Poseidon.attacking == False and frame % 120 == 0 and frame != 0:
                Poseidon.attacking = True
                Poseidon.attack_type = random.randint(1, 3)
                player.already_damaged = False

            # Fish

            if Poseidon.attack_type == 1 and Poseidon.attacking:
                # fische die von rechts nach links fliegen
                if Poseidon.attack_type == 1 and Poseidon.attacking:
                    # fische die von rechts nach links fliegen

                    if Poseidon.attacking_time == 0:
                        for i in range(10):
                            x = width + random.randint(0, 5)
                            y = (height - 150) - (i * 250)
                            flying_spears_spawn = pygame.Rect(x, y, 40, 50)
                            flying_spears_list.append(flying_spears_spawn)

                        spearspaces_unten = random.randint(int(height * 0.4), int(height_floor - 50))
                        spearspaces_oben = spearspaces_unten - spearspaces
                        # 2 bis 5 Sekunden Cooldown
                        Poseidon.cooldown = random.randint(120, 300)

                    """if random.random() == 1:
                        d = random.randint(0, int(spearspaces_oben))
                    else:
                        d = random.randint(int(spearspaces_unten), int(height_floor - 60))"""

                    if Poseidon.attacking_time <= 120:
                        for flying_spears_spawn in flying_spears_list:
                            flying_spears_spawn.x -= 16
                            #pygame.draw.rect(screen, (0, 255, 100), flying_spears_spawn)
                            screen.blit(Flying_Fish,flying_spears_spawn)

                        for flying_spears_spawn in flying_spears_list:
                            if flying_spears_spawn.colliderect(player.rect):
                                if not player.already_damaged:
                                    player.health -= 30
                                    player.already_damaged = True
                    else:
                        Poseidon.attacking_time = 0
                        Poseidon.attacking = False
                        player.already_damaged = False
                        flying_spears_list = []

            if Poseidon.attack_type == 2:
                if Poseidon.attacking_time == 0:
                    Poseidon.attacking_site = "right"

                elif Poseidon.attacking_time < 40:
                    if Poseidon.attacking_site == "right":
                        Poseidon_Wave.x = width - (Poseidon_Wave.width + 5)
                        Poseidon_Wave.y = height_floor - Poseidon_Wave.height
                        Poseidon_Wave.rect = pygame.Rect(Poseidon_Wave.x, Poseidon_Wave.y, Poseidon_Wave.width,Poseidon_Wave.height)
                        Poseidon_Wave.animation_state = 5
                        #pygame.draw.rect(screen, (0, 255, 100), Poseidon_Wave.rect)
                        screen.blit(Wave, (Poseidon_Wave.rect.x, Poseidon_Wave.rect.y))

                elif Poseidon.attacking_time <= 180:
                    if Poseidon.attacking_site == "right":
                        Poseidon_Wave.x -= 20
                        Poseidon_Wave.y = height_floor - Poseidon_Wave.height
                        Poseidon_Wave.rect = pygame.Rect(Poseidon_Wave.x, Poseidon_Wave.y, Poseidon_Wave.width,
                                                         Poseidon_Wave.height)

                        # check damage

                        if Poseidon_Wave.rect.colliderect(player.rect) and not player.already_damaged:
                            player.health -= 60
                            player.hit = True
                            player.already_damaged = True

                        #pygame.draw.rect(screen, (0, 255, 100), Poseidon_Wave.rect)
                        screen.blit(Wave,(Poseidon_Wave.rect.x,Poseidon_Wave.rect.y))
                        Poseidon_Wave.animation_state = 5

                elif Poseidon.attacking_time >= 180:
                    Poseidon.attacking_time = 0
                    Poseidon.attacking = False
                    Poseidon.already_damaged = False
                    after_dash = random.randint(1, 3)

            if Poseidon.attack_type == 3 and Poseidon.attacking:
                Poseidon.animation_state = 1
                if Poseidon.attacking_time <= 10:
                    Waterfall.x = player.x - player.width / 2
                    Waterfall.rect.update(Waterfall.x, Waterfall.y, Waterfall.width, Waterfall.height)
                    screen.blit(Waterfall_Warn, (Waterfall.x, Waterfall.y))
                elif Poseidon.attacking_time <= 25:
                    screen.blit(Waterfall_Warn, (Waterfall.x, Waterfall.y))
                elif Poseidon.attacking_time <= 45:
                    if Waterfall.rect.colliderect(player) and not player.already_damaged:
                        player.health -= Waterfall.dealt_damage
                        player.already_damaged = True
                        player.hit = True
                    screen.blit(Waterfall_image, (Waterfall.x, Waterfall.y))
                elif Poseidon.attacking_time == 75:
                    Poseidon.attacking_time = -1
                    player.already_damaged = False
                    Poseidon.attacking = False




            if Poseidon.attacking:
                Poseidon.attacking_time += 1

        elif boss_number == 3:
            Ares.animation_state = 0
            # sieg erkennen
            if Ares.health <= 0:
                game_status = "victory"
            # player and boss collisiona d
            if Ares.rect.colliderect(player.rect) and not player.already_damaged:
                player.health -= 30
                player.hit = True
                player.already_damaged = True

            if light_attack.rect.colliderect(Ares.rect) and attacking_frame:
                Ares.health -= light_attack.damage
                pygame.mixer.Sound.play(hitting_sound)
                light_attack.did_attack = True

            boss_bar = pygame.Rect(width / 3, height_floor - height / 192 + 15, Ares.health * 0.64, 30)

            # initialize attack
            if Ares.attacking == False and frame % 30 == 0 and not frame == 0:
                Ares.attacking = True
                Ares.attack_type = random.randint(1, 3)


            if Ares.attack_type == 1 and Ares.attacking:
                Ares.animation_state = 1
                if Ares.attacking_time >= 15:
                    ares_rage_1.x,ares_rage_1.y = Ares.x +Ares.width/2 - ares_rage_1.width/2, Ares.y +Ares.height/2 - ares_rage_1.height/2
                    ares_rage_1.rect.update(ares_rage_1.x,ares_rage_1.y,ares_rage_1.width,ares_rage_1.height)
                    if ares_rage_1.rect.colliderect(player.rect) and not player.already_damaged:
                        player.health -= ares_rage_1.dealt_damage
                        player.already_damaged = True
                        player.hit =True
                    screen.blit(Ares_Explosion_1,(ares_rage_1.x,ares_rage_1.y))
                if Ares.attacking_time == 45:
                    player.already_damaged = False
                if Ares.attacking_time >= 45:
                    ares_rage_2.x,ares_rage_2.y = Ares.x +Ares.width/2 - ares_rage_2.width/2, Ares.y +Ares.height/2 - ares_rage_2.height/2
                    ares_rage_1.rect.update(ares_rage_2.x, ares_rage_2.y, ares_rage_2.width, ares_rage_2.height)
                    if ares_rage_2.rect.colliderect(player.rect) and not player.already_damaged:
                        player.health -= ares_rage_2.dealt_damage
                        player.already_damaged = True
                        player.hit = True
                    screen.blit(Ares_Explosion_2, (ares_rage_2.x, ares_rage_2.y))
                if Ares.attacking_time == 60:
                    player.already_damaged = False
                    ares_rage_1.x, ares_rage_2.x = 2000, 2000
                    Ares.attacking = False
                    Ares.attacking_time = -1
                Ares.attacking_time += 1

            if Ares.attack_type == 2 and Ares.attacking:
                Ares.animation_state = 2
                if Ares.attacking_time % 5 == 0 and Ares.attacking_time < 90:
                    dagger_list.append(pygame.Rect(player.x + player.width/2, 0, 30, 50))
                if Ares.attacking_time >= 0:
                    for k in range(0, len(dagger_list)):
                        dagger_list[k].y += 25
                    if not player.already_damaged:
                        for g in range(0,len(dagger_list)):
                            if dagger_list[g].colliderect(player.rect):
                                player.health -= dagger.dealt_damage
                                player.already_damaged = True
                                player.hit = True
                                break
                    for d in range(0, len(dagger_list)):
                        screen.blit(Ares_Daggers,(dagger_list[d].x,dagger_list[d].y))
                if Ares.attacking_time == 180:
                    dagger_list = []
                    Ares.attacking_time = -1
                    player.already_damaged = False
                    Ares.attacking = False
                Ares.attacking_time += 1

            if Ares.attack_type == 3:
               Ares.animation_state = 3
               if Ares.attacking_time == 0:
                    Teleport_Destination = random.randint(0, width- Ares.rect.width)
               if Ares.attacking_time == 30:
                    Ares.x = Teleport_Destination
                    Ares.rect.update(Ares.x, Ares.y, Ares.width, Ares.height)
               if Ares.attacking_time < 30:
                    screen.blit(Ares_Assets[4],(Teleport_Destination -  Ares.width*0.1,Ares.y - Ares.width * 0.2))
               if Ares.attacking_time == 40:
                    Ares.attacking = False
                    player.already_damaged = False
                    Ares.attacking_time = -1
                    Ares.attack_type = 0
               Ares.attacking_time += 1




            #pygame.draw.rect(screen,(255,255,255),Ares.rect)






        #healing
        if healing and player.healpot_amount > 0:
            player.healpot_amount -= 1
            do_healing = True
            healing = False
            healing_frames = 20

        if do_healing:


            if healing_frames <= 10:
                player.health += 5
                if player.health >= player.health_max:
                    player.health = player.health_max


            if healing_frames <= 0:

                do_healing = False

        healing_frames -= 1


        #spieler Hp_bar update
        health_bar = pygame.Rect(width/76.8,height/43.2,player.health*(width/384),height/36)

        #boss zeichnen
        if boss_number ==1:
            screen.blit(Athena_Assets[athena.animation_state], (athena.x - 10, athena.y - 15))
        if boss_number == 2:
            screen.blit(Poseidon_Assets[Poseidon.animation_state],(Poseidon.x - 10,Poseidon.y - 15))
        if boss_number == 3 and player.x <= Ares.x:
            screen.blit(Ares_Assets[Ares.animation_state], (Ares.x -Ares.width* 0.1, Ares.y - Ares.height * 0.2))
        if boss_number == 3 and player.x >= Ares.x:
            screen.blit(pygame.transform.flip(Ares_Assets[Ares.animation_state],True,False), (Ares.x -Ares.width* 0.1, Ares.y - Ares.height * 0.2))


        # print player
        player.rect = pygame.Rect(player.x,player.y,player.width,player.height)
        #pygame.draw.rect(screen,(255,0,0),player.rect)

        #player graphics

        if player.health <= 0:
            game_status = "dead"
            screen.fill((181, 29, 29))
            player.animation = 2
            screen.blit(Game_Over, (width / 2 - Game_Over.get_width() / 2, height / 2 - Game_Over.get_height() / 2))
            screen.blit(Spacebar, (width / 2 - Spacebar.get_width() / 2, height / 1.5 - Spacebar.get_height() / 2))
        elif player.hit:
            #player hit sound
            if player.hit_timer ==15:
                pygame.mixer.Sound.play(getting_hit_Sound)
            #player hit animation
            player.animation = 5
            player.hit_timer -= 1
            if player.hit_timer == 0:
                player.hit_timer = 15
                player.hit = False
        elif do_healing:
            if healing_frames > 10:
                player.animation = 3
            if healing_frames <= 10:
               player.animation = 4
        elif attacking_time >0:
            player.animation = 1
        elif key_pressed[K_SPACE] and player.y > height/10* 8:
            player.animation = 0
        elif key_pressed[K_SPACE] and player.y < height/10* 8:
            player.animation = 7
        elif player.moving:
            player.animation = 9
        else:
            player.animation = 6

        player_animation(player.animation, player.attack_direction, Player_Assets, (player.x, player.y))

        # angriff zeigen
        if attacking_time > 0:
            if player.attack_direction == "left":
                screen.blit(Basic_Attack,(light_attack.rect.x,light_attack.rect.y))
            if player.attack_direction == "right":
                screen.blit(pygame.transform.flip(Basic_Attack, True, False), (light_attack.rect.x,light_attack.rect.y))



        #pygame.draw.rect(screen,(0,0,0), boss_bar_background)
        #pygame.draw.rect(screen,(130, 0, 0), boss_bar)


        # healthbar zeichnen
        pygame.draw.rect(screen, (0, 0, 0), health_bar_background)
        pygame.draw.rect(screen, (130, 0, 0), health_bar)
        flask_display(player.healpot_amount,Flask_Assets,Flask_Font,(health_bar.x,health_bar.y + health_bar.height * 2))





        bossHPbar = [True, pygame.Rect(width / 2 - boss_bar_background.width / 2, height * 0.95, boss_bar_background.width, 15),
        pygame.Rect(width / 2 - boss_bar_background.width / 2, height * 0.95, boss_bar_background.width * Bosses_for_Healthbar[boss_number].health / Bosses_for_Healthbar[boss_number].health_max, 15)]
        pygame.draw.rect(screen,(60,60,60),bossHPbar[1])
        pygame.draw.rect(screen,(130,0,0),bossHPbar[2])

        #Music
        if  not pygame.mixer_music.get_busy():
            Music_playing = False
            print("shiii works")

        if boss_number == 1:
            screen.blit(athena.name,(bossHPbar[1].centerx - athena.name.get_rect().width/2,bossHPbar[1].y - athena.name.get_rect().height - 5 ))
            if not Music_playing:
                pygame.mixer.music.load("Game_Main/Music and Sounds/Athena_Music.mp3")
                pygame.mixer_music.play()
                Music_playing = True
        if boss_number == 2:
            screen.blit(Poseidon.name, (bossHPbar[1].centerx - Poseidon.name.get_rect().width / 2, bossHPbar[1].y - Poseidon.name.get_rect().height - 5))
            if not Music_playing:
                pygame.mixer.music.load("Game_Main/Music and Sounds/Poseidon_Music.mp3")
                pygame.mixer_music.play()
                Music_playing = True
        if boss_number == 3:
            screen.blit(Ares.name, (bossHPbar[1].centerx - Ares.name.get_rect().width / 2, bossHPbar[1].y - Ares.name.get_rect().height - 5))
            if not Music_playing:
                pygame.mixer.music.load("Game_Main/Music and Sounds/Ares_Music.mp3")
                pygame.mixer_music.play()
                Music_playing = True


        attacking_frame = False
        player.moving = False
        frame += 1
        pygame.display.update()
        clock.tick(60)

    while game_status == "victory":
        player.healpot_amount = 10
        player.health = player.health_max
        athena.health = 1000
        Poseidon.health = Poseidon.health_max
        Ares.health = Ares.health_max

        if wintime > 0:
            Music_playing = False

            Victory_Sound = pygame.mixer.Sound("./Game_Main/Music and Sounds/victory-sound.mp3")
            pygame.mixer.Sound.set_volume(Victory_Sound,0.3)
            pygame.mixer.Sound.play(Victory_Sound)
        wintime += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.mixer_music.fadeout(1)
                    game_status = "alive"
                    wintime = 0
                    boss_number += 1
                    if boss_number == 4:
                        game_status = "victory roile"
        screen.fill((181,146,29))
        screen.blit(Victory, (width / 2 - Game_Over.get_width() / 2, height / 2 - Game_Over.get_height() / 2))
        screen.blit(Spacebar, (width / 2 - Spacebar.get_width() / 2, height / 1.5 - Spacebar.get_height() / 2))
        screen.blit(Player_Assets[8],(player.x,player.y))
        pygame.display.update()
        clock.tick()

    while game_status == "victory roile":
        Music_playing = False
        if wintime == 0:
            pygame.mixer_music.fadeout(1)
            pygame.mixer_music.load("./Game_Main/Music and Sounds/Fallen_Down.mp3")
            pygame.mixer_music.play()
        wintime += 1
        screen.fill((0,0,0))
        screen.blit(Thanks_Credit, (width / 2 - Thanks_Credit.get_width() / 2, height / 2 - Thanks_Credit.get_height() / 2))
        screen.blit(Names_Credit,(width / 2 - Names_Credit.get_width() / 2, (height / 2 - Names_Credit.get_height() / 2)+150))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                        game_status = "title_screen"
                        wintime = 0
        pygame.display.update()
        clock.tick()

    while game_status == "dead":
        athena.health = athena.health_max
        Poseidon.health = Poseidon.health_max
        Ares.health = Ares.health_max
        if deadtime == 0:
            Music_playing = False
            pygame.mixer_music.fadeout(1)
            pygame.mixer.music.load("./Game_Main/Music and Sounds/lost-sound.mp3")
            pygame.mixer_music.play()
        deadtime += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.mixer_music.fadeout(1)
                    game_status = "title_screen"
                    deadtime = 0
        screen.fill((181, 29, 29))
        if player.attack_direction == "left":
            screen.blit(Player_Assets[2], (player.x, player.y))
        if player.attack_direction == "right":
            screen.blit(pygame.transform.flip(Player_Assets[2], True, False), (player.x, player.y))
        screen.blit(Game_Over, (width / 2 - Game_Over.get_width() / 2, height / 2 - Game_Over.get_height() / 2))
        screen.blit(Spacebar, (width / 2 - Spacebar.get_width() / 2, height / 1.5 - Spacebar.get_height() / 2))

    if game_status == "title_screen":

        # play Music
        pygame.mixer_music.load("./Game_Main/Music and Sounds/Title.mp3")
        pygame.mixer_music.play()
        Music_cpos = 0

    while game_status == "title_screen":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Music playback
        Music_cpos += 1
        if Music_cpos == Title_Music_len:
            pygame.mixer_music.rewind()
        # Draw Background
        screen.blit(TitleBG, (0, 0))  # draws the Backround Image
        screen.blit(DisplayTitle,
                    (width / 2 - DisplayTitle.get_width() / 2, height / 5 - DisplayTitle.get_height() / 2))

        if Title_state == 1:  # Text and Rects for title state 1
            Wait_Bcuz_Else_Buggy += 1
            screen.blit(Start_Button, (width / 2 - Start_Button.get_width() / 2,
                                       height / 5 * 2 - Start_Button.get_height() / 2))  # Displays the start button

            Start_Button_rect = Start_Button.get_rect()
            Start_Button_rect.x = int(width / 2 - Start_Button.get_width() / 2)
            Start_Button_rect.y = int(height / 5 * 2 - Start_Button.get_height() / 2)

            screen.blit(Controls_Button, (width / 2 - Controls_Button.get_width() / 2,
                                          height / 5 * 3 - Controls_Button.get_height() / 2))

            Controls_Button_rect = Controls_Button.get_rect()
            Controls_Button_rect.x = int(width / 2 - Controls_Button.get_width() / 2)
            Controls_Button_rect.y = int(height / 5 * 3 - Controls_Button.get_height() / 2)

            screen.blit(Boss_Select_Button, (width / 2 - Boss_Select_Button.get_width() / 2,
                                             height / 5 * 4 - Boss_Select_Button.get_height() / 2))

            Boss_Select_Button_rect = Boss_Select_Button.get_rect()
            Boss_Select_Button_rect.x = int(width / 2 - Boss_Select_Button.get_width() / 2)
            Boss_Select_Button_rect.y = int(height / 5 * 4 - Boss_Select_Button.get_height() / 2)

        if Title_state == 2:
            Wait_Bcuz_Else_Buggy += 1
            screen.blit(Controls_Title,
                        (width / 2 - Controls_Title.get_width() / 2, height / 5 * 2 - Controls_Title.get_height() / 2))

            screen.blit(Back_Button,
                        (width / 2 - Back_Button.get_width() / 2, height / 5 * 4 - Back_Button.get_height() / 2))

            Back_Button_rect = Back_Button.get_rect()
            Back_Button_rect.x = int(width / 2 - Back_Button.get_width() / 2)
            Back_Button_rect.y = int(height / 5 * 4 - Back_Button.get_height() / 2)

            screen.blit(Controls_1, (width / 2 - Controls_1.get_width() / 2, height / 5 * 2 + (
                        (height / 5 * 4 - height / 5 * 2) / 5) - Controls_1.get_height() / 2))
            screen.blit(Controls_2, (width / 2 - Controls_2.get_width() / 2, height / 5 * 2 + (
                        (height / 5 * 4 - height / 5 * 2) / 5 * 2) - Controls_1.get_height() / 2))
            screen.blit(Controls_3, (width / 2 - Controls_3.get_width() / 2, height / 5 * 2 + (
                        (height / 5 * 4 - height / 5 * 2) / 5 * 3) - Controls_1.get_height() / 2))
            screen.blit(Controls_4, (width / 2 - Controls_4.get_width() / 2, height / 5 * 2 + (
                        (height / 5 * 4 - height / 5 * 2) / 5 * 4) - Controls_1.get_height() / 2))

        if Title_state == 3:
            Wait_Bcuz_Else_Buggy += 1
            screen.blit(Back_Button,
                        (width / 2 - Back_Button.get_width() / 2, height / 5 * 4 - Back_Button.get_height() / 2))

            Back_Button_rect = Back_Button.get_rect()
            Back_Button_rect.x = int(width / 2 - Back_Button.get_width() / 2)
            Back_Button_rect.y = int(height / 5 * 4 - Back_Button.get_height() / 2)

        mouse_pos = cursor()

        if pygame.mouse.get_pressed(3)[0]:
            if Title_state == 1:
                if mouse_pos.colliderect(Start_Button_rect):
                    pygame.mixer.Sound.play(button_clicked_sound)
                    boss_number = 1
                    game_status = "loading screen"
                    loading_time = 60
                    pygame.mixer_music.fadeout(1)
                if mouse_pos.colliderect(Controls_Button_rect) and Wait_Bcuz_Else_Buggy > 10:
                    pygame.mixer.Sound.play(button_clicked_sound)
                    Title_state = 2
                    Wait_Bcuz_Else_Buggy = 0
                if mouse_pos.colliderect(Boss_Select_Button_rect) and Wait_Bcuz_Else_Buggy > 10:
                    pygame.mixer.Sound.play(button_clicked_sound)
                    pygame.quit()
                    sys.exit()
            if Title_state == 2:
                if mouse_pos.colliderect(Back_Button_rect) and Wait_Bcuz_Else_Buggy > 10:
                    pygame.mixer.Sound.play(button_clicked_sound)
                    Title_state = 1
                    Wait_Bcuz_Else_Buggy = 0
            if Title_state == 3:
                if mouse_pos.colliderect(Back_Button_rect) and Wait_Bcuz_Else_Buggy > 10:
                    pygame.mixer.Sound.play(button_clicked_sound)
                    Title_state = 1
                    Wait_Bcuz_Else_Buggy = 0

        # end frame
        pygame.display.update()
        clock.tick(60)

    while game_status == "loading screen":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill((0, 0, 0))
        if loading_time > 0:
            print("loading")

        else:
            game_status = "alive"
            # reinitialize boss
            # enviroment
            loading_time = 0
            do_healing = False
            healing = False
            attacking_frame = False
            gravity = 1
            jump_height = height / 54
            screen_rect = screen.get_rect()
            double_jump = False
            double_jumping = False
            attacking = False
            attacking_time = 0
            frame_counter = 0
            damage_delay = 10

            frame = 0
            arrow_amount = int(width / 77)
            healing_frames = 0

            # floor definition
            height_floor = height - height / 10.8

            floor_rect = pygame.Rect(0, height_floor, width, height / 10.8 + 20)


            # schaden objekt
            class Damage:
                def __init__(self):
                    self.width = 30
                    self.height = 80
                    self.x = 0
                    self.y = 0
                    self.dealt_damage = 10
                    self.rect = pygame.Rect(500, height_floor - self.height, self.width, self.height)
                    self.already_damaged = False
                    self.attacking_time = 0


            # floor damage definition
            floor_damage = Damage()
            floor_damage.dealt_damage = 50
            floor_damage.x = 11000
            floor_damage.y = 10000
            floor_damage.rect = pygame.Rect(floor_damage.x, floor_damage.y, floor_damage.width, height_floor)

            # air arrows definition
            air_arrow = Damage()
            air_arrow.dealt_damage = 30
            air_arrows_list = []


            # bossklasse
            class Boss:
                def __init__(self, name):
                    self.width = width / 9.6
                    self.height = height / 3
                    self.y = height_floor - self.height
                    self.x = width / 2 - self.width / 2
                    self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
                    self.health_max = 1000
                    self.health = self.health_max
                    self.combat_timer = 0
                    self.attack_type = 1
                    self.attacking = False
                    self.attacking_time = 0
                    self.attacking_site = "left"
                    self.name = Helvetica.render(name, True, (255, 255, 255))
                    self.animation_state = "Temporary"


            athena = Boss("Athena, Goddess of Wisdom")


            # player definition

            class player:
                def __init__(self):
                    self.x = 300
                    self.y = height_floor - height / 10.8
                    self.height = height / 10.8
                    self.width = width / 38.4
                    self.velocity_x = width / 274
                    self.velocity_y = jump_height
                    self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
                    self.jumping = False
                    self.falling = False
                    self.crouched = False
                    self.hit = False
                    self.hit_timer = 10
                    self.attack_direction = "left"
                    self.health = 100
                    self.health_max = 100
                    self.alive = True
                    self.animation = "temporary"
                    self.moving = False
                    self.healpot_amount = 10
                    self.already_damaged = False


            player = player()


            # angriff klasse
            class attack:
                def __init__(self):
                    self.width = width / 24
                    self.height = height / 13.5
                    # angriff oben unten
                    self.y_left_right = player.y + height / 108
                    self.y_up = player.y - self.height
                    self.y_down = player.y + player.height
                    # angriff links rechts
                    self.x_right = player.x + player.width
                    self.x_left = player.x - self.width
                    self.x_up_down = player.x - (self.width - player.width) / 2
                    self.did_attack = False
                    self.damage = 20
                    self.rect = pygame.Rect(self.x_right, self.y_left_right, player.width, player.height)


            light_attack = attack()

            # healthbar
            health_bar_background = pygame.Rect(width / 96, height / 54, width / 3.76, height / 27)
            health_bar = pygame.Rect(width / 76.8, height / 43.2, player.health * ((width / 376 - width / 192) / 100),
                                     height / 36)

            boss_bar_background = pygame.Rect(width / 3 - 5, height_floor - height / 192 + 10, width / 3 + 10, 40)
            boss_bar = pygame.Rect(width / 3, height_floor - height / 192 + 10, athena.health * 0.64, 30)
        loading_time -= 1

        # bugfixing list because ke bock ka
        Bosses_for_Healthbar = ["Stragel", athena, Poseidon, Ares]
