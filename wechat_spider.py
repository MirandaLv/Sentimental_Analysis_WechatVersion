
# !/usr/bin/python
# coding: utf-8

# code source: https://blog.csdn.net/qiqiyingse/article/details/70050113
# the comment are translated to English to solve encoding errors
# Use phantomjs-2.1.1-linux-x86_64 by downloading from http://phantomjs.org/download.html
# Only can retrieve the recent 10 articles so far.

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from urllib import quote
from pyquery import PyQuery as pq
from selenium import webdriver

import requests
import time
import re
import json
import os


class weixin_spider:

    def __init__(self, kw):

        # structure function
        self.kw = kw

        # sougou wechat link
        # self.sogou_search_url = 'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=n&_sug_type_=' % quote(self.kw)

        self.sogou_search_url = 'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&s_from=input&_sug_=n&_sug_type_=' % quote \
            (self.kw)

        # fake spider
        self.headers = \
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 FirePHP/0refox/47.0 FirePHP/0.7.4.1'}

        # set up a sleep time
        self.timeout = 5
        self.s = requests.Session()


    def get_search_result_by_kw(self):

        self.log('The link is %s' % self.sogou_search_url)
        return self.s.get(self.sogou_search_url, headers=self.headers, timeout=self.timeout).content

    def get_wx_url_by_sougou_search_html(self, sougou_search_html):

        # Get wechat public platform link by returning sougou search_html
        doc = pq(sougou_search_html)
        # print doc('p[class="tit"]')('a').attr('href')
        # print doc('div[class=img-box]')('a').attr('href')

        # Use pyquery to deal with the content of the page, it can also use beautifulsoup.
        return doc('div[class=txt-box]')('p[class=tit]')('a').attr('href')

    def get_selenium_js_html(self, wx_url):

        # js render content, and return rendered html content
        browser = webdriver.PhantomJS(executable_path='/home/mirandalv/Downloads/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
        browser.get(wx_url)
        time.sleep(3)

        # get all dom
        html = browser.execute_script("return document.documentElement.outerHTML")
        return html

    def parse_wx_articles_by_html(self, selenium_html):

        # get wechat public account content from selenium_html
        doc = pq(selenium_html)
        return doc('div[class="weui_msg_card"]')

    def switch_arctiles_to_list(self, articles):

        # convert articles to data dictionary
        articles_list = []
        i = 1

        if articles:
            for article in articles.items():
                self.log(u'Start putting together(%d/%d)' % (i, len(articles)))
                articles_list.append(self.parse_one_article(article))
                i += 1
            # break

        return articles_list

    def parse_one_article(self, article):

        # parse one article
        article_dict = {}

        article = article('.weui_media_box[id]')

        title = article('h4[class="weui_media_title"]').text()
        self.log('Title is %s' % title)
        url = 'http://mp.weixin.qq.com' + article('h4[class="weui_media_title"]').attr('hrefs')
        self.log('Address is %s' % url)
        summary = article('.weui_media_desc').text()
        self.log('Summary is %s' % summary)
        date = article('.weui_media_extra_info').text()
        self.log('Publish time %s' % date)
        pic = self.parse_cover_pic(article)
        content = self.parse_content_by_url(url).html()

        contentfiletitle = self.kw + '/' + title + '_' + date + '.html'
        self.save_content_file(contentfiletitle, content)

        return {
            'title': title,
            'url': url,
            'summary': summary,
            'date': date,
            'pic': pic,
            'content': content
        }

    def parse_cover_pic(self, article):

        # parse cover picture
        pic = article('.weui_media_hd').attr('style')

        p = re.compile(r'background-image:url\((.*?)\)')
        rs = p.findall(pic)
        self.log('Cover is %s ' % rs[0] if len(rs) > 0 else '')

        return rs[0] if len(rs) > 0 else ''

    def parse_content_by_url(self, url):
        # parse content by url
        page_html = self.get_selenium_js_html(url)
        return pq(page_html)('#js_content')

    def save_content_file(self, title, content):

        # save content to a file
        with open(title, 'w') as f:
            f.write(content)

    def save_file(self, content):

        # write data into a file
        with open(self.kw + '/' + self.kw + '.txt', 'w') as f:
            f.write(content)

    def log(self, msg):

        # log
        print
        u'%s: %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg)

    def need_verify(self, selenium_html):

        # Sometimes they will lock ip, identify if it includes the tag of id=verify_change;
        return pq(selenium_html)('#verify_change').text() != ''

    def create_dir(self):

        # create a folder
        if not os.path.exists(self.kw):
            os.makedirs(self.kw)

    def run(self):

        # Step0 : make a working directory and give it a public account name
        self.create_dir()

        # step 1: use public wechat english name to identify the correct account
        self.log(u'The English of wechat account is %s' % self.kw)
        self.log(u'Start retrieving sougou engine')
        sougou_search_html = self.get_search_result_by_kw()

        # step 2: Identify the wechat public account link
        self.log(u'Succeed retrieving sougou search html, and start retrieving publich account wx_url')
        wx_url = self.get_wx_url_by_sougou_search_html(sougou_search_html)

        self.log(u'Succeed getting wx_url %s' % wx_url)


        # Step 3: Get rendered url after using selenium and phantomJs
        self.log(u'Start getting selenium html rendering')
        selenium_html = self.get_selenium_js_html(wx_url)

        # Step 4: Testing if the target website is blocked
        if self.need_verify(selenium_html):
            self.log(u'The website is blocked, try it later')
        else:

            # Step 5: Identify public account data
            self.log(u'Finish html rendering, and start parsing articles')
            articles = self.parse_wx_articles_by_html(selenium_html)
            self.log(u'Get wechat article %d' % len(articles))

            # Step 6: make a list of articles
            self.log(u'Start converting wechat articles to a dictionary')
            articles_list = self.switch_arctiles_to_list(articles)

            # Step 7: Convert dictionary list in step 5 to Json
            self.log(u'Finish making a list, and start converting to Json')
            data_json = json.dumps(articles_list)

            # Step 8: Start writing article
            self.log(u'Finish converting to Json, and start saving json files')
            self.save_file(data_json)

            self.log(u'Finallyyyyyyyyyy finished!!!!')


# main
if __name__ == '__main__':

    gongzhonghao = raw_input(u'What is the wechat public account name?')
    if not gongzhonghao:
        gongzhonghao = 'python6359'
    weixin_spider(gongzhonghao).run()
