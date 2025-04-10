import requests
from bs4 import BeautifulSoup


def parse_hse():
    response = requests.get("https://ba.hse.ru/news/")
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('div', class_='post__content').find('h2', class_='first_child').find('a', href=True)
    link = title['href']
    title1 = title.text
    return title1, link[2:]


def parse_mipt():
    response = requests.get("https://pk.mipt.ru/news/")
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('ul', class_='news-list').find('a', class_='title link')
    link = 'https://pk.mipt.ru' + title['href']
    title1 = title.text
    return title1, link


def parse_mirea():
    response = requests.get("https://priem.mirea.ru/news")
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('div', class_='row row-1 cols-3').find('div', class_='col-lg-4').find('div',
                                                                                            class_='article-header')
    title1 = title.find('span').text
    link = 'https://priem.mirea.ru' + title.find('a')['href']
    return title1, link


def parse_mephi():
    response = requests.get("https://admission.mephi.ru/news")
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('div', class_='view-content').find('div',
                                                         class_='views-row views-row-1 views-row-odd views-row-first')
    title1 = title.find('div', class_='element title').text
    link = 'https://priem.mirea.ru' + title.find('a')['href']
    return title1, link


def parse_misis():
    response = requests.get("https://misis.ru/applicants/notifications/")
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('div', class_="news-list").find('article').find('h3').find('a')
    title1 = title.text
    link = 'https://misis.ru' + title['href']
    return title1, link


def parse_mai():
    response = requests.get("https://priem.mai.ru/articles/")
    soup = BeautifulSoup(response.text, 'lxml')
    title = soup.find('div', class_="col-md-6").find('a')
    title1 = title.find('p').text.lstrip()
    link = 'https://priem.mai.ru' + title['href']
    return title1, link