import discord, pickle, random, time, os, dotenv, img2pdf, json, asyncio, atexit, sys, glob, winsound
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PIL import Image
import speech_recognition as sr
from pydub import AudioSegment
from mega import Mega
import tkinter as tk
from threading import Thread


description = (
'''
**TETITBbot Help**
Revision: 29032021rev4

Usage:
**!c**
1. **!c [URL]**     Get chegg answer. Ex: *!c https://chegg.com/homewo...*
**!cfg**
1. **!cfg display_scale view**     View current bot display scale
2. **!cfg display_scale [INTEGER]**     Change bot display scale
3. **!cfg shutdown**     Shutdown bot server

*Use this bot at your own risk*
''' )
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', description=description, intents=intents)


# Variable
dotenv.load_dotenv()
botToken = os.getenv("dcBotToken")
cgUname = os.getenv("cgUname")
cgPass = os.getenv("cgPass")
mUname = os.getenv("mUname")
mPass = os.getenv("mPass")
alert_duration = 1500 # milliseconds
alert_freq = 1000 # Hz
# Fixed window size
height = 720
width = 1280
display_scale = 100
if os.path.isfile('data/config'):
    ds = open('data/config','r')
    display_scale = ds.read()
    display_scale = display_scale[display_scale.find('#1:')+3:]
    ds.close()
    print('\tINFO: Using display scale: '+display_scale+'%')
    display_scale = float(display_scale)
else:
    print('\tINFO: Using default display scale (100%)')


mega = Mega()
m = mega.login(mUname,mPass)
is_active = False
while not is_active:
    m_active = m.find('nonactive',exclude_deleted=True)
    if not m_active:
        print('\tERROR: Another bot is currently active. Please try again when no other bot is active!')
    else:
        m.rename(m_active, 'active')
        print('\tINFO: Bot status changed to active.')
        print('\tINFO: Starting bot...')
        is_active = True
m_file = None


def is_visible_xpath(timeout,locator):
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
        return True
    except TimeoutException:
        return False

def is_visible_class(timeout,locator):
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, locator)))
        return True
    except TimeoutException:
        return False

def is_visible_id(timeout,locator):
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.ID, locator)))
        return True
    except TimeoutException:
        return False

def is_visible_tag(timeout,locator):
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.TAG_NAME, locator)))
        return True
    except TimeoutException:
        return False

def captcha_voice():
    # convert mp3 file to wav
    if os.path.isfile('C:/Users/Public/audio.mp3'):
        sound = AudioSegment.from_mp3("C:/Users/Public/audio.mp3")
        sound.export("C:/Users/Public/audio.wav", format="wav")

        # transcribe audio file                                                         
        AUDIO_FILE = "C:/Users/Public/audio.wav"

        # use the audio file as the audio source                                        
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.record(source)  # read the entire audio file                  
            captcha_text = r.recognize_google(audio)
            print("\t\tTranscription: " + captcha_text)
        
        os.remove('C:/Users/Public/audio.mp3')
        os.remove('C:/Users/Public/audio.wav')


# Starting
options = webdriver.ChromeOptions()

options.add_argument("--user-data-dir=data/chrome-data")
options.add_argument("window-size="+str(width)+','+str(height))
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"

driver = webdriver.Chrome(options=options,desired_capabilities=capa)

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'})
print('\tINFO: Use user agent: \n'+driver.execute_script("return navigator.userAgent;"))

driver.set_page_load_timeout(30)


def exit_handler():
    print('\tINFO: Please wait while exiting bot...')

    is_active = True
    while is_active:
        m_active = m.find('active',exclude_deleted=True)
        m.rename(m_active, 'nonactive')
        m_active = m.find('active',exclude_deleted=True)
        if m_active:
            print('\tWARNING: Error change bot status. Please wait, don\'t close the window!')
        else:
            print('\tINFO: Successfully changed bot status to nonactive. Exiting bot...')
            is_active = False

    driver.quit()

atexit.register(exit_handler)


# Process
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!cmd"))
    print('\tLogged in as:')
    print('\tUsername: '+str(bot.user.name))
    print('\tUser ID: '+str(bot.user.id))
    print('\t------READY------')


@bot.command()
async def cmd(ctx):
    msg_reply = description
    await ctx.reply(msg_reply, mention_author=True)
    print('\tINFO: Showing help to user')
    print('\tINFO: Finished processing request from '+ctx.author.mention)
    print('\t------DONE------')


run_timer = True

