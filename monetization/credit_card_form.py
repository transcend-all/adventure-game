import pygame
from monetization.button import Button

class CreditCardForm:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 32)
        self.inputs = {
            'card_number': '',
            'expiration_date': '',
            'cvv': '',
            'cardholder_name': ''
        }
        self.active_input = None
        self.submit_button = Button(400, 400, 100, 40, text="Submit", font=self.font)
        self.cancel_button = Button(520, 400, 100, 40, text="Cancel", font=self.font)

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), (200, 100, 400, 300))
        y = 120
        for label, value in self.inputs.items():
            label_surface = self.font.render(label.replace('_', ' ').title() + ':', True, (0, 0, 0))
            screen.blit(label_surface, (220, y))
            input_rect = pygame.Rect(220, y + 30, 360, 30)
            pygame.draw.rect(screen, (255, 255, 255), input_rect)
            if self.active_input == label:
                pygame.draw.rect(screen, (0, 0, 255), input_rect, 2)
            value_surface = self.font.render(value, True, (0, 0, 0))
            screen.blit(value_surface, (225, y + 35))
            y += 70

        self.submit_button.draw(screen)
        self.cancel_button.draw(screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.submit_button.is_clicked(event):
                return "submit"
            elif self.cancel_button.is_clicked(event):
                return "close"
            
            y = 120
            for label in self.inputs:
                input_rect = pygame.Rect(220, y + 30, 360, 30)
                if input_rect.collidepoint(event.pos):
                    self.active_input = label
                    break
                y += 70
            else:
                self.active_input = None

        elif event.type == pygame.KEYDOWN and self.active_input:
            if event.key == pygame.K_BACKSPACE:
                self.inputs[self.active_input] = self.inputs[self.active_input][:-1]
            else:
                self.inputs[self.active_input] += event.unicode

        return None

    def get_card_info(self):
        return self.inputs
