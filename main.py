# Author: Konstantinos Dimitriou
# Date: 27/05/2026


import pygame as pg
import pygame.gfxdraw as pg_gfxdraw
import sys
import random

"""
Next steps:
    Gameplay:
        - Backround: Make backround class with any functions needed.
        - Add hover over deck to show the rest of the cards in deck.
        - Add hover to button class.
        - Add screen changes to choose class, highscore, options, etc.
        - Add time buffer between main screen changes.
        - Add Choose class.
    Add-ons:
        - Add Classes.
    Bugs:
        - Fix number center in animation of damage dice.
    Visuals:
        - Make new win and lose titles.
        - Make title.
        - Make new buttons with hover option.
    Other:
        - Make scaling the screen possible.
        - Add debug mode for health and deck.
        - Clean up code.
        - Improve function names, 'update' is too generic.
"""


class card(pg.sprite.Sprite):
    def __init__(self, suit_and_value_path, position, revealed, card_size):
        # suit_and_value_path = "./Cards_png/" + suit + "_" + value + ".png"
        super().__init__()
        self.full_name = suit_and_value_path
        if suit_and_value_path == 'Empty':
            self.suit = suit_and_value_path
            self.value = suit_and_value_path
            self.revealed = False
            raw_backround = pg.image.load("./assets/cards_png/CardBackFace.png")
            #self.backside = pg.transform.scale(raw_backround, (180,250))
            self.backside = pg.transform.scale(raw_backround, card_size)
            #self.image = pg.transform.scale(raw_backround, (180,250))
            self.image = self.backside
            self.rect = self.image.get_rect()
            #self.initial_position = position
            #self.rect.center = position
            #self.used = False
        else:
            self.suit = suit_and_value_path.split('_')[1].split('/')[1]
            self.value = int(suit_and_value_path.split('_')[2].split('.')[0])
            self.revealed = revealed
            raw_backround = pg.image.load("./assets/cards_png/CardBackFace.png")
            #self.backside = pg.transform.scale(raw_backround, (180,250))
            self.backside = pg.transform.scale(raw_backround, card_size)
            #raw_image = pg.image.load("./Cards_png/" + suit + "_" + value + ".png")
            raw_image = pg.image.load(suit_and_value_path)
            # Rezise image if needed
            #self.image = pg.transform.scale(raw_image, (180,250))
            self.image = pg.transform.scale(raw_image, card_size)
            self.rect = self.image.get_rect()
        self.initial_position = position
        self.rect.center = position
        self.used = False
        self.click_sound = pg.mixer.Sound("./assets/sound_effects/sound_click.wav")

        self.in_animation = False
        self.animation_start_position = position
        self.animation_end_position = None
        self.animation_timer_max = 20
        self.animation_timer = 0

    def start_move_animation(self, start_position, end_position):
        self.in_animation = True
        self.animation_start_position = start_position
        self.animation_end_position = end_position
    
    def animation_function_current_point(self):
        SP = self.animation_start_position
        EP = self.animation_end_position
        TM = self.animation_timer_max
        CT = self.animation_timer
        # Determine path line
        #CP = ( (SP[0] * (TM - CT) + EP[0] * CT) / TM , (SP[1] * (TM - CT) + EP[1] * CT) / TM ) # straight line
        CP = ( (SP[0] * (TM - CT)**2 + EP[0] * CT**2) / TM**2 , (SP[1] * (TM - CT)**2 + EP[1] * CT**2) / TM**2 ) # slight parabola
        #CP = ( (SP[0] * (TM - CT)**3 + EP[0] * CT**3) / TM**3 , (SP[1] * (TM - CT)**3 + EP[1] * CT**3) / TM**3 ) # x^3 parabola
        # Determine path speed
        MP = ((SP[0]+EP[0])/2, (SP[1]+EP[1])/2)
        current_point = ( (SP[0] * (TM - CT) + EP[0] * CT) / TM + (CP[0]-MP[0])*(TM-CT)*CT/TM**2, (SP[1] * (TM - CT) + EP[1] * CT) / TM + (CP[1]-MP[1])*(TM-CT)*CT/TM**2)
        return current_point
    
    def draw(self, surface):
        if self.in_animation == True:
            if self.animation_timer == self.animation_timer_max:
                self.in_animation = False
                self.animation_timer = 0
            else:
                self.animation_timer += 1
                self.rect.center = self.animation_function_current_point()
                #self.rect.center = ( (self.animation_start_position[0] * (self.animation_timer_max - self.animation_timer) + self.animation_end_position[0] * self.animation_timer) / self.animation_timer_max , 
                #            (self.animation_start_position[1] * (self.animation_timer_max - self.animation_timer) + self.animation_end_position[1] * self.animation_timer) / self.animation_timer_max )

        if self.revealed == True:
            surface.blit(self.image, self.rect)
        else:
            surface.blit(self.backside, self.rect)

    def left_clicked(self):
        mouse_buttons = pg.mouse.get_pressed()
        mouse_position = pg.mouse.get_pos()
        if self.used == True: # If card was already clicked it cannot be clicked again.
            return False
        if mouse_buttons == (True, False, False): # Left click happened
            if self.rect.collidepoint(mouse_position): # Click happened inside card boundaries.
                #self.used = True
                self.click_sound.play()
                return True
    
    def right_clicked(self):
        mouse_buttons = pg.mouse.get_pressed()
        mouse_position = pg.mouse.get_pos()
        if self.used == True: # If card was already used it cannot be clicked again.
            return False
        if mouse_buttons == (False, False, True): # Right click happened
            if self.rect.collidepoint(mouse_position): # Click happened inside card boundaries.
                self.click_sound.play()
                return True


