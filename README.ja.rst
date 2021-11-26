.. image:: ./assets/banner.png
    :alt: Disnake Banner

disnake
==========

.. image:: https://discord.com/api/guilds/808030843078836254/embed.png
   :target: https://discord.gg/gJDbCw8aQy
   :alt: Discordサーバーの招待
.. image:: https://img.shields.io/pypi/v/disnake.svg
   :target: https://pypi.python.org/pypi/disnake
   :alt: PyPIのバージョン情報
.. image:: https://img.shields.io/pypi/pyversions/disnake.svg
   :target: https://pypi.python.org/pypi/disnake
   :alt: PyPIのサポートしているPythonのバージョン

disnake は機能豊富かつモダンで使いやすい、非同期処理にも対応したDiscord用のAPIラッパーです。

主な特徴
-------------

- ``async`` と ``await`` を使ったモダンなPythonらしいAPI。
- 適切なレート制限処理
- メモリと速度の両方を最適化。

インストール
-------------

**Python 3.8 以降のバージョンが必須です**

完全な音声サポートなしでライブラリをインストールする場合は次のコマンドを実行してください:

.. code:: sh

    # Linux/OS X
    python3 -m pip install -U disnake

    # Windows
    py -3 -m pip install -U disnake

音声サポートが必要なら、次のコマンドを実行しましょう:

.. code:: sh

    # Linux/OS X
    python3 -m pip install -U disnake[voice]

    # Windows
    py -3 -m pip install -U disnake[voice]


開発版をインストールしたいのならば、次の手順に従ってください:

.. code:: sh

    $ git clone https://github.com/DisnakeDev/disnake
    $ cd disnake
    $ python3 -m pip install -U .[voice]


オプションパッケージ
~~~~~~~~~~~~~~~~~~~~~~

* PyNaCl (音声サポート用)

Linuxで音声サポートを導入するには、前述のコマンドを実行する前にお気に入りのパッケージマネージャー(例えば ``apt`` や ``dnf`` など)を使って以下のパッケージをインストールする必要があります:

* libffi-dev (システムによっては ``libffi-devel``)
* python-dev (例えばPython 3.8用の ``python3.8-dev``)

簡単な例
--------------

.. code:: py

    import disnake

    class MyClient(disnake.Client):
        async def on_ready(self):
            print('Logged on as', self.user)

        async def on_message(self, message):
            # don't respond to ourselves
            if message.author == self.user:
                return

            if message.content == 'ping':
                await message.channel.send('pong')

    client = MyClient()
    client.run('token')

Botの例
~~~~~~~~~~~~~

.. code:: py

    import disnake
    from disnake.ext import commands

    bot = commands.Bot(command_prefix='>')

    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

    bot.run('token')

Slash Commandsの例
~~~~~~~~~~~~~~~~~~~~~~

.. code:: py

    import disnake
    from disnake.ext import commands

    bot = commands.Bot(command_prefix='>', test_guilds=[12345])

    @bot.slash_command()
    async def ping(inter):
        await inter.response.send_message('pong')

    bot.run('token')

Context Menusの例
~~~~~~~~~~~~~~~~~~~~~

.. code:: py

    import disnake
    from disnake.ext import commands

    bot = commands.Bot(command_prefix='>', test_guilds=[12345])

    @bot.user_command()
    async def avatar(inter, user):
        embed = disnake.Embed(title=str(user))
        embed.set_image(url=user.display_avatar.url)
        await inter.response.send_message(embed=embed)

    bot.run('token')

examplesディレクトリに更に多くのサンプルがあります。

リンク
------

- `ドキュメント <https://docs.disnake.dev>`_
- `公式Discordサーバー <https://discord.gg/gJDbCw8aQy>`_
- `Discord API <https://discord.gg/disnake-api>`_
