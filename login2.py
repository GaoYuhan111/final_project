import requests
import json
import re
import csv
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

result = []
key_word = input("Input the keyword: ")
page = input("Input the page you want to search: ")
for i in range(1, int(page) + 1):
    # build the search content
    data = {
        'containerid': '100103type=1&q={}'.format(key_word),
        'page_type': 'searchall',
        'page': i,
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36', }

    url = "https://m.weibo.cn/api/container/getIndex?"

    html = requests.get(url, headers=headers, params=data)

    print(html)

    if html.content:
        response = html.json()
        cards = response["data"]["cards"]

        for card in cards:
            # if "mblog" in card
            mblogs = "mblog"
            card_group = "card_group"
            if mblogs in card:
                # extract text
                text = card[mblogs]["text"]
                if "全文" in text:
                    url_blog = "https://m.weibo.cn/status/" + card[mblogs]["id"]
                    driver = webdriver.Chrome(ChromeDriverManager(version="100.0.4896.60").install())
                    driver.implicitly_wait(3)
                    driver.get(url_blog)
                    data_blog = driver.execute_script("return $render_data")
                    text = data_blog["status"]["text"]
                    driver.quit()
                # Extract the text and use regular expressions to delete HTML tags
                # re.compile the regular expression string to create a pattern object
                # re.S makes. Match all characters including newlines
                dr = re.compile(r'<[^>]+>', re.S)
                pattern1 = re.compile(r'(#)(.*)(#)')
                pattern2 = re.compile(r'(@)(.*)( )')
                pattern3 = re.compile("["
                                           u"\U0001F600-\U0001F64F"
                                           u"\U0001F300-\U0001F5FF"
                                           u"\U0001F680-\U0001F6FF"
                                           u"\U0001F1E0-\U0001F1FF"
                                           "]+", flags=re.UNICODE)
                pattern4 = re.compile(r'(【)(.*)(】)')
                textFinal = dr.sub('', text)
                textFinal = pattern1.sub(r'', textFinal)
                textFinal = pattern4.sub(r'', textFinal)
                textFinal = pattern3.sub(r'', textFinal)
                # Save the data in the list in the form of a dictionary
                result.append({
                    '发布时间': card[mblogs]["created_at"],
                    '微博id': card[mblogs]["id"],
                    '用户id': card[mblogs]["user"]["id"],
                    '用户名': card[mblogs]["user"]["screen_name"],
                    '微博地址': card[mblogs]["user"]["profile_url"],
                    '转发数': card[mblogs]["reposts_count"],
                    '评论数': card[mblogs]["comments_count"],
                    '点赞数': card[mblogs]["attitudes_count"],
                    '正文': dr.sub('', text),
                    '实验正文': textFinal})
            elif card_group in card:
                if card[card_group]:
                    num = 0
                    while num < len(card[card_group]):
                        if mblogs in card[card_group][num]:
                            text = card[card_group][num][mblogs]["text"]
                            dr = re.compile(r'<[^>]+>', re.S)
                            if "全文" in text:
                                url_blog = "https://m.weibo.cn/status/" + card[card_group][num][mblogs]["id"]
                                driver = webdriver.Chrome(ChromeDriverManager(version="100.0.4896.60").install())
                                driver.implicitly_wait(3)
                                driver.get(url_blog)
                                data_blog = driver.execute_script("return $render_data")
                                text = data_blog["status"]["text"]
                                driver.quit()
                            pattern1 = re.compile(r'(#)(.*)(#)')
                            pattern2 = re.compile(r'(@)(.*)( )')
                            pattern3 = re.compile("["
                                                  u"\U0001F600-\U0001F64F"
                                                  u"\U0001F300-\U0001F5FF"
                                                  u"\U0001F680-\U0001F6FF"
                                                  u"\U0001F1E0-\U0001F1FF"
                                                  "]+", flags=re.UNICODE)
                            pattern4 = re.compile(r'(【)(.*)(】)')
                            textFinal = dr.sub('', text)
                            textFinal = pattern1.sub(r'', textFinal)
                            textFinal = pattern4.sub(r'', textFinal)
                            textFinal = pattern3.sub(r'', textFinal)
                            result.append({
                                '发布时间': card[card_group][num][mblogs]["created_at"],
                                '微博id': card[card_group][num][mblogs]["id"],
                                '用户id': card[card_group][num][mblogs]["user"]["id"],
                                '用户名': card[card_group][num][mblogs]["user"]["screen_name"],
                                '微博地址': card[card_group][num][mblogs]["user"]["profile_url"],
                                '转发数': card[card_group][num][mblogs]["reposts_count"],
                                '评论数': card[card_group][num][mblogs]["comments_count"],
                                '点赞数': card[card_group][num][mblogs]["attitudes_count"],
                                '正文': dr.sub('', text),
                                '实验正文': textFinal})
                            break
                        num = num + 1
print(result)
print(len(result))

file_name = key_word + '.csv'
header = ['发布时间', '微博id', '用户id', '用户名', '微博地址', '转发数', '评论数', '点赞数', '正文', '实验正文']
with open(file_name, 'w', newline="", encoding='gb18030') as f:
    f_csv = csv.DictWriter(f, header)
    # Prevent repeated header writing
    with open(file_name, 'r', encoding='gb18030', newline="") as file:
        reader = csv.reader(file)
        if not [row for row in reader]:
            f_csv.writeheader()
            f_csv.writerows(result)
        else:
            f_csv.writerows(result)
        # Delay to prevent anti-crawler mechanism
        time.sleep(0.1)