def build_dungeon_deck():
    """
    Suits:      Spades  = S,
                Hearts  = H,
                Diamonds = D,
                Clubs   = C,
    Values:     A = 14, K = 13, Q = 12, J = 11, 10, 9, 8, 7, 6, 5, 4, 3, 2
    """
    deck = list()
    #Suits = ('Spades', 'Hearts', 'Diamonds', 'Clubs')
    Monsters_suits = ('Spades', 'Clubs')
    Support_suits = ('Hearts', 'Diamonds')
    Values = (14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2)
    #Values = (14, 13, 12, 11, 10, 9, 8)
    #print('Debug deck.')
    #sum_of_values = 0
    #for v in Values:
    #    sum_of_values += v*2
    #print('sum_of_values: ', sum_of_values)

    for suit in Monsters_suits:
        for value in Values:
            deck.append("./assets/cards_png/" + suit + "_" + str(value) + ".png")
    for suit in Support_suits:
        for value in Values[4:]:
            deck.append("./assets/cards_png/" + suit + "_" + str(value) + ".png")
    #print('Build deck size: ', len(deck))
    return deck


class dungeon:
    # Keeps track of the deck, open cards and the discards.
    def __init__(self):
        # Build deck
        self.base_deck = build_dungeon_deck()
        # Shuffle deck
        random.shuffle(self.base_deck)
        # Setup card lists
        self.open_cards = list()
        self.discards = list()

    def get_card(self):
        # Draw top card from deck
        card_choice_path = self.base_deck[0]
        # Remove card from rest of the deck
        self.base_deck.remove(card_choice_path)
        # Add card to open cards
        self.open_cards.append(card_choice_path)
        return card_choice_path

    def add_discard(self, discarded_card_path):
        self.open_cards.remove(discarded_card_path)
        self.discards.append(discarded_card_path)


