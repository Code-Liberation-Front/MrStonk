#cogs.Stockpull runs all of the message commands for stock pulling for MrStonk
from datetime import date
from datetime import datetime
from time import time
import nextcord
from nextcord.ext import commands
import yfinance
import config
import io
import matplotlib.pyplot as plt
import finnhub

extension = config.extension

class Stockpull(commands.Cog):

    def __init__(self, client):
        print("Stockpull initialized Successfully")
    
    @commands.command(pass_context = True)
    async def stock(self, ctx, ticker:str):
        data_stream = io.BytesIO()
        company = True
        finclient = finnhub.Client(api_key=config.APIKey)
        compinfo = finclient.company_profile2(symbol=ticker)
        if not compinfo:
            symbol = finclient.symbol_lookup(ticker)
            company = False
            for counter in range(0, symbol["count"]):
                if symbol["result"][counter]["symbol"] == ticker.upper():
                    compinfo = symbol["result"][counter]
                    compinfo["name"] = compinfo["description"]
        data = yfinance.download(tickers=ticker, period='1d', interval='1m')
        difference = finclient.quote(ticker.upper())
        yclose = difference["pc"]
        current = data.tail(1)['Open'].values[0]
        percentage = round(difference["dp"], 2)
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
        embed = nextcord.Embed(title=compinfo["name"], description=(f"{round(current, 2)} USD"), colour=color)
        embed.add_field(name="Loss/Gain", value=(f"{difference['d']} ({percentage}%)"), inline=True)
        if company:
            embed.set_thumbnail(url=compinfo["logo"])
            embed.add_field(name="Sector", value=compinfo["finnhubIndustry"], inline=True)
        embed.set_image(url=f"attachment://{ticker}.png")
        if company:
            dates = str(date.today())
            embed.add_field(name="Exchange", value=compinfo["exchange"], inline=False)
            news = finclient.company_news(ticker, _from=dates, to=dates)
            for counter in range(0, 3):
                if counter < len(news):
                    embed.add_field(name=news[counter]["headline"], value=news[counter]["url"], inline=False)
        await ctx.send(embed=embed, file=chart)

def setup(client):
    client.add_cog(Stockpull(client))