#cogs.Stockpull runs all of the message commands for stock pulling for MrStonk
import nextcord
from nextcord.ext import commands
import yfinance
import config
import io
import matplotlib.pyplot as plt

extension = config.extension

class Stockpull(commands.Cog):

    def __init__(self, client):
        print("Stockpull initialized Successfully")
    
    @commands.command(pass_context = True)
    async def stock(self, ctx, ticker):
        data_stream = io.BytesIO()
        tickerdata = yfinance.Ticker(ticker)
        compinfo = tickerdata.get_info()
        data = yfinance.download(tickers=ticker, period='1d', interval='1m')
        totaldata = yfinance.download(tickers=ticker)
        yclose = totaldata.tail(2)['Close'].values[0]
        current = data.tail(1)['Open'].values[0]
        percentage = -1 * round((1-(current/yclose)) * 100, 2)
        if(current-yclose) < 0:
            color = 0xff0000
        else:
            color = 0x00ff00
        print(data)
        plt.figure(figsize=(10,5))
        plt.plot(data.index, data["Open"])
        plt.xlabel("Datetime")
        plt.ylabel("Price (USD)")
        plt.plot([data.head(1).index, data.tail(1).index], [yclose, yclose], dashes = (4,5), label="Previous Close")
        leg = plt.legend(loc='upper center')
        plt.savefig(data_stream, format = 'png', dpi = 80, bbox_inches="tight")
        plt.close()
        data_stream.seek(0)
        chart = nextcord.File(data_stream, filename=f"{ticker}.png")
        embed = nextcord.Embed(title=compinfo["shortName"], description=(f"{round(current, 2)} USD"), colour=color)
        embed.add_field(name="Loss/Gain", inline=False, value=(f"{round(current-yclose, 2)} ({percentage}%)"), )
        embed.set_image(url=f"attachment://{ticker}.png")
        await ctx.send(embed=embed, file=chart)

def setup(client):
    client.add_cog(Stockpull(client))