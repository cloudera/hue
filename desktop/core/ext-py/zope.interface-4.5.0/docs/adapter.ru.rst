================
Реестр адаптеров
================

.. contents::

Реестры адаптеров предоставляют возможность для регистрации объектов которые
зависят от одной, или нескольких спецификаций интерфейсов и предоставляют
(возможно не напрямую) какой-либо интерфейс. В дополнение, регистрации имеют
имена. (Можно думать об именах как о спецификаторах предоставляемого
интерфейса.)

Термин "спецификация интерфейса" ссылается и на интерфейсы и на определения
интерфейсов, такие как определения интерфейсов реализованных некоторым классом.

Одиночные адаптеры
==================

Давайте рассмотрим простой пример использующий единственную требуемую
спецификацию::

  >>> from zope.interface.adapter import AdapterRegistry
  >>> import zope.interface

  >>> class IR1(zope.interface.Interface):
  ...     pass
  >>> class IP1(zope.interface.Interface):
  ...     pass
  >>> class IP2(IP1):
  ...     pass

  >>> registry = AdapterRegistry()

Мы зарегистрируем объект который зависит от IR1 и "предоставляет" IP2::

  >>> registry.register([IR1], IP2, '', 12)

После регистрации мы можем запросить объект снова::

  >>> registry.lookup([IR1], IP2, '')
  12

Заметьте, что мы используем целое в этом примере. В реальных приложениях вы
можете использовать объекты которые на самом деле зависят или предоставляют
интерфейсы. Реестр не заботиться о том, что регистрируется и таким образом мы
можем использовать целые, или строки что бы упростить наши примеры. Здесь есть
одно исключение. Регистрация значения None удаляет регистрацию для любого
зарегистрированного прежде значения.

Если объект зависит от спецификации он может быть запрошен с помощью
спецификации которая расширяет спецификацию от которой он зависит::

  >>> class IR2(IR1):
  ...     pass
  >>> registry.lookup([IR2], IP2, '')
  12

Мы можем использовать класс реализующий спецификацию для запроса объекта::

  >>> class C2:
  ...     zope.interface.implements(IR2)

  >>> registry.lookup([zope.interface.implementedBy(C2)], IP2, '')
  12

и объект может быть запрошен для интерфейсов которые предоставляемый объектом
интерфейс расширяет::

  >>> registry.lookup([IR1], IP1, '')
  12
  >>> registry.lookup([IR2], IP1, '')
  12

Но если вы требуете спецификацию которая не расширяет спецификацию от которой
зависит объект, вы не получите ничего::

  >>> registry.lookup([zope.interface.Interface], IP1, '')

Между прочим, вы можете передать значение по умолчанию при запросе::

  >>> registry.lookup([zope.interface.Interface], IP1, '', 42)
  42

Если вы пробуете получить интерфейс который объект не предоставляет вы также
не получите ничего::

  >>> class IP3(IP2):
  ...     pass
  >>> registry.lookup([IR1], IP3, '')

Вы также не получите ничего если вы используете неверное имя::

  >>> registry.lookup([IR1], IP1, 'bob')
  >>> registry.register([IR1], IP2, 'bob', "Bob's 12")
  >>> registry.lookup([IR1], IP1, 'bob')
  "Bob's 12"

Вы можете не использовать имя при запросе::

  >>> registry.lookup([IR1], IP1)
  12

Если мы регистрируем объект который предоставляет IP1::

  >>> registry.register([IR1], IP1, '', 11)

тогда этот объект будет иметь преимущество перед O(12)::

  >>> registry.lookup([IR1], IP1, '')
  11

Также, если мы регистрируем объект для IR2 тогда он будет иметь преимущество
когда используется IR2::

  >>> registry.register([IR2], IP1, '', 21)
  >>> registry.lookup([IR2], IP1, '')
  21

Поиск того, что (если вообще что-то) зарегистрировано
-----------------------------------------------------

Мы можем спросить есть-ли адаптер зарегистрированный для набора интерфейсов.
Это отличается от обычного запроса так как здесь мы ищем точное совпадение::

  >>> print registry.registered([IR1], IP1)
  11

  >>> print registry.registered([IR1], IP2)
  12

  >>> print registry.registered([IR1], IP2, 'bob')
  Bob's 12
  

  >>> print registry.registered([IR2], IP1)
  21

  >>> print registry.registered([IR2], IP2)
  None

В последнем примере, None был возвращен потому, что для данного интерфейса
ничего не было зарегистрировано.

