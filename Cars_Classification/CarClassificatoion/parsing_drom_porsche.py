#!/usr/bin/env python
# coding: utf-8

# In[80]:


from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import tqdm
import random 
import pandas as pd
import numpy as np


# ### Функция для перехода на новую страницу

# In[81]:


def new_page_click(browser, page_num):
    if page_num == 1:
        browser.find_element(By.XPATH, '/html/body/div[2]/div[5]/div[1]/div[1]/div[5]/div/div[2]/div/div/a').click()
        time.sleep(random.randint(1, 3))
    else:
        browser.find_element(By.XPATH, '/html/body/div[2]/div[4]/div[1]/div[1]/div[5]/div/div[2]/div/div/a').click()
        time.sleep(random.randint(1, 3))   


# ### Парсинг марки, модели и года выпуска

# In[115]:


def parsing_model(browser, num, page):
    xpath = f'/html/body/div[2]/div[{page}]/div[1]/div[1]/div[5]/div/div[1]/a[{num}]/div[2]/div[1]/div[1]/span'
    model = browser.find_element(By.XPATH, xpath)
    model = model.text
    return model


# ### Парсинг города продажи

# In[84]:


def parsing_city(browser, num, page):
    xpath = f'/html/body/div[2]/div[{page}]/div[1]/div[1]/div[5]/div/div[1]/a[{num}]/div[3]/div[2]/div/span'
    city = browser.find_element(By.XPATH, xpath)
    city = city.text
    time.sleep(random.randint(1, 3))
    return city


# ### Переход на страницу с автомобилем 

# In[85]:


def click_auto_page(browser, num, page):
    xpath = f'/html/body/div[2]/div[{page}]/div[1]/div[1]/div[5]/div/div[1]/a[{num}]/div[2]/div[1]'
    browser.find_element(By.XPATH, xpath).click()
    time.sleep(random.randint(1, 3))


# ### Парсинг характеристик автомобиля

# In[86]:


def parsing_characteristic(browser):
    xpath = '/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[2]'
    characteristic = browser.find_element(By.XPATH, xpath)
    characteristic = characteristic.text
    return characteristic    


# ### Парсинг количества владельцев 

# In[87]:


def parsing_number_of_owners(browser):
    try:
        xpath = '/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[3]/div[3]/div'
        owners = browser.find_element(By.XPATH, xpath)
        owners = owners.text
        owners = owners.split()
        return int(owners[0])
    except:
        owners = np.NaN
        return owners
    finally:
        time.sleep(random.randint(1, 3))
        


# ### Парсинг цены автомобиля 

# In[88]:


def parsing_price(browser):
    xpath = '/html/body/div[2]/div[4]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]'
    price = browser.find_element(By.XPATH, xpath)
    price = price.text
    price = price.split()[:-1]
    price = int(''.join(price))
    time.sleep(random.randint(1, 3))
    return price


# ### Заполняем марку модель и год автомобиля

# In[89]:


def change_model(model, auto):
    model = model.split()
    auto.append(model[0])
    auto.append(' '.join(model[1:-1])[:-1])
    auto.append(model[-1])


# ### Заполняем остальные характеристики автомобиля

# In[158]:


def change_characteristic(characteristic, auto):
    describe = ['Двигатель', 'Мощность', 'Коробка передач', 'Привод', 'Цвет', 'Пробег, км', 'Поколение']
    characteristic = characteristic.split('\n')
    for i in range(len(describe)):
        for j in range(len(characteristic)):
            if describe[i] in characteristic[j]:
                ch = characteristic[j].split()
                if i == 0:
                    if ch[1] == 'бензин,' or ch[1] == 'дизель,':
                        auto.append(ch[1][:-1])
                        auto.append(float(ch[2]))
                    else:
                        auto.append('электро')
                        auto.append(np.NaN)                      
                elif i == 1:
                    ch = ch[len(describe[i].split()):2]
                    auto.append(' '.join(ch))
                elif i == 5:
                    if ch[-1] == 'РФ':
                        ch = ch[:-4]
                        ch = ch[len(describe[i].split()):]
                        auto.append(int(''.join(ch)[:-1]))
                    elif ch[2] == 'новый':
                        auto.append(0)
                    else:
                        ch = ch[len(describe[i].split()):]
                        auto.append(int(''.join(ch))) 
                else:
                    ch = ch[len(describe[i].split()):]
                    auto.append(' '.join(ch))
                break
            elif j == (len(characteristic) - 1):
                if i == 0:
                    auto.append(np.NaN)
                    auto.append(np.NaN)
                else:
                    auto.append(np.NaN)


# ### Парсинг одного автомобиля 

# In[91]:


def parsing_auto(browser, num, page):
    auto = []
    model = parsing_model(browser, num, page) # парсим марку, модель и год выпуска
    change_model(model, auto) # заполняем список
    auto.append(parsing_city(browser, num, page)) # парсим город продажи и добавляем в список
    click_auto_page(browser, num, page) # кликаем на страницу с автомобилем
    characteristic = parsing_characteristic(browser) # парсим характеристики 
    change_characteristic(characteristic, auto) # заполняем список
    auto.append(parsing_number_of_owners(browser)) # парсим количество владельцев
    auto.append(parsing_price(browser)) # парсим цену
    browser.back() # переходим обратно на страницу с автомобилями 
    return auto 


# ### Парсим всю страницу 

# In[208]:


def parsing_page(browser, page, cars):
    # проходимся циклом по всем автомобилям на странице 
    for i in tqdm.trange(1, 21):
        cars.append(parsing_auto(browser, i, page))
    print('Парсинг страницы завершен')
            


# In[105]:


# cars = []


# ### Парсим drom.ru

# In[211]:


browser = webdriver.Chrome()
browser.get('https://auto.drom.ru/porsche/all/page70/?unsold=1')
try:
    for i in range(2, 8):
        parsing_page(browser, "4", cars)
        new_page_click(browser, i)
except Exception as ex:
    print(ex)
finally:
    browser.close()
    browser.quit()
    


# In[ ]:


# Иногда может возникать ошибка, что на странице нет какого-либо xpath, поэтому парсим 
# остаток страницы, пропуская автомобиль на котормо возникла ошибка


# In[169]:


browser = webdriver.Chrome()
browser.get('https://auto.drom.ru/porsche/all/page34/?unsold=1')
try:
    for i in range(6, 21):
        cars.append(parsing_auto(browser, i, "4"))
except Exception as ex:
    print(ex)
finally:
    browser.close()
    browser.quit()


# ### Создаем датафрейм с нашими автомобилями 

# In[216]:


df = pd.DataFrame(cars, columns = ["Марка", "Модель", "Год выпуска", "Город продажи",
                                   "Тип топлива", "Объем двигателя, л.", "Мощность, л.с.",
                                  "Коробка передач", "Привод", "Цвет", "Пробег, км",
                                  "Поколение", "Количество регистраций", "Цена, руб."])
df


# In[225]:


# Смотрим на типы данных
print('\nDatatypes\n', df.dtypes, sep='') 


# In[218]:


# Изменяем на целочисленный тип данных 'Мощность, л.с.'
df = df.astype({'Мощность, л.с.': np.float})


# ### Удаляем дубликаты 

# In[227]:


print(len(df)) 
df = df.drop_duplicates() 
print(len(df))


# In[229]:


df.to_csv('porsche_cars.csv') # Сохраянем датафрейм в .csv

