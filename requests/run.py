"""
    作者：zf
    功能：分析百度贴吧-玛瑙湾首页的回复数据
    目标字段：来源，链接地址，页码，类型(新帖/回复)，内容，发送人，时间
    版本：1.0
    日期：20191206
"""
import re
import time
import json
import requests
from selenium import webdriver
from bs4 import BeautifulSoup


def get_soup(url):
    r = requests.get(url, timeout=30)
    soup = BeautifulSoup(r.text, 'lxml')
    return soup


def get_top_info(url):
    """
        获取置顶栏的最新回复
    """
    # TODO：判断是否为新帖/最近回复帖
    div_top = get_soup(url).find('li', class_='j_thread_list thread_top j_thread_list clearfix')
    # div_list = get_soup(url).find_all('li', class_=re.compile('j_thread_list clearfix'))
    # for div_top in div_list:
    link_top = r'http://tieba.baidu.com' + div_top.find('a', class_="j_th_tit")['href']
    top_info = get_soup(link_top).find('div', class_='p_thread thread_theme_5')
    # 筛选出不包含style属性的标签
    page_info = int(top_info.find('span', class_='red', style=False).text)
    # print(type(page_info))
    for i in range(1, page_info + 1):
        link = link_top + '?pn={}'.format(i)
        print(link)
        # 配置并获得WebDriver对象
        browser = webdriver.Chrome()
        time.sleep(10)

        # 发起get请求
        browser.get(link)
        info = BeautifulSoup(browser.page_source, 'lxml')

        # 每楼的评论及评论时间
        floor_info = info.find_all('div', class_='l_post j_l_post l_post_bright')
        for j in floor_info:
            post_no = json.loads(j['data-field'])['content']['post_no']
            publish_time = json.loads(j['data-field'])['content']['date']
            content = j.find('div', class_='d_post_content j_d_post_content clearfix').text.strip()
            # print('第{}楼评论'.format(post_no), publish_time, content)
            print('第{}楼评论'.format(post_no))

            # 爬取回复失败(静态页面) --<div class ="core_reply j_lzl_wrapper hideLzl"></div>，分析可能是js动态渲染导致的。
            """
                <div class="d_post_content_main">
                <div class="core_reply j_lzl_wrapper">
                <div class="j_lzl_container core_reply_wrapper">
                <div class="lzl_cnt">
            """
            reply_info = j.find_all('div', class_='lzl_cnt')
            print(reply_info)

        time.sleep(10)
        browser.quit()


def main():
    """
        主函数
    """
    url = r'http://tieba.baidu.com/f?ie=utf-8&kw=%E7%8E%9B%E7%91%99%E6%B9%BE'
    # r = requests.get(url, timeout=30)
    # soup = BeautifulSoup(r.text, 'lxml')
    # 回复数量
    # div_list = soup.find_all('span', class_='threadlist_rep_num center_text', title='回复')
    # 最新回复时间
    # div_list = soup.find_all('span', class_='threadlist_reply_date pull_right j_reply_data', title='最后回复时间')

    # div_list = soup.find_all('li', class_='j_thread_list clearfix')
    # print(div_list)
    get_top_info(url)


if __name__ == '__main__':
    main()