@bot.command()
async def cfg(ctx, *arg):
    if not arg:
        msg_reply = 'Try using a command. See *!cfg help*'
        await ctx.reply(msg_reply, mention_author=True)
        print('\tINFO: '+msg_reply)
        print('\tINFO: Finished processing request from '+ctx.author.mention)
        print('\t------DONE------')

    elif 'help' == arg[0]:
        msg_reply = description
        await ctx.reply(msg_reply, mention_author=True)
        print('\tINFO: Showing !cfg help to user')
        print('\tINFO: Finished processing request from '+ctx.author.mention)
        print('\t------DONE------')

    elif 'display_scale' == arg[0]:
        global display_scale

        try:
            is_valid = arg[1]
        except Exception as e:
            msg_reply = 'Try using a command. See *!cfg help*'
            await ctx.reply(msg_reply, mention_author=True)
            print('\tINFO: '+msg_reply)
            print('\tINFO: Finished processing request from '+ctx.author.mention)
            print('\t------DONE------')

        if 'view' == arg[1]:
            msg_reply = 'Bot display scale is: '+str(display_scale)+'%'
            await ctx.reply(msg_reply, mention_author=True)
            print('\tINFO: '+msg_reply)

            print('\tINFO: Finished processing request from '+ctx.author.mention)
            print('\t------DONE------')

        else:
            try:
                is_float = float(arg[1])
                is_float + 1
            except Exception as e:
                msg_reply = 'Wrong value. See *!cfg help*'
                await ctx.reply(msg_reply, mention_author=True)
                print('\tINFO: '+msg_reply)
                print('\tINFO: Finished processing request from '+ctx.author.mention)
                print('\t------DONE------')

            display_scale = arg[1]
            ds = open('data/config','w')
            ds.write('displayScale#1:'+display_scale)
            ds.close()

            display_scale = float(display_scale)
            msg_reply = 'Display scale changed to: '+str(display_scale)+'%'
            await ctx.reply(msg_reply, mention_author=True)
            print('\tINFO: '+msg_reply)

            print('\tINFO: Finished processing request from '+ctx.author.mention)
            print('\t------DONE------')

    elif 'shutdown' == arg[0]:
        msg_reply = 'Shutting down the bot...'
        await ctx.reply(msg_reply, mention_author=True)
        print('\tINFO: '+msg_reply)
        sys.exit()

    elif 'timer' == arg[0]:
        global run_timer
        if 'true' == arg[1]:
            run_timer = True
            msg_reply = 'Timer enabled'
            await ctx.reply(msg_reply, mention_author=True)
            print('\tINFO: '+msg_reply)
        elif 'false' == arg[1]:
            run_timer = False
            msg_reply = 'Timer disabled'
            await ctx.reply(msg_reply, mention_author=True)
            print('\tINFO: '+msg_reply)
        else:
            msg_reply = 'Wrong parameter!'
            await ctx.reply(msg_reply, mention_author=True)
            print('\tINFO: '+msg_reply)

    else:
        msg_reply = 'Unsupported command. See *!cfg help*'
        await ctx.reply(msg_reply, mention_author=True)
        print('\tINFO: '+msg_reply)
        print('\tINFO: Finished processing request from '+ctx.author.mention)
        print('\t------DONE------')


url = ''
stx = None
urls = asyncio.Queue()
authors = asyncio.Queue()
sender = None
timer = time.time()
next_url = asyncio.Event()

