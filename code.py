# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

import datetime
import time
from tkinter import *
from tkinter import messagebox
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException
import chromedriver_autoinstaller

def start_crawling():
    # URL이 비어있으면
    if (input_url_var.get() == ''):
        messagebox.showwarning('크롤링', 'URL을 입력하세요.')
        return

    # 시작 버튼 재 눌림 방지
    crawling_button['state'] = DISABLED

    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options = options)

    # https://kin.naver.com/qna/expertAnswerList.naver?dirId=7010101
    input_url = input_url_var.get()
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # 진료 분야별 전체 URL
    url = '{}&queryTime={}%2015%3A28%3A18&page={}'

    # A열 제목 / B열 질문 / C열 답변 / D열 Q&A url
    A, B, C, D = [], [], [], []

    # 진료 분야
    medical_department = ''

    # 크로링 시작 시간
    start_time = time.time()

    # 1 ~ 100 페이지 크롤링
    for page in range(1, 100):
        try:
            driver.get(url.format(input_url, today, page))
            driver.implicitly_wait(10)

            # 진료 분야 추출
            if (page == 1):
                medical_department = driver.find_element(By.CSS_SELECTOR, 'div.s_header > h2').text

            # 페이지별 질문 목록 URL
            sub_url_list = [a.get_attribute('href') for a in driver.find_elements(By.CSS_SELECTOR, 'td.title > a')]
            for sub_url in sub_url_list:
                try:
                    # Q&A url
                    D.append(sub_url)
                    driver.get(sub_url)
                    time.sleep(1)

                    # 제목
                    title = driver.find_element(By.CSS_SELECTOR, 'div.c-heading__title-inner')
                    A.append(title.text)
                    print(title.text)

                    # 질문
                    question = driver.find_element(By.CSS_SELECTOR, 'div.c-heading__content')
                    B.append(question.text)

                    # 답변
                    answer = driver.find_element(By.CSS_SELECTOR, 'div.se-module.se-module-text')
                    C.append(answer.text)

                    # 크롤링 진행 시간 계산 및 출력
                    elapsed_time = time.time() - start_time
                    elapsed_time_label['text'] = f'크롤링 시간 : {int(elapsed_time)} 초'
                    root.update()

                except NoSuchElementException:
                    print('NoSuchElementException!')
                except InvalidArgumentException:
                    print('InvalidArgumentException!')

        # URL 오류 처리
        except InvalidArgumentException:
            messagebox.showwarning('크롤링', 'URL에 오류가 있습니다.')
            driver.quit() # driver process shut down
            crawling_button['state'] = NORMAL
            root.update()
            return

    # 진료 분야별 결과 엑셀 저장
    df = pd.DataFrame({'제목': A, '질문': B, '답변': C, 'Q&A url': D})
    df.to_excel(f'{medical_department}.xlsx', index=False)

    messagebox.showinfo('크롤링', '크롤링이 완료되었습니다.')
    driver.quit() # driver process shut down
    crawling_button['state'] = NORMAL
    root.update()

root = Tk()
root.resizable(False, False)
root.title('건강 관련 지식인 크롤링')

input_url_var = StringVar()
Label(root, text=' 진료과 URL ').grid(row=0, column=0, padx=10, pady=10)
Entry(root, textvariable=input_url_var, width=100).grid(row=0, column=1, padx=10, pady=10)
crawling_button = Button(root, text=' 크롤링 시작 ', command=start_crawling)
crawling_button.grid(row=1, column=0, padx=10, pady=10)
elapsed_time_label = Label(root, text='크롤링 시간 : 0 초')
elapsed_time_label.grid(row=1, column=1, padx=10, pady=10)

root.mainloop()
