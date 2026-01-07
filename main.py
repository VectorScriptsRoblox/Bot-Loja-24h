import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- 1. SISTEMA PARA O BOT NÃO DORMIR (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "O bot da loja está online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. CONFIGURAÇÃO DAS PERMISSÕES DO BOT ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- 3. SISTEMA DE TICKET (INTERFACE DO BOTÃO) ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Botão nunca expira

    @discord.ui.button(label="Abrir Ticket / Comprar", style=discord.ButtonStyle.green, custom_id="ticket_btn")
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Nome do canal do ticket
        channel_name = f"ticket-{user.name}".lower().replace(" ", "-")
        
        # Verifica se já existe um canal com esse nome
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            return await interaction.response.send_message(f"Você já tem um ticket aberto: {existing_channel.mention}", ephemeral=True)

        # Configura as permissões do canal (Privado)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # Cria o canal
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        
        await interaction.response.send_message(f"Seu ticket foi criado: {channel.mention}", ephemeral=True)
        
        # Mensagem de boas-vindas dentro do ticket
        embed = discord.Embed(
            title="🎫 Atendimento Loja",
            description=f"Olá {user.mention}, como podemos te ajudar?\n\n- Digite o produto que deseja.\n- Digite `!pix` para ver os dados de pagamento.",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed)

# --- 4. EVENTOS E COMANDOS ---

@bot.event
async def on_ready():
    bot.add_view(TicketView()) # Faz o botão funcionar mesmo se o bot reiniciar
    print(f"✅ Bot {bot.user} conectado com sucesso!")

# Comando para criar o painel de compras (Use apenas uma vez)
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="🛒 CENTRAL DE COMPRAS",
        description="Clique no botão abaixo para abrir seu ticket e realizar uma compra ou tirar dúvidas.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketView())

# Comando de PIX para usar dentro do ticket
@bot.command()
async def pix(ctx):
    embed = discord.Embed(
        title="💰 PAGAMENTO VIA PIX",
        description="Aqui estão os dados para o pagamento:",
        color=discord.Color.gold()
    )
    embed.add_field(name="🔑 Chave PIX (E-mail/CPF/Celular):", value="03768370399", inline=False)
    embed.add_field(name="👤 Nome do Recebedor:", value="Jociana Felix", inline=False)
    embed.add_field(name="💵 Valor:", value="R$ 10,00 (Exemplo)", inline=False)
    embed.set_footer(text="Após o pagamento, envie o comprovante aqui no ticket!")
    
    await ctx.send(embed=embed)

# --- 5. INICIALIZAÇÃO ---
if __name__ == "__main__":
    keep_alive() # Inicia o servidor Flask para o UptimeRobot
    token = os.environ.get('MTQ1ODUyMDQzNzI2MzY5NTg4Mg.GT44b6.kg9HF9RCp5SSYJ1214685uhl-5-mGTc7yKldnU') # Puxa o token do Render
    bot.run(token)