async def send_result(msg):
    global timer
    timer = time.time()

    msg_reply = 'Processing URL... \nhttps://www.'+msg
    msg_send = await stx.reply(sender+'\n'+msg_reply)
    print('\tINFO:'+msg_reply)

    url = 'https://www.' + msg
    try:
        if url != driver.current_url:
            driver.get(url)
            await asyncio.sleep(random.uniform(4,10))

            if 'denied' in driver.title:
                msg_reply = 'Captcha detected. Please wait while resolving it...'
                await msg_send.edit(content=sender+'\n'+msg_reply)
                print('\t\tCaptcha detected. Need to be resolved manually.')

            while 'denied' in driver.title:
                captcha_voice()
                winsound.Beep(alert_freq,alert_duration)
            
                if 'denied' not in driver.title:
                    msg_reply = 'Captcha resolved. Loading webpage...'
                    await msg_send.edit(content=sender+'\n'+msg_reply)
                    print('\t\t'+msg_reply)

            if driver.title == 'Page Not Found':
                msg_reply = 'Page not found. Check your URL!'
                await msg_send.edit(content=sender+'\n'+msg_reply)
                print('\t\tPage not found at URL:\n'+url)

    except Exception as e:
        msg_reply = 'Get Exception while accessing URL. Try again or contact dev!'
        await msg_send.edit(content=sender+'\n'+msg_reply)
        print('\tINFO: Get Exception while accessing URL:\n'+url)
        print('\tEXCEPTION: '+str(e))
  
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight") + 1
    top_height = 0
    head = 60.0
    plus = 0
    plus2 = 0
    if 'Solved:' in driver.title:
        head = 113.0
        plus = 14
        plus2 = 12

    n = 1
    chegg_head = float(display_scale/100.0)*head
    print('\tINFO: Using chegg_head: '+str(chegg_head))
    minus = - (head)
    print('\tINFO: Using minus: '+str(minus))
    width = driver.execute_script("return window.innerWidth")
    height = driver.execute_script("return window.innerHeight")
    
    msg_reply = 'Processing image...'
    await msg_send.edit(content=sender+'\n'+msg_reply)
    print('\tINFO: '+msg_reply)

    driver.execute_script("window.scrollTo(0, 0)")
    while top_height < total_height:
        filepath = 'data/cache/screenshot'+str(n)+'.png'
        driver.save_screenshot(filepath)

        if (top_height + 2 * height) < total_height + minus:
            top_height = top_height + height + minus
            if n == 1:
                top_height = top_height + plus
        else:
            break
            
        n = n + 1
        await asyncio.sleep(random.random())
        driver.execute_script('window.scrollTo(0,'+str(top_height)+')')


    images = [Image.open('data/cache/screenshot'+str(x)+'.png') for x in range(1,n+1)]

    scrollbar_width = 17
    x = 1
    for im in images:
        if x == n:
            chegg_head = chegg_head - float(display_scale/100.0)*plus2
        im = im.crop((0,chegg_head,im.size[0]-scrollbar_width,im.size[1]))
        im.save('data/cache/ans'+str(x)+'.png', quality=50)
        x = x + 1

    images = [Image.open('data/cache/ans'+str(x)+'.png') for x in range(1,n+1)]
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    total_height = sum(heights)

    new_im = Image.new('RGB', (max_width, total_height))

    y_offset = 0
    n = 0
    for im in images:
        new_im.paste(im, (0,y_offset))
        y_offset += im.size[1]

    new_im.save('data/cache/ans.png', quality=50)

    images = None

    msg_reply = 'Sending image...'
    await msg_send.edit(content=sender+'\n'+msg_reply)
    print('\tINFO: '+msg_reply)

    msg_reply = 'Done! :)'
    await stx.reply(sender+"\nHere is the result ", file=discord.File('data/cache/ans.png'))
    await msg_send.edit(content=sender+'\n'+msg_reply)
    print('\tINFO: '+msg_reply)


    driver.execute_script('window.scrollTo(0,'+str(random.randint(0,total_height-height))+')')

    next_url.set()

    timer = time.time()

    print('\tINFO: Finished processing request from '+sender+' at '+str(timer))
    print('\t------DONE------')


    await asyncio.sleep(15)
    await msg_send.delete()


async def url_task():
    global sender, timer
    await bot.wait_until_ready()

    while True:
        next_url.clear()
        url = await urls.get()
        sender = await authors.get()
        await send_result(url)
        await next_url.wait()


@bot.command()
async def c(ctx, *arg):
    global stx, timer
    stx = ctx

    if not arg:
        msg_reply = 'Try using a command. See *!c help*'
        await ctx.reply(msg_reply, mention_author=True)
        print('\tINFO: '+msg_reply)
        print('\tINFO: Finished processing request from '+ctx.author.mention)
        print('\t------DONE------')

    elif 'help' == arg[0]:
        msg_reply = description
        await ctx.reply(msg_reply, mention_author=True)
        print('\tINFO: Showing !c help to user')
        print('\tINFO: Finished processing request from '+ctx.author.mention)
        print('\t------DONE------')

    elif 'chegg.com' in arg[0]:
        timer = time.time()
        msg = arg[0]
        msg = msg[msg.find('chegg.com'):]
        await urls.put(msg)
        await authors.put(ctx.author.mention)
        msg_reply = 'Request has been added to the queue. Please wait...'
        msg_send = await ctx.reply(ctx.author.mention+'\n'+msg_reply, mention_author=True)
        print('\tINFO: '+msg_reply)
        await asyncio.sleep(15)
        await msg_send.delete()

    else:
        msg_reply = 'Unsupported command. See *!c help*'
        await ctx.reply(msg_reply, mention_author=True)
        print('\tINFO: '+msg_reply)
        print('\tINFO: Finished processing request from '+ctx.author.mention)
        print('\t------DONE------')



def redirect():
    global timer, run_timer
    while True:
        time.sleep(60)
        if ((time.time() - timer > random.randint(150,250)) and ('google.com' not in driver.current_url)) and (run_timer == True):
            driver.get('https://www.google.com')
            timer = time.time()

background_thread = Thread(target=redirect)
background_thread.daemon = True
background_thread.start()


bot.loop.create_task(url_task())
bot.run(botToken)
