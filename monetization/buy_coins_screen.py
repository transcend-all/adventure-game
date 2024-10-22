import pygame
from monetization.button import Button
from monetization.credit_card_info import CreditCardInfo
from monetization.credit_card_form import CreditCardForm

class BuyCoinsScreen:
    def __init__(self, screen, player, db_connection):
        self.screen = screen
        self.player = player
        self.db_connection = db_connection
        self.font = pygame.font.Font(None, 32)
        self.message = ""
        self.back_button = Button(650, 500, 140, 40, text="Back", font=self.font, bg_color=(255, 0, 0))
        self.buy_buttons = [
            Button(300, 150, 200, 40, text="Buy 100 Coins ($1)", font=self.font),
            Button(300, 200, 200, 40, text="Buy 500 Coins ($4)", font=self.font),
            Button(300, 250, 200, 40, text="Buy 1000 Coins ($7)", font=self.font),
        ]
        self.add_card_button = Button(300, 350, 200, 40, text="Add Credit Card", font=self.font)
        self.credit_card_info = CreditCardInfo(db_connection)
        self.credit_card_form = None

    def draw(self):
        """Render the inventory screen."""
        self.screen.fill((0, 0, 0))  # Clear the screen with a black background
        title_surface = self.font.render("Buy Coins", True, (255, 255, 255))
        self.screen.blit(title_surface, (350, 50))

        for button in self.buy_buttons:
            button.draw(self.screen)

        self.back_button.draw(self.screen)

        coins_text = f"Current Coins: {self.player.currency.coins}"
        coins_surface = self.font.render(coins_text, True, (255, 255, 255))
        self.screen.blit(coins_surface, (300, 100))

        if self.message:
            message_surface = self.font.render(self.message, True, (255, 255, 255))
            self.screen.blit(message_surface, (300, 300))

        self.add_card_button.draw(self.screen)

        if self.credit_card_form:
            self.credit_card_form.draw(self.screen)

        pygame.display.flip()

    def handle_event(self, event):
        if self.credit_card_form:
            result = self.credit_card_form.handle_event(event)
            if result == "close":
                self.credit_card_form = None
            elif result == "submit":
                self.save_credit_card()
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.buy_buttons):
                if button.is_clicked(event):
                    self.buy_coins(i)
            
            if self.add_card_button.is_clicked(event):
                self.credit_card_form = CreditCardForm(self.screen)
        
        if self.back_button.is_clicked(event):
            return "close_buy_coins"

    def buy_coins(self, button_index):
        coin_amounts = [100, 500, 1000]
        prices = [1, 4, 7]
        
        if self.credit_card_info.process_payment(prices[button_index]):
            self.player.currency.coins += coin_amounts[button_index]
            self.message = f"Successfully purchased {coin_amounts[button_index]} coins!"
        else:
            self.message = "Payment failed. Please try again."

    def save_credit_card(self):
        card_info = self.credit_card_form.get_card_info()
        print(f"Saving credit card for player: {self.player}")  # Debug print
        if self.credit_card_info.save_card_info(self.player.id, card_info):
            self.message = "Credit card information saved successfully!"
        else:
            self.message = "Failed to save credit card information."
        self.credit_card_form = None
