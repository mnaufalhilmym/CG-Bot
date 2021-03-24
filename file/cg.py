import discord, pickle, random, time, os, dotenv, img2pdf, json
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from PIL import Image
import speech_recognition as sr
from pydub import AudioSegment
from mega import Mega


description = '''**TETITBbot Help**\n
                Revision: 24032021\n\n
                Usage:\n
                1. **!getcg [URL]**     Get chegg answer. Ex: *!getcg https://chegg.com/homewo...*\n
                2. **!getcg help**     Show this help\n\n
                *Use this bot at your own risk*'''

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

# Variable
dotenv.load_dotenv()
botToken = os.getenv("dcBotToken")
siteEmail = os.getenv("cgUname")
sitePassword = os.getenv("cgPass")
megaEmail = os.getenv("mUname")
megaPassword = os.getenv("mPass")


print('\tINFO: Retrieving latest cache...')
mega = Mega()
m = mega.login(megaEmail,megaPassword)
m_file = m.find('cgCookies.pkl',exclude_deleted=True)
try:
    m.download(m_file,'data')
    if not os.path.isfile('data/cgCookies.pkl'):
        print('\tINFO: Failed to synchronized cache')
except Exception as e:
    pass
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

def captcha_voice(captcha_text):
    # convert mp3 file to wav
    if os.path.isfile('data/audio.mp3'):
        sound = AudioSegment.from_mp3("data/audio.mp3")
        sound.export("data/audio.wav", format="wav")

        # transcribe audio file                                                         
        AUDIO_FILE = "data/audio.wav"

        # use the audio file as the audio source                                        
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.record(source)  # read the entire audio file                  
            captcha_text = r.recognize_google(audio)
            print("\t\tTranscription: " + captcha_text)
        
        os.remove('data/audio.mp3')
        os.remove('data/audio.wav')

        return captcha_text


# Starting
options = webdriver.ChromeOptions()

options.add_argument("download.default_directory=C:/Users/Acer/Labs/cheggbot/CG-Bot/data")
settings = {
       "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings),
        'savefile.default_directory': 'C:/Users/Acer/Labs/cheggbot/CG-Bot/data/cache'}
options.add_experimental_option('prefs', prefs)
options.add_argument('--kiosk-printing')

options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
print('\tINFO: Use user agent: \n'+driver.execute_script("return navigator.userAgent;"))

driver.set_page_load_timeout(30)


