# казик
Нужно начать с того что логика казино да и вприницпе казино не было написано моими силами, а взята с этого [репозитория](https://github.com/InspiredImpact/casino-bot-for-discord)  
Также хочется заметить что тут заметны повторения некоторых функций и недоработки с моей стороны
## технические особенности
- Проверка на дурака - подразумевает под собой проверку на то, что был введен пользователь, а не роль или бот
- Все сообщения от бота - embed-ы (кроме логов в файле)
## команды ##
1) `/slots` - собственно крутить слоты, принимает *кол-во валюты* и *кол-во игр*
2) `/stats` - выводит *кол-во валюты* и *кол-во валюты закинутой в благотворительный фонд*, которые имеются у человека, который ввел эту команду
3) `/check_stats` - принимает *упоминание пользователя*, выводит *кол-во валюты* и *кол-во валюты закинутых в благотворительный фонд* упомянутого пользователя (имеется проверка на дурака)
4) `/daily` - выдает 100 *валюты*, в планах было сделать зависимость от роли, но не суждено :(
5) `/transfer` - принимает *упоминание пользователя*, перевод *валюты* другому человеку (имеется проверка на дурака) и комментарий к переводу
6) `/leaders` - выводит топ-10 по *кол-ву валюты*
7) `/donation_leaders` - выводит топ-10 под *кол-во валюты закинутой в благотворительный фонд*
## `config.py`
Ваш конфиг бота выглядит подобным образом:
```
TOKEN = "" # токен бота
CURRENCY1 = "" # название валюты в родительном падеже множественного числа
CURRENCY2 = "" # название валюты в именительном падеже множественного числа
GUILD_IDS = [] # айди сервера
BOT_CHANNEL_ID = [] # айди канала/каналов в которых будут удалятся сообщения или в которых будет использоваться бот
LOGS_CHANNEL_ID =  # айди канала для логов
```

Разжевываю за каждый пункт: 
- `TOKEN` - Токен бота в *дс*, вбивается в кавычки
- `CURRENCY1` - название валюты, которое будет упоминаться в командах в родительном падеже (кого? чего?) множественного числа, вбивается в кавычки
- `CURRENCY2` - название валюты, которое будет упоминаться в командах в именительном падеже (кто? что?) множественного числа, вбивается в кавычки
- `GUILD_IDS` - айди сервера, на котором используется бот (команды не будут работать, если айди не ввести), вбивается в квадратные скобки
- `BOT_CHANNEL_ID` - айди канала/ов (чата/ов), в котором/ых будет использоваться бот (чтобы не засорять чат), вбивается в квадратные скобки
- `LOGS_CHANNEL_ID` - айди канала для логов, вбивается просто айди без всего
# библиотеки
## [Pycord](https://pycord.dev/) *это очень важно, слеш-команды не будут работать и код не запустится* ##



### p.s
да знаю, выложил код бота в то время, в которое он не будет работать адекватно, рекомендации дам такие: на линуксе (x64, на x32 не пробовал, и не буду) вот [это](https://github.com/Sergeydigl3/zapret-discord-youtube-linux), ну и впринципы методы по обходу обходимого в моих звездах найдете ([вот здесь](https://github.com/stars/tecxz5/lists/%D0%BE%D0%B1%D1%85%D0%BE%D0%B4%D0%B8%D0%BC-%D0%BE%D0%B1%D1%85%D0%BE%D0%B4%D0%B8%D0%BC%D0%BE%D0%B5))
