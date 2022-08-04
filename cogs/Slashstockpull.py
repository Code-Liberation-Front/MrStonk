#cogs.Slashstockpull runs all of the message commands for stock pulling for MrStonk
from datetime import date
from discord import Interaction
import nextcord
from nextcord.ext import commands
import yfinance
import config
import io
import matplotlib.pyplot as plt
import finnhub

extension = config.extension

class Slashstockpull(commands.Cog):

    def __init__(self, client):
        print("Slashstockpull initialized Successfully")
        self.client = client
        self.finclient = finnhub.Client(api_key=config.APIKey)
    
    @nextcord.slash_command(name="stock", description="Pulls stock data for a specified ticker")
    async def stock(self, interaction : Interaction, ticker:str):
        data_stream = io.BytesIO()
        company = True
        compinfo = self.finclient.company_profile2(symbol=ticker)
        if not compinfo:
            symbol = self.finclient.symbol_lookup(ticker)
            company = False
            for counter in range(0, symbol["count"]):
                if symbol["result"][counter]["symbol"] == ticker.upper():
                    compinfo = symbol["result"][counter]
                    compinfo["name"] = compinfo["description"]
        data = yfinance.download(tickers=ticker, period='1d', interval='1m')
        difference = self.finclient.quote(ticker.upper())
        yclose = difference["pc"]
        current = difference["c"]
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
        embed = nextcord.Embed(title=f"{compinfo['name']} ({ticker.upper()})", description=(f"{round(current, 2)} USD"), colour=color)
        embed.add_field(name="Loss/Gain", value=(f"{round(difference['d'], 2)} ({percentage}%)"), inline=True)
        if company:
            embed.set_thumbnail(url=compinfo["logo"])
            embed.add_field(name="Sector", value=compinfo["finnhubIndustry"], inline=True)
        embed.set_image(url=f"attachment://{ticker}.png")
        if company:
            dates = str(date.today())
            embed.add_field(name="Exchange", value=compinfo["exchange"], inline=False)
            news = self.finclient.company_news(ticker, _from=dates, to=dates)
            for counter in range(0, 3):
                if counter < len(news):
                    embed.add_field(name=news[counter]["headline"], value=news[counter]["url"], inline=False)
        await interaction.response.send_message(embed=embed, file=chart)

    @nextcord.slash_command(name="stats", description="Gives statistics on a stock for the past 3 months")
    async def stats(self, interaction : Interaction, ticker:str):
        data_stream = io.BytesIO()
        data = yfinance.download(tickers=ticker, period='3mo', interval='1d')
        datall = yfinance.download(tickers=ticker)
        compinfo = self.finclient.company_profile2(symbol=ticker)
        if not compinfo:
            symbol = self.finclient.symbol_lookup(ticker)
            for counter in range(0, symbol["count"]):
                if symbol["result"][counter]["symbol"] == ticker.upper():
                    compinfo = symbol["result"][counter]
                    compinfo["name"] = compinfo["description"]
        hundredavg = (datall.tail(100)["Close"].sum()/100)
        fiftyavg = (datall.tail(50)["Close"].sum()/50)
        plt.figure(figsize=(10,5))
        plt.plot(data.index, data["Close"], label="Three Month Graph")
        plt.xlabel("Datetime")
        plt.ylabel("Price (USD)")
        plt.plot([data.head(1).index, data.tail(1).index], [hundredavg, hundredavg], dashes = (4,5), label="Hundred Day Avg")
        plt.plot([data.head(1).index, data.tail(1).index], [fiftyavg, fiftyavg], dashes = (4,5), label="Fifty Day Avg")
        leg = plt.legend(loc='upper center')
        plt.savefig(data_stream, format = 'png', dpi = 80, bbox_inches="tight")
        plt.close()
        data_stream.seek(0)
        chart = nextcord.File(data_stream, filename=f"{ticker}.png")
        embed = nextcord.Embed(title=f"{compinfo['name']} ({ticker.upper()})")
        embed.set_image(url=f"attachment://{ticker}.png")
        await interaction.response.send_message(embed=embed, file=chart)

def setup(client):
    client.add_cog(Slashstockpull(client))