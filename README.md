Russian version

Телеграм бот для парсинга сайта avito.ru и парсинга информации об авто по его VIN номеру.

Парсер может собирать подробную информацию об объявления с сайта avito.ru и отправлять её сообщением в телеграм.
Так же если ему в телеграм отправить VIN номер авто то он сможет достать из различных открытых источниках подробную информацию об автомобиле.
Если боту отправить ссылку на объявление авто, то он может предоставить VIN номер этого авто и государственный номер авто.

Парсинг объявлений:
1) Для запуска необходимо отправить ссылку для поиска (Напишите боту /start, чтобы получить информацию как сделать эту ссылку)
Эту ссылку можно поменять, для этого нужно просто отправить новую ссылку.
2) Далее нажимаем кнопку "Старт" и ждем когда нам придут объявления. Для приостановки поиска снизу будет кнопка "Стоп".

Для получения информации об авто нужно:
1) Отправить сообщение в котором будет содержаться VIN номер. 
2) Следом нужно решить капчу и ожидать ответа в котором будет информация об авто.


Перед запуском требуется провести настройки, файл с настройками находиться по пути (scripts > data > settings.ini)
1) yoo_token - Токен Yoomoney для того чтобы система подписок, как её настроить рассказано в видео (https://www.youtube.com/watch?v=u5AtW681f0Q)
2) card_receiver - Карта Yoomoney куда будет осуществляться перевод денег за оформление пользователем подписки.
3) subscribe_price - Цена подписки (RUB)
4) telegram_token - Токен бота в телеграм, получить токен можно в телеграм у бота (https://t.me/BotFather)


__________________________________________________________________________________________________

English version

Telegram bot for parsing the avito.ru website and parsing information about a car by its VIN number.

The parser can collect detailed information about ads on the avito.ru website and send it as a message in Telegram. 
Additionally, if you send the bot a car's VIN number in Telegram, it can retrieve detailed information about the car from various open sources. 
If you send the bot a link to a car ad, it can provide you with the VIN number and license plate number of that car.

Ad parsing:
1) To start, you need to send a link to search for (Write /start to the bot to get information on how to make this link). You can change this link by simply sending a new one.
2) Next, click the "Start" button and wait for ads to come in. To pause the search, there is a "Stop" button at the bottom.

To get information about a car, you need to:
1) Send a message containing the VIN number.
2) Solve the captcha and wait for a response containing information about the car.

Before starting, you need to configure the settings. The settings file can be found at (scripts > data > settings.ini)
1) yoo_token - Yoomoney token for setting up subscriptions, instructions on how to do this can be found in this video (https://www.youtube.com/watch?v=u5AtW681f0Q)
2) card_receiver - Yoomoney card to which the user subscription fee will be transferred.
3) subscribe_price - Subscription price (RUB)
4) telegram_token - Telegram bot token. You can get the token from the bot in Telegram (https://t.me/BotFather)