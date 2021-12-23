import os

if __name__ == "__main__":
    with open("secrets/token.txt", "r") as f:
        token = f.read()

    os.environ["BOT_TOKEN"] = token

    import test_bot.main
