

  **Механика программы лояльности**  
**12Storeez**

1. Потребитель заходит в личный кабинет и смотрит количество баллов. Вся собранная информация о потребителе вместе с данными карт передаются в Mindbox с помощью сервиса получения предварительной информации о заказе. В ответ вернется информация о доступном балансе на картах, количестве баллов, которое можно потратить в следующем заказе.

2. При оформлении заказа, потребитель должен указать, хочет ли он потратить баллы, или накопить. Если выбирает "Начислить баллы", то после перехода статуса заказа в "Выполнен", потребителю начисляется Х от потраченной суммы денег.  Во втором случае, когда потребитель выбирает "Использовать накопленные баллы", до Х% от стоимости покупки оплачивается баллами, которые замораживаются на счете до того момента, как статус заказа станет "Выполнен". При создании заказа используется сервис оформления заказа.

3. После того как бэк подтвердила изменение статуса заказа в “Выполнен”, сайт должен подтвердить успешность завершения покупки с помощью сервиса изменения заказа. После этого, в зависимости от того, выбрал потребитель потратить баллы или накопить, изменяется количество баллов. Если потребитель решил накопить, то ему начисляются Х от потраченной суммы в баллах. Если потратить, то замороженные баллы окончательно сгорают.   
4. Для того, чтобы ПЛ работала в оффлайн-точках, необходимо наладить импорт информации о магазинах