if os.path.isfile("data/cgCookies.pkl"):

    url = 'https://www.google.com'
    connect = False
    while not connect:
        try:
            driver.get(url)
            print('\tINFO: Accessing URL:\n'+url)
            time.sleep(random.uniform(2,4))

            if 'Google' in driver.title:
                connect = True
                print('\tINFO: Successfully accessed URL:\n'+url)

        except Exception as e:
            print('\tINFO: Get Exception while accessing URL:\n'+url)
            continue
            
    cookies = pickle.load(open("data/cgCookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    print('\tINFO: Cache loaded')

else:

    url = 'https://www.chegg.com/auth?action=login&redirect=https%3A%2F%2Fwww.chegg.com%2F'
    connect = False
    while not connect:

        try:

            if url != driver.current_url:
                driver.get(url)
            print('\tINFO: Accessing URL:\n'+url)
            time.sleep(random.uniform(2,3))

            xpath = '//*[@id="emailForSignIn"]'
            if is_visible_xpath(5,xpath):
                driver.find_element_by_xpath(xpath).send_keys(siteEmail)
                print('\tINFO: Email '+siteEmail+' Filled')
                time.sleep(random.uniform(2,3))
            
            xpath = '//*[@id="passwordForSignIn"]'
            if is_visible_xpath(5,xpath):
                driver.find_element_by_xpath(xpath).send_keys(sitePassword)
                print('\tINFO: Password '+sitePassword+' Filled')
                time.sleep(random.uniform(2,3))

            xpath = '//button[@class="login-button button flat"]'
            if is_visible_xpath(5,xpath):
                driver.find_element_by_xpath(xpath).click()
                print('\tINFO: Login Button Clicked')

            if is_visible_xpath(5,'//*[@id="eggshell-5"]/img'):
                print('\tINFO: Login Successful')
                time.sleep(random.uniform(1,2))
                pickle.dump(driver.get_cookies() , open("data/cgCookies.pkl","wb"))
                print('\tINFO: Cache saved')

                connect = True
            
            else:
                print('\tINFO: Login Failed')
                print('\t\tReason:')
                if 'denied' in driver.title:
                    print('\t\tCaptcha detected. Need to be resolved manually.')
                    
                    captcha_text = '0'
                    while captcha_text == '0' and 'denied' in driver.title:
                        captcha_text = captcha_voice(captcha_text)

                    while 'denied' in driver.title:
                        continue

                    if 'denied' not in driver.title:
                        print('\t\tCaptcha resolved. Loading webpage...')

                else:
                    print('\t\tUnknown reason')
                    input('\t\tEnter to continue')

        except Exception as e:
            print('\tINFO: Get Exception while loging in URL:\n'+url)
            continue

filepath = 'data/cache/initial.png'
driver.save_screenshot(filepath)
im = Image.open(filepath)
vw_width, vw_height = im.size
im.close()

height = vw_height
width = vw_width - 20

# Process
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!getcg help"))
    print('\tLogged in as:')
    print('\tUsername: '+str(bot.user.name))
    print('\tUser ID: '+str(bot.user.id))
    print('\t------READY------')

@bot.event
async def on_message(message):

    # Prevent bot to reply to itself
    if message.author.id == bot.user.id:
        return

    elif message.content.startswith('!getcg'):

        msg = message.content

        if '!getcg help' in msg:

            msg_reply = (
                '**TETITBbot Help**\n'+
                'Revision: 24032021\n\n'
                'Usage:\n'+
                '1. **!getcg [URL]**     Get chegg answer. Ex: *!getcg https://chegg.com/homewo...*\n'+
                '2. **!getcg help**     Show this help\n\n'+
                '*Use this bot at your own risk*'
                )
            await message.reply(msg_reply, mention_author=True)
            print('\tINFO: Showing help to user')
            
        elif 'chegg.com' in msg:

            msg = msg[msg.find('chegg.com'):]

            msg_reply = 'Opening URL... \nhttps://www.'+msg
            await message.reply(msg_reply, mention_author=True)
            print('\tINFO: '+msg_reply)

            url = 'https://www.' + msg
            connect = False
            bot_state = False
            while not connect:

                try:
                    if url != driver.current_url:
                        driver.get(url)

                    if is_visible_xpath(5,'/html/body/div[1]/div[4]/oc-component/div[1]/div/a'):
                        connect = True
                        bot_state = True

                    else:
                        print('\tINFO: Failed accessing URL:\n'+url)
                        print('\t\tReason:')

                        if 'denied' in driver.title:
                            msg_reply = 'Captcha detected. Please wait while resolving it...'
                            await message.reply(msg_reply, mention_author=True)
                            print('\t\tCaptcha detected. Need to be resolved manually.')
                            
                            captcha_text = '0'
                            while captcha_text == '0' and 'denied' in driver.title:
                                captcha_text = captcha_voice(captcha_text)

                            while 'denied' in driver.title:
                                continue
                            
                            if 'denied' not in driver.title:
                                msg_reply = 'Captcha resolved. Loading webpage...'
                                await message.reply(msg_reply, mention_author=True)
                                print('\t\t'+msg_reply)

                        elif driver.title == 'Page Not Found':
                            msg_reply = 'Page not found. Check your URL!'
                            await message.reply(msg_reply, mention_author=True)
                            print('\t\tPage not found at URL:\n'+url)
                            break

                        else:
                            print('\t\tUnknown reason')
                            input('\t\tEnter to continue')

                except Exception as e:
                    msg_reply = 'Get Exception while accessing URL. Try again or contact dev!'
                    await message.reply(msg_reply, mention_author=True)
                    print('\tINFO: Get Exception while accessing URL:\n'+url)
                    break

            if bot_state:

                time.sleep(random.uniform(1,2))

                if 'denied' in driver.title:

                    msg_reply = 'Captcha detected. Please wait while resolving it...'
                    await message.reply(msg_reply, mention_author=True)
                    print('\t\tCaptcha detected. Need to be resolved manually.')
                    
                    captcha_text = '0'
                    while captcha_text == '0' and 'denied' in driver.title:
                        captcha_text = captcha_voice(captcha_text)

                    while 'denied' in driver.title:
                        continue

                    if 'denied' not in driver.title:
                        msg_reply = 'Captcha resolved. Loading webpage...'
                        await message.reply(msg_reply, mention_author=True)
                        print('\t\t'+msg_reply)

                    # Atempting to beat captcha but still won't work

                    # if is_visible_xpath(5,"//iframe[@role='presentation']"):
                    #     driver.switch_to.frame(driver.find_element_by_xpath("//iframe[@role='presentation']"))
                    #     print("switched to //iframe[@role='presentation']")

                    # if is_visible_xpath(5,'//*[@id="recaptcha-anchor"]'):
                    #     driver.find_element_by_xpath('//*[@id="recaptcha-anchor"]').click()
                    #     print("//*[@id='recaptcha-anchor'] clicked")
                    #     time.sleep(random.uniform(3,6))

                    # driver.switch_to.default_content()
                    # print("switch_to.default_content()")

                    # if is_visible_xpath(5,"//iframe[@title='recaptcha challenge']"):
                    #     driver.switch_to.frame(driver.find_element_by_xpath("//iframe[@title='recaptcha challenge']"))
                    #     print("switched to//iframe[@title='recaptcha challenge']")
                        
                    #     # driver.switch_to.default_content()
                    #     # print("switch_to.default_content()")

                    #     if is_visible_xpath(5,'//button[@id="recaptcha-audio-button"]'):
                    #         driver.find_element_by_xpath('//button[@id="recaptcha-audio-button"]').click()
                    #         print('//button[@id="recaptcha-audio-button"] clicked')
                    #         time.sleep(random.uniform(3,6))

                    #         if is_visible_xpath(5,'//a[@title="Alternatively, download audio as MP3"]'):
                    #             driver.find_element_by_xpath('//a[@title="Alternatively, download audio as MP3"]').click()
                    #             print('//a[@title="Alternatively, download audio as MP3"]')
                    # time.sleep(random.uniform(59,62))


                    # is_visible_class(3,'rc-audiochallenge-tdownload-link')
                    # link = driver.find_element_by_class_name('rc-audiochallenge-tdownload-link')
                    # href = link.get_attribute('href')
                    # link.send_keys(Keys.COMMAND + 't')
                    # driver.get(href)
                    # captcha_voice()
                    # link.send_keys(Keys.COMMAND + 'w')
                    # is_visible_class(3,'audio-response')
                    # driver.find_element_by_id('audio-response').send_keys(captcha_text)
                    # driver.find_element_by_id('recaptcha-verify-button').click()


                driver.switch_to.default_content()

                if is_visible_class(3,'question-text'):
                    msg_reply = 'Page loaded successfully. Processing image...'
                    await message.reply(msg_reply, mention_author=True)
                    print('\tINFO: '+msg_reply)

                total_height = driver.execute_script("return document.body.parentNode.scrollHeight") + 1
                top_height = 0


                n = 1
                # minus = -60
                minus = -249
                while top_height < total_height:

                    filepath = 'data/cache/screenshot'+str(n)+'.png'
                    driver.save_screenshot(filepath)
                    n = n + 1

                    if (top_height + height) < total_height + minus:
                        # top_height = top_height + height + minus
                        top_height = top_height + height + minus
                    else:
                        break

                    driver.execute_script("window.scrollTo(0, {})".format(top_height))

                driver.execute_script("window.scrollTo(0, 0)")

                images = [Image.open('data/cache/screenshot'+str(x)+'.png') for x in range(1,n)]

                x = 1
                for im in images:
                    # im = im.crop((0,60,width,height))
                    im = im.crop((0,75,width,height))
                    im.save('data/cache/ans'+str(x)+'.png', quality=50)
                    x = x + 1

                images = [Image.open('data/cache/ans'+str(x)+'.png') for x in range(1,n)]
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

                # image = Image.open('data/cache/ans.png')
                # pdf = open('data/cache/ans.pdf', 'wb')

                # pdf.write(img2pdf.convert(image.filename))
                # image.close()
                # pdf.close()

                msg_reply = 'Sending image...'
                await message.reply(msg_reply, mention_author=True)
                print('\tINFO: '+msg_reply)

                await message.channel.send(file=discord.File('data/cache/ans.png'))

                msg_reply = 'Done! :)'
                await message.reply(msg_reply, mention_author=True)
                print('\tINFO: '+msg_reply)

                pickle.dump(driver.get_cookies() , open("data/cgCookies.pkl","wb"))
                print('\tINFO: Cache saved')

                try:
                    m_file = m.find('cgCookies.pkl')
                    m.rename(m_file, 'cgCookies.pkl.backup')
                except Exception as e:
                    print('\tINFO: Failed to rename cache')
                    pass

                try:
                    m.upload('data/cgCookies.pkl')
                    if m.find('cgCookies.pkl'):
                        print('\tINFO: Cache synchronized')
                    else:
                        print('\tINFO: Failed to synchronize cache')
                except Exception as e:
                    print('\tINFO: Failed to synchronize cache')
                    pass
                    
                driver.get('https://www.google.com/')

        else:

            msg_reply = 'Unsupported command. See *!getcg help*'
            await message.reply(msg_reply, mention_author=True)
            print('\tINFO: '+msg_reply)

    await bot.process_commands(message)

bot.run(botToken)
