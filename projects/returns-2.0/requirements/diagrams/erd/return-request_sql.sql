-- ERD-RET: модель данных заявки на возврат
-- СУБД: MariaDB 10.3 (схема монолита). Описание полей — return-request_erd.md
-- Существующие таблицы (cms_orders, cms_order_positions, cms_users_user, cms_return_method,
-- cms_return_reasons_groups, cms_return_reasons) не меняются.

-- Справочники

CREATE TABLE cms_return_status_groups (
    id            INT(11)      NOT NULL AUTO_INCREMENT,
    code          VARCHAR(32)  NOT NULL,
    client_title  VARCHAR(255) NOT NULL,
    icon_type     VARCHAR(16)  NOT NULL,
    _order        INT(11)      NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_return_status_groups_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE cms_return_statuses (
    id                     INT(11)      NOT NULL AUTO_INCREMENT,
    code                   VARCHAR(32)  NOT NULL,
    title                  VARCHAR(255) NOT NULL,
    group_id               INT(11)      NOT NULL,
    is_client_cancellable  TINYINT(1)   NOT NULL DEFAULT 0,
    _order                 INT(11)      NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_return_statuses_code (code),
    KEY idx_return_statuses_group (group_id),
    CONSTRAINT fk_return_statuses_group FOREIGN KEY (group_id) REFERENCES cms_return_status_groups (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE cms_return_position_statuses (
    id     INT(11)      NOT NULL AUTO_INCREMENT,
    code   VARCHAR(32)  NOT NULL,
    title  VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_return_position_statuses_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE cms_refund_methods (
    id                     INT(11)      NOT NULL AUTO_INCREMENT,
    code                   VARCHAR(32)  NOT NULL,
    title                  VARCHAR(255) NOT NULL,
    requires_bank_details  TINYINT(1)   NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_refund_methods_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Заявка на возврат

CREATE TABLE cms_returns (
    id                     INT(11)              NOT NULL AUTO_INCREMENT,
    number                 VARCHAR(32)          NOT NULL,
    order_id               INT(11)              NOT NULL,
    user_id                INT(11)              NOT NULL,
    status_id              INT(11)              NOT NULL,
    channel                VARCHAR(16)          NOT NULL,
    return_method_id       INT(11)              NOT NULL,
    refund_method_id       INT(11)              NOT NULL,
    return_country_iso     VARCHAR(2)           NULL,
    return_city            VARCHAR(255)         NULL,
    return_city_fias       VARCHAR(255)         NULL,
    point_provider         VARCHAR(255)         NULL,
    point_id               VARCHAR(32)          NULL,
    store_code             SMALLINT(6) UNSIGNED NULL,
    point_name             VARCHAR(255)         NULL,
    point_address          VARCHAR(512)         NULL,
    point_schedule         TEXT                 NULL,
    point_lat              DECIMAL(10,7)        NULL,
    point_lng              DECIMAL(10,7)        NULL,
    pickup_postal          VARCHAR(255)         NULL,
    pickup_street          VARCHAR(255)         NULL,
    pickup_house           VARCHAR(255)         NULL,
    pickup_housing         VARCHAR(255)         NULL,
    pickup_flat            VARCHAR(255)         NULL,
    pickup_address_manual  TINYINT(1)           NOT NULL DEFAULT 0,
    courier_date           DATE                 NULL,
    courier_time_from      VARCHAR(5)           NULL,
    courier_time_to        VARCHAR(5)           NULL,
    courier_interval_code  VARCHAR(255)         NULL,
    timezone               VARCHAR(64)          NULL,
    return_until_date      DATE                 NULL,
    support_comment        TEXT                 NULL,
    version                INT(10) UNSIGNED     NOT NULL DEFAULT 1,
    onec_id                VARCHAR(64)          NULL,
    rcrm_id                VARCHAR(64)          NULL,
    created_at             DATETIME             NOT NULL,
    updated_at             DATETIME             NOT NULL,
    received_at            DATETIME             NULL,
    completed_at           DATETIME             NULL,
    cancelled_at           DATETIME             NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_returns_number (number),
    KEY idx_returns_order (order_id),
    KEY idx_returns_user_created (user_id, created_at),
    KEY idx_returns_status (status_id),
    KEY idx_returns_onec (onec_id),
    KEY idx_returns_rcrm (rcrm_id),
    CONSTRAINT fk_returns_order FOREIGN KEY (order_id) REFERENCES cms_orders (id) ON DELETE RESTRICT,
    CONSTRAINT fk_returns_user FOREIGN KEY (user_id) REFERENCES cms_users_user (id),
    CONSTRAINT fk_returns_status FOREIGN KEY (status_id) REFERENCES cms_return_statuses (id),
    CONSTRAINT fk_returns_return_method FOREIGN KEY (return_method_id) REFERENCES cms_return_method (id),
    CONSTRAINT fk_returns_refund_method FOREIGN KEY (refund_method_id) REFERENCES cms_refund_methods (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE cms_return_positions (
    id                        INT(11)       NOT NULL AUTO_INCREMENT,
    return_id                 INT(11)       NOT NULL,
    order_position_id         INT(11)       NOT NULL,
    status_id                 INT(11)       NULL,
    reason_group_id           INT(11)       NOT NULL,
    reason_id                 INT(11)       NULL,
    previous_position_status  INT(2)        NOT NULL,
    refund_amount             DECIMAL(10,2) NULL, -- предложено, в ECOMDEV-2587 нет
    refund_bonus_amount       DECIMAL(10,2) NULL, -- предложено, в ECOMDEV-2587 нет
    created_at                DATETIME      NOT NULL,
    updated_at                DATETIME      NOT NULL,
    PRIMARY KEY (id),
    KEY idx_return_positions_return (return_id),
    KEY idx_return_positions_order_position (order_position_id),
    CONSTRAINT fk_return_positions_return FOREIGN KEY (return_id) REFERENCES cms_returns (id),
    CONSTRAINT fk_return_positions_order_position FOREIGN KEY (order_position_id) REFERENCES cms_order_positions (id) ON DELETE RESTRICT,
    CONSTRAINT fk_return_positions_status FOREIGN KEY (status_id) REFERENCES cms_return_position_statuses (id),
    CONSTRAINT fk_return_positions_reason_group FOREIGN KEY (reason_group_id) REFERENCES cms_return_reasons_groups (id),
    CONSTRAINT fk_return_positions_reason FOREIGN KEY (reason_id) REFERENCES cms_return_reasons (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE cms_return_bank_details (
    id                         INT(11)          NOT NULL AUTO_INCREMENT,
    return_id                  INT(11)          NOT NULL,
    version                    INT(10) UNSIGNED NOT NULL,
    payload_encrypted          TEXT             NOT NULL,
    is_bank_details_confirmed  TINYINT(1)       NOT NULL DEFAULT 0,
    created_at                 DATETIME         NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_return_bank_details_version (return_id, version),
    CONSTRAINT fk_return_bank_details_return FOREIGN KEY (return_id) REFERENCES cms_returns (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE cms_return_history (
    id          INT(11)          NOT NULL AUTO_INCREMENT,
    return_id   INT(11)          NOT NULL,
    version     INT(10) UNSIGNED NOT NULL,
    status_id   INT(11)          NOT NULL,
    source      VARCHAR(16)      NOT NULL,
    author_id   INT(11)          NULL,
    snapshot    LONGTEXT         NOT NULL CHECK (JSON_VALID(snapshot)),
    created_at  DATETIME         NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_return_history_version (return_id, version),
    KEY idx_return_history_status (status_id),
    CONSTRAINT fk_return_history_return FOREIGN KEY (return_id) REFERENCES cms_returns (id),
    CONSTRAINT fk_return_history_status FOREIGN KEY (status_id) REFERENCES cms_return_statuses (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Начальные значения справочников

INSERT INTO cms_return_status_groups (code, client_title, icon_type, _order) VALUES
('pending',   'Возврат ожидает обработки', 'in_progress', 1),
('accepted',  'Заявка на возврат принята', 'in_progress', 2),
('received',  'Возврат принят',            'in_progress', 3),
('completed', 'Возврат завершен',          'done',        4),
('cancelled', 'Возврат отменен',           'cancelled',   5);

INSERT INTO cms_return_statuses (code, title, group_id, is_client_cancellable, _order) VALUES
('pending',      'Возврат ожидает обработки', (SELECT id FROM cms_return_status_groups WHERE code = 'pending'),   1, 1),
('accepted',     'Заявка на возврат принята', (SELECT id FROM cms_return_status_groups WHERE code = 'accepted'),  1, 2),
('confirmation', 'Подтверждение возврата',    (SELECT id FROM cms_return_status_groups WHERE code = 'accepted'),  1, 3),
('sent',         'Возврат отправлен',         (SELECT id FROM cms_return_status_groups WHERE code = 'accepted'),  1, 4),
('received',     'Возврат принят',            (SELECT id FROM cms_return_status_groups WHERE code = 'received'),  0, 5),
('completed',    'Возврат завершен',          (SELECT id FROM cms_return_status_groups WHERE code = 'completed'), 0, 6),
('cancelled',    'Возврат отменен',           (SELECT id FROM cms_return_status_groups WHERE code = 'cancelled'), 0, 7);

INSERT INTO cms_return_position_statuses (code, title) VALUES
('accepted',  'Принято'),
('cancelled', 'Отменено');

INSERT INTO cms_refund_methods (code, title, requires_bank_details) VALUES
('original_payment', 'Тем же способом, которым оплачен заказ', 0),
('bank_details',     'По банковским реквизитам',               1);