class gameboard:
    def __init__(self, surface, settings):
        display_width = surface.get_width()
        display_heigth = surface.get_height()
        #print('settings:', settings)

        self.settings = settings.copy()
        #print('settings:', self.settings)

        self.dice_animation_timer_max = 20
        self.dice_animation_timer = self.dice_animation_timer_max
        self.dice_animation = False
        self.dice_animation_rotation = 'clockwise'

        self.card_animation_timer_max = 10
        self.card_animation_timer = 0

        #self.display_scale = display_width * display_heigth / 1000000
        self.display_scale = display_heigth / 1000

        #self.card_size = (180, 250) # (display_width * display_heigth / 1000000 * 180 , display_width * display_heigth / 1000000 * 250)
        self.card_size = (self.display_scale * 180 , self.display_scale * 250)
        #print('self.card_size: ', self.card_size)
        #self.card_size = (18, 25)

        self.change_mode = False
        #self.deck_position = (95,130) # (cardsize/2 + 5, cardsize/2 + 5)
        #self.deck_position = (self.card_size[0]/2 + 5, self.card_size[1]/2 + 5)
        card_size_buffer = self.card_size[0]/36
        self.deck_position = (self.card_size[0]/2 + card_size_buffer, self.card_size[1]/2 + card_size_buffer)
        #self.open_card_positions = ((300,130), (500,130), (700,130), (900,130))
        #self.open_card_positions = (( 3 * display_width / 10,130), (5 * display_width / 10,130), (7 * display_width / 10,130), (9 * display_width / 10,130))
        self.open_card_positions = (( 3 * display_width / 10, self.card_size[1]/2 + card_size_buffer)
                                    , (3 * display_width / 10 + self.card_size[0] + 2*card_size_buffer, self.card_size[1]/2 + card_size_buffer)
                                    , (3 * display_width / 10 + 2*self.card_size[0] + 4*card_size_buffer, self.card_size[1]/2 + card_size_buffer)
                                    , (3 * display_width / 10 + 3*self.card_size[0] + 6*card_size_buffer, self.card_size[1]/2 + card_size_buffer))
        self.current_open_card_positions = list()
        #self.weapon_position =  (500, 500)
        self.weapon_position = (display_width/2 , display_heigth/2)
        #self.kill_position =  (500, 550)
        #self.kill_position = (display_width/2, display_heigth/2 + 50)
        self.kill_position = (display_width/2, display_heigth/2)
        #self.health_points_position = (100, 900)
        self.health_points_position = (100, display_heigth - 100)
        #self.discard_position = (905, 870) #(screen_width - 95, screen_height-130)
        #self.discard_position = (display_width - 95, display_heigth - 130)
        self.discard_position = (display_width - self.card_size[0]/2 - card_size_buffer, display_heigth - self.card_size[1]/2 - card_size_buffer)

        self.board_dungeon = dungeon()

        self.weapon_card = None
        self.kill_cards = list()
        self.open_cards = list()
        self.discard_cards = list()

        self.number_of_full_draws = -1 # Start at -1 so that after the initial draw it is zero.

        # Setup dungeon card
        current_card_path = 'Empty'
        self.dungeon_card = card(current_card_path, self.deck_position, revealed=False, card_size=self.card_size)

        # Setup open cards
        self.redraw_room()

        self.last_kill = None

        self.redraw_available = True

        self.maximum_health_points = 20
        self.current_health_points = self.maximum_health_points

        self.game_result = None
        self.score = 0


    def fill(self, open_positions):
        if len(self.board_dungeon.base_deck)<3:
            self.end_game()
        else:
            self.redraw_available = True
            #print("open_positions: ",open_positions)
            for card_position in open_positions:
                current_card_path = self.board_dungeon.get_card()
                current_card =card(current_card_path, card_position, revealed=True, card_size=self.card_size)
                current_card.start_move_animation(start_position = self.deck_position, end_position = card_position)
                self.open_cards.append(current_card)
    
    def redraw_room(self):
        # Initial draw
        if self.number_of_full_draws == -1:
            # Play shuffle sound
            shuffle_sound = pg.mixer.Sound("./assets/sound_effects/shuffle.wav")
            shuffle_sound.play()
            self.number_of_full_draws += 1
            # Setup open cards
            for card_position in self.open_card_positions:
                current_card_path = self.board_dungeon.get_card()
                current_card = card(current_card_path, card_position, revealed=True, card_size=self.card_size)
                current_card.start_move_animation(start_position=self.deck_position, end_position=card_position)
                self.open_cards.append(current_card)
            return None
        
        # Redraw only if room is full and room was not redrawn in the previous turn.
        if self.redraw_available == False or len(self.current_open_card_positions)>0:
            return None
        self.redraw_available = False

        self.number_of_full_draws += 1

        # Play shuffle sound
        shuffle_sound = pg.mixer.Sound("./assets/sound_effects/shuffle.wav")
        shuffle_sound.play()

        # Add open cards back to the bottom of the dungeon
        dummy_list = self.open_cards.copy()
        for open_card in self.open_cards:
            # Adjust dungeon
            self.board_dungeon.base_deck.append(open_card.full_name)
            self.board_dungeon.open_cards.remove(open_card.full_name)
            # Adjust game board
            dummy_list.remove(open_card)
        self.open_cards = dummy_list.copy()
        # Setup open cards
        for card_position in self.open_card_positions:
            current_card_path = self.board_dungeon.get_card()
            current_card = card(current_card_path, card_position, revealed=True, card_size=self.card_size)
            current_card.start_move_animation(start_position=self.deck_position, end_position=card_position)
            self.open_cards.append(current_card)

    def draw(self, surface):
        display_width = surface.get_width()
        display_heigth = surface.get_height()

        # Draw dungeon card
        self.dungeon_card.draw(surface)
        # Draw open cards
        for open_card in self.open_cards:
            open_card.draw(surface)
        # Draw weapon
        if self.weapon_card != None:
            self.weapon_card.draw(surface)
        # Draw kills
        if len(self.kill_cards) > 0:
            for kill_card in self.kill_cards:
                kill_card.draw(surface)
        # Draw discards
        if len(self.discard_cards) > 0:
            for discard_card in self.discard_cards:
                discard_card.draw(surface)
        
        # Display current health points.
        hp_font = pg.font.SysFont('Liberation Sans', int(self.card_size[1]//5.5))

        d20_basic_image_raw = pg.image.load("./assets/dice_png/d20_basic_image.png")
        dice_size = (self.card_size[0] , self.card_size[0])
        d20_image = pg.transform.scale(d20_basic_image_raw, dice_size)
        d20_rect = d20_image.get_rect(center = (self.card_size[0]/1.5, display_heigth - self.card_size[0]/1.5))
        if self.dice_animation_rotation == 'clockwise':
            rot_angle = 20
        elif self.dice_animation_rotation == 'counterclockwise':
            rot_angle = -20
        else:
            print('error: rotation direction not possible.')
            rot_angle = 0
        if self.dice_animation == True:
            if self.dice_animation_timer > 0:
                self.dice_animation_timer -= 1
                d20_image = pg.transform.rotate(d20_image, rot_angle * self.dice_animation_timer   )
                d20_rect = d20_image.get_rect(center = (self.card_size[0]/1.5, display_heigth - self.card_size[0]/1.5))
                hp_text = hp_font.render(str(random.randint(1,20)), True, (0, 0, 0))
                hp_text = pg.transform.rotate(hp_text, 9 + rot_angle * self.dice_animation_timer)
            else:
                self.dice_animation = False
                self.dice_animation_timer = self.dice_animation_timer_max
                hp_text = hp_font.render(str(self.current_health_points), True, (0, 0, 0))
                hp_text = pg.transform.rotate(hp_text, 9)
        else:
            # Draw simple HP
            hp_text = hp_font.render(str(self.current_health_points), True, (0, 0, 0))
            hp_text = pg.transform.rotate(hp_text, 9)
        surface.blit(d20_image, d20_rect)

        text_center = (d20_rect.center[0] + d20_rect.center[0]/15, d20_rect.center[1] - d20_rect.center[1]/70 )
        hp_text_rect = hp_text.get_rect(center = text_center)
        
        surface.blit(hp_text, hp_text_rect)

        # Draw rules
        draw_rules = self.settings[0]
        if draw_rules == True:
            display_width = surface.get_width()
            display_heigth = surface.get_height()
            rules_raw_image = pg.image.load("./assets/images_png/rules.png")
            rules_image = pg.transform.scale(rules_raw_image, (display_width/2.7,display_heigth/2.7))
            rules_rect = rules_image.get_rect()
            rules_rect.center = (display_width/2.7/2 , display_heigth/2)
            surface.blit(rules_image, rules_rect)


    def handle_weapon(self, given_card):
        if self.weapon_card != None:
            # Move current weapon to discards
            discarded_weapon_card = card(
                suit_and_value_path = self.weapon_card.full_name,
                position = self.weapon_card.rect.center,
                revealed = True,
                card_size=self.card_size
                )
            discarded_weapon_card.start_move_animation(
                start_position = self.weapon_position,
                end_position = self.discard_position
            )
            self.discard_cards.append(discarded_weapon_card)
            self.board_dungeon.add_discard(self.weapon_card.full_name)
            # Move posible kill pool to discrads
            if len(self.kill_cards) > 0:
                for kill_card in self.kill_cards:
                    discarded_kill_card = card(
                        suit_and_value_path = kill_card.full_name,
                        position = kill_card.rect.center,
                        revealed = True,
                        card_size=self.card_size
                        )
                    discarded_kill_card.start_move_animation(
                        start_position = kill_card.rect.center,
                        end_position = self.discard_position
                    )
                    self.discard_cards.append(discarded_kill_card)
                    self.board_dungeon.add_discard(kill_card.full_name)
                    # Empty kill card pool
                    self.kill_cards = list()      
        # Equip new weapon
        self.weapon_card = card(
            suit_and_value_path = given_card.full_name,
            position = given_card.rect.center,
            revealed = True,
            card_size=self.card_size)
        self.weapon_card.start_move_animation(
            start_position = given_card.rect.center,
            end_position = self.weapon_position
        )
        self.last_kill = 123456789

    def handle_potion(self, given_card):
        if self.current_health_points != self.maximum_health_points:
            self.dice_animation = True
            self.dice_animation_rotation = 'counterclockwise'
        self.current_health_points = min(self.maximum_health_points, self.current_health_points + given_card.value)
        # Add card to discards pool
        discarded_potion_card = card(suit_and_value_path = given_card.full_name,
                                            position = given_card.rect.center,
                                            revealed = True,
                                            card_size=self.card_size)
        discarded_potion_card.start_move_animation(
            start_position = given_card.rect.center,
            end_position = self.discard_position
        )
        self.discard_cards.append(discarded_potion_card)
        self.board_dungeon.add_discard(given_card.full_name)

    def handle_monster_barehand(self, given_card):
        damage_recieved = given_card.value
        self.dice_animation = True
        self.dice_animation_rotation = 'clockwise'
        # Add card to discards pool
        discarded_monster_card = card(suit_and_value_path = given_card.full_name,
                                            #position = self.discard_position,
                                            position = given_card.rect.center,
                                            revealed = True,
                                            card_size=self.card_size)
        discarded_monster_card.start_move_animation(
            start_position = given_card.rect.center,
            end_position = self.discard_position
        )
        self.discard_cards.append(discarded_monster_card)
        self.board_dungeon.add_discard(given_card.full_name)   
        # Calculate damage
        self.current_health_points = self.current_health_points - damage_recieved

    def handle_monster(self, given_card):# Card is Monster
        if self.weapon_card != None and self.last_kill >= given_card.value: # Weapon is equipped and can beat monster
            # Compute recieved damage
            damage_recieved = max(0, given_card.value - self.weapon_card.value)
            if damage_recieved>0:
                self.dice_animation = True
                self.dice_animation_rotation = 'clockwise'
            # Keep card as last kill
            self.last_kill = given_card.value
            # Add card to kill pool
            current_kill_card = card(suit_and_value_path = given_card.full_name,
                                                    #position = (self.kill_position[0], self.kill_position[0] + 40*len(self.kill_cards) + 40),
                                                    position = (self.kill_position[0], self.kill_position[1] + self.card_size[1]/6*len(self.kill_cards) + self.card_size[1]/5),
                                                    #position = given_card.rect.center,
                                                    revealed = True,
                                                    card_size=self.card_size
                                                    )
            current_kill_card.start_move_animation(
                start_position = given_card.rect.center,
                end_position = (self.kill_position[0], self.kill_position[1] + self.card_size[1]/6*len(self.kill_cards) + self.card_size[1]/5)
            )
            self.kill_cards.append(current_kill_card)
            self.current_health_points = self.current_health_points - damage_recieved
        else: # Is monster, no weapon or weapon cannot be used.
            self.handle_monster_barehand(given_card)
            
        # DEBUG HEAL
        #self.current_health_points = self.maximum_health_points -1

    def update(self):      
        # Check if any card got clicked
        cards_to_check = self.open_cards.copy()
        cards_to_check.append(self.dungeon_card)
        for checking_card in cards_to_check:
            if checking_card.left_clicked() == True and checking_card.revealed == True:
                checking_card.used = True
                self.current_open_card_positions.append(checking_card.initial_position)
                # Handle different cases based on card 
                if checking_card.suit == 'Diamonds': # Card is weapon
                    self.handle_weapon(checking_card)
                elif checking_card.suit == 'Hearts': # Card is potion
                    self.handle_potion(checking_card)
                else: # Card is monster
                    self.handle_monster(checking_card)
                # Remove card from open card pool
                self.open_cards.remove(checking_card)
            elif checking_card.right_clicked() == True and checking_card.revealed == True and self.weapon_card!= None:
                checking_card.used = True
                self.current_open_card_positions.append(checking_card.initial_position)
                self.handle_monster_barehand(checking_card)
                self.open_cards.remove(checking_card)
            elif checking_card.right_clicked() == True and checking_card.revealed == False:
                self.redraw_room()

    def end_game(self):
        self.change_mode = True
        if self.current_health_points>0:
            #print('YOU WON!')
            self.game_result = 'WIN'
            if self.current_health_points == self.maximum_health_points:
                score = self.maximum_health_points
                for remaining_card in self.open_cards:
                    if remaining_card.suit == 'Hearts':
                        score += remaining_card.value
            else:
                score = self.current_health_points
        else:
            #print('YOU LOST!')
            self.game_result = 'LOSE'
            score = 0
            for remaining_card in self.board_dungeon.base_deck:
                remaining_card_suit = remaining_card.split('_')[1].split('/')[1]
                if remaining_card_suit == 'Spades' or remaining_card_suit == 'Clubs':
                    score -= int(remaining_card.split('_')[2].split('.')[0])
        self.score = score
        with open('./save_files/highscore.txt', 'r') as highscore_file:
            vector = []
            for line in highscore_file:
                vector.append(int(line))
            vector.append(score)
            vector.sort(reverse=True)
        with open('./save_files/highscore.txt', 'w') as updated_highscore_file:
            for score in vector[:10]:
                updated_highscore_file.write(str(score)+'\n')


class button:
    def __init__(self, surface, name_and_path, position):
        display_width = surface.get_width()
        display_heigth = surface.get_height()
        self.button_width = display_width/4
        self.button_height = display_heigth/8
        button_raw_image = pg.image.load(name_and_path)
        self.button_image = pg.transform.scale(button_raw_image, (self.button_width, self.button_height))
        self.button_image_alternative = None
        self.rect = self.button_image.get_rect()
        self.rect.center = position
        self.click_sound = pg.mixer.Sound("./assets/sound_effects/sound_click.wav")
        self.button_click_buffer_max = 5
        self.button_click_buffer = self.button_click_buffer_max
    
    def set_alternative_image(self, name_and_path):
        button_raw_image = pg.image.load(name_and_path)
        self.button_image_alternative = pg.transform.scale(button_raw_image, (self.button_width, self.button_height))

    def draw(self, surface):
        surface.blit(self.button_image, self.rect)

    def hover(self):
        pass

    def left_clicked(self):
        mouse_buttons = pg.mouse.get_pressed()
        mouse_position = pg.mouse.get_pos()
        if mouse_buttons == (True, False, False): # Left click happened
            if self.rect.collidepoint(mouse_position): # Click happened inside button boundaries.
                if self.button_click_buffer == self.button_click_buffer_max:
                    self.click_sound.play()
                    self.button_click_buffer = 0
                    return True
                else:
                    self.button_click_buffer += 1
                    return False


class backround:
    def __init__(self, surface):
        display_width = surface.get_width()
        display_heigth = surface.get_height()
        #GREEN = (20, 100, 20)
        #surface.fill(GREEN)
        raw_backround_image = pg.image.load("./assets/textures_png/woodTexture.png")

        # raw_backround_image.set_alpha(100) # Changes opacity of image
        
        backround_image = pg.transform.scale(raw_backround_image, (display_width,display_heigth))
        backround_rect = backround_image.get_rect()
        surface.blit(backround_image, backround_rect)
        # Draw backround effects and animations
        #backround_animations(surface)
        pass

def draw_backround(surface):
    display_width = surface.get_width()
    display_heigth = surface.get_height()
    #GREEN = (20, 100, 20)
    #surface.fill(GREEN)
    raw_backround_image = pg.image.load("./assets/textures_png/woodTexture.png")

    # raw_backround_image.set_alpha(100) # Changes opacity of image
    
    backround_image = pg.transform.scale(raw_backround_image, (display_width,display_heigth))
    backround_rect = backround_image.get_rect()
    surface.blit(backround_image, backround_rect)
    # Draw backround effects and animations
    #backround_animations(surface)
    

def draw_transparent_circle(surface, center, radius, color, alpha_level):
    pg_gfxdraw.filled_circle(surface, center[0],center[1],radius,(color[0],color[1],color[2],alpha_level))


def backround_animations(surface):
    display_width = surface.get_width()
    display_heigth = surface.get_height()
    draw_transparent_circle(surface, (0,0), 100, (255,120,0), 100)
    draw_transparent_circle(surface, (0,0), 200, (255,120,0), 100)
    draw_transparent_circle(surface, (0,0), 300, (255,120,0), 100)


class start_screen:
    def __init__(self, surface):
        self.change_mode = False
        self.next_mode = None
        # Other modes: 'game_screen', 'choose_class_screen', 'options_screen', 'highscore_screen', 'quit'
        display_width = surface.get_width()
        display_heigth = surface.get_height()

        # Setup buttons
        new_game_button_position = (display_width/2 , 2 * display_heigth/8)
        self.new_game_button = button(surface, "./assets/buttons_png/new_game_button.png", new_game_button_position)

        #choose_class_button_position = (display_width/2 , 3 * display_heigth/8 + 10)
        #self.choose_class_button = button(surface, "./assets/buttons_png/choose_class_button.png", choose_class_button_position)
        highscore_button_position = (display_width/2 , 3 * display_heigth/8 + 10)
        self.highscore_button = button(surface, "./assets/buttons_png/highscore_button.png", highscore_button_position)

        options_button_position = (display_width/2 , 4 * display_heigth/8 + 20)
        self.options_button = button(surface, "./assets/buttons_png/options_button.png", options_button_position)

        #highscore_button_position = (display_width/2 , 5 * display_heigth/8 + 30)
        #self.highscore_button = button(surface, "./assets/buttons_png/highscore_button.png", highscore_button_position)
        credits_button_position = (display_width/2 , 5 * display_heigth/8 + 30)
        self.credits_button = button(surface, "./assets/buttons_png/credits_button.png", credits_button_position)

        quit_button_position = (display_width/2 , 6 * display_heigth/8 + 40)
        self.quit_button = button(surface, "./assets/buttons_png/quit_button.png", quit_button_position)


    def draw(self, surface):
        display_width = surface.get_width()
        display_heigth = surface.get_height()

        # Draw title
        title_width = display_width/2
        title_height = display_heigth/10

        scoundrel_raw_image = pg.image.load("./assets/images_png/SCOUNDREL_RAW.png")
        scoundrel_scaled = pg.transform.scale(scoundrel_raw_image, (title_width,title_height))
        scoundrel_rect = scoundrel_scaled.get_rect()
        scoundrel_rect.center = (display_width/2 , display_heigth/10)

        # Draw title
        surface.blit(scoundrel_scaled, scoundrel_rect)
        # Draw buttons
        self.new_game_button.draw(surface)
        self.highscore_button.draw(surface)
        #self.choose_class_button.draw(surface)
        self.options_button.draw(surface)
        self.credits_button.draw(surface)
        self.quit_button.draw(surface)


    def update(self):
        if self.new_game_button.left_clicked() == True:

            open_gate_sfx = pg.mixer.Sound("./assets/sound_effects/Gate_Open_00.mp3")
            open_gate_sfx.play()

            self.change_mode = True
            self.next_mode = 'game_screen'
        elif self.highscore_button.left_clicked() == True:
            self.change_mode = True
            self.next_mode = 'highscore_screen'
        #elif self.choose_class_button.left_clicked() == True:
        #    self.change_mode = True
        #    self.next_mode = 'choose_class_screen'
        elif self.options_button.left_clicked() == True:
            self.change_mode = True
            self.next_mode = 'options_screen'
        elif self.credits_button.left_clicked() == True:
            self.change_mode = True
            self.next_mode = 'credits_screen'
        
        elif self.quit_button.left_clicked() == True:
            self.change_mode = True
            self.next_mode = 'quit'


class end_screen:
    def __init__(self, surface, game_result):
        self.game_result = game_result
        self.score = str(1234)
        self.change_mode = False
        #self.center = (0,0)
        
        display_width = surface.get_width()
        display_heigth = surface.get_height()

        title_width = display_width/2
        title_height = display_heigth/10

        if self.game_result == 'WIN':
            result_title_raw_image = pg.image.load("./assets/images_png/you_won.png")
        elif self.game_result == 'LOSE':
            result_title_raw_image = pg.image.load("./assets/images_png/you_lost.png")
        else:
            print('error end screen generation, wrong game result')
            print('self.game_result: ',self.game_result)
        self.result_title_scaled = pg.transform.scale(result_title_raw_image, (title_width,title_height))
        self.title_rect = self.result_title_scaled.get_rect()
        self.title_rect.center = (display_width/2 , display_heigth/10)

        self.score_button_position = (display_width/2 , 2 * display_heigth/8)
        self.back_to_start_button_position = (display_width/2 + display_width/4 + 30, 2 * display_heigth/8 )

        self.score_button = button(surface, "./assets/buttons_png/score_button.png", self.score_button_position)
        self.back_to_start_button = button(surface, "./assets/buttons_png/back_to_start_screen_button.png", self.back_to_start_button_position)
    
    def draw(self, surface):
        display_width = surface.get_width()
        display_heigth = surface.get_height()

        surface.blit(self.score_button.button_image, self.score_button.rect)
        surface.blit(self.back_to_start_button.button_image, self.back_to_start_button.rect)
        surface.blit(self.result_title_scaled, self.title_rect)

        # Draw score
        score_font = pg.font.SysFont('Liberation Sans', 40)
        score_text = score_font.render(self.score, True, (1, 1, 1))
        score_points_position = (display_width/2 - 50, 2 * display_heigth/8 - 10)
        surface.blit(score_text, score_points_position)
    
    def update(self):
        if self.back_to_start_button.left_clicked() == True:
            self.change_mode = True


class choose_class_screen:
    def __init__(self, surface):
        display_width = surface.get_width()
        display_heigth = surface.get_height()
        self.back_button_position = (display_width/2 + display_width/4 + 30, 2 * display_heigth/8)
        self.back_button = button(surface, "./assets/buttons_png/back_button.png", self.back_button_position)
        self.change_mode = False
    def update(self):
        if self.back_button.left_clicked() == True:
            self.change_mode = True
    def draw(self, surface):
        surface.blit(self.back_button.button_image, self.back_button.rect)


class options_screen:
    def __init__(self, surface):
        display_width = surface.get_width()
        display_heigth = surface.get_height()
        self.rules_button_position = (display_width/2 , 2 * display_heigth/8)
        self.rules_button = button(surface, "./assets/buttons_png/rules_button_on.png", self.rules_button_position)
        self.rules_button.set_alternative_image("./assets/buttons_png/rules_button_off.png")
        self.rules_on = False
        self.music_button_position = (display_width/2 , 3 * display_heigth/8 + 10)
        self.music_button = button(surface, "./assets/buttons_png/music_button_on.png", self.music_button_position)
        self.music_button.set_alternative_image("./assets/buttons_png/music_button_off.png")
        self.music_on = False
        self.back_button_position = (display_width/2 + display_width/4 + 30, 2 * display_heigth/8)
        self.back_button = button(surface, "./assets/buttons_png/back_button.png", self.back_button_position)
        self.change_mode = False

    def update(self):
        if self.back_button.left_clicked() == True:
            self.change_mode = True
        elif self.music_button.left_clicked() == True:
            self.music_on = not self.music_on
        elif self.rules_button.left_clicked() == True:
            self.rules_on = not self.rules_on
        
    def draw(self, surface):
        surface.blit(self.back_button.button_image, self.back_button.rect)
        if self.music_on:
            surface.blit(self.music_button.button_image, self.music_button.rect)
        else:
            surface.blit(self.music_button.button_image_alternative, self.music_button.rect)
        if self.rules_on:
            surface.blit(self.rules_button.button_image, self.rules_button.rect)
        else:
            surface.blit(self.rules_button.button_image_alternative, self.rules_button.rect)


class credits_screen:
    def __init__(self, surface):
        display_width = surface.get_width()
        display_heigth = surface.get_height()
        self.back_button_position = (display_width/2 + display_width/4 + 30, 2 * display_heigth/8)
        self.back_button = button(surface, "./assets/buttons_png/back_button.png", self.back_button_position)
        self.change_mode = False
    def update(self):
        if self.back_button.left_clicked() == True:
            self.change_mode = True
    def draw(self, surface):
        display_width = surface.get_width()
        display_heigth = surface.get_height()

        credits_title_position = (display_width/2 - 100, display_heigth/10)
        credits_position = (display_width/2, display_heigth/12 + display_heigth/12)

        surface.blit(self.back_button.button_image, self.back_button.rect)

        # Draw credits
        credits_title_font = pg.font.SysFont('Liberation Sans', 40)
        credits_title_text = credits_title_font.render('CREDITS:', True, (250, 250, 250))
        credits_title_text.get_rect(center=credits_title_position)
        surface.blit(credits_title_text, credits_title_position)

        highscore_font = pg.font.SysFont('Liberation Sans', 20)
        with open('./asset_credits.txt', 'r') as credits_file:
            i = 0
            for line in credits_file:
                highscore_text = highscore_font.render(line[:-1], True, (250, 250, 250))
                highscore_rect = highscore_text.get_rect(center=( credits_position[0], credits_position[1] + i*display_heigth/34))
                i += 1
                surface.blit(highscore_text, highscore_rect)


class highscore_screen:
    def __init__(self, surface):
        display_width = surface.get_width()
        display_heigth = surface.get_height()
        self.back_button_position = (display_width/2 + display_width/4 + 30, 2 * display_heigth/8)
        self.back_button = button(surface, "./assets/buttons_png/back_button.png", self.back_button_position)
        self.change_mode = False
    def update(self):
        if self.back_button.left_clicked() == True:
            self.change_mode = True
    def draw(self, surface):
        display_width = surface.get_width()
        display_heigth = surface.get_height()
        highscore_title_position = (display_width/2 - 100, display_heigth/10)
        highscores_position = (display_width/2, display_heigth/10 + display_heigth/10)

        surface.blit(self.back_button.button_image, self.back_button.rect)

        # Draw highscores
        highscore_title_font = pg.font.SysFont('Liberation Sans', 40)
        highscore_title_text = highscore_title_font.render('HIGHSCORE', True, (250, 250, 250))
        highscore_title_text.get_rect(center=highscore_title_position)
        surface.blit(highscore_title_text, highscore_title_position)

        highscore_font = pg.font.SysFont('Liberation Sans', 40)
        with open('./save_files/highscore.txt', 'r') as highscore_file:
            i = 0
            for line in highscore_file:
                #print(line)
                highscore_text = highscore_font.render(line[:-1], True, (250, 250, 250))
                highscore_rect = highscore_text.get_rect(center=( highscores_position[0], highscores_position[1] + i*display_heigth/12))
                i += 1
                surface.blit(highscore_text, highscore_rect)

        #highscore_text = score_font.render(self.score, True, (1, 1, 1))
        #score_points_position = (display_width/2 - 50, 2 * display_heigth/8 - 10)
        #surface.blit(score_text, score_points_position)

class game_wrapper:
    def __init__(self, surface):
        self.game_state = 'start_screen'
        self.music_on = False
        self.rules_on = True
        self.start = start_screen(surface)
        #self.choose_class = choose_class_screen(surface)
        self.highscore = highscore_screen(surface)
        self.options = options_screen(surface)
        self.options.rules_on = self.rules_on
        self.options.music_on = self.music_on
        self.credits = credits_screen(surface)
        self.backround_music = pg.mixer.Sound("./assets/sound_effects/pirate_tavern_loop.wav")
        #self.start_music()
    
    def start_music(self):
        self.backround_music.set_volume(0.1)
        self.backround_music.play(loops=-1)

    def update(self, surface):
        if self.music_on == False:
            #self.backround_music.stop()
            self.backround_music.fadeout(60)
        else:
            if self.backround_music.get_num_channels() == 0: # i.e. sound is not already playing
                self.backround_music.play(loops=-1)

        if self.game_state == 'start_screen':
            self.start.update()
            if self.start.change_mode == True:
                #self.game = gameboard(surface)
                self.start.change_mode = False
                self.game_state = self.start.next_mode
                if self.game_state == 'game_screen':
                    settings = [self.rules_on]
                    self.game = gameboard(surface, settings)
        elif self.game_state == 'end_screen':
            self.end.update()
            if self.end.change_mode == True:
                self.end.change_mode = False
                self.game_state = 'start_screen'

        elif self.game_state == 'game_screen':
            self.game.update()
            if len(self.game.current_open_card_positions)>=3:
                self.game.fill(self.game.current_open_card_positions)
                self.game.current_open_card_positions = list()
            if self.game.current_health_points <=0:
                self.game.end_game()
            if self.game.change_mode == True:
                self.end = end_screen(surface, self.game.game_result)
                self.game_state = 'end_screen'
                self.end.score = str(self.game.score)

        elif self.game_state == 'choose_class_screen':
            self.choose_class.update()
            if self.choose_class.change_mode == True:
                self.choose_class.change_mode = False
                self.game_state = 'start_screen'

        elif self.game_state == 'options_screen':
            self.options.update()
            if self.options.change_mode == True:
                self.options.change_mode = False
                self.game_state = 'start_screen'
            self.music_on = self.options.music_on
            self.rules_on = self.options.rules_on

        elif self.game_state == 'highscore_screen':
            self.highscore.update()
            if self.highscore.change_mode == True:
                self.highscore.change_mode = False
                self.game_state = 'start_screen'

        elif self.game_state == 'credits_screen':
            self.credits.update()
            if self.credits.change_mode == True:
                self.credits.change_mode = False
                self.game_state = 'start_screen'
            #pass
        elif self.game_state == 'quit':
            pg.quit()
            sys.exit()
        else:
            print('screen_state_error, update')
            pg.quit()
            sys.exit()

    def draw(self, surface):
        draw_backround(surface)
        if self.game_state == 'start_screen':
            self.start.draw(surface)

        elif self.game_state == 'credits_screen':
            self.credits.draw(surface)

        elif self.game_state == 'end_screen':
            self.end.draw(surface)

        elif self.game_state == 'game_screen':
            self.game.draw(surface)

        elif self.game_state == 'choose_class_screen':
            self.choose_class.draw(surface)

        elif self.game_state == 'options_screen':
            self.options.draw(surface)

        elif self.game_state == 'highscore_screen':
            self.highscore.draw(surface)

        elif self.game_state == 'quit':
            pg.quit()
            sys.exit()

        else:
            print('screen_state_error, draw')
            print('self.game_state: ',self.game_state)
            pg.quit()
            sys.exit()

def main():
    # load assets
    icon = pg.image.load("./assets/images_png/game_icon.png")

    # Initialize pygame engine
    pg.init()
    
    # Screen information
    SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
    #SCREEN_WIDTH, SCREEN_HEIGHT = 1920 , 1080
    #SCREEN_WIDTH, SCREEN_HEIGHT = 1760 , 900
    
    #SCREEN_WIDTH, SCREEN_HEIGHT = 1280 , 800
    
    #SCREEN_WIDTH, SCREEN_HEIGHT = 800 , 600
    #SCREEN_WIDTH, SCREEN_HEIGHT = 500 , 500

    # Define colours used
    GREEN = (20, 100, 20)

    # Setup display
    #DISPLAYSURF = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    DISPLAYSURF = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pg.SRCALPHA)
    DISPLAYSURF.fill(GREEN)

    draw_backround(DISPLAYSURF)

    pg.display.set_caption("Game of the year (2026)!")
    pg.display.set_icon(icon)
    #display_surface = pg.display.set_mode((1080,1920))

    FPS = pg.time.Clock()
    FramesPerSecond = 60
    FPS.tick(FramesPerSecond)

    # Initiallize game
    GAME = game_wrapper(DISPLAYSURF)

    # Start game
    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                sys.exit()

        GAME.update(surface=DISPLAYSURF)
        GAME.draw(surface=DISPLAYSURF)
            
        # Update display
        pg.display.update()
        FPS.tick(FramesPerSecond)


if __name__=='__main__':
    main()

