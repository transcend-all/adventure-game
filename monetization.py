# monetization.py

class Monetization:
    def __init__(self, currency):
        """Initialize the monetization system with a reference to the player's currency."""
        self.currency = currency

        # Pricing for coin purchases (in USD or equivalent)
        self.coin_packages = {
            'small': {'coins': 100, 'price_usd': 0.99},
            'medium': {'coins': 500, 'price_usd': 4.99},
            'large': {'coins': 1200, 'price_usd': 9.99},
            'crypto_package': {'coins': 1000, 'price_crypto': '0.001 BTC'}
        }

    def show_coin_packages(self):
        """Display available coin packages to the player."""
        print("Available coin packages:")
        for package_name, package in self.coin_packages.items():
            if 'price_usd' in package:
                print(f"{package_name.capitalize()} Package: {package['coins']} coins for ${package['price_usd']}")
            if 'price_crypto' in package:
                print(f"{package_name.capitalize()} Package: {package['coins']} coins for {package['price_crypto']}")

    def purchase_coins(self, package_name, payment_method='usd'):
        """Simulate the purchase of a coin package."""
        if package_name in self.coin_packages:
            package = self.coin_packages[package_name]
            
            if payment_method == 'usd' and 'price_usd' in package:
                print(f"Processing payment of ${package['price_usd']} for {package['coins']} coins...")
                # Simulate a successful payment transaction
                self.currency.add_coins(package['coins'])
                print(f"Successfully purchased {package['coins']} coins!")
            elif payment_method == 'crypto' and 'price_crypto' in package:
                print(f"Processing cryptocurrency payment of {package['price_crypto']} for {package['coins']} coins...")
                # Simulate a successful cryptocurrency transaction
                self.currency.add_coins(package['coins'])
                print(f"Successfully purchased {package['coins']} coins!")
            else:
                print(f"Invalid payment method or package for {package_name}.")
        else:
            print(f"Package {package_name} not found.")

# Example usage
if __name__ == "__main__":
    # Assuming the player's currency system is already set up
    player_currency = Currency()

    # Initialize the monetization system
    monetization_system = Monetization(player_currency)

    # Show available coin packages
    monetization_system.show_coin_packages()

    # Simulate purchasing a small package with USD
    monetization_system.purchase_coins('small', payment_method='usd')

    # Simulate purchasing a crypto package with cryptocurrency
    monetization_system.purchase_coins('crypto_package', payment_method='crypto')
