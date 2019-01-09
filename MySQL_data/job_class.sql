-- phpMyAdmin SQL Dump
-- version 4.8.2
-- https://www.phpmyadmin.net/
--
-- 主機: 127.0.0.1
-- 產生時間： 2019-01-09 10:04:07
-- 伺服器版本: 10.1.34-MariaDB
-- PHP 版本： 7.2.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `job_recommendation`
--

-- --------------------------------------------------------

--
-- 資料表結構 `job_class`
--

CREATE TABLE `job_class` (
  `classNo` varchar(11) NOT NULL,
  `className` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 資料表的匯出資料 `job_class`
--

INSERT INTO `job_class` (`classNo`, `className`) VALUES
('1', '管理/行政/財經/法務'),
('2', '行銷/業務/服務'),
('3', '教育/媒體/傳播'),
('4', '軟硬體研發/製造/工程'),
('5', '其他專業 (農林漁牧/餐飲/醫學/軍警/物流/採購等...)');

--
-- 已匯出資料表的索引
--

--
-- 資料表索引 `job_class`
--
ALTER TABLE `job_class`
  ADD PRIMARY KEY (`classNo`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
