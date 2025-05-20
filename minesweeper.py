import pygame
import random
import sys
import time
from pygame import mixer

# Oyun ayarları
pygame.init()
pygame.display.set_caption("Modern Mayın Tarlası")
clock = pygame.time.Clock()
mixer.init()

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
BACKGROUND = (240, 240, 240)
BORDER = (180, 180, 180)

# Zorluk Seviyeleri
DIFFICULTY = {
    "KOLAY": {"size": (8, 8), "mines": 10, "cell_size": 60},
    "NORMAL": {"size": (16, 16), "mines": 40, "cell_size": 40},
    "ZOR": {"size": (24, 16), "mines": 99, "cell_size": 35}
}

# Görseller ve Sesler
def load_resources():
    # Görseller
    images = {}
    
    # Görsel dosyalarını yüklemeyi dene, yoksa kendimiz oluştur
    try:
        images["mine"] = pygame.transform.scale(pygame.image.load("mine.png").convert_alpha(), (32, 32))
    except (FileNotFoundError, pygame.error):
        images["mine"] = pygame.transform.scale(create_mine_image(), (32, 32))
        
    try:
        images["flag"] = pygame.transform.scale(pygame.image.load("flag.png").convert_alpha(), (32, 32))
    except (FileNotFoundError, pygame.error):
        images["flag"] = pygame.transform.scale(create_flag_image(), (32, 32))
        
    try:
        images["explosion"] = pygame.transform.scale(pygame.image.load("explosion.png").convert_alpha(), (32, 32))
    except (FileNotFoundError, pygame.error):
        images["explosion"] = pygame.transform.scale(create_explosion_image(), (32, 32))
    
    # Yazı tipleri
    fonts = {
        "small": pygame.font.Font(None, 24),
        "medium": pygame.font.Font(None, 32),
        "large": pygame.font.Font(None, 48),
        "title": pygame.font.Font(None, 72)
    }
    
    # Ses efektleri (opsiyonel)
    sounds = {}
    try:
        sounds["click"] = mixer.Sound("click.wav")
        sounds["explosion"] = mixer.Sound("explosion.wav")
        sounds["win"] = mixer.Sound("win.wav")
        sounds["flag"] = mixer.Sound("flag.wav")
    except:
        pass
    
    return images, fonts, sounds

# Eğer görüntü dosyaları bulunamazsa, bu fonksiyonlar basit görseller oluşturur
def create_mine_image():
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(surface, BLACK, (16, 16), 12)
    pygame.draw.line(surface, BLACK, (16, 4), (16, 28), 3)
    pygame.draw.line(surface, BLACK, (4, 16), (28, 16), 3)
    pygame.draw.line(surface, BLACK, (8, 8), (24, 24), 3)
    pygame.draw.line(surface, BLACK, (8, 24), (24, 8), 3)
    return surface

def create_flag_image():
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.rect(surface, BLACK, (14, 16, 4, 14))
    pygame.draw.rect(surface, BLACK, (8, 28, 16, 4))
    pygame.draw.polygon(surface, RED, [(18, 6), (18, 20), (6, 13)])
    return surface

def create_explosion_image():
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(surface, RED, (16, 16), 14)
    pygame.draw.circle(surface, ORANGE, (16, 16), 10)
    pygame.draw.circle(surface, YELLOW, (16, 16), 6)
    return surface

