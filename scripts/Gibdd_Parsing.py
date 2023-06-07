import aiohttp
import ast
import Gibdd_Types
from datetime import datetime, timedelta
import ssl
import matplotlib.pyplot as plt
import urllib.request


async def gibdd(user_id, captcha_nums, captcha):
    data_diagnostic_card = []
    mileage_diagnostic_card = []
    ad_counter = 1
    report_of_car = ":sport_utility_vehicle: *Отчет об Автомобиле* \n\n"
    timeout = aiohttp.ClientTimeout(total=15)

    try:
        info_car = captcha.split("&")
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/history', ssl=False, data={'vin': info_car[1], 'checkType': 'history', 'captchaWord': captcha_nums,'captchaToken': info_car[0]}) as history:
                history = ast.literal_eval(await history.text())
        try:
            if str(history['message']) == "Проверка CAPTCHA не была пройдена из-за неверного введенного значения.":
                yield f":prohibited: Проверка CAPTCHA не была пройдена из-за неверного введенного значения.\n*Повторите попытку ввода!*", False
            elif str(history['message']) == "Проверка CAPTCHA не была пройдена, поскольку не был передан ее код.":
                yield f":prohibited: Проверка CAPTCHA не была пройдена, поскольку не был передан ее код.\n*Отправте VIN заново!*", False
            elif str(history['message']) == "Срок действия кода CAPTCHA устарел, попробуйте снова.":
                yield f":prohibited: Срок действия кода CAPTCHA устарел!\n*Отправте VIN заново!*", False
            else:
                raise Exception
        except Exception:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/dtp', ssl=False, data={'vin': info_car[1], 'checkType': 'aiusdtp', 'captchaWord': captcha_nums, 'captchaToken': info_car[0]}) as dtp:
                    dtp = ast.literal_eval(await dtp.text())
                async with session.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/wanted', ssl=False, data={'vin': info_car[1], 'checkType': 'wanted', 'captchaWord': captcha_nums, 'captchaToken': info_car[0]}) as wanted:
                    wanted = ast.literal_eval(await wanted.text())
                async with session.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/restrict', ssl=False, data={'vin': info_car[1], 'checkType': 'restricted', 'captchaWord': captcha_nums, 'captchaToken': info_car[0]}) as restrict:
                    restrict = ast.literal_eval(await restrict.text())
                async with session.post('https://easy.gost.ru/', ssl=False, data={'vin': info_car[1]}) as company_reviews:
                    company_reviews = await company_reviews.text()
                async with session.post('https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/diagnostic', ssl=False, data={'vin': info_car[1], 'checkType': 'diagnostic', 'captchaWord': captcha_nums, 'captchaToken': info_car[0]}) as diagnostic:
                    diagnostic = await diagnostic.text()
                    diagnostic = ast.literal_eval(diagnostic.replace("null","'null'").replace("true","'true'").replace("false", "'false'"))


            if history["status"] == 404:
                yield f":oncoming_automobile: *Информация об автомобиле*\n:prohibited: *Данные не найдены!*", False
            else:
                owners = ":busts_in_silhouette: *История регистраций*\n"
                carinfo = ":oncoming_automobile: *Информация об авто*\n"
                car_keys = ["•Модель: ", "•Цвет: ", "•Тип ТС: ", "•Год: ", "•Объем двигателя: ",
                            "•Номер двигателя: ", "•Мощность двигателя: ", "•Категория: ", "•VIN номер: ",
                            "•Номер кузова: ", "•Кем выдан ПТС: ", "•Номер ПТС: ", "•Владельцев по ПТС: ", "•Пробег: ", "•Количество ДТП: "]
                car_values = [(lambda: history["RequestResult"]["vehicle"]["model"]),
                              (lambda: history["RequestResult"]["vehicle"]["color"]),
                              (lambda: Gibdd_Types.typeAuto[history["RequestResult"]["vehicle"]["type"]]),
                              (lambda: history["RequestResult"]["vehicle"]["year"]),
                              (lambda: history["RequestResult"]["vehicle"]["engineVolume"]),
                              (lambda: history["RequestResult"]["vehicle"]["engineNumber"]),
                              (lambda: history["RequestResult"]["vehicle"]["powerHp"]),
                              (lambda: history["RequestResult"]["vehicle"]["category"]),
                              (lambda: history["RequestResult"]["vehicle"]["vin"]),
                              (lambda: history["RequestResult"]["vehicle"]["bodyNumber"]),
                              (lambda: history["RequestResult"]["vehiclePassport"]["issue"]),
                              (lambda: history["RequestResult"]["vehiclePassport"]["number"]),
                              (lambda: len(history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"])),
                              (lambda: f'{diagnostic["RequestResult"]["diagnosticCards"][0]["odometerValue"]}км ({diagnostic["RequestResult"]["diagnosticCards"][0]["dcDate"]})'),
                              (lambda: len(dtp["RequestResult"]["Accidents"]))]

                for i in range(len(car_keys)):
                    try:
                        carinfo += f"*{car_keys[i]}*`{car_values[i]()}`\n"
                    except Exception:
                        pass

                first, skip_sending = True, False
                for i in range(len(history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"])):
                    try:
                        persontype = "Физ. лицо" if history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["simplePersonType"] == "Natural" else "Юр. лицо"
                        owners += f'•*{history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["from"]}* по *{history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["to"]}* - *{persontype}*\n\t*Основания: *_{Gibdd_Types.typeOperation[history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["lastOperation"]]}_\n\n'
                    except KeyError:
                        persontype = "Физ. лицо" if history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["simplePersonType"] == "Natural" else "Юр. лицо"
                        owners += f'•*{history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["from"]}* по *Н.В.* - *{persontype}*\n*Владеет: {duration_days((datetime.now()-datetime.strptime(history["RequestResult"]["ownershipPeriods"]["ownershipPeriod"][i]["from"], "%Y-%m-%d")).days)}*\n'
                    if len(owners) > 3800:
                        if first:
                            yield f"{carinfo}\n{owners}", False
                            first, skip_sending, owners = False, True, ":warning: *Продолжение истории регистраций*\n\n"
                        else:
                            yield f"{owners}", False
                            owners = ":warning: *Продолжение истории регистраций*\n\n"
                if not skip_sending:
                    yield f"{carinfo}\n{owners}", False


            try:
                diagnostic_card = f":page_facing_up: *Диагностичекая карта*\n\n•*Номер:* `{diagnostic['RequestResult']['diagnosticCards'][0]['dcNumber']}`\n•*Осмотр проведен:* `{diagnostic['RequestResult']['diagnosticCards'][0]['dcDate']}`\n•*Действует до:* `{diagnostic['RequestResult']['diagnosticCards'][0]['dcExpirationDate']}`\n"
                diagnostic_card += f"•*Пробег:* `{diagnostic['RequestResult']['diagnosticCards'][0]['odometerValue']}км`\n•*Адрес:* `{diagnostic['RequestResult']['diagnosticCards'][0]['pointAddress']}`"
                yield diagnostic_card, False
                data_diagnostic_card.append(diagnostic['RequestResult']['diagnosticCards'][0]['dcDate'])
                mileage_diagnostic_card.append(int(diagnostic['RequestResult']['diagnosticCards'][0]['odometerValue']))
            except Exception:
                pass


            try:
                diagnostic_card = f":page_with_curl: *Истекшие ДК*\n\n"
                for i in range(len(diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'])):
                    diagnostic_card += f"•*Номер:* `{diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['dcNumber']}`\n•*Осмотр проведен:* `{diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['dcDate']}`\n"
                    diagnostic_card += f"•*Истек:* `{diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['dcExpirationDate']}`\n•*Пробег:* `{diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['odometerValue']}км`\n\n"
                    data_diagnostic_card.append(diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['dcDate'])
                    mileage_diagnostic_card.append(int(diagnostic['RequestResult']['diagnosticCards'][0]['previousDcs'][i]['odometerValue']))
                graph, twist = create_graph(data_diagnostic_card, mileage_diagnostic_card, user_id)
                if graph:
                    yield diagnostic_card, f"graph{user_id}.png"
                    report_of_car += f":check_mark_button: Пробег на авто *не скручивали*\n\n" if not twist else f":prohibited: *Скручивали пробег* на авто!\n\n"
                else:
                    yield diagnostic_card, False
                    report_of_car += f":white_question_mark: Мало информации о пробеге\n\n"
            except Exception as e:
                report_of_car += f":white_question_mark: Мало информации о пробеге\n\n"


            try:
                if restrict["RequestResult"]["records"] == []:
                    report_of_car += f":check_mark_button: На авто не накладывались *ограничения*\n\n"
                else:
                    len_restrict = len(restrict['RequestResult']['records'])
                    text_len_restrict = "записи" if len_restrict >= 2 and len_restrict <=4 else "запись" if len_restrict == 1 else "записей"
                    text_find = "Найдена" if len_restrict == 1 else "Найдено"
                    report_of_car += f":prohibited: {text_find} `{len_restrict}` {text_len_restrict} об *ограничениях*!\n\n"
            except Exception:
                report_of_car += f":prohibited: *Ошибка при получении данных об ограничениях! :(*\n\n"


            try:
                if str(wanted["RequestResult"]) == "{'records':, 'count': 0, 'error': 0}" or str(wanted["RequestResult"]) == "{'records': [], 'count': 0, 'error': 0}":
                    report_of_car += f":check_mark_button: Авто не числилось в *розыске*\n\n"
                else:
                    report_of_car += f":prohibited: Авто числится в *розыске*!!!\nПодробно можете узнать на сайте [ГИБДД](https://xn--90adear.xn--p1ai/check/auto)\n*VIN*: {info_car[1]}\n\n"
            except Exception:
                report_of_car += f":prohibited: *Ошибка при получении данных о розыске! :(*\n\n"


            if "не найден среди отзывных кампаний" in company_reviews:
                report_of_car += f":check_mark_button: На авто не было *отзывных кампаний*\n\n"
            else:
                report_of_car += f":prohibited: Найдена информация об *отзывных кампаниях*!\nПолную информацию можете получить пройдя по [ссылке в тексте.](https://easy.gost.ru/)\nVIN: `{info_car[1]}`\n\n"


            if dtp["RequestResult"]["Accidents"] == []:
                report_of_car += f":check_mark_button: Нет зафиксированных *ДТП*\n\n"
                yield report_of_car, False
            else:
                report_of_car += f':prohibited: *Зафиксированных ДТП: {len(dtp["RequestResult"]["Accidents"])}*\n\n'
                yield report_of_car, False
                for i in range(len(dtp["RequestResult"]["Accidents"])):
                    points = str(dtp['RequestResult']["Accidents"][i]['DamagePoints']).replace("'","").replace("[","").replace("]","").replace(" ", "")
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    with urllib.request.urlopen(fr"https://vin01.ru/images/s.php?map={points}", context=ssl_context) as u, open(fr'data\data_photo/dtpscr{user_id}.jpg', 'wb') as f:
                        f.write(u.read())
                    dtp_info = "*ДТП*\n"
                    dtp_keys = ["•Дата: ", "•Номер: ", "•Тип: ", "•Состояние: ", "•Участников: ", "•Место: "]
                    dtp_values = [(lambda: dtp['RequestResult']["Accidents"][i]["AccidentDateTime"]),
                                  (lambda: dtp['RequestResult']["Accidents"][i]["AccidentNumber"]),
                                  (lambda: dtp['RequestResult']["Accidents"][i]["AccidentType"]),
                                  (lambda: dtp['RequestResult']["Accidents"][i]["VehicleDamageState"]),
                                  (lambda: dtp['RequestResult']["Accidents"][i]["VehicleAmount"]),
                                  (lambda: dtp['RequestResult']["Accidents"][i]["AccidentPlace"])]
                    for y in range(len(dtp_keys)):
                        try:
                            dtp_info += f"*{dtp_keys[y]}*`{dtp_values[y]()}`"
                        except KeyError:
                            pass
                    yield dtp_info + f"\n*{ad_counter}/{len(dtp['RequestResult']['Accidents'])}*", f"dtpscr{user_id}.jpg"
                    ad_counter += 1
    except Exception as e:
        yield f"*Ошибка!* Скорее всего произошли ошибки на сайте ГИБДД. Повторите попытку!", False


def create_graph(data, mileage, id_user):
    twisted_mileage = False
    if len(data) < 3:
        return False, False

    data_sorted = list(sorted(data))
    all_dict = {item: mileage[data.index(item)] for item in data_sorted}

    for mil in range(1, len(data_sorted)):
        if int(all_dict[data_sorted[mil-1]]) > int(all_dict[data_sorted[mil]]):
            twisted_mileage = True

    plt.figure(figsize=(7, 7))
    plt.plot(all_dict.keys() , all_dict.values(), linewidth=2, color='#34495E')
    plt.fill_between(all_dict.keys(), all_dict.values(), 0, facecolor='#34495E', interpolate=True, alpha=0.5)

    if len(data) >= 5:
        plt.xticks(rotation=45)
    plt.title('График пробега')
    plt.savefig(fr'data\data_photo/graph{id_user}.png')
    return True, twisted_mileage


def duration_days(count_days):
    years = count_days // 365
    months = (count_days % 365) // 30
    weeks = ((count_days % 365) % 30) // 7
    days = ((count_days % 365) % 30) % 7 + weeks*7
    duration_list = []
    if years > 0:
        duration_list.append(f"{years} {'год' if years == 1 else 'года' if 2 <= years <= 4 else 'лет'}")
    if months > 0:
        duration_list.append(f"{months} {'месяц' if months == 1 else 'месяца' if 2 <= months <= 4 else 'месяцев'}")
    if days > 0:
        duration_list.append(f"{days} {'день' if days == 1 else 'дня' if 2 <= days <= 4 else 'дней'}")
    return ", ".join(duration_list)