[**1\. Сервис получения предварительной информации о заказе**](#1.-сервис-получения-предварительной-информации-о-заказе)	**[2](#1.-сервис-получения-предварительной-информации-о-заказе)**

[**2\. Сервис оформления заказа**](#2.-сервис-оформления-заказа)	**[3](#2.-сервис-оформления-заказа)**

[**3\. Сервис подтверждения заказа**](#3.-сервис-подтверждения-заказа)	**[5](#3.-сервис-подтверждения-заказа)**

[**4\. Сервис отмены заказа**](#4.-сервис-отмены-заказа)	**[8](#4.-сервис-отмены-заказа)**

[**5\. Сервис возврата заказа**](#5.-сервис-возврата-заказа)	**[10](#5.-сервис-возврата-заказа)**

[**6\. Чтение баланса потребителя**](#6.-чтение-баланса-потребителя)	**[13](#6.-чтение-баланса-потребителя)**

[**7\. Импорт оффлайн-точек**](#7.-импорт-оффлайн-точек)	**[14](#7.-импорт-оффлайн-точек)**

[**8\. История начислений баланса**](#8.-история-начислений-баланса-полное-описание-всех-полей:-https://12storeez.directcrm.ru/operations/balancehistory/help)  
[**Полное описание всех полей: https\://12storeez.directcrm.ru/operations/BalanceHistory/help**](#8.-история-начислений-баланса-полное-описание-всех-полей:-https://12storeez.directcrm.ru/operations/balancehistory/help)	**[15](#8.-история-начислений-баланса-полное-описание-всех-полей:-https://12storeez.directcrm.ru/operations/balancehistory/help)**

[**9\. Отправка пароля**](#9.-отправка-пароля)	**[15](#9.-отправка-пароля)**

[**10\. Получение данных о потребителе**](#10.-получение-данных-о-потребителе)	**[16](#10.-получение-данных-о-потребителе)**

[**11\. Аутентификация потребителя на кассе**](#11.-аутентификация-потребителя-на-кассе)	**[17](#11.-аутентификация-потребителя-на-кассе)**

[**12\. Импорт в Mindbox нового или редактирование старого клиента**](#12.-импорт-в-mindbox-нового-или-редактирование-старого-клиента)	**[19](#12.-импорт-в-mindbox-нового-или-редактирование-старого-клиента)**

[**13\. Сервис пересчета стоимости заказа**](#13.-сервис-пересчета-стоимости-заказа)	**[20](#13.-сервис-пересчета-стоимости-заказа)**

[**14\. Получение информации о заказе**](#14.-получение-информации-о-заказе)	**[21](#14.-получение-информации-о-заказе)**

[**15\. Редактирование заказа без процессинга**](#15.-редактирование-заказа-без-процессинга)	**[22](#15.-редактирование-заказа-без-процессинга)**

[**Статья про ПЛ**](https://developers.mindbox.ru/page/loyaloffline)

Показать юзеру балльный счет  
[https\://developers.mindbox.ru/docs/%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B1%D0%B0%D0%BB%D0%B0%D0%BD%D1%81%D0%B0-%D0%BF%D0%BE%D1%82%D1%80%D0%B5%D0%B1%D0%B8%D1%82%D0%B5%D0%BB%D1%8F](https://developers.mindbox.ru/docs/%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B1%D0%B0%D0%BB%D0%B0%D0%BD%D1%81%D0%B0-%D0%BF%D0%BE%D1%82%D1%80%D0%B5%D0%B1%D0%B8%D1%82%D0%B5%D0%BB%D1%8F)

Предварительный расчет (показать юзеру что можно применить на заказ в корзине или на кассе)  
[https\://developers.mindbox.ru/docs/preorderxml](https://developers.mindbox.ru/docs/preorderxml)

Изменение заказа (у вас уже есть)  
[https\://developers.mindbox.ru/docs/%D0%B8%D0%B7%D0%BC%D0%B5%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B7%D0%B0%D0%BA%D0%B0%D0%B7%D0%B0](https://developers.mindbox.ru/docs/%D0%B8%D0%B7%D0%BC%D0%B5%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B7%D0%B0%D0%BA%D0%B0%D0%B7%D0%B0)

# Устаревшая интеграция

## 1\. Сервис получения предварительной информации о заказе {#1.-сервис-получения-предварительной-информации-о-заказе}

Полное описание всех полей и пример:  
[https\://12storeez.directcrm.ru/operations/PreOrderInfo/help](https://12storeez.directcrm.ru/operations/PreOrderInfo/help)

| POST https\://12storeez-services.directcrm.ru/v2.1/orders/get-pre-order-info?operation=PreOrderInfo Accept: application/xml Content-Type: application/xml Authorization: DirectCrm key="\*\*\*" \<order\>   \<customer\> 	\<email\>test@mindbox.ru\</email\> 	\<mobilePhone\>79001234567\</mobilePhone\>    	\<fullName\>\</fullName\> 	\<ids\>   	\<storeezWebsiteId\>1097945505\</storeezWebsiteId\> 	\</ids\> 	\<isAuthorized\>false\</isAuthorized\>   \</customer\>   \<staff\> 	\<externalId\>RFzRqDuM\</externalId\>   \</staff\>   \<actualAmountForCustomer\>237028.98\</actualAmountForCustomer\>   \<deliveryCost\>10054130.08\</deliveryCost\>   \<paidAmount\>17802642.29\</paidAmount\>   \<lines\> 	\<line\>   	\<sku\>     	\<productId\>101316\</productId\>     	\<skuId\>104605\</skuId\>     	\<basePricePerItem\>15335408.37\</basePricePerItem\>   	\</sku\>   	\<quantity\>1\</quantity\>   	\<status\>InCart\</status\> 	\</line\> 	\</lines\>   \<customFields\> 	\<deliveryaddress\>\</deliveryaddress\> 	\<deliveryCostType\>15874\</deliveryCostType\> 	\<deliverymethod\>\</deliverymethod\> 	\<deliveryType\>Пункт выдачи BoxBerry\</deliveryType\> 	\<transportCompany\>14\</transportCompany\>   \</customFields\>   \<area\>12storeez.com\</area\>   \<calculationDateTimeUtc\>2016-04-13 17:36:47.282\</calculationDateTimeUtc\>   \<pointOfContact\>12storeez.com\</pointOfContact\> \</order\>  |
| :---- |

## 2\. Сервис оформления заказа {#2.-сервис-оформления-заказа}

Полное описание всех полей и пример:  
[https\://12storeez.directcrm.ru/operations/CheckoutOrder/help](https://12storeez.directcrm.ru/operations/CheckoutOrder/help)

Пример вызова:

| POST https\://12storeez-services.directcrm.ru/v2.1/orders/create?operation=CheckoutOrder Accept: application/xml Content-Type: application/xml Authorization: DirectCrm key="\*\*\*" \<order\>    \<pointOfContact\>12storeez.com\</pointOfContact\>   \<customer\>     \<email\>test@mindbox.ru\</email\>     \<mobilePhone\>79001234567\</mobilePhone\> \<fullName\>\</fullName\> \<ids\>       \<storeezWebsiteId\>269571253\</storeezWebsiteId\>     \</ids\>          \</customer\>     \<actualAmountForCustomer\>3528831.89\</actualAmountForCustomer\>   \<deliveryCost\>19639262.12\</deliveryCost\>   \<paidAmount\>15053859.33\</paidAmount\>   \<lines\>     \<line\>       \<customFields\>         \<discount\>10848709.61\</discount\>       \</customFields\>       \<discounts\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>196q51ou\</id\>           \<amount\>19517260\</amount\>         \</discount\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>JaVFk\</id\>           \<amount\>11824674.62\</amount\>         \</discount\>       \</discounts\>       \<sku\>         \<productId\>101996\</productId\>         \<skuId\>104605\</skuId\>         \<basePricePerItem\>3443449.75\</basePricePerItem\>       \</sku\>       \<quantity\>4125638.13\</quantity\>       \<giftCard\>         \<id\>1Kdy\</id\>         \<getFromPool\>true\</getFromPool\>       \</giftCard\>       \<status\>InCart\</status\>     \</line\>     \</lines\>    \<payments\>     \<payment\>       \<type\>bank-card\</type\>       \<amount\>9355509.05\</amount\>     \</payment\>     \<payment\>       \<type\>cash\</type\>       \<amount\>5690913.92\</amount\>     \</payment\>     \<payment\>       \<type\>card\</type\>       \<amount\>4204428.97\</amount\>     \</payment\>   \</payments\>   \<discounts\>     \<discount\>       \<type\>externalPromoAction\</type\>       \<id\>gXqBMk0O3\</id\>       \<amount\>4723978.43\</amount\>     \</discount\>     \<discount\>       \<type\>balance\</type\>       \<card\>         \<number\>OjZDoiXo2\</number\>       \</card\>       \<amount\>11886131.85\</amount\>     \</discount\>   \</discounts\>   \<customFields\>     \<deliveryaddress\>\</deliveryaddress\>     \<deliveryCostType\>fire\</deliveryCostType\>     \<deliverymethod\>\</deliverymethod\>     \<deliveryType\>3149\</deliveryType\>     \<transportCompany\>15\</transportCompany\>   \</customFields\>      \<ids\>     \<storeez.com\>968503022\</storeez.com\>   \</ids\>   \<createdDateTimeUtc\>2016-07-21 17:22:47.303\</createdDateTimeUtc\>   \<preOrderDiscountedTotalPrice\>7930444.92\</preOrderDiscountedTotalPrice\> \</order\>  |
| :---- |

## 3\. Сервис подтверждения заказа {#3.-сервис-подтверждения-заказа}

Полное описанией всех полей и пример: [https\://12storeez.directcrm.ru/operations/ConfirmOrder/help](https://12storeez.directcrm.ru/operations/ConfirmOrder/help) 

| POST https\://12storeez-services.directcrm.ru/v2.1/orders/update-order?operation=ConfirmOrder Accept: application/xml Content-Type: application/xml Authorization: DirectCrm key="\*\*\*" \<order\>   \<pointOfContact\>FCXzz51\</pointOfContact\>   \<customer\>     \<email\>test@mindbox.ru\</email\>     \<fullName\>\</fullName\>         \<discountCard\>       \<ids\>         \<number\>12345\</number\>       \</ids\>     \</discountCard\>     \<ids\>       \<storeezWebsiteId\>439887032\</storeezWebsiteId\>     \</ids\>     \<customFields\>       \<balance\>581167519\</balance\>       \<nps\>\</nps\>       \<npscount\>0\</npscount\>       \<otsenka\>781351903\</otsenka\>     \</customFields\>     \<isAuthorized\>false\</isAuthorized\>   \</customer\>   \<staff\>     \<externalId\>IHNQUO21yO\</externalId\>   \</staff\>   \<actualAmountForCustomer\>10868025.49\</actualAmountForCustomer\>   \<deliveryCost\>3995212.31\</deliveryCost\>   \<totalPrice\>13204008.11\</totalPrice\>   \<lines\>     \<line\>       \<customFields\>         \<discount\>991972.43\</discount\>       \</customFields\>       \<discounts\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>r40hmVpTT\</id\>           \<amount\>9547688.38\</amount\>         \</discount\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>TZsBMsh\</id\>           \<amount\>9749870.48\</amount\>         \</discount\>       \</discounts\>       \<sku\>         \<productId\>101996\</productId\>         \<skuId\>104605\</skuId\>         \<basePricePerItem\>7588844.82\</basePricePerItem\>       \</sku\>       \<quantity\>18583219.9\</quantity\>       \<giftCard\>         \<id\>Ck7EC8zi79\</id\>       \</giftCard\>       \<status\>InCart\</status\>     \</line\>     \<line\>       \<customFields\>         \<discount\>1339417.44\</discount\>       \</customFields\>       \<discounts\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>aRazMxc463u\</id\>           \<amount\>12202879.07\</amount\>         \</discount\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>GNTNnJq\</id\>           \<amount\>16354816.73\</amount\>         \</discount\>       \</discounts\>       \<sku\>         \<productId\>101996\</productId\>         \<skuId\>104605\</skuId\>         \<basePricePerItem\>20155910.56\</basePricePerItem\>       \</sku\>       \<quantity\>18801846.09\</quantity\>       \<giftCard\>         \<id\>khSqev\</id\>       \</giftCard\>       \<status\>InCart\</status\>     \</line\>   \</lines\>   \<payments\>     \<payment\>       \<type\>giftCard\</type\>       \<id\>ePeRtv2\</id\>       \<amount\>7221341.77\</amount\>     \</payment\>     \<payment\>       \<type\>nal-nalozh\</type\>       \<amount\>13974429.08\</amount\>     \</payment\>       \<payment\>       \<type\>sb-online\</type\>       \<amount\>13735349.9\</amount\>     \</payment\>     \<payment\>       \<type\>bank-transfer\</type\>       \<amount\>20294421.04\</amount\>     \</payment\>   \</payments\>   \<discounts\>     \<discount\>       \<type\>promoCode\</type\>       \<id\>gVUzWJeZKP\</id\>       \<amount\>14278199.46\</amount\>     \</discount\>     \<discount\>       \<type\>externalPromoAction\</type\>       \<id\>vaLZPU6y\</id\>       \<amount\>10127422.45\</amount\>     \</discount\>     \<discount\>       \<type\>balance\</type\>       \<card\>         \<number\>USfxyHsZ\</number\>       \</card\>       \<amount\>4238724.22\</amount\>     \</discount\>   \</discounts\>   \<ids\>     \<storeez.com\>311722112\</storeez.com\>   \</ids\>   \<updatedDateTimeUtc\>2015-03-20 17:56:47.198\</updatedDateTimeUtc\> \</order\>  |
| :---- |

## 4\. Сервис отмены заказа {#4.-сервис-отмены-заказа}

Полное описанией всех полей и пример: [https\://12storeez.directcrm.ru/operations/CancelOrder/help](https://12storeez.directcrm.ru/operations/CancelOrder/help) 

| POST https\://12storeez-services.directcrm.ru/v2.1/orders/update-order?operation=CancelOrder Accept: application/xml Content-Type: application/xml Authorization: DirectCrm key="\*\*\*" \<order\>   \<pointOfContact\>FCXzz51\</pointOfContact\>   \<customer\>     \<email\>test@mindbox.ru\</email\>     \<fullName\>\</fullName\>         \<discountCard\>       \<ids\>         \<number\>12345\</number\>       \</ids\>     \</discountCard\>     \<ids\>       \<storeezWebsiteId\>439887032\</storeezWebsiteId\>     \</ids\>     \<customFields\>       \<balance\>581167519\</balance\>       \<nps\>\</nps\>       \<npscount\>0\</npscount\>       \<otsenka\>781351903\</otsenka\>     \</customFields\>     \<isAuthorized\>false\</isAuthorized\>   \</customer\>   \<staff\>     \<externalId\>IHNQUO21yO\</externalId\>   \</staff\>   \<actualAmountForCustomer\>10868025.49\</actualAmountForCustomer\>   \<deliveryCost\>3995212.31\</deliveryCost\>   \<totalPrice\>13204008.11\</totalPrice\>   \<lines\>     \<line\>       \<customFields\>         \<discount\>991972.43\</discount\>       \</customFields\>       \<discounts\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>r40hmVpTT\</id\>           \<amount\>9547688.38\</amount\>         \</discount\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>TZsBMsh\</id\>           \<amount\>9749870.48\</amount\>         \</discount\>       \</discounts\>       \<sku\>         \<productId\>101996\</productId\>         \<skuId\>104605\</skuId\>         \<basePricePerItem\>7588844.82\</basePricePerItem\>       \</sku\>       \<quantity\>18583219.9\</quantity\>       \<giftCard\>         \<id\>Ck7EC8zi79\</id\>       \</giftCard\>       \<status\>InCart\</status\>     \</line\>     \<line\>       \<customFields\>         \<discount\>1339417.44\</discount\>       \</customFields\>       \<discounts\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>aRazMxc463u\</id\>           \<amount\>12202879.07\</amount\>         \</discount\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>GNTNnJq\</id\>           \<amount\>16354816.73\</amount\>         \</discount\>       \</discounts\>       \<sku\>         \<productId\>101996\</productId\>         \<skuId\>104605\</skuId\>         \<basePricePerItem\>20155910.56\</basePricePerItem\>       \</sku\>       \<quantity\>18801846.09\</quantity\>       \<giftCard\>         \<id\>khSqev\</id\>       \</giftCard\>       \<status\>InCart\</status\>     \</line\>   \</lines\>   \<payments\>     \<payment\>       \<type\>giftCard\</type\>       \<id\>ePeRtv2\</id\>       \<amount\>7221341.77\</amount\>     \</payment\>     \<payment\>       \<type\>nal-nalozh\</type\>       \<amount\>13974429.08\</amount\>     \</payment\>       \<payment\>       \<type\>sb-online\</type\>       \<amount\>13735349.9\</amount\>     \</payment\>     \<payment\>       \<type\>bank-transfer\</type\>       \<amount\>20294421.04\</amount\>     \</payment\>   \</payments\>   \<discounts\>     \<discount\>       \<type\>promoCode\</type\>       \<id\>gVUzWJeZKP\</id\>       \<amount\>14278199.46\</amount\>     \</discount\>     \<discount\>       \<type\>externalPromoAction\</type\>       \<id\>vaLZPU6y\</id\>       \<amount\>10127422.45\</amount\>     \</discount\>     \<discount\>       \<type\>balance\</type\>       \<card\>         \<number\>USfxyHsZ\</number\>       \</card\>       \<amount\>4238724.22\</amount\>     \</discount\>   \</discounts\>   \<ids\>     \<storeez.com\>311722112\</storeez.com\>   \</ids\>   \<updatedDateTimeUtc\>2015-03-20 17:56:47.198\</updatedDateTimeUtc\> \</order\>  |
| :---- |

## 5\. Сервис возврата заказа {#5.-сервис-возврата-заказа}

[https\://12storeez.directcrm.ru/operations/ReturnOrder/help](https://12storeez.directcrm.ru/operations/ReturnOrder/help)

| POST https\://12storeez-services.directcrm.ru/v2.1/orders/update-order?operation=ReturnOrder Accept: application/xml Content-Type: application/xml Authorization: DirectCrm key="\*\*\*" \<order\>   \<pointOfContact\>FCXzz51\</pointOfContact\>   \<customer\>     \<email\>test@mindbox.ru\</email\>     \<fullName\>\</fullName\>         \<discountCard\>       \<ids\>         \<number\>12345\</number\>       \</ids\>     \</discountCard\>     \<ids\>       \<storeezWebsiteId\>439887032\</storeezWebsiteId\>     \</ids\>     \<customFields\>       \<balance\>581167519\</balance\>       \<nps\>\</nps\>       \<npscount\>0\</npscount\>       \<otsenka\>781351903\</otsenka\>     \</customFields\>     \<isAuthorized\>false\</isAuthorized\>   \</customer\>   \<staff\>     \<externalId\>IHNQUO21yO\</externalId\>   \</staff\>   \<actualAmountForCustomer\>10868025.49\</actualAmountForCustomer\>   \<deliveryCost\>3995212.31\</deliveryCost\>   \<totalPrice\>13204008.11\</totalPrice\>   \<lines\>     \<line\>       \<customFields\>         \<discount\>991972.43\</discount\>       \</customFields\>       \<discounts\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>r40hmVpTT\</id\>           \<amount\>9547688.38\</amount\>         \</discount\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>TZsBMsh\</id\>           \<amount\>9749870.48\</amount\>         \</discount\>       \</discounts\>       \<sku\>         \<productId\>101996\</productId\>         \<skuId\>104605\</skuId\>         \<basePricePerItem\>7588844.82\</basePricePerItem\>       \</sku\>       \<quantity\>18583219.9\</quantity\>       \<giftCard\>         \<id\>Ck7EC8zi79\</id\>       \</giftCard\>       \<status\>InCart\</status\>     \</line\>     \<line\>       \<customFields\>         \<discount\>1339417.44\</discount\>       \</customFields\>       \<discounts\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>aRazMxc463u\</id\>           \<amount\>12202879.07\</amount\>         \</discount\>         \<discount\>           \<type\>externalPromoAction\</type\>           \<id\>GNTNnJq\</id\>           \<amount\>16354816.73\</amount\>         \</discount\>       \</discounts\>       \<sku\>         \<productId\>101996\</productId\>         \<skuId\>104605\</skuId\>         \<basePricePerItem\>20155910.56\</basePricePerItem\>       \</sku\>       \<quantity\>18801846.09\</quantity\>       \<giftCard\>         \<id\>khSqev\</id\>       \</giftCard\>       \<status\>InCart\</status\>     \</line\>   \</lines\>   \<payments\>     \<payment\>       \<type\>giftCard\</type\>       \<id\>ePeRtv2\</id\>       \<amount\>7221341.77\</amount\>     \</payment\>     \<payment\>       \<type\>nal-nalozh\</type\>       \<amount\>13974429.08\</amount\>     \</payment\>       \<payment\>       \<type\>sb-online\</type\>       \<amount\>13735349.9\</amount\>     \</payment\>     \<payment\>       \<type\>bank-transfer\</type\>       \<amount\>20294421.04\</amount\>     \</payment\>   \</payments\>   \<discounts\>     \<discount\>       \<type\>promoCode\</type\>       \<id\>gVUzWJeZKP\</id\>       \<amount\>14278199.46\</amount\>     \</discount\>     \<discount\>       \<type\>externalPromoAction\</type\>       \<id\>vaLZPU6y\</id\>       \<amount\>10127422.45\</amount\>     \</discount\>     \<discount\>       \<type\>balance\</type\>       \<card\>         \<number\>USfxyHsZ\</number\>       \</card\>       \<amount\>4238724.22\</amount\>     \</discount\>   \</discounts\>   \<ids\>     \<storeez.com\>311722112\</storeez.com\>   \</ids\>   \<updatedDateTimeUtc\>2015-03-20 17:56:47.198\</updatedDateTimeUtc\> \</order\>  |
| :---- |

## 6\. Чтение баланса потребителя {#6.-чтение-баланса-потребителя}

Полное описание всех полей:  
[https\://12storeez.directcrm.ru/operations/BalanceRead/help](https://12storeez.directcrm.ru/operations/BalanceRead/help)

| POST https\://api.mindbox.ru/v3/operations/sync?endpointId=12storeez\&operation=BalanceRead Content-Type: application/xml Accept: application/xml Authorization: Mindbox secretKey="\*\*\*" \<operation\>   \<customer\>     \<ids\>       \<storeezWebsiteId\>1305656139\</storeezWebsiteId\>     \</ids\>     \</customer\>   \<executionDateTimeUtc\>2017-01-23 16:57:25.442\</executionDateTimeUtc\> \</operation\> |
| :---- |

**Ответ:**

| \<result\>   \<status\>Success\</status\>   \<balances\> 	\<balance\>   	\<total\>15849144.4\</total\>   	\<available\>18231055.51\</available\>   	\<blocked\>13640217.62\</blocked\>   	\<systemName\>q1Jd3LfrjJ\</systemName\> 	\</balance\> 	\<balance\>   	\<total\>15802650.38\</total\>   	\<available\>10564961.1\</available\>   	\<blocked\>14867434.49\</blocked\>   	\<systemName\>KfG1thQamU\</systemName\> 	\</balance\>   \</balances\> \</result\> |
| :---- |

## 7\. Импорт оффлайн-точек {#7.-импорт-оффлайн-точек}

Подробнее:   
[https\://developers.mindbox.ru/v3.0/docs/%D0%BC%D0%B0%D1%81%D1%81%D0%BE%D0%B2%D1%8B%D0%B9-%D0%B8%D0%BC%D0%BF%D0%BE%D1%80%D1%82-%D0%BC%D0%B0%D0%B3%D0%B0%D0%B7%D0%B8%D0%BD%D0%BE%D0%B2](https://developers.mindbox.ru/v3.0/docs/%D0%BC%D0%B0%D1%81%D1%81%D0%BE%D0%B2%D1%8B%D0%B9-%D0%B8%D0%BC%D0%BF%D0%BE%D1%80%D1%82-%D0%BC%D0%B0%D0%B3%D0%B0%D0%B7%D0%B8%D0%BD%D0%BE%D0%B2)

![][image1]

| POST https\://12storeez-services.directcrm.ru/v2/import?operation=DirectCrm.PointsOfContacts.Import\&csvCodePage=65001HTTP/1.1Authorization: Basic \*\*\*= Accept: application/xmlContent-Type: text/csv ExternalId;Name;Comment;ParentChannelExternalIdShopTverskaya9;Магазин на Тверской, 9;Первый магазин в Москве\!;15  |
| :---- |

## 8\. История начислений баланса Полное описание всех полей: [https\://12storeez.directcrm.ru/operations/BalanceHistory/help](https://12storeez.directcrm.ru/operations/BalanceHistory/help) {#8.-история-начислений-баланса-полное-описание-всех-полей:-https://12storeez.directcrm.ru/operations/balancehistory/help}

| POST https\://api.mindbox.ru/v3/operations/sync?endpointId=12storeez\&operation=BalanceHistory Content-Type: application/xml Accept: application/xml Authorization: Mindbox secretKey="\*\*\*" \<operation\>   \<customer\>     \<ids\>       \<storeezWebsiteId\>85119864\</storeezWebsiteId\>     \</ids\>   \</customer\>   \<page\>     \<pageNumber\>1823396191\</pageNumber\>     \<itemsPerPage\>1000\</itemsPerPage\>     \<sinceDateTimeUtc\>2015-11-20 12:33:55.252\</sinceDateTimeUtc\>     \<tillDateTimeUtc\>2017-04-27 12:33:55.252\</tillDateTimeUtc\>   \</page\>   \<executionDateTimeUtc\>2017-02-14 12:33:55.252\</executionDateTimeUtc\> \</operation\>  |
| :---- |

## 9\. Отправка пароля  {#9.-отправка-пароля}

| POST https\://api.mindbox.ru/v3/operations/async?endpointId=12storeez\&operation=SendPassword Content-Type: application/json Accept: application/json Authorization: Mindbox secretKey="\*\*\*\*" {   "customer": {    "mobilePhone": "79269202222",     "ids": {       "storeezWebsiteId": "1534743209"     },        "subscriptions": \[       {         "brand": "12storeez",         "pointOfContact": "Email",         "valueByDefault": true,         "isSubscribed": true       },       {         "brand": "12storeez",         "pointOfContact": "Sms",                "valueByDefault": false,         "isSubscribed": false       }     \]   },   "smsMailing": {     "customParameters": {       "password": "Z498NLpAU"     }   },   "executionDateTimeUtc": "2015-11-13T12:10:31.797Z" } |
| :---- |

## 

## 10\. Получение данных о потребителе {#10.-получение-данных-о-потребителе}

Вы посылаете запрос по номеру телефона или уникальному ID.

| POST https\://api.mindbox.ru/v3/operations/sync?endpointId=12storeez\&operation=UserInformation Content-Type: application/xml Accept: application/xml Authorization: Mindbox secretKey="\*\*\*" \<operation\>   \<customer\>     \<mobilePhone\>79001234567\</mobilePhone\>     \<ids\>       \<storeezWebsiteId\>759157724\</storeezWebsiteId\>     \</ids\>   \</customer\>   \<executionDateTimeUtc\>2016-04-17 13:28:41.196\</executionDateTimeUtc\> \</operation\>  JSON: {   "customer": {     "mobilePhone": 79001234567,     "ids": {       "storeezWebsiteId": 59344     }   } }    |
| :---- |

В ответ возвращается следующее:  
[https\://12storeez.directcrm.ru/operations/UserInformation/help\#JSON-ExampleResponseBody](https://12storeez.directcrm.ru/operations/UserInformation/help#JSON-ExampleResponseBody)

**Запрос о заказах потребителя:**

| GET https\://12storeez-services.directcrm.ru/v2.1/orders/by-customer?operation=DirectCrm.V21CustomerOrderListOperation\&countToReturn={Максимальное количество заказов для возврата}\&storeezWebsiteId={Идентификатор потребителя}\&orderLineStatuses={Статусы заказов для возврата через запятую}Accept: application/xmlContent-Type: application/xmlAuthorization: DirectCrm key="\*\*\*"  |
| :---- |

## 11\. Аутентификация потребителя на кассе {#11.-аутентификация-потребителя-на-кассе}

* Отправка кода  
* Переотправка кода  
* Проверка кода

**Отправка кода подтверждения**

| POST https\://api.mindbox.ru/v3/operations/sync?endpointId=12storeez\&operation=Offline.SendMobilePhoneAuthorizationCode Content-Type: application/xml Accept: application/xml Authorization: Mindbox secretKey="\*\*"  \<operation\>  \<customer\>    \<mobilePhone\>79001234567\</mobilePhone\>  \</customer\>  \<pointOfContact\>ID магазина\</pointOfContact\>\</operation\>  |
| :---- |

**Переотправка кода**

| POST https\://api.mindbox.ru/v3/operations/sync?endpointId=12storeez\&operation=Offline.ResendMobilePhoneConfirmationCode Content-Type: application/xml Accept: application/xml Authorization: Mindbox secretKey="BqYYRTXLjXbaB1SyUGiF" \<operation\>   \<customer\>     \<mobilePhone\>79001234567\</mobilePhone\>   \</customer\>   \<pointOfContact\>ID магазина\</pointOfContact\>   \<executionDateTimeUtc\>2015-11-21 12:38:36.391\</executionDateTimeUtc\> \</operation\>  |
| :---- |

**Проверка кода**

| POST https\://api.mindbox.ru/v3/operations/sync?endpointId=12storeez\&operation=Offline.CheckMobilePhoneAuthorizationCode Content-Type: application/xml Accept: application/xml Authorization: Mindbox secretKey="\*\*\*" \<operation\>   \<customer\>     \<mobilePhone\>79001234567\</mobilePhone\>     \<ids\>             \<storeezWebsiteId\>1039553548\</storeezWebsiteId\>     \</ids\>    \</customer\>   \<authentificationCode\>1234567\</authentificationCode\>   \<pointOfContact\>ID магазина\</pointOfContact\>   \<executionDateTimeUtc\>2015-10-22 12:38:36.375\</executionDateTimeUtc\> \</operation\>  |
| :---- |

12\. Передача данных о потребителе

| POST https\://api.mindbox.ru/v3/operations/async?endpointId=12storeez\&operation=CustomerPersonalData Content-Type: application/json Accept: application/json Authorization: Mindbox secretKey="\*\*" {   "customer": {     "ids": {       "storeezWebsiteId": "495041080"     },     "email": "test@mindbox.ru",     "birthDate": "1990-01-31",     "mobilePhone": "79001234567",     "lastName": "",     "firstName": "",     "middleName": "",      },   "executionDateTimeUtc": "2018-01-14T17:07:04.205Z" }  |
| :---- |

## 

## 12\. Импорт в Mindbox нового или редактирование старого клиента  {#12.-импорт-в-mindbox-нового-или-редактирование-старого-клиента}

Этот метод следует вызывать, когда в базу 12storeez попал новый клиент или возникла необходимость отредактировать старого. Этот метод \_не\_ отправляет письма. Только добавляет в базу новые данные потребителя :)

Если каких-то данных нет (например mobilephone или email), то узел передавать не нужно. 

| POST https\://api.mindbox.ru/v3/operations/async?endpointId=12storeez\&operation=CreateNewUserorEdit Content-Type: application/json Accept: application/json Authorization: Mindbox secretKey="\*\*" {   "customer": {     "birthDate": "1990-01-31",     "mobilePhone": "79269202222",     "lastName": "Смирнов",     "firstName": "Александр",     "email": "test@mindbox.ru",     "ids": {       "storeezWebsiteId": "2109111723"     },         "subscriptions": \[       {         "brand": "12storeez",         "pointOfContact": "Sms",         "valueByDefault": true,         "isSubscribed": true       },       {         "brand": "12storeez",         "pointOfContact": "Email",         "valueByDefault": true,         "isSubscribed": true       }     \]   } }  |
| :---- |

## 13\. Сервис пересчета стоимости заказа {#13.-сервис-пересчета-стоимости-заказа}

Если необходимо изменить состав, изменить используемое количество баллов и т.д. для существующего заказа, то вместо сервиса предварительной информации вызывается пересчет. 

Существующий заказ \-\> Сервис пересчета \-\> Сервис оформления \-\> Сервис подтверждения

[https\://12storeez.directcrm.ru/operations/RecalculateOrder/help](https://12storeez.directcrm.ru/operations/RecalculateOrder/help)

| POST https\://12storeez-services.directcrm.ru/v2.1/orders/get-order-recalculation-info?operation=RecalculateOrder Accept: application/xml Content-Type: application/xml Authorization: DirectCrm key="\*\*\*" \<order\>   \<pointOfContact\>StqciAN15\</pointOfContact\>   \<customer\> 	\<storeezWebsiteId\>72686760\</storeezWebsiteId\>   \</customer\>   \<actualAmountForCustomer\>20366546.99\</actualAmountForCustomer\>   \<deliveryCost\>1353420.44\</deliveryCost\>   \<totalPrice\>8671909.45\</totalPrice\>   \<lines\> 	\<line\>   	  	\<discounts\>     	\<discount\>       	\<type\>externalPromoAction\</type\>       	\<id\>ZdFEWbTIw\</id\>       	\<amount\>3671737.63\</amount\>     	\</discount\>     	\</discounts\>   	\<sku\>     	\<skuId\>105328\</skuId\>     	\<productId\>101996\</productId\>     	\<basePricePerItem\>5366177.4\</basePricePerItem\>   	\</sku\>   	\<quantity\>1\</quantity\>   	\<status\>303\</status\> 	\</line\> 	  \</lines\>   \<payments\> 	\<payment\>   	\<type\>cash\</type\> \<amount\>10375419.75\</amount\> 	\</payment\>   \</payments\>    \<ids\> 	 	\<storeez.com\>124011535\</storeez.com\>   \</ids\>   \<staff\>   \</staff\> \</order\> |
| :---- |

## 14\. Получение информации о заказе {#14.-получение-информации-о-заказе}

Сервис для получения информации о заказе. Позволяет узнать, в каком сейчас статусе заказ находится в системе Mindbox.

| POST https\://api.mindbox.ru/v3/operations/sync?endpointId=12storeez\&operation=GetOrderinfo Content-Type: application/xml; charset=utf-8 Accept: application/xml Authorization: Mindbox secretKey="\*\*\*" \<operation\>   \<order\>     \<ids\>       \<externalSystemstoreez.com\>1538377259\</externalSystemstoreez.com\>     \</ids\>   \</order\> \</operation\>  |
| :---- |

## 15\. Редактирование заказа без процессинга {#15.-редактирование-заказа-без-процессинга}

В запросе обязательно передавать полную информацию по заказу.   
Документация по методу: [https\://12storeez.mindbox.ru/campaigns/1070/operations/1573/help](https://12storeez.mindbox.ru/campaigns/1070/operations/1573/help)   
Пример запроса:

| POST  \<?xml version="1.0" encoding="utf-8"?\> \<operation\>     \<customer\>         \<ids\>             \<storeezWebsiteId\>1707630\</storeezWebsiteId\>         \</ids\>     \</customer\> \<order\>  \<customFields\>       \<reviewGiven\>{Оставлен отзыв}\</reviewGiven\>     \</customFields\> \<ids\>     \<mindbox\>1449724\</mindbox\>   \</ids\>     \<pointOfContact\>118\</pointOfContact\>     \<lines\>         \<line\>         \<product\>             \<sku\>             \<ids\>                 \<storeez.com\>120782\</storeez.com\>                 \</ids\>               \</sku\>             \</product\>             \<basePricePerItem\>1000\</basePricePerItem\>             \<quantity\>1\</quantity\>             \<lineNumber\>1\</lineNumber\>             \<discountedPrice\>1000\</discountedPrice\>             \<status\>411\</status\>         \</line\>     \</lines\>     \</order\> \<executionDateTimeUtc\>2022-03-22 17:55\</executionDateTimeUtc\> \</operation\>   |
| :---- |

## 16\. Редактирование заказа “Клиент оценил заказ”

В запросе передается только флаг, что отзыв оставлен, и статус заказа. Остальная информация не нужна.   
Документация по методу: [https\://12storeez.mindbox.ru/campaigns/operations/8468/help](https://12storeez.mindbox.ru/campaigns/operations/8468/help) 

#### Если в заказе есть позиции с разными статуса заказа. 

Описание запроса

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/sync?endpointId=12storeez\&operation=EditOrderNoProcessingv2\&deviceUUID={UUID устройства} |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="\*\*\*" |
| :---- |

**Тело запроса**

| {  "customer": {    "ids": {      "storeezWebsiteId": "Идентификатор клиента"    }  },  "order": {    "ids": {      "mindboxId": "Идентификатор заказа"    },    "customFields": {      "reviewGiven": "Оставлен отзыв. Передается значение true\>"    },    "lines": \[      {        "product": {          "ids": {            "storeez.com": "ИД продукта"          }        },        "quantity": "Кол-во позиций",        "status": "Статус заказа",        "discountedPriceOfLine": "Цена для покупателя за линию чека (без учета отмены и возврата линии)"      },      {        "product": {          "ids": {            "storeez.com": "ИД продукта"          }        },        "quantity": "Кол-во позиций",        "status": "Статус заказа",        "discountedPriceOfLine": "Цена для покупателя за линию чека (без учета отмены и возврата линии)"      }    \]  }} |
| :---- |

#### Если в заказе все позиции имеют один единый статус

Описание запроса

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/sync?endpointId=12storeez\&operation=EditOrderNoProcessingv3\&deviceUUID={UUID устройства} |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="\*\*\*" |
| :---- |

**Тело запроса**

| {  "customer": {    "ids": {      "storeezWebsiteId": "\<Идентификатор клиента\>"    }  },  "orderLinesStatus": "\<Статус для всех линий заказа\>",  "order": {    "ids": {      "mindboxId": "\<Идентификатор заказа в Mindbox\>"    },    "customFields": {      "reviewGiven": "\<Отзыв оставлен?\>"    }  }} |
| :---- |

# Интеграция с API Mindbox (не актуально)

## 2.1 Процессинг заказов

### Эта часть заменяет сервисы 1-4 из старой интеграции.

Оформление заказа может быть как авторизованным покупателем, так и неавторизованным (заказ в один клик и т.п.).  
При оформлении заказа авторизованным покупателем применяются персональные скидки, есть возможность оплатить заказ баллами.  
При оформлении заказа неавторизованным покупателем могут быть начислены баллы за заказ.

![][image2]

### Оформление заказа авторизованным покупателем

В корзине интернета-магазина вызывается операция [Website.CalculateAuthorizedCart](https://12storeez.mindbox.ru/campaigns/operations/303/help), которая пересчитывает корзину и возвращает цены с учетом персональных скидок, начисленные и списанные баллы и сообщения для отображения пользователю. 

Если на сайте используется собственный механизм скидок, то сначала сайт применяет свои скидки, затем вызывает операцию [Website.CalculateAuthorizedCart](https://12storeez.mindbox.ru/campaigns/operations/303/help),передавая туда примененные скидки. Операция возвращает итоговый расчет, с учетом и скидок сайта и скидок в Майндбокс.

Операция должна вызываться при каждом изменении корзины: при изменении состава, при применении промокода или при использовании бонусных баллов.

Расчет корзины обычно занимает 200-300мс. Для визуального ускорения работы сайта рекомендуется вызывать операцию асинхронно: изначально показываются базовые цены с учетом скидок на сайте и прелоадер, через 200-300мс подгружаются и отображаются персональные скидки.

После того, как все скидки пересчитаны, промокоды и баллы применены, пользователь нажимает “Оформить заказ”.

При нажатии на кнопку вызывается операция [Website.BeginAuthroziedOrderTransaction](https://12storeez.mindbox.ru/campaigns/operations/305/help), которая блокирует баллы, промокоды, подарочные карты и фиксирует скидки по текущим акциям.  
Если с момента вызова [Website.CalculateAuthorizedCart](https://12storeez.mindbox.ru/campaigns/operations/303/help) цена заказа изменилась (например, акция закончилась), метод вернет статус PriceHasBeenChanged.   
В этом случае необходимо отобразить пользователю ошибку и заново рассчитать скидки с помощью операции [Website.CalculateAuthorizedCart](https://12storeez.mindbox.ru/campaigns/operations/303/help). 

После успешного ответа, сайт сохраняет заказ в свою базу данных и при успешном результате асинхронно вызывает операцию [Website.CommitOrderTransaction](https://12storeez.mindbox.ru/campaigns/operations/307/help).  
В случае ошибки сайт должен отменить транзакцию с помощью операции [Website.RollbackOrderTransaction](https://12storeez.mindbox.ru/campaigns/operations/308/help).

### Оформление заказа неавторизованным покупателем

Имеет смысл использовать общий процесс для авторизованных и неавторизованных покупателей так как в программе не заложены персональные скидки.

В корзине интернета-магазина вызывается операция [Website.CalculateUnauthorizedCart](https://developers.mindbox.ru/docs/processing-calculate), которая пересчитывает корзину и возвращает цены с учетом публичных скидок, сообщения для отображения пользователю. 

Если на сайте используется собственный механизм скидок, то сначала сайт применяет свои скидки, затем вызывает операцию [Website.CalculateUnauthorizedCart](https://developers.mindbox.ru/docs/processing-calculate),передавая туда примененные скидки. Операция возвращает итоговый расчет, с учетом и скидок сайта и скидок в Майндбокс.

Операция должна вызываться при каждом изменении корзины: при изменении состава, при применении промокода или при использовании бонусных баллов.

Расчет корзины обычно занимает 200-300мс. Для визуального ускорения работы сайта рекомендуется вызывать операцию асинхронно: изначально показываются базовые цены с учетом скидок на сайте и прелоадер, через 200-300мс подгружаются и отображаются скидки Майндбокс.

После того, как все скидки пересчитаны, промокоды и баллы применены, пользователь вводит емейл или телефон и нажимает “Оформить заказ”.

При нажатии на кнопку вызывается операция [Website.BeginUnauthroziedOrderTransaction](https://developers.mindbox.ru/docs/processing-begin-order-transaction), в которую передается емейл и телефон, который ввел пользователь. Операция блокирует промокоды, подарочные карты и фиксирует скидки по текущим акциям.  
Если с момента вызова [Website.CalculateUnauthorizedCart](https://developers.mindbox.ru/docs/processing-calculate) цена заказа изменилась (например, акция закончилась), метод вернет статус PriceHasBeenChanged.   
В этом случае необходимо отобразить пользователю ошибку и заново рассчитать скидки с помощью операции [Website.CalculateUnauthorizedCart](https://developers.mindbox.ru/docs/processing-calculate). 

После успешного ответа, сайт сохраняет заказ в свою базу данных и при успешном результате асинхронно вызывает операцию [Website.CommitOrderTransaction](https://developers.mindbox.ru/docs/processing-commit-order-transaction).  
В случае ошибки сайт должен отменить транзакцию с помощью операции [Website.RollbackOrderTransaction](https://developers.mindbox.ru/docs/processing-rollback-order-transaction).

## 2.2 Смена статуса без расчета

### Заменяет сервисы 4-5 старой интеграции.

При смене статуса одной позиции заказа или всех позиций вызывается операция [Website.UpdateOrder](https://12storeez.mindbox.ru/campaigns/operations/3994/help), в которую передается id заказа, id товаров и актуальные статусы позиций.   
Необходимо все события по отмены заказа перенести на новый тип обмена. Т.е сейчас при отмене заказа вызывается тип [https\://docs.google.com/document/d/1q6KSUUz\_jCcufEjr088PygVKkyA0bcSrmCCNGl\_5mPk/edit\#heading=h.lam8nvkhsroo](https://docs.google.com/document/d/1q6KSUUz_jCcufEjr088PygVKkyA0bcSrmCCNGl_5mPk/edit#heading=h.lam8nvkhsroo) необходимо заметить на запрос описанный ниже \+ добавить параметры в котором будет фиксироваться причина отмены заказа.   
**Важно:** значения которые передавали в пункте 4 остаются без изменений. Ниже в запросе указали поля, которые приходили ранее по обмену. Пожалуйста, если какие-то поля не включены в обмен напишите менеджеру. 

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/{sync/async}?endpointId=12storeez\&operation=Website.UpdateOrder |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="Секретный\_ключ" |
| :---- |

**Тело запроса**

| {  "pointOfContact": "\<Внешний идентификатор точки контакта\>",  "order": {    "ids": {      "mindboxId": "\<Идентификатор заказа в Mindbox\>",      "externalSystemstoreez.com": "\<Идентификатор заказа Идентификатор 12storeez.com\>",    },    "customFields": {      "deliveryType": "\<Способ доставки для транзакционных\>",      "fitting": "\<Примерка\>",      "forblogger": "\<for\_blogger\>",      "paylink": "\<Ссылка на оплату\>",       "reasoncancellation": "\<Передаете 1 или 2, где 1 \- Отмена из\-за неоплаты, 2 \- отмена заказа в личном кабинете \>",      "sendletter": "\<Отправлять ли письмо?\>"    },    "lines": \[      {        "product": {          "ids": {            "storeez.com": "\<Id Product в Сайт 12storeez.com\>"          }        },        "quantity": "\<Количество продукта\>",        "customFields": {          "positionStatus": "\<Статус позиции\>"        },        "status": "\<Статус позиции заказа\>"      },      {        "product": {          "ids": {            "storeez.com": "\<Id Product в Сайт 12storeez.com\>"          }        },        "quantity": "\<Количество продукта\>",        "customFields": {          "positionStatus": "\<Статус позиции\>"        },        "status": "\<Статус позиции заказа\>"      }    \]  },  "executionDateTimeUtc": "\<Дата и время выполнения (можно использовать для выполнения запроса задним числом)\>"} |
| :---- |

Причины отмены заказа: 

| Идентификатор | Значение |
| :---- | :---- |
| otm-1 | Нет примерки |
| otm-2 | Нет наложенного платежа |
| otm-3 | Не готова ждать заказ (сборный) |
| otm-4 | Передумала |
| otm-5 | Нет в наличии |
| otm-6 | Брак/плохое качество |
| otm-7 | Купила в магазине/шоуруме |
| otm-8 | Не оплатила |
| otm-9 | Оплатила другой заказ |
| otm-10 | Оформила два одинаковых заказа |
| otm-11 | Тестовый |
| otm-12 | Отмена из ЛК |
| otm-13 | Технический сбой |
| otm-14 | Клиент не вышел на связь |
| otm-15 | Заказ не был оплачен, отменен автоматически |

# Обновление процессинга передачи заказов 2024

Мы обновляем процесс передачи заказов, переходя от использования незакрытых заказов (транзакций) и двухшагового создания заказа к одноэтапному процессу создания заказа за один вызов операции.

## Изменения, которые необходимо внести:

### Шаг 1\. Оформление заказа

**Раньше:** каждый заказ нужно было дополнительно подтверждать (коммитить) и отправлять ид транзакции, чтобы он был обработан системой лояльности.  
**Сейчас:** система лояльности работает с «автокоммитом», заказы создаются и обрабатываются сразу за один шаг без необходимости дополнительного подтверждения.

**Отказываемся от следующих методов:**

* ConfirmOrder (подтверждение заказа)  
* CheckoutOrder (оформление заказа)  
* Offline.BeginAnonymousOrderTransaction (оформление заказа анонимом)  
* Offline.BeginAuthorizedOrderTransaction (оформление заказа авторизованного пользователя)  
* Offline.BeginUnauthorizedOrderTransaction (оформление заказа не авторизованного пользователя)  
* Offline.CommitOrderTransaction (подтверждение заказа)  
* PreOrderInfo (предварительный расчет заказа)

**Будут вызываться только 4 события:** 

* [BeginAuthorizedOrderTransaction](#создание-чека-авторизованного-клиента) \- *Создание чека авторизованного клиента*BeginAuthorizedOrderTransaction   
* [BeginUnauthorizedOrderTransaction](#создание-чека-неавторизованного-клиента) \- Создание чека неавторизованного клиента  
* [BeginAnonymousOrderTransaction](#создание-чека-анонимного-клиента) \- Создание анонимного чека  
* [Website.CalculateAuthorizedCart и Website.CalculateUnauthorizedCart](https://developers.mindbox.ru/docs/preorder) \- предварительный расчет заказа

**Важно:** в начало транзакции сохранения заказа (Begin) добавляем ключ идемпотентности, чтобы избежать дублирования при повторной попытке создания заказа. Ключ идемпотентности необходимо генерировать заново для каждого уникального запроса. Если запрос с ключом А был успешно выполнен, второй запрос с ключом А будет отклонен системой.

### Шаг 2\. Отмена заказа

**Раньше:** при отмене заказа или отмене транзакции вызывались отдельные события (Отмена заказа (CancelOrder) и отмена транзакции (Offline.RollbackOrderTransaction))  
**Сейчас:** все обновления статуса заказа необходимо передавать одним методом обновлением статуса заказа UpdateOrder. Т.е в случае, когда rollback или  CancelOrder отменял заказ и дальнейшая работа с заказом не предполагается, необходимо теперь вызвать операцию Website.UpdateOrder и явно передать статус "Отменен".

### Шаг 3\. Проверка URL запросов к Mindbox

**Сейчас:** многие запросы от вас приходят в устаревшем формате, что затрудняет анализ логов запросов, которые поступают от вашей системы, например: https\://12storeez-services.directcrm.ru/.  
**Что нужно:** необходимо, чтобы все запросы по API направлялись по URL: https\://api.mindbox.ru/.

### Описание методов

#### Создание чека авторизованного клиента {#создание-чека-авторизованного-клиента}

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/sync?endpointId={Идентификатор точки интеграции}\&operation=BeginAuthorizedOrderTransaction\&transactionId={Ключ идемпотентности (Guid)} |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="Секретный\_ключ" |
| :---- |

**Тело запроса**

| {  "order": {    "ids": {      "externalSystemstoreez.com": "\<Идентификатор заказа\>"    },    "totalPrice": "\<Итоговая сумма, полученная от клиента\>",    "coupons": \[      {        "ids": {          "code": "Значение промокода"        }      }    \],    "lines": \[      {        "quantity": "\<Количество товаров\>",        "lineNumber": "\<Порядковый номер позиции заказа\>",        "product": {          "ids": {            "storeez.com": "\<Идентификатор продукта\>"          }        },        "status": {          "ids": {            "externalId": "\<Идентификатор статуса заказа\>"          }        },        "basePricePerItem": "\<Базовая стоимость продукта\>",        "lineId": 1      }    \],    "payments": \[      {        "type": "\<Тип оплаты (card)\>",        "amount":  "\<Итоговая сумма, которую оплатил клиент\>"      }    \]  },  "pointOfContact":  "\<Идентификатор точки контакта\>",  "customer": {    "ids": {      "mindboxId":  "\<Id клиента в Mindbox\>"    }  }} |
| :---- |

#### Создание чека неавторизованного клиента {#создание-чека-неавторизованного-клиента}

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/sync?endpointId={Идентификатор точки интеграции}\&operation=BeginUnauthorizedOrderTransaction\&transactionId={Ключ идемпотентности (Guid)} |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="Секретный\_ключ" |
| :---- |

**Тело запроса**

| {  "order": {    "ids": {      "externalSystemstoreez.com": "\<Идентификатор заказа\>"    },    "totalPrice": "\<Итоговая сумма, полученная от клиента\>",     "coupons": \[      {        "ids": {          "code": "Значение промокода"        }      }    \],    "lines": \[      {        "quantity": "\<Количество товаров\>",        "lineNumber": "\<Порядковый номер позиции заказа\>",        "product": {          "ids": {            "storeez.com": "\<Идентификатор продукта\>"          }        },        "status": {          "ids": {            "externalId": "\<Идентификатор статуса заказа\>"          }        },        "basePricePerItem": "\<Базовая стоимость продукта\>",        "lineId": 1      }    \],    "payments": \[      {        "type": "\<Тип оплаты (card)\>",        "amount":  "\<Итоговая сумма, которую оплатил клиент\>"      }    \]  },  "pointOfContact":  "\<Идентификатор точки контакта\>",  "customer": {    "mobilePhone": "\<Мобильный телефон клиента\>"  }} |
| :---- |

#### Создание чека анонимного клиента {#создание-чека-анонимного-клиента}

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/sync?endpointId={Идентификатор точки интеграции}\&operation=BeginAnonymousOrderTransaction\&transactionId={Ключ идемпотентности (Guid)} |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="Секретный\_ключ" |
| :---- |

**Тело запроса**

| {  "order": {    "ids": {      "externalSystemstoreez.com": "\<Идентификатор заказа\>"    },    "totalPrice": "\<Итоговая сумма, полученная от клиента\>",     "coupons": \[      {        "ids": {          "code": "Значение промокода"        }      }    \],    "lines": \[      {        "quantity": "\<Количество товаров\>",        "lineNumber": "\<Порядковый номер позиции заказа\>",        "product": {          "ids": {            "storeez.com": "\<Идентификатор продукта\>"          }        },        "status": {          "ids": {            "externalId": "\<Идентификатор статуса заказа\>"          }        },        "basePricePerItem": "\<Базовая стоимость продукта\>",        "lineId": 1      }    \],    "payments": \[      {        "type": "\<Тип оплаты (card)\>",        "amount":  "\<Итоговая сумма, которую оплатил клиент\>"      }    \]  },  "pointOfContact":  "\<Идентификатор точки контакта\>"} |
| :---- |

#### Обновление статуса заказа(обновление заказа)

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/{sync/async}?endpointId=12storeez\&operation=Website.UpdateOrderv2 |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="Секретный\_ключ" |
| :---- |

**Тело запроса**

| {  "pointOfContact": "\<Внешний идентификатор точки контакта\>",  "order": {    "ids": {      "mindboxId": "\<Идентификатор заказа в Mindbox\>",      "externalSystemstoreez.com": "\<Идентификатор заказа Идентификатор 12storeez.com\>",    },     "coupons": \[      {        "ids": {          "code": "Значение промокода"        }      }    \],    "customFields": {      "deliveryType": "\<Способ доставки для транзакционных\>",      "fitting": "\<Примерка\>",      "forblogger": "\<for\_blogger\>",      "paylink": "\<Ссылка на оплату\>",       "reasoncancellation": "\<Передаете 1 или 2, где 1 \- Отмена из\-за неоплаты, 2 \- отмена заказа в личном кабинете \>",      "sendletter": "\<Отправлять ли письмо?\>"    },    "lines": \[      {        "product": {          "ids": {            "storeez.com": "\<Id Product в Сайт 12storeez.com\>"          }        },        "quantity": "\<Количество продукта\>",        "customFields": {          "positionStatus": "\<Статус позиции\>"        },        "status": "\<Статус позиции заказа\>"      },      {        "product": {          "ids": {            "storeez.com": "\<Id Product в Сайт 12storeez.com\>"          }        },        "quantity": "\<Количество продукта\>",        "customFields": {          "positionStatus": "\<Статус позиции\>"        },        "status": "\<Статус позиции заказа\>"      }    \]  },  "executionDateTimeUtc": "\<Дата и время выполнения (можно использовать для выполнения запроса задним числом)\>"} |
| :---- |

#### Предварительный расчет заказа

Сервис используется в корзине интернет-магазина или на кассе оффлайн-магазина. В сервис передается полный состав заказа со всеми внешними акциями, которые нужно к нему применить.

В ответ возвращается информация о заказе с пересчитанными ценами (с учетом активных в данный момент промоакций, промокодов и других скидок), и детальной информации о всех скидках, запрошенных покупателем.

В процессе расчета скидок Mindbox может разделить одну линию на несколько. Подробнее о распределении скидок можно почитать [тут](https://help.mindbox.ru/docs/split-and-spread). В этом случае в ответе вернется несколько линий с одинаковым lineId, по которому клиент может понять, какая именно позиция была разделена. Клиент должен корректно обработать такую ситуацию и каждой новой линии присвоить свой уникальный идентификатор для последующих запросов.

Бывает 2 типа корзины: 

* пользователь авторизован. [Описание метода](https://12storeez.mindbox.ru/campaigns/operations/303/help)   
* не авторизованный клиент. [Описание метода](https://12storeez.mindbox.ru/campaigns/operations/304/help)

Пример запроса для авторизованного пользователя 

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/sync?endpointId={Идентификатор точки интеграции}\&operation=Website.CalculateAuthorizedCart\&transactionId={Ключ идемпотентности (Guid)} |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="Секретный\_ключ" |
| :---- |

**Тело запроса**

| {  "order": {    "bonusPoints": \[      {        "amount": 0      }    \],    "coupons": \[      {        "ids": {          "code": "Значение промокода"        }      }    \],    "lines": \[      {        "basePricePerItem": 29000,        "quantity": 1,        "lineId": 228719,        "lineNumber": null,        "customFields": {          "positionStatus": "new"        },        "product": {          "ids": {            "storeez.com": "228719"          }        },        "status": {          "ids": {            "externalId": 101          }        }      },      {        "basePricePerItem": 41000,        "quantity": 1,        "lineId": 211932,        "lineNumber": null,        "customFields": {          "positionStatus": "new"        },        "product": {          "ids": {            "storeez.com": "211932"          }        },        "status": {          "ids": {            "externalId": 101          }        }      }    \]  },  "customer": {    "ids": {      "storeezWebsiteId": "1234-test"    }  } |
| :---- |

# Возврат заказа: добавление трек номера

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/async?endpointId={Идентификатор точки интеграции}\&operation=ReturnTrackNumber |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="Секретный\_ключ" |
| :---- |

**Тело запроса**

| {  "order": {    "ids": {      "externalSystemstoreez.com": "\<Идентификатор заказа Идентификатор 12storeez.com\>"    },    "customFields": {      "returnTrackNumber": "\<Трек-номер возврата\>"    }  }} |
| :---- |

# Транзакционные письма по заказу

## Сформирована ссылка на оплату

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/async?endpointId={Идентификатор точки интеграции}\&operation=OrderPaymentPrompt |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="Секретный\_ключ" |
| :---- |

**Тело запроса**

| {  "customer": {    "email": "\<Email\>"  },  "emailMailing": {    "customParameters": {      "paylink": "\<Параметр paylink для письма\>"    }  }} |
| :---- |

# Запрос кода авторизации через звонок клиенту

## Запрос кода авторизации через звонок касса

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/async?endpointId={Идентификатор точки интеграции}\&operation=Offline.SendMobilePhoneAuthorizationCodeflashcall |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="Секретный\_ключ" |
| :---- |

**Тело запроса**

| {  "customer": {    "mobilePhone": "Номер телефона клиента"  }} |
| :---- |

## Запрос кода авторизации через звонок сайт/мобильное приложение

| Метод | Post |
| :---- | :---- |
| URL | https\://api.mindbox.ru/v3/operations/async?endpointId={Идентификатор точки интеграции}\&operation=Web.SendMobilePhoneAuthorizationCodeflashcall |

**Заголовок**

| Content-Type: application/json; charset=utf\-8Accept: application/jsonAuthorization: Mindbox secretKey="Секретный\_ключ" |
| :---- |

**Тело запроса**

| {  "customer": {    "mobilePhone": "Номер телефона клиента"  }} |
| :---- |

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>