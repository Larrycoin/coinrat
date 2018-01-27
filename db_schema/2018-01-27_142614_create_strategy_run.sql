CREATE TABLE `strategy_runs`
(
    `id` VARCHAR(36) PRIMARY KEY NOT NULL,
    `run_at` INT NOT NULL,
    `market_nme` VARCHAR(128) NOT NULL,
    `market_configuration` TEXT NOT NULL,
    `strategy_name` VARCHAR(128) NOT NULL,
    `strategy_configuration` TEXT NOT NULL,
    `interval_left` INT NOT NULL,
    `interval_right` INT,
    `candle_storage` VARCHAR(128) NOT NULL,
    `order_torage` VARCHAR(128) NOT NULL
);
