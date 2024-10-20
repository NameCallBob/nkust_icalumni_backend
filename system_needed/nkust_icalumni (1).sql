-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2024-10-20 21:08:07
-- 伺服器版本： 10.4.27-MariaDB
-- PHP 版本： 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `nkust_icalumni`
--
CREATE DATABASE IF NOT EXISTS `nkust_icalumni` DEFAULT CHARACTER SET utf32 COLLATE utf32_general_ci;
USE `nkust_icalumni`;

-- --------------------------------------------------------

--
-- 資料表結構 `article_article`
--

CREATE TABLE `article_article` (
  `id` bigint(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `content` longtext NOT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `publish_at` datetime(6) DEFAULT NULL,
  `expire_at` datetime(6) DEFAULT NULL,
  `view_count` int(10) UNSIGNED NOT NULL CHECK (`view_count` >= 0),
  `link` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `article_articleimage`
--

CREATE TABLE `article_articleimage` (
  `id` bigint(20) NOT NULL,
  `image` varchar(100) NOT NULL,
  `pic_type` varchar(5) NOT NULL,
  `article_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add blacklisted token', 6, 'add_blacklistedtoken'),
(22, 'Can change blacklisted token', 6, 'change_blacklistedtoken'),
(23, 'Can delete blacklisted token', 6, 'delete_blacklistedtoken'),
(24, 'Can view blacklisted token', 6, 'view_blacklistedtoken'),
(25, 'Can add outstanding token', 7, 'add_outstandingtoken'),
(26, 'Can change outstanding token', 7, 'change_outstandingtoken'),
(27, 'Can delete outstanding token', 7, 'delete_outstandingtoken'),
(28, 'Can view outstanding token', 7, 'view_outstandingtoken'),
(29, 'Can add private', 8, 'add_private'),
(30, 'Can change private', 8, 'change_private'),
(31, 'Can delete private', 8, 'delete_private'),
(32, 'Can view private', 8, 'view_private'),
(33, 'Can add password reset code', 9, 'add_passwordresetcode'),
(34, 'Can change password reset code', 9, 'change_passwordresetcode'),
(35, 'Can delete password reset code', 9, 'delete_passwordresetcode'),
(36, 'Can view password reset code', 9, 'view_passwordresetcode'),
(37, 'Can add graduate', 10, 'add_graduate'),
(38, 'Can change graduate', 10, 'change_graduate'),
(39, 'Can delete graduate', 10, 'delete_graduate'),
(40, 'Can view graduate', 10, 'view_graduate'),
(41, 'Can add position', 11, 'add_position'),
(42, 'Can change position', 11, 'change_position'),
(43, 'Can delete position', 11, 'delete_position'),
(44, 'Can view position', 11, 'view_position'),
(45, 'Can add member', 12, 'add_member'),
(46, 'Can change member', 12, 'change_member'),
(47, 'Can delete member', 12, 'delete_member'),
(48, 'Can view member', 12, 'view_member'),
(49, 'Can add 產業列', 13, 'add_industry'),
(50, 'Can change 產業列', 13, 'change_industry'),
(51, 'Can delete 產業列', 13, 'delete_industry'),
(52, 'Can view 產業列', 13, 'view_industry'),
(53, 'Can add 公司', 14, 'add_company'),
(54, 'Can change 公司', 14, 'change_company'),
(55, 'Can delete 公司', 14, 'delete_company'),
(56, 'Can view 公司', 14, 'view_company'),
(57, 'Can add 產品', 15, 'add_product'),
(58, 'Can change 產品', 15, 'change_product'),
(59, 'Can delete 產品', 15, 'delete_product'),
(60, 'Can view 產品', 15, 'view_product'),
(61, 'Can add article', 16, 'add_article'),
(62, 'Can change article', 16, 'change_article'),
(63, 'Can delete article', 16, 'delete_article'),
(64, 'Can view article', 16, 'view_article'),
(65, 'Can add article image', 17, 'add_articleimage'),
(66, 'Can change article image', 17, 'change_articleimage'),
(67, 'Can delete article image', 17, 'delete_articleimage'),
(68, 'Can view article image', 17, 'view_articleimage'),
(69, 'Can add slide image', 18, 'add_slideimage'),
(70, 'Can change slide image', 18, 'change_slideimage'),
(71, 'Can delete slide image', 18, 'delete_slideimage'),
(72, 'Can view slide image', 18, 'view_slideimage'),
(73, 'Can add company image', 19, 'add_companyimage'),
(74, 'Can change company image', 19, 'change_companyimage'),
(75, 'Can delete company image', 19, 'delete_companyimage'),
(76, 'Can view company image', 19, 'view_companyimage'),
(77, 'Can add product image', 20, 'add_productimage'),
(78, 'Can change product image', 20, 'change_productimage'),
(79, 'Can delete product image', 20, 'delete_productimage'),
(80, 'Can view product image', 20, 'view_productimage'),
(81, 'Can add self image', 21, 'add_selfimage'),
(82, 'Can change self image', 21, 'change_selfimage'),
(83, 'Can delete self image', 21, 'delete_selfimage'),
(84, 'Can view self image', 21, 'view_selfimage'),
(85, 'Can add recruit', 22, 'add_recruit'),
(86, 'Can change recruit', 22, 'change_recruit'),
(87, 'Can delete recruit', 22, 'delete_recruit'),
(88, 'Can view recruit', 22, 'view_recruit'),
(89, 'Can add contact', 23, 'add_contact'),
(90, 'Can change contact', 23, 'change_contact'),
(91, 'Can delete contact', 23, 'delete_contact'),
(92, 'Can view contact', 23, 'view_contact'),
(93, 'Can add recruit image', 24, 'add_recruitimage'),
(94, 'Can change recruit image', 24, 'change_recruitimage'),
(95, 'Can delete recruit image', 24, 'delete_recruitimage'),
(96, 'Can view recruit image', 24, 'view_recruitimage'),
(97, 'Can add notice', 25, 'add_notice'),
(98, 'Can change notice', 25, 'change_notice'),
(99, 'Can delete notice', 25, 'delete_notice'),
(100, 'Can view notice', 25, 'view_notice');

-- --------------------------------------------------------

--
-- 資料表結構 `company_company`
--

CREATE TABLE `company_company` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `positions` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `products` varchar(255) NOT NULL,
  `product_description` longtext NOT NULL,
  `photo` varchar(100) DEFAULT NULL,
  `website` varchar(500) NOT NULL,
  `address` longtext DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `clicks` bigint(20) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `member_id` bigint(20) NOT NULL,
  `industry_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `company_company`
--

INSERT INTO `company_company` (`id`, `name`, `positions`, `description`, `products`, `product_description`, `photo`, `website`, `address`, `email`, `clicks`, `phone_number`, `created_at`, `member_id`, `industry_id`) VALUES
(1, '國立高雄科技大學智慧商務系', '工讀生', '結合商業與科技領域的跨學科學系，旨在培養具備數位科技、商務管理及創新應用能力的專業人才。該系專注於智慧商務的理論與實務，包括電子商務、大數據分析、雲端運算、物聯網、行動商務等，並強調產學合作與實務經驗的累積，以提升學生的競爭力。學生畢業後可從事多種商務與科技相關工作，例如數位行銷、數據分析、系統管理及電子商務規劃等。該系亦積極培養學生的創新思維與跨領域協作能力，為智慧商務產業提供新一代專業人才。', '系統設計、行銷、電子商務', '暫無簡介', 'static/company/maxresdefault.jpg', 'https://ic.nkust.edu.tw/', '80778 高雄市三民區建工路415號', 'vhoffice01@nkust.edu.tw', 0, '07-3831332', '2024-10-19 19:26:11.573555', 1, 1);

-- --------------------------------------------------------

--
-- 資料表結構 `company_industry`
--

CREATE TABLE `company_industry` (
  `id` bigint(20) NOT NULL,
  `title` varchar(50) NOT NULL,
  `intro` longtext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `company_industry`
--

INSERT INTO `company_industry` (`id`, `title`, `intro`) VALUES
(1, '教育', '教育');

-- --------------------------------------------------------

--
-- 資料表結構 `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2024-10-19 18:44:26.086739', '1', '會長', 1, '[{\"added\": {}}]', 11, 2),
(2, '2024-10-19 18:44:35.056370', '2', '理事', 1, '[{\"added\": {}}]', 11, 2),
(3, '2024-10-19 18:44:45.010678', '3', '管理員', 1, '[{\"added\": {}}]', 11, 2),
(4, '2024-10-19 18:44:57.252931', '1', '國立高雄科技大學智慧商務系 - 113', 1, '[{\"added\": {}}]', 10, 2),
(5, '2024-10-19 19:10:55.989696', '1', '楊兆彬 - 管理員', 1, '[{\"added\": {}}]', 12, 2),
(6, '2024-10-19 19:14:47.575350', '1', '楊兆彬 - 管理員', 2, '[]', 12, 2),
(7, '2024-10-19 19:15:33.532210', '2', '楊兆彬 - 管理員', 1, '[{\"added\": {}}]', 12, 2),
(8, '2024-10-19 19:16:08.411768', '3', '楊兆彬 - 管理員', 1, '[{\"added\": {}}]', 12, 2),
(9, '2024-10-19 19:16:37.771909', '4', '楊兆彬 - 管理員', 1, '[{\"added\": {}}]', 12, 2),
(10, '2024-10-19 19:19:24.417688', '1', 'kuasmis@gmail.com - 楊兆彬 - 管理員', 2, '[{\"changed\": {\"fields\": [\"Private\"]}}]', 12, 2),
(11, '2024-10-19 19:20:09.812035', '1', '教育', 1, '[{\"added\": {}}]', 13, 2),
(12, '2024-10-19 19:26:11.574559', '1', '國立高雄科技大學智慧商務系', 1, '[{\"added\": {}}]', 14, 2),
(13, '2024-10-20 05:53:26.676896', '1', 'Recruit object (1)', 1, '[{\"added\": {}}]', 22, 2),
(14, '2024-10-20 05:54:49.205626', '1', 'Small Image for 打掃工讀生多位', 1, '[{\"added\": {}}]', 24, 2),
(15, '2024-10-20 05:55:16.083205', '1', 'Contact object (1)', 1, '[{\"added\": {}}]', 23, 2),
(16, '2024-10-20 15:32:58.872464', '1', 'SelfImage object (1)', 1, '[{\"added\": {}}]', 21, 2),
(17, '2024-10-20 15:34:41.043710', '2', 'SelfImage object (2)', 1, '[{\"added\": {}}]', 21, 2),
(18, '2024-10-20 15:35:24.258862', '3', 'SelfImage object (3)', 1, '[{\"added\": {}}]', 21, 2),
(19, '2024-10-20 15:35:49.842162', '4', 'SelfImage object (4)', 1, '[{\"added\": {}}]', 21, 2),
(20, '2024-10-20 15:37:19.858608', '1', 'CompanyImage object (1)', 1, '[{\"added\": {}}]', 19, 2),
(21, '2024-10-20 15:39:39.517709', '2', 'CompanyImage object (2)', 1, '[{\"added\": {}}]', 19, 2),
(22, '2024-10-20 15:50:47.490713', '1', 'SlideImage object (1)', 1, '[{\"added\": {}}]', 18, 2),
(23, '2024-10-20 15:52:32.061256', '2', 'SlideImage object (2)', 1, '[{\"added\": {}}]', 18, 2);

-- --------------------------------------------------------

--
-- 資料表結構 `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(16, 'article', 'article'),
(17, 'article', 'articleimage'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(14, 'company', 'company'),
(13, 'company', 'industry'),
(4, 'contenttypes', 'contenttype'),
(10, 'member', 'graduate'),
(12, 'member', 'member'),
(11, 'member', 'position'),
(25, 'notice', 'notice'),
(19, 'picture', 'companyimage'),
(20, 'picture', 'productimage'),
(21, 'picture', 'selfimage'),
(18, 'picture', 'slideimage'),
(9, 'Private', 'passwordresetcode'),
(8, 'Private', 'private'),
(15, 'product', 'product'),
(23, 'recruit', 'contact'),
(22, 'recruit', 'recruit'),
(24, 'recruit', 'recruitimage'),
(5, 'sessions', 'session'),
(6, 'token_blacklist', 'blacklistedtoken'),
(7, 'token_blacklist', 'outstandingtoken');

-- --------------------------------------------------------

--
-- 資料表結構 `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2024-10-19 18:34:52.717016'),
(2, 'contenttypes', '0002_remove_content_type_name', '2024-10-19 18:34:52.742842'),
(3, 'auth', '0001_initial', '2024-10-19 18:34:52.839904'),
(4, 'auth', '0002_alter_permission_name_max_length', '2024-10-19 18:34:52.865079'),
(5, 'auth', '0003_alter_user_email_max_length', '2024-10-19 18:34:52.868735'),
(6, 'auth', '0004_alter_user_username_opts', '2024-10-19 18:34:52.872035'),
(7, 'auth', '0005_alter_user_last_login_null', '2024-10-19 18:34:52.875043'),
(8, 'auth', '0006_require_contenttypes_0002', '2024-10-19 18:34:52.876046'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2024-10-19 18:34:52.879587'),
(10, 'auth', '0008_alter_user_username_max_length', '2024-10-19 18:34:52.882906'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2024-10-19 18:34:52.885914'),
(12, 'auth', '0010_alter_group_name_max_length', '2024-10-19 18:34:52.892425'),
(13, 'auth', '0011_update_proxy_permissions', '2024-10-19 18:34:52.895433'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2024-10-19 18:34:52.898944'),
(15, 'Private', '0001_initial', '2024-10-19 18:34:53.060829'),
(16, 'admin', '0001_initial', '2024-10-19 18:34:53.111948'),
(17, 'admin', '0002_logentry_remove_auto_add', '2024-10-19 18:34:53.117283'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2024-10-19 18:34:53.121801'),
(19, 'article', '0001_initial', '2024-10-19 18:34:53.156166'),
(20, 'member', '0001_initial', '2024-10-19 18:34:53.214531'),
(21, 'company', '0001_initial', '2024-10-19 18:34:53.305170'),
(22, 'notice', '0001_initial', '2024-10-19 18:34:53.342160'),
(23, 'product', '0001_initial', '2024-10-19 18:34:53.373866'),
(24, 'picture', '0001_initial', '2024-10-19 18:34:53.461214'),
(25, 'recruit', '0001_initial', '2024-10-19 18:34:53.550908'),
(26, 'sessions', '0001_initial', '2024-10-19 18:34:53.569899'),
(27, 'token_blacklist', '0001_initial', '2024-10-19 18:34:53.640957'),
(28, 'token_blacklist', '0002_outstandingtoken_jti_hex', '2024-10-19 18:34:53.648742'),
(29, 'token_blacklist', '0003_auto_20171017_2007', '2024-10-19 18:34:53.661977'),
(30, 'token_blacklist', '0004_auto_20171017_2013', '2024-10-19 18:34:53.691909'),
(31, 'token_blacklist', '0005_remove_outstandingtoken_jti', '2024-10-19 18:34:53.700603'),
(32, 'token_blacklist', '0006_auto_20171017_2113', '2024-10-19 18:34:53.708496'),
(33, 'token_blacklist', '0007_auto_20171017_2214', '2024-10-19 18:34:55.190945'),
(34, 'token_blacklist', '0008_migrate_to_bigautofield', '2024-10-19 18:34:55.398470'),
(35, 'token_blacklist', '0010_fix_migrate_to_bigautofield', '2024-10-19 18:34:55.407465'),
(36, 'token_blacklist', '0011_linearizes_history', '2024-10-19 18:34:55.408948'),
(37, 'token_blacklist', '0012_alter_outstandingtoken_user', '2024-10-19 18:34:55.413698'),
(38, 'member', '0002_member_private', '2024-10-19 19:13:52.057715');

-- --------------------------------------------------------

--
-- 資料表結構 `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('c4xb8r2xu1ic0cakyzkozvn1dui8ewff', '.eJxVjMsOwiAQRf-FtSE8SgGX7v0GMsMMUjU0Ke3K-O_apAvd3nPOfYkE21rT1nlJE4mzMOL0uyHkB7cd0B3abZZ5busyodwVedAurzPx83K4fwcVev3WDGQdK3LFgiILrIyDCC5oREs0Fq-zKt6TG-I4GMzWow4YYoDsNJN4fwAEJTiJ:1t2EPq:rQBH1GJqCxLU2PAtpHKMuimGu-gtwR10Amcl4EMidu4', '2024-11-02 18:43:06.439417');

-- --------------------------------------------------------

--
-- 資料表結構 `member_graduate`
--

CREATE TABLE `member_graduate` (
  `id` bigint(20) NOT NULL,
  `school` longtext NOT NULL,
  `grade` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `member_graduate`
--

INSERT INTO `member_graduate` (`id`, `school`, `grade`) VALUES
(1, '國立高雄科技大學智慧商務系', '113');

-- --------------------------------------------------------

--
-- 資料表結構 `member_member`
--

CREATE TABLE `member_member` (
  `id` bigint(20) NOT NULL,
  `name` varchar(30) NOT NULL,
  `home_phone` varchar(15) DEFAULT NULL,
  `mobile_phone` varchar(15) DEFAULT NULL,
  `gender` varchar(1) NOT NULL,
  `address` longtext DEFAULT NULL,
  `is_paid` tinyint(1) NOT NULL,
  `intro` longtext DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `photo` varchar(100) DEFAULT NULL,
  `date_joined` date NOT NULL,
  `graduate_id` bigint(20) DEFAULT NULL,
  `position_id` bigint(20) DEFAULT NULL,
  `private_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `member_member`
--

INSERT INTO `member_member` (`id`, `name`, `home_phone`, `mobile_phone`, `gender`, `address`, `is_paid`, `intro`, `birth_date`, `photo`, `date_joined`, `graduate_id`, `position_id`, `private_id`) VALUES
(1, '楊兆彬', '0222856679', '0966683955', 'O', '新北市蘆洲區光明路50巷38號4樓', 1, 'django後端工程師', '2003-06-25', 'static/member/300.jpg', '2024-10-20', 1, 3, 2),
(2, '楊兆彬', '0222856679', '0966683955', 'O', '新北市', 1, '全端工程師', '2003-06-25', 'static/member/300_nb7sejW.jpg', '2024-10-20', 1, 3, 1),
(3, '楊兆彬', '0222856679', '0966683955', 'M', '蘆洲區', 1, '前端工程師', '2003-06-25', 'static/member/300_DlOdmQW.jpg', '2024-10-20', 1, 3, 4),
(4, '楊兆彬', '0222856679', '0966683955', 'F', '光明路', 1, '哈摟', '2003-06-25', 'static/member/300_gwlxWOe.jpg', '2024-10-20', 1, 3, 5);

-- --------------------------------------------------------

--
-- 資料表結構 `member_position`
--

CREATE TABLE `member_position` (
  `id` bigint(20) NOT NULL,
  `title` longtext NOT NULL,
  `priority` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `member_position`
--

INSERT INTO `member_position` (`id`, `title`, `priority`) VALUES
(1, '會長', 1),
(2, '理事', 3),
(3, '管理員', 100);

-- --------------------------------------------------------

--
-- 資料表結構 `notice_notice`
--

CREATE TABLE `notice_notice` (
  `id` bigint(20) NOT NULL,
  `email_notifications` tinyint(1) NOT NULL,
  `sms_notifications` tinyint(1) NOT NULL,
  `news_notifications` tinyint(1) NOT NULL,
  `promo_notifications` tinyint(1) NOT NULL,
  `member_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `picture_companyimage`
--

CREATE TABLE `picture_companyimage` (
  `id` bigint(20) NOT NULL,
  `image` varchar(100) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` longtext DEFAULT NULL,
  `priority` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `company_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `picture_companyimage`
--

INSERT INTO `picture_companyimage` (`id`, `image`, `title`, `description`, `priority`, `active`, `created_at`, `company_id`) VALUES
(1, 'static/company_image/hq720.jpg', '歡迎', 'QRCode掃描了解更多', 0, 1, '2024-10-20 15:37:19.857605', 1),
(2, 'static/company_image/mqdefault.jpg', '宣傳', '空拍', 1, 1, '2024-10-20 15:39:39.517709', 1);

-- --------------------------------------------------------

--
-- 資料表結構 `picture_productimage`
--

CREATE TABLE `picture_productimage` (
  `id` bigint(20) NOT NULL,
  `image` varchar(100) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` longtext DEFAULT NULL,
  `priority` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `product_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `picture_selfimage`
--

CREATE TABLE `picture_selfimage` (
  `id` bigint(20) NOT NULL,
  `image` varchar(100) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` longtext DEFAULT NULL,
  `priority` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `member_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `picture_selfimage`
--

INSERT INTO `picture_selfimage` (`id`, `image`, `title`, `description`, `priority`, `active`, `created_at`, `updated_at`, `member_id`) VALUES
(1, 'static/self_image/blink-5.png', '程式碼_1', '很多程式碼', 0, 1, '2024-10-20 15:32:58.866943', '2024-10-20 15:32:58.866943', 2),
(2, 'static/self_image/helloworld12.png', '程式碼_2', '很多程式碼', 1, 1, '2024-10-20 15:34:41.042707', '2024-10-20 15:34:41.042707', 2),
(3, 'static/self_image/codecompletion.png', '程式碼_1', '很多程式碼', 1, 1, '2024-10-20 15:35:24.257859', '2024-10-20 15:35:24.257859', 1),
(4, 'static/self_image/20107810x9r5Y7NoPW.png', '程式碼_3', '很多城市馬', 1, 1, '2024-10-20 15:35:49.840696', '2024-10-20 15:35:49.840696', 1);

-- --------------------------------------------------------

--
-- 資料表結構 `picture_slideimage`
--

CREATE TABLE `picture_slideimage` (
  `id` bigint(20) NOT NULL,
  `type` longtext NOT NULL,
  `image` varchar(100) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` longtext DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `picture_slideimage`
--

INSERT INTO `picture_slideimage` (`id`, `type`, `image`, `title`, `description`, `active`, `created_at`) VALUES
(1, 'None', 'static/slide/326431594_911615443529376_4304352214119373700_n.jpg', '智慧商務系友會 交接大會', NULL, 1, '2024-10-20 15:50:47.489712'),
(2, 'None', 'static/slide/411367604_755973239902103_7787603375567019156_n.jpg', '智慧商務系聯誼會交接大會', NULL, 1, '2024-10-20 15:52:32.060128');

-- --------------------------------------------------------

--
-- 資料表結構 `private_passwordresetcode`
--

CREATE TABLE `private_passwordresetcode` (
  `id` bigint(20) NOT NULL,
  `code` varchar(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `expires_at` datetime(6) NOT NULL,
  `private_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `private_private`
--

CREATE TABLE `private_private` (
  `id` int(11) NOT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `private_private`
--

INSERT INTO `private_private` (`id`, `email`, `password`, `is_active`, `is_staff`, `is_superuser`, `last_login`, `date_joined`) VALUES
(1, 'c110156220@nkust.edu.tw', 'pbkdf2_sha256$720000$Ou7mYdXPiLnMZvriIfaBwl$4moZ3Kqr2Luk0pX0pMDgaK2fLoWwP0MWycelkcxYAVA=', 1, 1, 1, '2024-10-19 18:38:59.742165', '2024-10-19 18:38:59.742165'),
(2, 'kuasmis@gmail.com', 'pbkdf2_sha256$720000$TpnhuhAwjweA53TJoNTfjz$cSvgwOrYqZWZAdpFuXJPbih4b1odXw+R9UbHmbI1I0o=', 1, 1, 1, '2024-10-19 18:43:06.439417', '2024-10-19 18:39:22.735727'),
(3, 'robin92062574@gmail.com', 'pbkdf2_sha256$720000$YinWnNewHYTBdm86mdwOa2$Mor01AMCZMbCleJHryhKIKdTuj8VMvGYrr3O9ShrIfM=', 1, 1, 1, '2024-10-19 18:41:40.107920', '2024-10-19 18:41:40.107920'),
(4, 'robin92062544@gmail.com', 'pbkdf2_sha256$720000$FQykFgz7dUkNFXXlaOvFr9$tIDvv2Mngi/QajPuIsZzMSr5x9jaMiKyOQe15yxKp9Q=', 1, 1, 1, '2024-10-19 18:41:51.589571', '2024-10-19 18:41:51.589571'),
(5, 'robin92062522@gmail.com', 'pbkdf2_sha256$720000$AfLyeDgwkHggKTdidfNKX4$tQ56oVv5xFjHFNU68CYCk4f8fmGx3++aNkH1HKwkOng=', 1, 1, 1, '2024-10-19 18:42:05.043080', '2024-10-19 18:42:05.043080');

-- --------------------------------------------------------

--
-- 資料表結構 `private_private_groups`
--

CREATE TABLE `private_private_groups` (
  `id` bigint(20) NOT NULL,
  `private_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `private_private_user_permissions`
--

CREATE TABLE `private_private_user_permissions` (
  `id` bigint(20) NOT NULL,
  `private_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `product_product`
--

CREATE TABLE `product_product` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `photo` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `company_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `recruit_contact`
--

CREATE TABLE `recruit_contact` (
  `id` bigint(20) NOT NULL,
  `name` longtext NOT NULL,
  `phone` longtext NOT NULL,
  `email` varchar(254) NOT NULL,
  `recruit_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `recruit_contact`
--

INSERT INTO `recruit_contact` (`id`, `name`, `phone`, `email`, `recruit_id`) VALUES
(1, '楊兆彬', '0966683955', 'c110156220@nkust.edu.tw', 1);

-- --------------------------------------------------------

--
-- 資料表結構 `recruit_recruit`
--

CREATE TABLE `recruit_recruit` (
  `id` bigint(20) NOT NULL,
  `title` varchar(50) NOT NULL,
  `intro` longtext NOT NULL,
  `info_clicks` int(11) NOT NULL,
  `deadline` date NOT NULL,
  `release_date` date NOT NULL,
  `active` tinyint(1) NOT NULL,
  `company_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `recruit_recruit`
--

INSERT INTO `recruit_recruit` (`id`, `title`, `intro`, `info_clicks`, `deadline`, `release_date`, `active`, `company_id`) VALUES
(1, '打掃工讀生多位', '<p>協助維持環境乾淨</p>', 0, '2024-12-25', '2024-10-20', 1, 1);

-- --------------------------------------------------------

--
-- 資料表結構 `recruit_recruitimage`
--

CREATE TABLE `recruit_recruitimage` (
  `id` bigint(20) NOT NULL,
  `image` varchar(100) NOT NULL,
  `image_type` varchar(5) NOT NULL,
  `recruit_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `recruit_recruitimage`
--

INSERT INTO `recruit_recruitimage` (`id`, `image`, `image_type`, `recruit_id`) VALUES
(1, 'static/recruit/images.jpg', 'small', 1);

-- --------------------------------------------------------

--
-- 資料表結構 `token_blacklist_blacklistedtoken`
--

CREATE TABLE `token_blacklist_blacklistedtoken` (
  `id` bigint(20) NOT NULL,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `token_blacklist_outstandingtoken`
--

CREATE TABLE `token_blacklist_outstandingtoken` (
  `id` bigint(20) NOT NULL,
  `token` longtext NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `jti` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `token_blacklist_outstandingtoken`
--

INSERT INTO `token_blacklist_outstandingtoken` (`id`, `token`, `created_at`, `expires_at`, `user_id`, `jti`) VALUES
(1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyOTUzNzUxMSwiaWF0IjoxNzI5NDUxMTExLCJqdGkiOiJkMmI1NTBlZWE4MjM0ZWIzOTcwOTM3NDQ0ZDc2OTFlMyIsInVzZXJfaWQiOjF9.cirlGG1M4e1P0zPvNiQ5JHYpR3Lj2zqlVl_9joyPxWA', '2024-10-20 19:05:11.605779', '2024-10-21 19:05:11.000000', 1, 'd2b550eea8234eb3970937444d7691e3');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `article_article`
--
ALTER TABLE `article_article`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `article_articleimage`
--
ALTER TABLE `article_articleimage`
  ADD PRIMARY KEY (`id`),
  ADD KEY `article_articleimage_article_id_204d0ae3_fk_article_article_id` (`article_id`);

--
-- 資料表索引 `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- 資料表索引 `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- 資料表索引 `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- 資料表索引 `company_company`
--
ALTER TABLE `company_company`
  ADD PRIMARY KEY (`id`),
  ADD KEY `company_company_member_id_26702064_fk_member_member_id` (`member_id`),
  ADD KEY `company_company_industry_id_8997df25_fk_company_industry_id` (`industry_id`);

--
-- 資料表索引 `company_industry`
--
ALTER TABLE `company_industry`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_Private_private_id` (`user_id`);

--
-- 資料表索引 `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- 資料表索引 `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- 資料表索引 `member_graduate`
--
ALTER TABLE `member_graduate`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `member_member`
--
ALTER TABLE `member_member`
  ADD PRIMARY KEY (`id`),
  ADD KEY `member_member_graduate_id_8879cb6d_fk_member_graduate_id` (`graduate_id`),
  ADD KEY `member_member_position_id_4ed12437_fk_member_position_id` (`position_id`),
  ADD KEY `member_member_private_id_8d31c101_fk_Private_private_id` (`private_id`);

--
-- 資料表索引 `member_position`
--
ALTER TABLE `member_position`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `notice_notice`
--
ALTER TABLE `notice_notice`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `member_id` (`member_id`);

--
-- 資料表索引 `picture_companyimage`
--
ALTER TABLE `picture_companyimage`
  ADD PRIMARY KEY (`id`),
  ADD KEY `picture_companyimage_company_id_7e75f98b_fk_company_company_id` (`company_id`);

--
-- 資料表索引 `picture_productimage`
--
ALTER TABLE `picture_productimage`
  ADD PRIMARY KEY (`id`),
  ADD KEY `picture_productimage_product_id_2592fe49_fk_product_product_id` (`product_id`);

--
-- 資料表索引 `picture_selfimage`
--
ALTER TABLE `picture_selfimage`
  ADD PRIMARY KEY (`id`),
  ADD KEY `picture_selfimage_member_id_acf4db57_fk_member_member_id` (`member_id`);

--
-- 資料表索引 `picture_slideimage`
--
ALTER TABLE `picture_slideimage`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `private_passwordresetcode`
--
ALTER TABLE `private_passwordresetcode`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`),
  ADD KEY `Private_passwordrese_private_id_0791519e_fk_Private_p` (`private_id`);

--
-- 資料表索引 `private_private`
--
ALTER TABLE `private_private`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- 資料表索引 `private_private_groups`
--
ALTER TABLE `private_private_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `Private_private_groups_private_id_group_id_160157bc_uniq` (`private_id`,`group_id`),
  ADD KEY `Private_private_groups_group_id_7f98ab6c_fk_auth_group_id` (`group_id`);

--
-- 資料表索引 `private_private_user_permissions`
--
ALTER TABLE `private_private_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `Private_private_user_per_private_id_permission_id_6207e7b6_uniq` (`private_id`,`permission_id`),
  ADD KEY `Private_private_user_permission_id_a31c1ba0_fk_auth_perm` (`permission_id`);

--
-- 資料表索引 `product_product`
--
ALTER TABLE `product_product`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_product_company_id_0965fde9_fk_company_company_id` (`company_id`);

--
-- 資料表索引 `recruit_contact`
--
ALTER TABLE `recruit_contact`
  ADD PRIMARY KEY (`id`),
  ADD KEY `recruit_contact_recruit_id_6e062e99_fk_recruit_recruit_id` (`recruit_id`);

--
-- 資料表索引 `recruit_recruit`
--
ALTER TABLE `recruit_recruit`
  ADD PRIMARY KEY (`id`),
  ADD KEY `recruit_recruit_company_id_dd385a61_fk_company_company_id` (`company_id`);

--
-- 資料表索引 `recruit_recruitimage`
--
ALTER TABLE `recruit_recruitimage`
  ADD PRIMARY KEY (`id`),
  ADD KEY `recruit_recruitimage_recruit_id_5e079e6e_fk_recruit_recruit_id` (`recruit_id`);

--
-- 資料表索引 `token_blacklist_blacklistedtoken`
--
ALTER TABLE `token_blacklist_blacklistedtoken`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token_id` (`token_id`);

--
-- 資料表索引 `token_blacklist_outstandingtoken`
--
ALTER TABLE `token_blacklist_outstandingtoken`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq` (`jti`),
  ADD KEY `token_blacklist_outs_user_id_83bc629a_fk_Private_p` (`user_id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `article_article`
--
ALTER TABLE `article_article`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `article_articleimage`
--
ALTER TABLE `article_articleimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=101;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `company_company`
--
ALTER TABLE `company_company`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `company_industry`
--
ALTER TABLE `company_industry`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `member_graduate`
--
ALTER TABLE `member_graduate`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `member_member`
--
ALTER TABLE `member_member`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `member_position`
--
ALTER TABLE `member_position`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `notice_notice`
--
ALTER TABLE `notice_notice`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `picture_companyimage`
--
ALTER TABLE `picture_companyimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `picture_productimage`
--
ALTER TABLE `picture_productimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `picture_selfimage`
--
ALTER TABLE `picture_selfimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `picture_slideimage`
--
ALTER TABLE `picture_slideimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `private_passwordresetcode`
--
ALTER TABLE `private_passwordresetcode`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `private_private`
--
ALTER TABLE `private_private`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `private_private_groups`
--
ALTER TABLE `private_private_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `private_private_user_permissions`
--
ALTER TABLE `private_private_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `product_product`
--
ALTER TABLE `product_product`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `recruit_contact`
--
ALTER TABLE `recruit_contact`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `recruit_recruit`
--
ALTER TABLE `recruit_recruit`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `recruit_recruitimage`
--
ALTER TABLE `recruit_recruitimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `token_blacklist_blacklistedtoken`
--
ALTER TABLE `token_blacklist_blacklistedtoken`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `token_blacklist_outstandingtoken`
--
ALTER TABLE `token_blacklist_outstandingtoken`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `article_articleimage`
--
ALTER TABLE `article_articleimage`
  ADD CONSTRAINT `article_articleimage_article_id_204d0ae3_fk_article_article_id` FOREIGN KEY (`article_id`) REFERENCES `article_article` (`id`);

--
-- 資料表的限制式 `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- 資料表的限制式 `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- 資料表的限制式 `company_company`
--
ALTER TABLE `company_company`
  ADD CONSTRAINT `company_company_industry_id_8997df25_fk_company_industry_id` FOREIGN KEY (`industry_id`) REFERENCES `company_industry` (`id`),
  ADD CONSTRAINT `company_company_member_id_26702064_fk_member_member_id` FOREIGN KEY (`member_id`) REFERENCES `member_member` (`id`);

--
-- 資料表的限制式 `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_Private_private_id` FOREIGN KEY (`user_id`) REFERENCES `private_private` (`id`);

--
-- 資料表的限制式 `member_member`
--
ALTER TABLE `member_member`
  ADD CONSTRAINT `member_member_graduate_id_8879cb6d_fk_member_graduate_id` FOREIGN KEY (`graduate_id`) REFERENCES `member_graduate` (`id`),
  ADD CONSTRAINT `member_member_position_id_4ed12437_fk_member_position_id` FOREIGN KEY (`position_id`) REFERENCES `member_position` (`id`),
  ADD CONSTRAINT `member_member_private_id_8d31c101_fk_Private_private_id` FOREIGN KEY (`private_id`) REFERENCES `private_private` (`id`);

--
-- 資料表的限制式 `notice_notice`
--
ALTER TABLE `notice_notice`
  ADD CONSTRAINT `notice_notice_member_id_49c339d8_fk_member_member_id` FOREIGN KEY (`member_id`) REFERENCES `member_member` (`id`);

--
-- 資料表的限制式 `picture_companyimage`
--
ALTER TABLE `picture_companyimage`
  ADD CONSTRAINT `picture_companyimage_company_id_7e75f98b_fk_company_company_id` FOREIGN KEY (`company_id`) REFERENCES `company_company` (`id`);

--
-- 資料表的限制式 `picture_productimage`
--
ALTER TABLE `picture_productimage`
  ADD CONSTRAINT `picture_productimage_product_id_2592fe49_fk_product_product_id` FOREIGN KEY (`product_id`) REFERENCES `product_product` (`id`);

--
-- 資料表的限制式 `picture_selfimage`
--
ALTER TABLE `picture_selfimage`
  ADD CONSTRAINT `picture_selfimage_member_id_acf4db57_fk_member_member_id` FOREIGN KEY (`member_id`) REFERENCES `member_member` (`id`);

--
-- 資料表的限制式 `private_passwordresetcode`
--
ALTER TABLE `private_passwordresetcode`
  ADD CONSTRAINT `Private_passwordrese_private_id_0791519e_fk_Private_p` FOREIGN KEY (`private_id`) REFERENCES `private_private` (`id`);

--
-- 資料表的限制式 `private_private_groups`
--
ALTER TABLE `private_private_groups`
  ADD CONSTRAINT `Private_private_groups_group_id_7f98ab6c_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `Private_private_groups_private_id_310a79fd_fk_Private_private_id` FOREIGN KEY (`private_id`) REFERENCES `private_private` (`id`);

--
-- 資料表的限制式 `private_private_user_permissions`
--
ALTER TABLE `private_private_user_permissions`
  ADD CONSTRAINT `Private_private_user_permission_id_a31c1ba0_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `Private_private_user_private_id_3ed71c46_fk_Private_p` FOREIGN KEY (`private_id`) REFERENCES `private_private` (`id`);

--
-- 資料表的限制式 `product_product`
--
ALTER TABLE `product_product`
  ADD CONSTRAINT `product_product_company_id_0965fde9_fk_company_company_id` FOREIGN KEY (`company_id`) REFERENCES `company_company` (`id`);

--
-- 資料表的限制式 `recruit_contact`
--
ALTER TABLE `recruit_contact`
  ADD CONSTRAINT `recruit_contact_recruit_id_6e062e99_fk_recruit_recruit_id` FOREIGN KEY (`recruit_id`) REFERENCES `recruit_recruit` (`id`);

--
-- 資料表的限制式 `recruit_recruit`
--
ALTER TABLE `recruit_recruit`
  ADD CONSTRAINT `recruit_recruit_company_id_dd385a61_fk_company_company_id` FOREIGN KEY (`company_id`) REFERENCES `company_company` (`id`);

--
-- 資料表的限制式 `recruit_recruitimage`
--
ALTER TABLE `recruit_recruitimage`
  ADD CONSTRAINT `recruit_recruitimage_recruit_id_5e079e6e_fk_recruit_recruit_id` FOREIGN KEY (`recruit_id`) REFERENCES `recruit_recruit` (`id`);

--
-- 資料表的限制式 `token_blacklist_blacklistedtoken`
--
ALTER TABLE `token_blacklist_blacklistedtoken`
  ADD CONSTRAINT `token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`);

--
-- 資料表的限制式 `token_blacklist_outstandingtoken`
--
ALTER TABLE `token_blacklist_outstandingtoken`
  ADD CONSTRAINT `token_blacklist_outs_user_id_83bc629a_fk_Private_p` FOREIGN KEY (`user_id`) REFERENCES `private_private` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
