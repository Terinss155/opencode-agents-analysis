// Пример аннотаций swag и DTO для гейта mobile-monorepo-go — правила: openapi-spec/references/swagger.md, разделы 2.2 и 4;
// контракт — references/mobile.md (раздел 8 — гейт).
// УСЛОВНЫЙ ресурс «избранные магазины пользователя»: такого эндпоинта нет; пара к mobile-new-endpoint.yml.
// Swagger гейта (docs/mobile_api/*) генерируется из этих комментариев и тегов — сгенерированные файлы руками не правятся.
// Код функций повторяет стиль существующих прокси (service/cart.go, service/product.go) и приведён для контекста:
// в задаче на гейт аналитик описывает контракт, а не код.
//
// Изменено 17.11.2026 (решения knowledge/_archive/skills_2026-11-17/Анализ_скиллов_эндпоинты.md, часть 2, §6.1):
//   - теги DTO — json + example (практика гейта); binding / enums / extensions убраны — в гейте не используются,
//     обязательность и nullable — в комментарии к полю (swagger.md, раздел 4, п. 5);
//   - список — массив в result + total (mobile.md, раздел 6);
//   - своя ошибка гейта — фактический формат {"error": {"message", "details"}} (mobile.md, раздел 8, п. 4).

package service

// ---------- DTO (internal/app/models/dto/favouritestore) ----------

// AddFavouriteStoreRequest — тело запроса добавления магазина в избранное.
type AddFavouriteStoreRequest struct {
	// Обязательное. Код магазина из списка магазинов (условно: GET /api/v1/stores, поле store_code), целое ≥ 1
	StoreCode int `json:"store_code" example:"42"`
}

// FavouriteStore — магазин из избранного пользователя. Все поля приходят всегда.
type FavouriteStore struct {
	// Код магазина — передаётся в store_code при удалении из избранного
	StoreCode int `json:"store_code" example:"42"`
	// Название магазина для карточки
	Title string `json:"title" example:"12 STOREEZ Цветной"`
	// Адрес магазина одной строкой — город, улица, дом
	Address string `json:"address" example:"Москва, Цветной бульвар, 15с1"`
	// Часы работы сегодня для вывода в карточке; может быть null — магазин сегодня закрыт или часы не заданы в админке
	WorkHours *string `json:"work_hours" example:"10:00–22:00"`
	// Можно ли забронировать товар в этом магазине — показывать кнопку «Забронировать»
	IsReservationAvailable bool `json:"is_reservation_available" example:"true"`
}

// GetFavouriteStoresResponse — ответ списка избранных магазинов.
type GetFavouriteStoresResponse struct {
	// Признак успешного ответа
	Success bool `json:"success" example:"true"`
	// Избранные магазины текущей страницы; пустой массив — избранных нет
	Result []FavouriteStore `json:"result"`
	// Общее количество избранных магазинов без учёта пагинации
	Total int `json:"total" example:"2"`
}

// FavouriteStoreResponse — ответ добавления магазина в избранное.
type FavouriteStoreResponse struct {
	// Признак успешного ответа
	Success bool           `json:"success" example:"true"`
	Result  FavouriteStore `json:"result"`
}

// MobileErrorResponse — ответ монолита с ошибкой, который гейт возвращает как есть.
type MobileErrorResponse struct {
	// Всегда false для ошибки
	Success bool `json:"success" example:"false"`
	Result  struct {
		// Код ошибки Mobile API (BaseController монолита) — по нему МП выбирает ветку обработки
		ErrorCode int `json:"error_code" example:"1015"`
		// Общее сообщение ошибки; для части кодов — фиксированный текст
		ErrorText string `json:"error_text" example:"Ошибка валидации данных"`
		// Ошибки по полям для форм ввода; пустой массив — ошибка не привязана к полю
		ErrorData []MobileFieldError `json:"error_data"`
	} `json:"result"`
	// Добавляется гейтом, если монолит ответил статусом, отличным от 200
	IsErrorFromPHP bool `json:"isErrorFromPHP" example:"true"`
}

// MobileFieldError — ошибка поля из error_data.
type MobileFieldError struct {
	// Имя поля запроса с ошибкой; пустая строка — общая ошибка
	Target string `json:"target" example:"store_code"`
	// Предметный код из ResponseErrorCode монолита — общий с сайтом
	Code string `json:"code" example:"20471"`
	// Текст ошибки для показа под полем
	Message string `json:"message" example:"Магазин не найден"`
}

// Своя ошибка гейта (заголовки, разбор тела) — существующий dto.ErrorResponse (internal/app/models/dto/common/error_response.go):
//   {"error": {"message": "<текст>", "details": {"<поле>": ["<текст>"]}}}
// Новый DTO для неё не создаётся.

// ---------- Методы сервиса (internal/app/service/favourite_store.go) ----------

