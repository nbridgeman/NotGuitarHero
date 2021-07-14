import pygame
import random

pygame.init()
pygame.font.init()
pygame.mixer.init()
# pygame.mixer.music.load("DrumBeat.mp3")

from pygame.locals import (
    RLEACCEL,
    K_a,
    K_s,
    K_d,
    K_f,
    K_g,
    K_j,
    K_ESCAPE,
    KEYDOWN,
    KEYUP,
    QUIT,
)

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
COL_A = 45
COL_S = 135
COL_D = 225
COL_F = 315
COL_G = 405
COLS = [COL_A, COL_S, COL_D, COL_F, COL_G]

GAME_FONT = pygame.font.SysFont("Calibri", 24)

class PlayerNote(pygame.sprite.Sprite):
    def __init__(self, column, color):
        super(PlayerNote, self).__init__()
        self.surf = pygame.Surface((64, 64))
        self.color = color
        self.rect = self.surf.get_rect()
        self.rect.center = (column, SCREEN_HEIGHT - 64)
        self.active = False

    def show(self):
        self.surf.fill(self.color)
        self.active = True

    def hide(self):
        self.surf.fill((0, 0, 0))
        self.active = False

    def is_active(self):
        return self.active

class PlayerStrum(pygame.sprite.Sprite):
    def __init__(self):
        super(PlayerStrum, self).__init__()
        self.surf = pygame.Surface((450, 8))
        self.surf.set_alpha(100)
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.rect.center = (COL_D, SCREEN_HEIGHT - 64)
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_time >= 150:
            self.kill()

class Note(pygame.sprite.Sprite):
    def __init__(self):
        super(Note, self).__init__()
        self.surf = pygame.Surface((64, 64))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.column = random.choice(COLS)
        self.rect.center = (self.column, 0)

    def update(self):
        self.rect.move_ip(0, 5)
        if self.rect.top >= SCREEN_HEIGHT:
            self.kill()
            return True
        return False

    def get_col(self):
        return self.column

class Score(pygame.sprite.Sprite):
    def __init__(self):
        super(Score, self).__init__()
        self.surf = pygame.Surface((64, 32))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.notes_spawned = 1
        self.notes_hit = 1
        self.score = (self.notes_hit / self.notes_spawned) * 100
        self.surf = GAME_FONT.render(str.format('{0:.2f}', self.score) + '%', False, (0, 0, 0))
        self.rect.center = ((525, 180))

    def add_spawned_note(self):
        self.notes_spawned += 1

    def add_hit_note(self):
        self.notes_hit += 1

    def update(self):
        self.score = (self.notes_hit / self.notes_spawned) * 100
        self.surf = GAME_FONT.render(str.format('{0:.2f}', self.score) + '%', False, (0, 0, 0))

def note_is_active(note, a_note, s_note, d_note, f_note, g_note):
    if (note.get_col() == COL_A and a_note.is_active()) or (note.get_col() == COL_S and s_note.is_active()) or (note.get_col() == COL_D and d_note.is_active()) or (note.get_col() == COL_F and f_note.is_active()) or (note.get_col() == COL_G and g_note.is_active()):
        return True
    else:
        return False

def check_collision(strum, notes, a_note, s_note, d_note, f_note, g_note, score):
    collisions = pygame.sprite.spritecollide(strum, notes, False)
    for note in collisions:
        if note_is_active(note, a_note, s_note, d_note, f_note, g_note):
            note.kill()
            score.add_spawned_note()
            score.add_hit_note()
            score.update()

def main():
    background = pygame.image.load("background.png")
    a_note = PlayerNote(COL_A, ((0, 255, 0)))
    s_note = PlayerNote(COL_S, ((255, 0, 0)))
    d_note = PlayerNote(COL_D, ((255, 255, 0)))
    f_note = PlayerNote(COL_F, ((0, 0, 255)))
    g_note = PlayerNote(COL_G, ((255, 165, 0)))
    score = Score()
    notes = pygame.sprite.Group()
    player_strums = pygame.sprite.Group()
    player_notes = pygame.sprite.Group()
    player_notes.add(a_note, s_note, d_note, f_note, g_note)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player_notes, score)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    ADDNOTE = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDNOTE, 750)
    # pygame.mixer.music.play(-1, 0, 0)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_a:
                    a_note.show()
                if event.key == K_s:
                    s_note.show()
                if event.key == K_d:
                    d_note.show()
                if event.key == K_f:
                    f_note.show()
                if event.key == K_g:
                    g_note.show()
                if event.key == K_j:
                    strum = PlayerStrum()
                    player_strums.add(strum)
                    all_sprites.add(strum)
            elif event.type == KEYUP:
                if event.key == K_a:
                    a_note.hide()
                if event.key == K_s:
                    s_note.hide()
                if event.key == K_d:
                    d_note.hide()
                if event.key == K_f:
                    f_note.hide()
                if event.key == K_g:
                    g_note.hide()
            elif event.type == QUIT:
                running = False
            elif event.type == ADDNOTE:
                new_note = Note()
                notes.add(new_note)
                all_sprites.add(new_note)

        screen.blit(background, (0, 0))
        for note in notes:
            missed = note.update()
            if missed:
                score.add_spawned_note()
                score.update()
        for strum in player_strums:
            strum.update()
        for strum in player_strums:
            check_collision(strum, notes, a_note, s_note, d_note, f_note, g_note, score)
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()
