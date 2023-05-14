import datetime
import time

import discord
from discord.ext import tasks
client = discord.Client(intents=discord.Intents.default())

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup as bs

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-gpu")
options.add_argument("--disable-infobars")
options.add_argument('--disable-features=VizDisplayCompositor')
options.add_argument("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.70")
service = ChromeService(executable_path='/usr/lib/chromium-browser/chromedriver')
browser = webdriver.Chrome(service=service, options=options)

global compare_count
compare_count = 0

def data_compare():
    browser.get("https://event.lottecinema.co.kr/NLCHS/Event/DetailList?code=20")

    soup = bs(browser.page_source, 'html.parser')
    soup_selecter = soup.select("#contents > ul > li:nth-child(1)")

    global com_event_name

    com_event = soup_selecter[0].find('img')
    com_event_name = com_event['alt']

@tasks.loop(minutes=60)
async def lotte_event():
    global compare_count
    global com_event_name

    if compare_count == 0:
        data_compare()
        print("최초 데이터 호출 완료")
    
    compare_count = compare_count + 1

    browser.get("https://event.lottecinema.co.kr/NLCHS/Event/DetailList?code=20")

    soup = bs(browser.page_source, 'html.parser')
    soup_selecter = soup.select("#contents > ul > li:nth-child(1)")

    event = soup_selecter[0].find('img')
    event_name = event['alt']
    event_image = event['src']
    event_date = soup_selecter[0].find('div', class_='itm_date').get_text()

    if compare_count > 1:
        if com_event_name != event_name:
            now_time = datetime.datetime.now()
            channel = client.get_channel('Channel_ID')
            uptime = now_time.strftime('%Y-%m-%d %H:%M:%S')

            print("Log : 새로운 이벤트("+event_name+")이 감지되었습니다.")
            embed = discord.Embed(title="새로운 이벤트가 감지되었습니다.", color=0x013668)
            embed.add_field(name="이벤트 이름", value=event_name, inline=False)
            embed.add_field(name="이벤트 기간", value=event_date, inline=False)
            embed.add_field(name="이벤트 바로가기", value="[바로가기](<https://event.lottecinema.co.kr/NLCHS/Event/DetailList?code=20)", inline=False)
            embed.set_image(url=event_image)
            embed.set_footer(text="데이터 수신 시간 : "+uptime)
            await channel.send(embed=embed)

            time.sleep(5)
            data_compare()

@client.event
async def on_ready():
    client_id = str(client.user.id)
    print('클라이언트 ID : ' + client_id)
    game = discord.Game("롯데시네마")
    await client.change_presence(status=discord.Status.online, activity=game)
    print("연결 완료")
    if not lotte_event.is_running():   
        lotte_event.start()

client.run('TOKEN')
