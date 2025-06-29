#!/usr/bin/env python3
import os
import time
import json
import requests
import threading
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

class FinancialBot:
    def __init__(self):
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.admin_id = os.environ.get('ADMIN_ID')
        self.offset = 0
        self.running = False
        
    def send_message(self, chat_id, text, keyboard=None):
        data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
        if keyboard:
            data['reply_markup'] = json.dumps(keyboard)
        try:
            response = requests.post(f'https://api.telegram.org/bot{self.token}/sendMessage', json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def handle_start(self, chat_id, user_name):
        welcome = """Привет! Снизу я расскажу про наши условия и услуги, которые мы предоставляем. А так же про условия, с которыми вы соглашаетесь.

Наш Бот поможет автоматически оплатить услуги европейской картой, сделать перевод на зарубежный счёт или просто купить дискорд нитро.

**Список доступных команд:**
/menu - главное меню и список доступных услуг
/help - помощь с использованием бота
/address - список доступных адресов
/price - действующий прайс-лист

**Общая инструкция по использованию нашего сервиса:**

1) Выберите нужную услугу по команде /menu.
2) Выберите валюту, в которой необходимо произвести оплату.
3) Отправьте в чат сумму оплаты; бот сам рассчитает комиссию.
4) Выберите удобный способ оплаты: либо на наш адрес в криптовалюте, либо на российский банк.
5) Произведите оплату по выбранному вами адресу. Как только мы получим средства, мы позаботимся о вашей услуге.

Если что-либо идёт не так, или вам нужна услуга, не включенная в меню, вы всегда можете обращаться к нам, тэгнув @swiwell или @Deadkid. Ответить мы сможем с 11:00 до 22:00 по мск.

Обратите внимание, что мы не можем гарантировать моментальное выполнение заказа, в рабочее время ответ поддержки может занять до часа.

**Важно:** Если ваш платеж был отправлен, но по какой-либо причине оплата с нашей карты не была произведена, мы вернем вам сумму оплаты за вычетом 50% нашей комиссии. В случае успешной оплаты, но последующего возврата средств по какой-либо причине, вам будет возвращена сумма за вычетом 100% нашей комиссии. При возврате средств на крипто-адреса, может возникнуть комиссия платформы в зависимости от выбранной сети.

Пожалуйста обратите внимание, что проверка получения платежей в рублях пока проходит вручную.

Выберите нужную услугу:"""
        
        keyboard = {'inline_keyboard': [
            [{'text': '💳 Оплата зарубежной картой', 'callback_data': 'foreign_payment'}],
            [{'text': '💸 Перевод на зарубежную карту', 'callback_data': 'foreign_transfer'}],
            [{'text': '👤 Другое (связаться с оператором)', 'callback_data': 'contact_operator'}]
        ]}
        
        success = self.send_message(chat_id, welcome, keyboard)
        if chat_id != self.admin_id:
            self.send_message(self.admin_id, f"Новый пользователь: {user_name} (ID: {chat_id})")
        return success
    
    def handle_menu(self, chat_id):
        menu_text = """📋 **Главное меню услуг**

Выберите нужную категорию услуг:

🔹 **Популярные услуги:**
• Discord Nitro
• Spotify Premium
• Netflix подписки
• YouTube Premium
• ChatGPT Plus

🔹 **Переводы и платежи:**
• Переводы на европейские карты
• Оплата зарубежных сервисов
• Покупки в европейских магазинах

🔹 **Дополнительные услуги:**
• Steam, Epic Games покупки
• Apple ID пополнение
• Google Play платежи

Выберите категорию или используйте команды:"""
        
        keyboard = {'inline_keyboard': [
            [{'text': '🎮 Discord & Gaming', 'callback_data': 'gaming_services'}],
            [{'text': '🎵 Подписки и стриминг', 'callback_data': 'streaming_services'}],
            [{'text': '💸 Переводы и платежи', 'callback_data': 'transfer_services'}],
            [{'text': '📞 Связаться с оператором', 'callback_data': 'contact_operator'}],
            [{'text': '🔙 Назад в главное меню', 'callback_data': 'back_to_main'}]
        ]}
        
        return self.send_message(chat_id, menu_text, keyboard)
    
    def handle_help(self, chat_id):
        help_text = """❓ **Помощь по использованию бота**

**Основные команды:**
/menu - главное меню услуг
/help - эта справка
/address - реквизиты для оплаты
/price - актуальный прайс-лист

**Как сделать заказ:**
1. Выберите услугу в /menu
2. Укажите валюту оплаты
3. Отправьте сумму в чат
4. Выберите способ оплаты
5. Переведите средства по реквизитам
6. Ожидайте выполнения услуги

**Поддержка:**
• Рабочие часы: 11:00 - 22:00 МСК
• Операторы: @swiwell, @realdealkid
• Время ответа: до 1 часа

**Важные условия:**
• Возврат при неуспешной оплате: -50% комиссии
• Возврат после успешной оплаты: -100% комиссии
• Проверка рублевых платежей - вручную

Есть вопросы? Свяжитесь с оператором!"""
        
        keyboard = {'inline_keyboard': [
            [{'text': '📋 Главное меню', 'callback_data': 'menu'}],
            [{'text': '💬 Связаться с оператором', 'callback_data': 'contact_operator'}],
            [{'text': '🔙 На главную', 'callback_data': 'back_to_main'}]
        ]}
        
        return self.send_message(chat_id, help_text, keyboard)
    
    def handle_address(self, chat_id):
        address_text = """📍 **Реквизиты для оплаты**

**Криптовалютные адреса:**

**Bep 20 :**
`0x3d128fa1ecda325c3b812d81983066e821d06c8b`

**Sol :**
`AuLgJc683BK7T2cD5e5vwNM9YXaUZpcwDe37RSiq4M2k`

**USDT (TRC20):**
`TGi5BLRCjZusbJAM5LFhdRQU6KPeXLg6Eq`

**Tether (ERC20):**
`0x3d128fa1ecda325c3b812d81983066e821d06c8b`

**Внутренний перевод Bybit:**
`20504633`

**Российские банки:**
• Тинькофф:  5536914013162536 Артем К

*Точные реквизиты предоставляются после оформления заказа*

**Внимание:** Обязательно указывайте в комментарии к переводу ваш Telegram ID для быстрой идентификации платежа."""
        
        keyboard = {'inline_keyboard': [
            [{'text': '💳 Оформить заказ', 'callback_data': 'foreign_payment'}],
            [{'text': '📋 Главное меню', 'callback_data': 'menu'}],
            [{'text': '🔙 На главную', 'callback_data': 'back_to_main'}]
        ]}
        
        return self.send_message(chat_id, address_text, keyboard)
    
    def handle_price(self, chat_id):
        price_text = """💰 **Действующий прайс-лист**

**Комиссии по услугам:**

🔹 **Оплата зарубежными картами:**
• До $100 - комиссия 8%
• $100-500 - комиссия 6%
• Свыше $500 - комиссия 5%

🔹 **Переводы на зарубежные карты:**
• До €200 - комиссия 10%
• €200-1000 - комиссия 8%
• Свыше €1000 - комиссия 6%

*минимальная комиссия 3$*
*Курсы валют обновляются каждый час*

Точная стоимость рассчитывается при оформлении заказа."""
        
        keyboard = {'inline_keyboard': [
            [{'text': '💳 Оформить заказ', 'callback_data': 'foreign_payment'}],
            [{'text': '📋 Главное меню', 'callback_data': 'menu'}],
            [{'text': '🔙 На главную', 'callback_data': 'back_to_main'}]
        ]}
        
        return self.send_message(chat_id, price_text, keyboard)
    
    def handle_foreign_payment(self, chat_id, user_name):
        payment_text = """💳 **Оплата зарубежной картой**

Мы поможем оплатить любые зарубежные сервисы нашей европейской картой:

🔹 **Что можем оплатить:**
• Подписки (Netflix, Spotify, Adobe и др.)
• Gaming (Steam, Epic Games, Blizzard)
• Сервисы (ChatGPT, Midjourney, Notion)
• Интернет-магазины (Amazon, eBay и др.)
• Мобильные приложения и игры

**Как оформить заказ:**
1. Укажите название сервиса/товара
2. Приложите ссылку (если есть)
3. Укажите сумму оплаты
4. Выберите валюту для расчета
5. Произведите оплату по нашим реквизитам

Комиссия: 5-8% в зависимости от суммы
Время выполнения: от 15 минут до 2 часов

Готовы оформить заказ?"""
        
        keyboard = {'inline_keyboard': [
            [{'text': '📝 Оформить заказ сейчас', 'callback_data': 'create_payment_order'}],
            [{'text': '💰 Посмотреть тарифы', 'callback_data': 'price'}],
            [{'text': '👤 Связаться с оператором', 'callback_data': 'contact_operator'}],
            [{'text': '🔙 Назад в меню', 'callback_data': 'menu'}]
        ]}
        
        self.send_message(chat_id, payment_text, keyboard)
        
        admin_msg = f"""💳 Заявка на оплату зарубежной картой
Пользователь: {user_name} (ID: {chat_id})
Время: {datetime.now().strftime('%H:%M %d/%m/%Y')}
Статус: Просмотр условий"""
        
        return self.send_message(self.admin_id, admin_msg)
    
    def handle_foreign_transfer(self, chat_id, user_name):
        transfer_text = """💸 **Перевод на зарубежную карту**

Переводим средства на европейские и американские банковские карты:

🔹 **Поддерживаемые банки:**
• Visa, Mastercard (Европа)
• American Express
• Revolut, Wise
• Немецкие банки (Sparkasse, Deutsche Bank)
• Польские банки (PKO, mBank)

**Процесс перевода:**
1. Укажите данные получателя
2. Сумму перевода в USD/EUR
3. Реквизиты карты получателя
4. Произведите оплату + комиссия
5. Перевод поступит в течение 1-3 дней

Комиссия: 6-10% в зависимости от суммы
Минимальная сумма: $50
Максимальная сумма: $5000 за раз

Начнем оформление?"""
        
        keyboard = {'inline_keyboard': [
            [{'text': '📝 Оформить перевод', 'callback_data': 'create_transfer_order'}],
            [{'text': '💰 Посмотреть тарифы', 'callback_data': 'price'}],
            [{'text': '👤 Связаться с оператором', 'callback_data': 'contact_operator'}],
            [{'text': '🔙 Назад в меню', 'callback_data': 'menu'}]
        ]}
        
        self.send_message(chat_id, transfer_text, keyboard)
        
        admin_msg = f"""💸 Заявка на перевод на зарубежную карту
Пользователь: {user_name} (ID: {chat_id})
Время: {datetime.now().strftime('%H:%M %d/%m/%Y')}
Статус: Просмотр условий"""
        
        return self.send_message(self.admin_id, admin_msg)
    
    def handle_contact_operator(self, chat_id, user_name):
        contact_text = """👤 **Связь с оператором**

Вы можете связаться с нашими операторами для:
• Получения персональной консультации
• Оформления нестандартных заказов  
• Решения возникших проблем
• Получения статуса вашего заказа

**Наши операторы:**
👨‍💼 @swiwell - основной оператор
👨‍💼 @realdeadlkid - технический оператор

**Режим работы:**
🕐 11:00 - 22:00 по московскому времени
📞 Время ответа: до 1 часа в рабочее время

Оператор уже уведомлен о вашем обращении и скоро свяжется с вами.

Опишите ваш вопрос в следующем сообщении."""
        
        keyboard = {'inline_keyboard': [
            [{'text': '📋 Вернуться в меню', 'callback_data': 'menu'}],
            [{'text': '🔙 На главную', 'callback_data': 'back_to_main'}]
        ]}
        
        self.send_message(chat_id, contact_text, keyboard)
        
        admin_msg = f"""👤 ЗАПРОС СВЯЗИ С ОПЕРАТОРОМ
Пользователь: {user_name} (ID: {chat_id})
Время: {datetime.now().strftime('%H:%M %d/%m/%Y')}

Пользователь запрашивает связь с оператором.
Свяжитесь с ним в ближайшее время."""
        
        return self.send_message(self.admin_id, admin_msg)
    
    def handle_create_order(self, chat_id, order_type, user_name):
        if order_type == 'payment':
            order_text = """📝 **Оформление заказа на оплату**

Для оформления заказа отправьте следующую информацию:

1️⃣ Название сервиса/товара
2️⃣ Ссылку (если есть)
3️⃣ Сумму оплаты и валюту
4️⃣ Любые дополнительные детали

**Пример:**
"Netflix подписка на месяц
$15.99
Нужна подписка для региона ЕU"

После получения информации оператор рассчитает итоговую стоимость с комиссией и предоставит реквизиты для оплаты."""
        
        elif order_type == 'transfer':
            order_text = """📝 **Оформление заказа на перевод**

Для оформления перевода отправьте:

1️⃣ Сумму перевода и валюту
2️⃣ Страну получателя
3️⃣ Банк получателя (если известен)
4️⃣ Срочность перевода

**Внимание:** Реквизиты карты получателя будут запрошены отдельно в защищенном виде.

**Пример:**
"€500 в Германию
Банк: Deutsche Bank
Стандартная скорость (1-3 дня)"

Оператор рассчитает комиссию и предоставит инструкции."""
        else:
            order_text = "Неизвестный тип заказа."
        
        keyboard = {'inline_keyboard': [
            [{'text': '👤 Связаться с оператором', 'callback_data': 'contact_operator'}],
            [{'text': '🔙 Назад', 'callback_data': 'menu'}]
        ]}
        
        self.send_message(chat_id, order_text, keyboard)
        
        admin_msg = f"""📝 Заявка на оформление заказа
Тип: {'Оплата картой' if order_type == 'payment' else 'Перевод на карту'}
Пользователь: {user_name} (ID: {chat_id})
Время: {datetime.now().strftime('%H:%M %d/%m/%Y')}

Пользователь готов оформить заказ. Ожидайте детали в следующих сообщениях."""
        
        return self.send_message(self.admin_id, admin_msg)
    
    def handle_callback(self, chat_id, data, user_name):
        if data == 'foreign_payment':
            return self.handle_foreign_payment(chat_id, user_name)
        elif data == 'foreign_transfer':
            return self.handle_foreign_transfer(chat_id, user_name)
        elif data == 'contact_operator':
            return self.handle_contact_operator(chat_id, user_name)
        elif data == 'menu':
            return self.handle_menu(chat_id)
        elif data == 'help':
            return self.handle_help(chat_id)
        elif data == 'address':
            return self.handle_address(chat_id)
        elif data == 'price':
            return self.handle_price(chat_id)
        elif data == 'back_to_main':
            return self.handle_start(chat_id, user_name)
        elif data == 'create_payment_order':
            return self.handle_create_order(chat_id, 'payment', user_name)
        elif data == 'create_transfer_order':
            return self.handle_create_order(chat_id, 'transfer', user_name)
    
    def process_update(self, update):
        try:
            if 'message' in update:
                message = update['message']
                chat_id = str(message['chat']['id'])
                user_name = message['from'].get('first_name', 'Пользователь')
                
                if 'text' in message:
                    text = message['text'].strip()
                    
                    if text.startswith('/start'):
                        self.handle_start(chat_id, user_name)
                    elif text.startswith('/menu'):
                        self.handle_menu(chat_id)
                    elif text.startswith('/help'):
                        self.handle_help(chat_id)
                    elif text.startswith('/address'):
                        self.handle_address(chat_id)
                    elif text.startswith('/price'):
                        self.handle_price(chat_id)
                    else:
                        admin_msg = f"""💬 Сообщение от пользователя:
От: {user_name} (ID: {chat_id})
Время: {datetime.now().strftime('%H:%M %d/%m/%Y')}
Сообщение: {text}"""
                        self.send_message(self.admin_id, admin_msg)
                        
                        response = """Ваше сообщение передано оператору. 
                        
Оператор ответит в рабочее время (11:00-22:00 МСК).
Используйте команды для быстрого доступа к услугам:

/menu - список услуг
/help - помощь  
/price - тарифы"""
                        
                        self.send_message(chat_id, response)
            
            elif 'callback_query' in update:
                callback = update['callback_query']
                chat_id = str(callback['message']['chat']['id'])
                data = callback['data']
                user_name = callback['from'].get('first_name', 'Пользователь')
                
                self.handle_callback(chat_id, data, user_name)
                
                requests.post(f'https://api.telegram.org/bot{self.token}/answerCallbackQuery',
                            json={'callback_query_id': callback['id']}, timeout=5)
                
        except Exception as e:
            print(f"Error processing update: {e}")
    
    def poll_updates(self):
        while self.running:
            try:
                response = requests.get(f'https://api.telegram.org/bot{self.token}/getUpdates',
                                     params={'offset': self.offset, 'timeout': 30}, timeout=35)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok') and data.get('result'):
                        updates = data['result']
                        
                        for update in updates:
                            self.process_update(update)
                            self.offset = update['update_id'] + 1
                        
                        if updates:
                            print(f"Processed {len(updates)} updates")
                
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(5)
    
    def start_polling(self):
        if not self.running:
            self.running = True
            polling_thread = threading.Thread(target=self.poll_updates, daemon=True)
            polling_thread.start()
            
            if self.admin_id:
                self.send_message(self.admin_id, "🟢 Финансовый бот запущен на Render.com!")
            
            print("Financial bot polling started on Render.com")
    
    def stop_polling(self):
        self.running = False

telegram_bot = FinancialBot()

@app.route('/')
def health():
    return jsonify({'status': 'online', 'bot_active': telegram_bot.running, 'timestamp': datetime.now().isoformat()})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if update:
            telegram_bot.process_update(update)
        return "OK"
    except Exception as e:
        print(f"Webhook error: {e}")
        return "Error", 500

if __name__ == '__main__':
    telegram_bot.start_polling()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
