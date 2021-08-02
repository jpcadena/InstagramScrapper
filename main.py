from selenium import webdriver as wd
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import pandas as pd

# configuracion inciial de libreria y archivo json con credenciales
opt = wd.ChromeOptions()
mobile_emulation = {"userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 "
                                 "(KHTML, like Gecko) Chrome/92.0.4515 Mobile Safari/535.19"}
opt.add_experimental_option("mobileEmulation", mobile_emulation)
opt.add_argument("--log-level=3")
bot = wd.Chrome(options=opt, executable_path=ChromeDriverManager().install())
json_file = open('credentials.json',)
credentials = json.load(json_file)
href_splitter = "https://www.instagram.com/"
href_splitter_id = "p/B166OkVBPJR/comments/c/"
href_splitter_liked_by = "p/B166OkVBPJR/c/"
href_splitter_users = "p/B166OkVBPJR/"


# funcion para iniciar sesion
def login(driver, data):
    driver.set_window_size(500, 950)
    driver.get('https://www.instagram.com')
    time.sleep(5)
    driver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div/div/div/div[3]/button[1]').click()
    time.sleep(5)
    username_field = driver.find_element_by_xpath('//*[@id="loginForm"]/div[1]/div[3]/div/label/input')
    username_field.send_keys(data['username'])
    time.sleep(5)
    password_field = driver.find_element_by_xpath('//*[@id="loginForm"]/div[1]/div[4]/div/label/input')
    password_field.send_keys(data['password'])
    time.sleep(5)
    driver.find_element_by_xpath('//*[@id="loginForm"]/div[1]/div[6]/button').click()
    time.sleep(10)
    driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/button').click()
    time.sleep(15)
    return driver

# Ingreso a url solicitada TESLA y a seccion comentarios
time.sleep(5)
bot = login(bot, credentials)
time.sleep(5)
bot.get(credentials['url'])
time.sleep(15)
bot.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[3]/div[1]/div/div[2]/div[1]/a').click()
time.sleep(5)
print("started")
fBody = bot.find_element_by_xpath("//div[@class='onbq7']")
time.sleep(5)
comments_count_loading = 0
# likes_post = bot.find_elements_by_xpath("//div[@class='HbPOm _9Ytll']//span")  # QhbhU
# for lp in likes_post:
#     likes_post_str = likes_post.text.split("\n")[0]
# time.sleep(5)

# scroll para cargar mas comentarios y ver respuestas de comentarios
while comments_count_loading < 1:
    time.sleep(5)
    button_loading = bot.find_elements_by_xpath("//*[@id='react-root']/section/main/div/ul/li/div/button")
    buttons = bot.find_elements_by_xpath("//button[contains(.,'View replies')]")
    try:
        time.sleep(5)
        for btn in buttons:
            time.sleep(5)
            bot.execute_script("arguments[0].click();", btn)
        time.sleep(5)
        for btn_l in button_loading:
            time.sleep(5)
            bot.execute_script("arguments[0].click();", btn_l)
        time.sleep(5)
    except Exception as e:
        time.sleep(5)
        print(e)
    comments_count_loading += 1
    time.sleep(5)

# buscando elementos de comentarios
time.sleep(5)
print("---------- comentarios")
ig_comments_list = bot.find_elements_by_xpath("//div[@class='C4VMK']//span")
comments_list = []
for comment in ig_comments_list:
    comment_str = str(comment.text.split("\n")[0])
    print("comentario: ", comment_str)
    comments_list.append(comment_str)
count = 0
comments_list.pop(0)

# buscando tags de usuarios en post original
if not str(comments_list[0]) is None:
    cadena = str(comments_list[0])
    if '@'in cadena:
        tag_count = cadena.count('@')
        comment_splitted = cadena.split('@ ', tag_count)
        for com in comment_splitted:
            if '@' in com:
                count = count + 1
        print("contador:", count)

# buscando elementos para fechas
print("---------- dates")
ig_dates_list = bot.find_elements_by_xpath("//div[@class='C4VMK']//time")
dates_list = []
for date in ig_dates_list:
    date_str = str(date.get_attribute("datetime"))
    print("date: ", date_str)
    dates_list.append(date_str)

# buscando elementos para IDs y usuarios
print("---------- ids and users")
ig_ids_list = bot.find_elements_by_xpath("//div[@class='C4VMK']//a")
ids_list = []
id_link_list_total = []
caption_users = []
users_list = []
j = 0
for id in ig_ids_list:
    cu_flag = True
    id_link = str(id.get_attribute("href"))
    id_link_list = id_link.split(href_splitter, 1)
    href_str = id_link_list[1]
    id_link_list_total.append(href_str)
    for cad in comment_splitted:
        if '@' in cad:
            cad_splitted = cad.split('@', 1)[1]
            if ' ' in cad_splitted:
                cad_final = cad_splitted.split(' ', 1)[0]
            else:
                cad_final = cad_splitted
            caption_users.append(cad_final)
    for c_users in caption_users:
        href_str_cleaned = href_str.rsplit('/', 1)[0]
        if href_str_cleaned == c_users:
            cu_flag = False
    if cu_flag:
        if j > 1:
            if not str(id_link_list_total[j-1]).startswith(href_splitter_users) and not str(id_link_list_total[j]).startswith(href_splitter_users):
                j = j + 1
                time.sleep(5)
                continue
        if href_str.startswith(href_splitter_id):
            id_str_list = href_str.split(href_splitter_id, 1)[1]
            id_str = id_str_list.rsplit('/', 1)[0]
            print("id: ", id_str)
            ids_list.append(id_str)
        elif href_str.startswith(href_splitter_liked_by):
            print("href con liked by")
        else:
            user_str = href_str.rsplit('/', 1)[0]
            print("user: ", user_str)
            users_list.append(user_str)
    j = j + 1

# buscando likes a traves de sus elementos y los historicos de fechas
print("---------- likes")
ig_likes_list = bot.find_elements_by_xpath("//div[@class='_7UhW9  PIoXz       MMzan   _0PwGv         uL8Hv         ']//a")
likes_list = []
time_list = []
m = 0
for i in ig_likes_list:
    i_str = str(i.text.split("\n")[0])
    if i_str.endswith('y') or i_str.endswith('m') or i_str.endswith('w') or i_str.endswith('d') or i_str.endswith('h') or i_str.endswith('s'):
        if len(time_list) != len(likes_list):
            zero_str = '0 likes'
            likes_list.append(zero_str)
        date_str = i_str
        print("date", date_str)
        time_list.append(date_str)
    else:
        if i_str.endswith('like') or i_str.endswith('likes'):
            like_str = i_str
            print("like: ", like_str)
            likes_list.append(like_str)
if len(time_list) != len(likes_list):
    likes_list.append('0 likes')

# agregando listas al DF
print(likes_list)
data_tuples = list(zip(comments_list, dates_list, likes_list, ids_list, users_list))
df = pd.DataFrame(data_tuples, columns=['Post', 'Date', 'LikesComment', 'IdComment', 'UserName'])
print(df.head())
print(df.tail())
print("end")
