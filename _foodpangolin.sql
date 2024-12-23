-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： localhost:8889
-- 產生時間： 2024 年 12 月 13 日 03:02
-- 伺服器版本： 8.0.35
-- PHP 版本： 8.2.20

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `	foodpangolin`
--

-- --------------------------------------------------------

--
-- 資料表結構 `customer_details`
--

CREATE TABLE `customer_details` (
  `customer_id` int NOT NULL,
  `password` varchar(100) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `address` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `customer_details`
--

INSERT INTO `customer_details` (`customer_id`, `password`, `full_name`, `address`) VALUES
(1, 'pass1234', '客戶A', '台北市大安路10號'),
(2, 'pass5678', '客戶B', '新北市新店區中興路200號'),
(3, 'pass9101', '客戶C', '桃園市中壢區中央路50號');

-- --------------------------------------------------------

--
-- 資料表結構 `delivery_person_details`
--

CREATE TABLE `delivery_person_details` (
  `delivery_id` int NOT NULL,
  `password` varchar(100) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `vehicle_info` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `delivery_person_details`
--

INSERT INTO `delivery_person_details` (`delivery_id`, `password`, `full_name`, `vehicle_info`) VALUES
(1, 'pass987', '送貨員A', '摩托車123'),
(2, 'pass654', '送貨員B', '汽車ABC'),
(3, 'pass321', '送貨員C', '自行車XYZ');

-- --------------------------------------------------------

--
-- 資料表結構 `menu`
--

CREATE TABLE `menu` (
  `menu_id` int NOT NULL,
  `restaurant_id` int DEFAULT NULL,
  `item_name` varchar(100) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `availability` tinyint(1) DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `menu`
--

INSERT INTO `menu` (`menu_id`, `restaurant_id`, `item_name`, `price`, `availability`) VALUES
(1, 1, '炸雞', 150.00, 1),
(2, 1, '可樂', 50.00, 1),
(3, 2, '披薩', 300.00, 1),
(4, 2, '沙拉', 120.00, 1),
(5, 3, '壽司', 200.00, 1),
(6, 3, '味噌湯', 80.00, 1);

-- --------------------------------------------------------

--
-- 資料表結構 `orders`
--

CREATE TABLE `orders` (
  `order_id` int NOT NULL,
  `customer_id` int DEFAULT NULL,
  `restaurant_id` int DEFAULT NULL,
  `delivery_person_id` int DEFAULT NULL,
  `order_status` enum('pending','confirmed','delivering','completed') DEFAULT 'pending',
  `total_amount` decimal(10,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `orders`
--

INSERT INTO `orders` (`order_id`, `customer_id`, `restaurant_id`, `delivery_person_id`, `order_status`, `total_amount`, `created_at`) VALUES
(1, 1, 1, 1, 'completed', 600.00, '2024-12-11 14:11:14'),
(2, 2, 2, 2, 'completed', 420.00, '2024-12-11 14:11:14'),
(3, 3, 3, 3, 'completed', 280.00, '2024-12-11 14:11:14');

-- --------------------------------------------------------

--
-- 資料表結構 `order_details`
--

CREATE TABLE `order_details` (
  `detail_id` int NOT NULL,
  `order_id` int DEFAULT NULL,
  `menu_id` int DEFAULT NULL,
  `quantity` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `order_details`
--

INSERT INTO `order_details` (`detail_id`, `order_id`, `menu_id`, `quantity`) VALUES
(1, 1, 1, 2),
(2, 1, 3, 1),
(3, 2, 4, 1),
(4, 2, 3, 1),
(5, 3, 5, 1),
(6, 3, 6, 1);

-- --------------------------------------------------------

--
-- 資料表結構 `platform_details`
--

CREATE TABLE `platform_details` (
  `platform_id` int NOT NULL,
  `password` varchar(100) NOT NULL,
  `platform_name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `platform_details`
--

INSERT INTO `platform_details` (`platform_id`, `password`, `platform_name`) VALUES
(1, 'platformPass', '平台系統');

-- --------------------------------------------------------

--
-- 資料表結構 `restaurant_details`
--

CREATE TABLE `restaurant_details` (
  `restaurant_id` int NOT NULL,
  `password` varchar(100) NOT NULL,
  `restaurant_name` varchar(100) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `contact_number` varchar(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `restaurant_details`
--

INSERT INTO `restaurant_details` (`restaurant_id`, `password`, `restaurant_name`, `address`, `contact_number`) VALUES
(1, 'pass123', '炸雞餐廳', '台北市信義路1號', '0912345678'),
(2, 'pass456', '披薩商家', '新北市永和區中正路100號', '0922345678'),
(3, 'pass789', '壽司店', '台中市南屯區五權西路200號', '0933345678');

-- --------------------------------------------------------

--
-- 資料表結構 `reviews`
--

CREATE TABLE `reviews` (
  `review_id` int NOT NULL,
  `order_id` int DEFAULT NULL,
  `customer_id` int DEFAULT NULL,
  `rating` int DEFAULT NULL,
  `comments` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ;

--
-- 傾印資料表的資料 `reviews`
--

INSERT INTO `reviews` (`review_id`, `order_id`, `customer_id`, `rating`, `comments`, `created_at`) VALUES
(1, 1, 1, 5, '炸雞很好吃，外送也很快！', '2024-12-11 14:11:14'),
(2, 2, 2, 4, '披薩不錯，但沙拉味道一般。', '2024-12-11 14:11:14'),
(3, 3, 3, 3, '壽司新鮮，但味噌湯偏鹹。', '2024-12-11 14:11:14');

-- --------------------------------------------------------

--
-- 資料表結構 `settlements`
--

CREATE TABLE `settlements` (
  `settlement_id` int NOT NULL,
  `order_id` int DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `user_id` int DEFAULT NULL,
  `settled_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `settlements`
--

INSERT INTO `settlements` (`settlement_id`, `order_id`, `amount`, `user_id`, `settled_at`) VALUES
(1, 1, 600.00, 1, '2024-12-11 14:26:33'),
(2, 1, 600.00, 4, '2024-12-11 14:26:33'),
(3, 1, 600.00, 10, '2024-12-11 14:26:33'),
(4, 2, 420.00, 2, '2024-12-11 14:26:33'),
(5, 2, 420.00, 5, '2024-12-11 14:26:33'),
(6, 2, 420.00, 10, '2024-12-11 14:26:33'),
(7, 3, 280.00, 3, '2024-12-11 14:26:33'),
(8, 3, 280.00, 6, '2024-12-11 14:26:33'),
(9, 3, 280.00, 10, '2024-12-11 14:26:33');

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `user_id` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `role` int NOT NULL,
  `role_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `users`
--

INSERT INTO `users` (`user_id`, `username`, `role`, `role_id`, `created_at`) VALUES
(1, '炸雞餐廳', 1, 1, '2024-12-11 14:11:14'),
(2, '披薩商家', 1, 2, '2024-12-11 14:11:14'),
(3, '壽司店', 1, 3, '2024-12-11 14:11:14'),
(4, '送貨員A', 2, 1, '2024-12-11 14:11:14'),
(5, '送貨員B', 2, 2, '2024-12-11 14:11:14'),
(6, '送貨員C', 2, 3, '2024-12-11 14:11:14'),
(7, '客戶A', 3, 1, '2024-12-11 14:11:14'),
(8, '客戶B', 3, 2, '2024-12-11 14:11:14'),
(9, '客戶C', 3, 3, '2024-12-11 14:11:14'),
(10, '平台系統', 4, 1, '2024-12-11 14:11:14');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `customer_details`
--
ALTER TABLE `customer_details`
  ADD PRIMARY KEY (`customer_id`);

--
-- 資料表索引 `delivery_person_details`
--
ALTER TABLE `delivery_person_details`
  ADD PRIMARY KEY (`delivery_id`);

--
-- 資料表索引 `menu`
--
ALTER TABLE `menu`
  ADD PRIMARY KEY (`menu_id`),
  ADD KEY `restaurant_id` (`restaurant_id`);

--
-- 資料表索引 `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `restaurant_id` (`restaurant_id`),
  ADD KEY `delivery_person_id` (`delivery_person_id`);

--
-- 資料表索引 `order_details`
--
ALTER TABLE `order_details`
  ADD PRIMARY KEY (`detail_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `menu_id` (`menu_id`);

--
-- 資料表索引 `platform_details`
--
ALTER TABLE `platform_details`
  ADD PRIMARY KEY (`platform_id`);

--
-- 資料表索引 `restaurant_details`
--
ALTER TABLE `restaurant_details`
  ADD PRIMARY KEY (`restaurant_id`);

--
-- 資料表索引 `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`review_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `customer_id` (`customer_id`);

--
-- 資料表索引 `settlements`
--
ALTER TABLE `settlements`
  ADD PRIMARY KEY (`settlement_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `customer_details`
--
ALTER TABLE `customer_details`
  MODIFY `customer_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `delivery_person_details`
--
ALTER TABLE `delivery_person_details`
  MODIFY `delivery_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `menu`
--
ALTER TABLE `menu`
  MODIFY `menu_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `order_details`
--
ALTER TABLE `order_details`
  MODIFY `detail_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `platform_details`
--
ALTER TABLE `platform_details`
  MODIFY `platform_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `restaurant_details`
--
ALTER TABLE `restaurant_details`
  MODIFY `restaurant_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `reviews`
--
ALTER TABLE `reviews`
  MODIFY `review_id` int NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `settlements`
--
ALTER TABLE `settlements`
  MODIFY `settlement_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `menu`
--
ALTER TABLE `menu`
  ADD CONSTRAINT `menu_ibfk_1` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurant_details` (`restaurant_id`);

--
-- 資料表的限制式 `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customer_details` (`customer_id`),
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurant_details` (`restaurant_id`),
  ADD CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`delivery_person_id`) REFERENCES `delivery_person_details` (`delivery_id`);

--
-- 資料表的限制式 `order_details`
--
ALTER TABLE `order_details`
  ADD CONSTRAINT `order_details_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  ADD CONSTRAINT `order_details_ibfk_2` FOREIGN KEY (`menu_id`) REFERENCES `menu` (`menu_id`);

--
-- 資料表的限制式 `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customer_details` (`customer_id`);

--
-- 資料表的限制式 `settlements`
--
ALTER TABLE `settlements`
  ADD CONSTRAINT `settlements_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  ADD CONSTRAINT `settlements_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