lookup1
-------

Запрос одиночного адаптера - это наиболее частая операция и для нее есть
специализированная версия запроса которая получает на вход единственный
требуемый интерфейс::

  >>> registry.lookup1(IR2, IP1, '')
  21
  >>> registry.lookup1(IR2, IP1)
  21

Адаптация на практике
---------------------

Реестр адаптеров предназначен для поддержки адаптации когда один объект
реализующий интерфейс адаптируется к другому объекту который поддерживает
другой интерфейс. Реестр адаптеров также поддерживает вычисление адаптеров. В
этом случае мы должны регистрировать фабрики для адаптеров::

   >>> class IR(zope.interface.Interface):
   ...     pass

   >>> class X:
   ...     zope.interface.implements(IR)
           
   >>> class Y:
   ...     zope.interface.implements(IP1)
   ...     def __init__(self, context):
   ...         self.context = context

  >>> registry.register([IR], IP1, '', Y)

В этом случае мы регистрируем класс как фабрику. Теперь мы можем вызвать
`queryAdapter` для получения адаптированного объекта::

  >>> x = X()
  >>> y = registry.queryAdapter(x, IP1)
  >>> y.__class__.__name__
  'Y'
  >>> y.context is x
  True

Мы также можем регистрировать и запрашивать по имени::

  >>> class Y2(Y):
  ...     pass

  >>> registry.register([IR], IP1, 'bob', Y2)
  >>> y = registry.queryAdapter(x, IP1, 'bob')
  >>> y.__class__.__name__
  'Y2'
  >>> y.context is x
  True

Когда фабрика для адаптера возвращает `None` - это рассматривается как если бы
адаптер не был найден. Это позволяет нам избежать адаптации (по желанию) и дает
возможность фабрике адаптера определить возможна ли адаптация основываясь на
состоянии объекта который адаптируется::

  >>> def factory(context):
  ...     if context.name == 'object':
  ...         return 'adapter'
  ...     return None

  >>> class Object(object):
  ...     zope.interface.implements(IR)
  ...     name = 'object'

  >>> registry.register([IR], IP1, 'conditional', factory) 
  >>> obj = Object()
  >>> registry.queryAdapter(obj, IP1, 'conditional')
  'adapter'
  >>> obj.name = 'no object'
  >>> registry.queryAdapter(obj, IP1, 'conditional') is None
  True
  >>> registry.queryAdapter(obj, IP1, 'conditional', 'default')
  'default'

Альтернативный метод для предоставления такой же функциональности как и
`queryAdapter()` - это `adapter_hook()`::

  >>> y = registry.adapter_hook(IP1, x)
  >>> y.__class__.__name__
  'Y'
  >>> y.context is x
  True
  >>> y = registry.adapter_hook(IP1, x, 'bob')
  >>> y.__class__.__name__
  'Y2'
  >>> y.context is x
  True

`adapter_hook()` просто меняет порядок аргументов для объекта и интерфейса. Это
используется для встраивания в механизм вызовов интерфейсов.

Адаптеры по умолчанию
---------------------

Иногда вы можете захотеть предоставить адаптер который не будет ничего
адаптировать. Для этого нужно передать None как требуемый интерфейс::

  >>> registry.register([None], IP1, '', 1)

после этого вы можете использовать этот адаптер для интерфейсов для которых у
вас нет конкретного адаптера::

  >>> class IQ(zope.interface.Interface):
  ...     pass
  >>> registry.lookup([IQ], IP1, '')
  1

Конечно, конкретные адаптеры все еще используются когда необходимо::

  >>> registry.lookup([IR2], IP1, '')
  21

Адаптеры классов
----------------

Вы можете регистрировать адаптеры для определений классов, что будет похоже на
регистрацию их для классов::

  >>> registry.register([zope.interface.implementedBy(C2)], IP1, '', 'C21')
  >>> registry.lookup([zope.interface.implementedBy(C2)], IP1, '')
  'C21'

Адаптеры для словарей
---------------------

В какой-то момент было невозможно регистрировать адаптеры основанные на
словарях из-за ошибки. Давайте удостоверимся что это теперь работает::

  >>> adapter = {}
  >>> registry.register((), IQ, '', adapter)
  >>> registry.lookup((), IQ, '') is adapter
  True

Удаление регистрации
--------------------

