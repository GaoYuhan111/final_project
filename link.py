import requests
import xlwt
import re
import json
import time
from pyecharts import options as opts
from pyecharts.charts import Page, Tree

headers = {'User-agert': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36','Connection':'close'}

with open('sina_cookies.txt','r',encoding='utf-8') as f:
    cookies_dict = json.loads(f.read())

class Tool:
    deleteImg = re.compile('<img.*?>')
    newLine = re.compile('<tr>|<div>|</tr>|</div>')
    deleteAite = re.compile('//.*?:')
    deleteAddr = re.compile('<a.*?>.*?</a>|<a href=' + '\'https:')
    deleteTag = re.compile('<.*?>')
    deleteWord = re.compile('回复@|回覆@|回覆|回复')

    @classmethod
    def replace(cls, x):
        x = re.sub(cls.deleteWord, '', x)
        x = re.sub(cls.deleteImg, '', x)
        x = re.sub(cls.deleteAite, '', x)
        x = re.sub(cls.deleteAddr, '', x)
        x = re.sub(cls.newLine, '', x)
        x = re.sub(cls.deleteTag, '', x)
        return x.strip()


class link(object):
    all_blogs = []

    def get_dict(self, name, blogid):
        dict = {}
        dict["children"] = []
        for n in self.all_blogs:
            if n[2] == blogid:
                dict_ = self.get_dict(n[0], n[1])
                dict["children"].append(dict_)
        if len(dict["children"]) == 0:
            del dict["children"]
        dict["name"] = name
        return dict

    def get_link(self):
        target_id = input("Input the id of the microblog: ")
        target_name = input("Input the name of the producer: ")
        target_ids = []
        target_ids.append(target_id)
        blog = [target_name, target_id, 0]
        self.all_blogs.append(blog)

        #File = open('link.txt', "w")
        excel = xlwt.Workbook(encoding='utf-8')
        tier = 1
        while len(target_ids) is not 0:
            sheet = excel.add_sheet('tier-' + str(tier))
            sheet.write(0, 0, 'userid')
            sheet.write(0, 1, 'name')
            sheet.write(0, 2, 'time')
            sheet.write(0, 3, 'text')
            sheet.write(0, 4, 'likes')
            sheet.write(0, 5, 'blogid')
            sheet.write(0, 6, 'forwardblogid')
            temp_ids = []
            count = 0
            for n in range(len(target_ids)):
                i = 0
                while True:
                    url = 'https://m.weibo.cn/api/statuses/repostTimeline?id=' + target_ids[n] + '&page='
                    i = i + 1
                    url = url + str(i)
                    print(url)
                    try:
                        response = requests.get(url, headers=headers, cookies=cookies_dict)
                        resjson = json.loads(response.text)
                        dataset = resjson.get('data')
                        if dataset is None:
                            print("No more forwarding.")
                            time.sleep(5)
                            break
                        data = dataset.get('data')
                        for j in range(0, len(data)):
                            temp = data[j]
                            blog_id = temp.get('id')
                            user = temp.get('user')
                            text = temp.get('text')
                            text = Tool.replace(text)
                            userid = user.get('id')
                            screen_name = user.get('screen_name')
                            created_at = temp.get('created_at')
                            attitudes_count = temp.get('attitudes_count')
                            count += 1
                            #File.write(text.encode('utf-8') + '\n')
                            sheet.write(count, 0, userid)
                            sheet.write(count, 1, screen_name)
                            sheet.write(count, 2, created_at)
                            sheet.write(count, 3, text)
                            sheet.write(count, 4, attitudes_count)
                            sheet.write(count, 5, blog_id)
                            sheet.write(count, 6, target_ids[n])
                            temp_ids.append(blog_id)
                            blog = []
                            blog.append(screen_name)
                            blog.append(blog_id)
                            blog.append(target_ids[n])
                            self.all_blogs.append(blog)
                        print("get " + str(count) + " pieces of data")
                        time.sleep(5)
                    except Exception as e:
                        print(e)
                    #break
            #break
            target_ids = temp_ids
            tier = tier + 1
        #File.close()
        excel.save('link.xls')
        blog_dict = [self.get_dict(target_name, target_id)]
        tree = (
            Tree().add("", blog_dict).set_global_opts(title_opts=opts.TitleOpts(title="Link forwarding"))
        )
        tree.render()


if __name__ == '__main__':
    Link = link()
    Link.get_link()
