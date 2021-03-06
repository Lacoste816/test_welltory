### Вопросы:

1. С какими проблемами можно столкнуться при таком способе хранения состояния обработки входных данных?
2. Что предпринять, если происходит “гонка” обновления данных операции в Operation и часть данных может перезаписываться
   старыми?
3. Как решить проблему с большим количеством UPDATE операций в PostgreSQL? И на каком уровне стоит ее решать?
4. Как можно спроектировать сервис для отслеживания состояния обработки входных JSON по всему pipeline, чтобы избежать
   подобных проблем? Какие минусы у вашего варианта реализации такого сервиса?

### Ответы:

1. Собственно как описано в других вопросах ниже можно получить race condition когда статусы поменяются в другом
   порядке. Также если нагрузка большая - большое количество апдейтов будет работать не быстро (апдейты могут ждать
   освобождения row level блокировок, а в крайнем случае при неподходящих настройках/архитектуре бд - может и дедлок
   произойти(
   маловероятно)). Если сервисы отправляют статусы синхронно с выполнение остального скода в них -> скорость ответы от
   сервиса Operation будет напрямую влиять на время прохождения операции по pipelin-у. В случае некорректной обработки
   ошибок в сервисах -> в случае неответа сервиса Operation - может прерваться пайплайн. Если ошибки обрабатываются
   корректно то просто потеряется обновление статуса -> что приведет к тому что пайплайн будучи выполненым фактически (
   например) будет считаться невыполненным и логика приложения не отдаст данные дальше. А в случае роста нагрузки рано
   или поздно оно упрется в предел производительности. Просто горизонтально масштабировать сервис Operation также
   вероятно будет нельзя так как упрется в производительности бд на апдейты.

2. Один из вариантов - заложить логику с проверкой предыдущего состояния, то есть если мы знаем что пайплайн new ->
   status1 -> status2 -> done то перех в статус1 возможен только из new, если он уже в status2 - игнорировать команду.
   Второй - пересмотреть архитектуру чтоб исключить саму возможность гонки. См. пункт 3-4

3. (ответ на 3-4 вопросы) Я бы предложил переделать архитектуру сервиса Operation на получение данных из очереди (т.е.
   сервисы кладут обновление статуса в очередь), это исключит возможность "гонки", исключит вероятность потери
   обновлений статусов + позволит собирать некий буфер обновления перед записью в базу (делать один апдейт раз в
   секунду/несколько секунд например с всеми накопленными данными, что исключит конкурирующие вопросы в бд) + Уменьшит
   само количество апдейтов так как если за время накопления придет 3 изменения статуса по одной операции -> можно
   писать в бд сразу последний пришедший (актуальный статус). При получении запроса на получение статуса операции ->
   проверяем сначала буфер (dict - хешмап структура, очень быстрая операция), если там есть статус -> отдаем его, он
   актуальный. Если нет -> select из бд. Можно формировать очередь и самим сервисом по получению запроса от апи (если
   использование http апи принципиально) - но мне видится очередь более надежным средством доставки и не решает проблему
   гонки само по себе.