Вы можете удалить регистрацию регистрируя None вместо объекта::

  >>> registry.register([zope.interface.implementedBy(C2)], IP1, '', None)
  >>> registry.lookup([zope.interface.implementedBy(C2)], IP1, '')
  21

Конечно это значит, что None не может быть зарегистрирован. Это исключение к
утверждению выше о том, что реестр не заботиться о том, что регистрируется.

Мульти-адаптеры
===============

Вы можете адаптировать несколько спецификаций::

  >>> registry.register([IR1, IQ], IP2, '', '1q2')
  >>> registry.lookup([IR1, IQ], IP2, '')
  '1q2'
  >>> registry.lookup([IR2, IQ], IP1, '')
  '1q2'

  >>> class IS(zope.interface.Interface):
  ...     pass
  >>> registry.lookup([IR2, IS], IP1, '')

  >>> class IQ2(IQ):
  ...     pass

  >>> registry.lookup([IR2, IQ2], IP1, '')
  '1q2'

  >>> registry.register([IR1, IQ2], IP2, '', '1q22')
  >>> registry.lookup([IR2, IQ2], IP1, '')
  '1q22'

Мульти-адаптация
----------------

Вы можете адаптировать несколько объектов::

  >>> class Q:
  ...     zope.interface.implements(IQ)

Как и с одиночными адаптерами, мы регистрируем фабрику которая возвращает
класс::

  >>> class IM(zope.interface.Interface):
  ...     pass
  >>> class M:
  ...     zope.interface.implements(IM)
  ...     def __init__(self, x, q):
  ...         self.x, self.q = x, q
  >>> registry.register([IR, IQ], IM, '', M)

И затем мы можем вызвать `queryMultiAdapter` для вычисления адаптера::

  >>> q = Q()
  >>> m = registry.queryMultiAdapter((x, q), IM)
  >>> m.__class__.__name__
  'M'
  >>> m.x is x and m.q is q
  True

и, конечно, мы можем использовать имена::

  >>> class M2(M):
  ...     pass
  >>> registry.register([IR, IQ], IM, 'bob', M2)
  >>> m = registry.queryMultiAdapter((x, q), IM, 'bob')
  >>> m.__class__.__name__
  'M2'
  >>> m.x is x and m.q is q
  True

Адаптеры по умолчанию
---------------------

Как и для одиночных адаптеров вы можете определить адаптер по умолчанию передав
None вместо *первой* спецификации::

  >>> registry.register([None, IQ], IP2, '', 'q2')
  >>> registry.lookup([IS, IQ], IP2, '')
  'q2'

Нулевые адаптеры
================

Вы можете также адаптировать без спецификации::

  >>> registry.register([], IP2, '', 2)
  >>> registry.lookup([], IP2, '')
  2
  >>> registry.lookup([], IP1, '')
  2

Перечисление именованных адаптеров
----------------------------------

Адаптеры имеют имена. Иногда это полезно для получения всех именованных
адаптеров для заданного интерфейса::

  >>> adapters = list(registry.lookupAll([IR1], IP1))
  >>> adapters.sort()
  >>> assert adapters == [(u'', 11), (u'bob', "Bob's 12")]

Это работает также и для мульти-адаптеров::

  >>> registry.register([IR1, IQ2], IP2, 'bob', '1q2 for bob')
  >>> adapters = list(registry.lookupAll([IR2, IQ2], IP1))
  >>> adapters.sort()
  >>> assert adapters == [(u'', '1q22'), (u'bob', '1q2 for bob')]

И даже для нулевых адаптеров::

  >>> registry.register([], IP2, 'bob', 3)
  >>> adapters = list(registry.lookupAll([], IP1))
  >>> adapters.sort()
  >>> assert adapters == [(u'', 2), (u'bob', 3)]

Подписки
========

Обычно мы хотим запросить объект который наиболее близко соответствует
спецификации. Иногда мы хотим получить все объекты которые соответствуют
какой-либо спецификации. Мы используем подписки для этого. Мы подписываем
объекты для спецификаций и затем позже находим все подписанные объекты::

  >>> registry.subscribe([IR1], IP2, 'sub12 1')
  >>> registry.subscriptions([IR1], IP2)
  ['sub12 1']

Заметьте, что в отличие от обычных адаптеров подписки не имеют имен.

Вы можете иметь несколько подписчиков для одной спецификации::

  >>> registry.subscribe([IR1], IP2, 'sub12 2')
  >>> registry.subscriptions([IR1], IP2)
  ['sub12 1', 'sub12 2']