// GetFavouriteStores godoc
//
// @Summary      Список избранных магазинов
// @Description  Proxy to GET /mobile/favourite-stores
// @Description  Магазины, отмеченные пользователем на экране «Магазины», последний добавленный — первым.
// @Description  Без limit / offset возвращается первая страница из 50 магазинов.
//
// @Tags         FavouriteStores
// @Accept       json
// @Produce      json
// @Security     Bearer
//
// @Param        X-Platform  header  string   true   "Платформа приложения"                                  Enums(android, ios)
// @Param        X-Version   header  string   true   "Версия приложения"                                     example(1.16.1)
// @Param        limit       query   integer  false  "Количество магазинов на странице. Без параметра — 50"  minimum(1) maximum(1000) default(50) example(50)
// @Param        offset      query   integer  false  "Сколько магазинов пропустить от начала списка. Без параметра — 0"  minimum(0) maximum(100000) default(0) example(0)
//
// @Success      200  {object}  GetFavouriteStoresResponse  "Список избранных магазинов"
// @Failure      400  {object}  MobileErrorResponse         "error_code 1015 — limit или offset вне допустимого диапазона"
// @Failure      401  {object}  MobileErrorResponse         "Сессия истекла (error_code 1002)"
// @Failure      500  {object}  MobileErrorResponse         "Непредвиденная ошибка"
//
// @Router       /api/v1/favourite-stores [get]
func (s *favouriteStoreService) GetFavouriteStores(c *fiber.Ctx) error {
	siteApiUrl := fmt.Sprintf("%s/%s", s.service.cfg.Site.BaseInternalUrl, s.service.cfg.Site.FavouriteStoresPath)

	// isCrutch = false — query-параметры (limit, offset) передаются в монолит (mobile.md, раздел 8, п. 2)
	return helpers.ProxyToSite(s.service.logger, c, s.service.cfg, s.service.restyClient, siteApiUrl, resty.MethodGet, nil, false)
}

// AddFavouriteStore godoc
//
// @Summary      Добавление магазина в избранное
// @Description  Proxy to POST /mobile/favourite-stores
// @Description  Отмечает магазин избранным. Повторное добавление того же магазина — 200, запись не дублируется.
//
// @Tags         FavouriteStores
// @Accept       json
// @Produce      json
// @Security     Bearer
//
// @Param        X-Platform  header  string                    true  "Платформа приложения"  Enums(android, ios)
// @Param        X-Version   header  string                    true  "Версия приложения"     example(1.16.1)
// @Param        request     body    AddFavouriteStoreRequest  true  "Магазин, который добавляется в избранное"
//
// @Success      200  {object}  FavouriteStoreResponse  "Магазин добавлен в избранное"
// @Failure      400  {object}  MobileErrorResponse     "error_code 1015; error_data[].code: 20470 — store_code не передан, 20471 — магазин не найден или закрыт"
// @Failure      401  {object}  MobileErrorResponse     "Сессия истекла (error_code 1002)"
// @Failure      500  {object}  MobileErrorResponse     "Непредвиденная ошибка"
//
// @Router       /api/v1/favourite-stores [post]
func (s *favouriteStoreService) AddFavouriteStore(c *fiber.Ctx) error {
	siteApiUrl := fmt.Sprintf("%s/%s", s.service.cfg.Site.BaseInternalUrl, s.service.cfg.Site.FavouriteStoresPath)

	return helpers.ProxyToSite(s.service.logger, c, s.service.cfg, s.service.restyClient, siteApiUrl, resty.MethodPost, nil, false)
}

// DeleteFavouriteStore godoc
//
// @Summary      Удаление магазина из избранного
// @Description  Proxy to DELETE /mobile/favourite-stores/{store_code}
// @Description  Снимает отметку «избранный». Если магазина нет в избранном пользователя — 404.
//
// @Tags         FavouriteStores
// @Accept       json
// @Produce      json
// @Security     Bearer
//
// @Param        X-Platform  header  string   true  "Платформа приложения"                                      Enums(android, ios)
// @Param        X-Version   header  string   true  "Версия приложения"                                         example(1.16.1)
// @Param        store_code  path    integer  true  "Код магазина — result[].store_code из списка избранных"  minimum(1) example(42)
//
// @Success      200  {object}  dto.EmptyResponse    "Магазин удалён из избранного"
// @Failure      400  {object}  dto.ErrorResponse    "Своя ошибка гейта: store_code в пути не число — {\"error\": {\"message\": ...}}"
// @Failure      401  {object}  MobileErrorResponse  "Сессия истекла (error_code 1002)"
// @Failure      404  {object}  MobileErrorResponse  "Магазина нет в избранном пользователя (error_code 1009 — Предложение, mobile.md, раздел 4.1, п. 4)"
// @Failure      500  {object}  MobileErrorResponse  "Непредвиденная ошибка"
//
// @Router       /api/v1/favourite-stores/{store_code} [delete]
func (s *favouriteStoreService) DeleteFavouriteStore(c *fiber.Ctx) error {
	path := fmt.Sprintf(s.service.cfg.Site.FavouriteStorePath, c.Params("store_code"))
	siteApiUrl := fmt.Sprintf("%s/%s", s.service.cfg.Site.BaseInternalUrl, path)

	return helpers.ProxyToSite(s.service.logger, c, s.service.cfg, s.service.restyClient, siteApiUrl, resty.MethodDelete, nil, false)
}
