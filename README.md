# КАЗИК + ЭКОНОМИКА
Нужно начать с того что логика казино да и вприницпе казино не было написано моими силами, а взято с этого [репозитория](https://github.com/InspiredImpact/casino-bot-for-discord)  
Также хочется заметить что тут заметны повторения некоторых функций и недоработки с моей стороны
## КОМАНДЫ ##
- **/slots** - Само казино, имеет две опции:  
1. Сумма ставки  
2. Кол-во игр *необязательно, ограничено тремя играми*  
- **/balance** - Вывод баланса  
- **/leaders** - Топ-10 пользователей с наибольшим кол-вом монет  
- **/daily** - Ежедневный бонус в размере 100 монет *тут влияет время вашего сервера*  
- **/transfer** - Перевод от одного пользователя к другому, имеет две опции:  
1. Пользователь *упоминание через @*  
2. Сумма перевода  
- **/donate** - Вывод монет в "Благотворительный фонд", имеет одну опцию:
1. Сумма средств, которые вы хотите отдать в благотворительный фонд  
- **/donation_leaders** - Топ-10 пользователей с наибольшим кол-вом монет, которые отдали в "Благотворителный фонд"
# КАКИЕ БИБЛИОТЕКИ?
## [Pycord](https://pycord.dev/) *это очень важно, слеш-команды не будут работать и код не запустится* ##
Дальше идут:  
**sqlite3** для работы с базой данных  
**random** и **math** для вычеслений слотов
# КАКИЕ РЕКОМЕНДАЦИИ?
Код сделан для чисто локального бота со своими друзьями на сервере, не знаю правда кому нужно столько функционала и не каждый в sqlite разберется  
Если вы сделали мультисерверного бота то не забудьте упоминуть этот репозиторий, будет очень приятно  
  
  
  
-# P.S.
**КОД НЕ АКТУЛЕН С ЕГО ПУБЛИКАЦИИ** 