Если подписчики зарегистрированы для одних и тех же требуемых интерфейсов, они
возвращаются в порядке определения.

Вы можете зарегистрировать подписчики для всех спецификаций используя None::

  >>> registry.subscribe([None], IP1, 'sub_1')
  >>> registry.subscriptions([IR2], IP1)
  ['sub_1', 'sub12 1', 'sub12 2']

Заметьте, что новый подписчик возвращается первым. Подписчики определенные
для менее общих требуемых интерфейсов возвращаются перед подписчиками
для более общих интерфейсов.

Подписки могут смешиваться между несколькими совместимыми спецификациями::

  >>> registry.subscriptions([IR2], IP1)
  ['sub_1', 'sub12 1', 'sub12 2']
  >>> registry.subscribe([IR1], IP1, 'sub11')
  >>> registry.subscriptions([IR2], IP1)
  ['sub_1', 'sub12 1', 'sub12 2', 'sub11']
  >>> registry.subscribe([IR2], IP2, 'sub22')
  >>> registry.subscriptions([IR2], IP1)
  ['sub_1', 'sub12 1', 'sub12 2', 'sub11', 'sub22']
  >>> registry.subscriptions([IR2], IP2)
  ['sub12 1', 'sub12 2', 'sub22']

Подписки могут существовать для нескольких спецификаций::

  >>> registry.subscribe([IR1, IQ], IP2, 'sub1q2')
  >>> registry.subscriptions([IR1, IQ], IP2)
  ['sub1q2']

Как и с одиночными подписчиками и адаптерами без подписок, вы можете определить
None для первого требуемого интерфейса, что бы задать значение по умолчанию::

  >>> registry.subscribe([None, IQ], IP2, 'sub_q2')
  >>> registry.subscriptions([IS, IQ], IP2)
  ['sub_q2']
  >>> registry.subscriptions([IR1, IQ], IP2)
  ['sub_q2', 'sub1q2']

Вы можете создать подписки которые независимы от любых спецификаций::

  >>> list(registry.subscriptions([], IP1))
  []

  >>> registry.subscribe([], IP2, 'sub2')
  >>> registry.subscriptions([], IP1)
  ['sub2']
  >>> registry.subscribe([], IP1, 'sub1')
  >>> registry.subscriptions([], IP1)
  ['sub2', 'sub1']
  >>> registry.subscriptions([], IP2)
  ['sub2']

Удаление регистрации подписчиков
--------------------------------

Мы можем удалять регистрацию подписчиков. При удалении регистрации подписчика
мы можем удалить регистрацию заданного адаптера::

  >>> registry.unsubscribe([IR1], IP1, 'sub11')
  >>> registry.subscriptions([IR1], IP1)
  ['sub_1', 'sub12 1', 'sub12 2']

Если мы не задаем никакого значения тогда подписки будут удалены для всех
подписчиков совпадающих с заданным интерфейсом::

  >>> registry.unsubscribe([IR1], IP2)
  >>> registry.subscriptions([IR1], IP1)
  ['sub_1']

Адаптеры подписки
-----------------

Обычно мы регистрируем фабрики для адаптеров которые затем позволяют нам
вычислять адаптеры, но с подписками мы получаем несколько адаптеров. Это пример
подписчика для нескольких объектов::

  >>> registry.subscribe([IR, IQ], IM, M)
  >>> registry.subscribe([IR, IQ], IM, M2)

  >>> subscribers = registry.subscribers((x, q), IM)
  >>> len(subscribers)
  2
  >>> class_names = [s.__class__.__name__ for s in subscribers]
  >>> class_names.sort()
  >>> class_names
  ['M', 'M2']
  >>> [(s.x is x and s.q is q) for s in subscribers]
  [True, True]

подписчики фабрик адаптеров не могут возвращать None::

  >>> def M3(x, y):
  ...     return None

  >>> registry.subscribe([IR, IQ], IM, M3)
  >>> subscribers = registry.subscribers((x, q), IM)
  >>> len(subscribers)
  2

Обработчики
-----------

Обработчик - это подписанная фабрика которая не возвращает нормального
значения. Она возвращает None. Обработчик отличается от адаптеров тем, что он
делает всю работу когда вызывается фабрика.

Для регистрации обработчика надо просто передать None как предоставляемый
интерфейс::

  >>> def handler(event):
  ...     print 'handler', event

  >>> registry.subscribe([IR1], None, handler)
  >>> registry.subscriptions([IR1], None) == [handler]
  True