class Cell:
    def __init__(self, row, col, cell_size):
        self.row = row
        self.col = col
        self.size = cell_size
        self.mine = False
        self.revealed = False
        self.flagged = False
        self.value = 0  # Çevredeki mayın sayısı
        
    def draw(self, screen, images, fonts, x_offset, y_offset, reveal_mines=False):
        x = self.col * self.size + x_offset
        y = self.row * self.size + y_offset
        
        # Temel kare
        if self.revealed:
            pygame.draw.rect(screen, LIGHT_GRAY, (x, y, self.size, self.size))
        else:
            # 3D efekti için
            pygame.draw.rect(screen, GRAY, (x, y, self.size, self.size))
            pygame.draw.rect(screen, WHITE, (x, y, self.size, self.size), 1)
            pygame.draw.line(screen, DARK_GRAY, (x + self.size - 1, y), (x + self.size - 1, y + self.size - 1), 1)
            pygame.draw.line(screen, DARK_GRAY, (x, y + self.size - 1), (x + self.size - 1, y + self.size - 1), 1)
        
        # Çerçeve
        pygame.draw.rect(screen, BORDER, (x, y, self.size, self.size), 1)
        
        # İçerik
        if self.revealed:
            if self.mine:
                image_rect = images["explosion"].get_rect(center=(x + self.size // 2, y + self.size // 2))
                screen.blit(images["explosion"], image_rect)
            elif self.value > 0:
                # Sayı renkleri
                colors = [BLUE, GREEN, RED, PURPLE, CYAN, YELLOW, BLACK, GRAY]
                text = fonts["medium"].render(str(self.value), True, colors[self.value-1])
                text_rect = text.get_rect(center=(x + self.size // 2, y + self.size // 2))
                screen.blit(text, text_rect)
        elif self.flagged:
            image_rect = images["flag"].get_rect(center=(x + self.size // 2, y + self.size // 2))
            screen.blit(images["flag"], image_rect)
        # X tuşu basıldığında mayınları gösterme
        elif reveal_mines and self.mine:
            image_rect = images["mine"].get_rect(center=(x + self.size // 2, y + self.size // 2))
            screen.blit(images["mine"], image_rect)
            
    def contains_point(self, point, x_offset, y_offset):
        x, y = point
        cell_x = self.col * self.size + x_offset
        cell_y = self.row * self.size + y_offset
        return (cell_x <= x < cell_x + self.size) and (cell_y <= y < cell_y + self.size)

class MinesweeperGame:
    def __init__(self, difficulty="NORMAL"):
        self.set_difficulty(difficulty)
        self.reset_game()
        self.images, self.fonts, self.sounds = load_resources()
        
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        config = DIFFICULTY[difficulty]
        self.rows, self.cols = config["size"]
        self.mines_count = config["mines"]
        self.cell_size = config["cell_size"]
        self.screen_width = self.cols * self.cell_size + 40
        self.screen_height = self.rows * self.cell_size + 100
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
    def reset_game(self):
        # Oyun tahtası oluştur
        self.board = [[Cell(row, col, DIFFICULTY[self.difficulty]["cell_size"]) 
                      for col in range(self.cols)] 
                      for row in range(self.rows)]
        self.game_over = False
        self.win = False
        self.mines_placed = False
        self.start_time = None
        self.elapsed_time = 0
        self.flags_placed = 0
        self.reveal_mines = False  # X tuşu için eklenen değişken
    
    def place_mines(self, first_row, first_col):
        # İlk tıklamadan sonra mayınları yerleştir (ilk tıklama güvenli olsun)
        mines_placed = 0
        while mines_placed < self.mines_count:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            
            # İlk tıklanan hücre ve çevresine mayın koymama
            if (abs(row - first_row) <= 1 and abs(col - first_col) <= 1) or self.board[row][col].mine:
                continue
                
            self.board[row][col].mine = True
            mines_placed += 1
        
        # Hücre değerlerini hesapla (çevresindeki mayın sayısı)
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.board[row][col].mine:
                    # Çevredeki mayınları say
                    for r in range(max(0, row-1), min(self.rows, row+2)):
                        for c in range(max(0, col-1), min(self.cols, col+2)):
                            if self.board[r][c].mine:
                                self.board[row][col].value += 1
    
    def reveal_cell(self, row, col):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
            
        cell = self.board[row][col]
        
        # Zaten açık veya bayraklı hücreleri atla
        if cell.revealed or cell.flagged:
            return
            
        cell.revealed = True
        
        # Mayına tıklandıysa oyun biter
        if cell.mine:
            self.game_over = True
            self.play_sound("explosion")
            return
            
        # Değeri 0 olan hücrelerde rekürsif olarak komşuları da aç
        if cell.value == 0:
            for r in range(max(0, row-1), min(self.rows, row+2)):
                for c in range(max(0, col-1), min(self.cols, col+2)):
                    if (r, c) != (row, col):
                        self.reveal_cell(r, c)
        
        self.play_sound("click")
        self.check_win()
    
    def toggle_flag(self, row, col):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
            
        cell = self.board[row][col]
        
        if not cell.revealed:
            cell.flagged = not cell.flagged
            self.flags_placed += 1 if cell.flagged else -1
            self.play_sound("flag")
            self.check_win()  # Bayrak koyunca/kaldırınca da kazanma durumunu kontrol et
    
    def check_win(self):
        # Kazanma durumunu kontrol et
        
        # Tüm mayınlar bayraklandıysa kazanma durumu
        all_mines_flagged = True
        correct_flags = 0
        
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.board[row][col]
                if cell.mine and not cell.flagged:
                    all_mines_flagged = False
                if cell.mine and cell.flagged:
                    correct_flags += 1
        
        # Tüm mayınlar doğru şekilde işaretlendiyse ve bayrak sayısı mayın sayısına eşitse
        if all_mines_flagged and correct_flags == self.mines_count and self.flags_placed == self.mines_count:
            self.win = True
            self.game_over = True
            self.play_sound("win")
            return
            
        # Alternatif kontrol: Mayın olmayan tüm hücreler açıldıysa oyun kazanılır
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.board[row][col]
                if not cell.mine and not cell.revealed:
                    return
        
        self.win = True
        self.game_over = True
        self.play_sound("win")
    
    def reveal_all_mines(self):
        # Tüm mayınları göster
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col].mine:
                    self.board[row][col].revealed = True
    
    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass
    
    def draw(self):
        self.screen.fill(BACKGROUND)
        
        # Oyun tahtası ortalama
        x_offset = (self.screen_width - (self.cols * self.cell_size)) // 2
        y_offset = (self.screen_height - (self.rows * self.cell_size)) // 2 + 30
        
        # Üst bilgi
        self.draw_header(x_offset, y_offset)
        
        # Tahtayı çiz
        for row in range(self.rows):
            for col in range(self.cols):
                self.board[row][col].draw(self.screen, self.images, self.fonts, x_offset, y_offset, self.reveal_mines)
        
        # Oyun sonu ekranı
        if self.game_over:
            self.draw_game_over(x_offset, y_offset)
    
    def draw_header(self, x_offset, y_offset):
        # Süre
        time_text = f"Süre: {int(self.elapsed_time)}" if self.start_time else "Süre: 0"
        time_surface = self.fonts["medium"].render(time_text, True, BLACK)
        self.screen.blit(time_surface, (10, 10))
        
        # Kalan mayın sayısı
        mines_text = f"Mayınlar: {self.mines_count - self.flags_placed}"
        mines_surface = self.fonts["medium"].render(mines_text, True, BLACK)
        mines_rect = mines_surface.get_rect(right=self.screen_width - 10, top=10)
        self.screen.blit(mines_surface, mines_rect)
        
        # Zorluk seviyesi
        difficulty_text = f"Zorluk: {self.difficulty}"
        difficulty_surface = self.fonts["small"].render(difficulty_text, True, BLACK)
        difficulty_rect = difficulty_surface.get_rect(centerx=self.screen_width // 2, top=10)
        self.screen.blit(difficulty_surface, difficulty_rect)
        
        # X tuşu bilgisi
        if not self.game_over:
            hint_text = "X: Mayınları göster (hile)"
            hint_surface = self.fonts["small"].render(hint_text, True, DARK_GRAY)
            hint_rect = hint_surface.get_rect(centerx=self.screen_width // 2, top=30)
            self.screen.blit(hint_surface, hint_rect)
    
    def draw_game_over(self, x_offset, y_offset):
        # Yarı saydam arka plan
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Mesaj
        message = "KAZANDINIZ!" if self.win else "KAYBETTİNİZ!"
        message_surface = self.fonts["large"].render(message, True, WHITE)
        message_rect = message_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
        self.screen.blit(message_surface, message_rect)
        
        # Süre bilgisi
        time_text = f"Tamamlama süresi: {int(self.elapsed_time)} saniye" if self.win else ""
        if self.win:
            time_surface = self.fonts["medium"].render(time_text, True, WHITE)
            time_rect = time_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
            self.screen.blit(time_surface, time_rect)
        
        # Yeniden oyna düğmesi
        replay_text = "Yeniden oynamak için ENTER tuşuna basın"
        replay_surface = self.fonts["medium"].render(replay_text, True, WHITE)
        replay_rect = replay_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 60))
        self.screen.blit(replay_surface, replay_rect)
        
        # Zorluk değiştirme bilgisi
        difficulty_text = "Zorluk değiştirmek için 1 (Kolay), 2 (Normal) veya 3 (Zor) tuşlarına basın"
        difficulty_surface = self.fonts["small"].render(difficulty_text, True, WHITE)
        difficulty_rect = difficulty_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))
        self.screen.blit(difficulty_surface, difficulty_rect)
    
    def draw_start_screen(self):
        self.screen.fill(BACKGROUND)
        
        # Başlık
        title_text = "MAYIN TARLASI"
        title_surface = self.fonts["title"].render(title_text, True, BLACK)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 80))
        self.screen.blit(title_surface, title_rect)
        
        # Başlangıç talimatı
        start_text = "Başlamak için herhangi bir tuşa basın"
        start_surface = self.fonts["medium"].render(start_text, True, BLACK)
        start_rect = start_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(start_surface, start_rect)
        
        # Zorluk seviyeleri
        difficulty_text = "Zorluk seçmek için: 1 (Kolay), 2 (Normal), 3 (Zor)"
        difficulty_surface = self.fonts["small"].render(difficulty_text, True, BLACK)
        difficulty_rect = difficulty_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        self.screen.blit(difficulty_surface, difficulty_rect)
        
        # Kontroller
        controls_text = "Sol tık: Hücre aç | Sağ tık: Bayrak koy/kaldır | X: Mayınları göster (hile)"
        controls_surface = self.fonts["small"].render(controls_text, True, BLACK)
        controls_rect = controls_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
        self.screen.blit(controls_surface, controls_rect)
        
        # Geliştirici bilgisi
        dev_text = "Modern Mayın Tarlası v1.1"
        dev_surface = self.fonts["small"].render(dev_text, True, DARK_GRAY)
        dev_rect = dev_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        self.screen.blit(dev_surface, dev_rect)
        
        pygame.display.flip()
    
    def handle_click(self, pos, right_click=False):
        if self.game_over:
            return
            
        x_offset = (self.screen_width - (self.cols * self.cell_size)) // 2
        y_offset = (self.screen_height - (self.rows * self.cell_size)) // 2 + 30
        
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col].contains_point(pos, x_offset, y_offset):
                    if right_click:
                        self.toggle_flag(row, col)
                    else:
                        if not self.mines_placed:
                            self.start_time = time.time()
                            self.place_mines(row, col)
                            self.mines_placed = True
                        self.reveal_cell(row, col)
                    return

def main():
    game = MinesweeperGame("NORMAL")
    
    # Başlangıç ekranı
    show_start_screen = True
    
    running = True
    while running:
        if show_start_screen:
            game.draw_start_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        game.set_difficulty("KOLAY")
                    elif event.key == pygame.K_2:
                        game.set_difficulty("NORMAL")
                    elif event.key == pygame.K_3:
                        game.set_difficulty("ZOR")
                    show_start_screen = False
                    game.reset_game()
        else:
            # Zamanı güncelle
            if game.start_time and not game.game_over:
                game.elapsed_time = time.time() - game.start_time
                
            # Olayları işle
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Sol tık
                        game.handle_click(event.pos)
                    elif event.button == 3:  # Sağ tık
                        game.handle_click(event.pos, right_click=True)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and game.game_over:
                        game.reset_game()
                    elif event.key == pygame.K_1 and game.game_over:
                        game.set_difficulty("KOLAY")
                        game.reset_game()
                    elif event.key == pygame.K_2 and game.game_over:
                        game.set_difficulty("NORMAL")
                        game.reset_game()
                    elif event.key == pygame.K_3 and game.game_over:
                        game.set_difficulty("ZOR")
                        game.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        show_start_screen = True
                    elif event.key == pygame.K_x:  # X tuşuna basılınca
                        game.reveal_mines = not game.reveal_mines  # Mayınları gösterme durumunu değiştir
            
            # Ekranı güncelle
            game.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
