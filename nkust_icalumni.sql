-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2024-10-19 13:08:22
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

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

--
-- 傾印資料表的資料 `article_article`
--

INSERT INTO `article_article` (`id`, `title`, `content`, `active`, `created_at`, `publish_at`, `expire_at`, `view_count`, `link`) VALUES
(1, '高科大校友會教師節健行活動', '<p>￼所有老師們教師節快樂</p>', 1, '2024-10-06 19:02:37.035614', '2024-09-28 00:59:00.000000', '2024-10-30 18:59:00.000000', 1, 'https://www.facebook.com/nkustic?locale=zh_TW');

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

--
-- 傾印資料表的資料 `article_articleimage`
--

INSERT INTO `article_articleimage` (`id`, `image`, `pic_type`, `article_id`) VALUES
(2, 'static/article/460981117_505441102397413_4513285111100183927_n_Hn8DSte.jpg', 'small', 1),
(3, 'static/article/461497033_505441049064085_8210974127045321954_n.jpg', 'small', 1),
(4, 'static/article/461415733_505441075730749_4510248790991197002_n.jpg', 'small', 1),
(5, 'static/article/461295074_505441082397415_5927974448808684503_n.jpg', 'small', 1),
(6, 'static/article/461171229_505441129064077_3438465100273537116_n.jpg', 'small', 1),
(7, 'static/article/461191476_505441022397421_2376097113832818973_n.jpg', 'small', 1),
(8, 'static/article/461319454_505441059064084_2350791166938593657_n.jpg', 'small', 1),
(9, 'static/article/461161937_505441005730756_6019999216374866961_n.jpg', 'small', 1);

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
(49, 'Can add industry', 13, 'add_industry'),
(50, 'Can change industry', 13, 'change_industry'),
(51, 'Can delete industry', 13, 'delete_industry'),
(52, 'Can view industry', 13, 'view_industry'),
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
(89, 'Can add notice', 23, 'add_notice'),
(90, 'Can change notice', 23, 'change_notice'),
(91, 'Can delete notice', 23, 'delete_notice'),
(92, 'Can view notice', 23, 'view_notice'),
(93, 'Can add recruit image', 24, 'add_recruitimage'),
(94, 'Can change recruit image', 24, 'change_recruitimage'),
(95, 'Can delete recruit image', 24, 'delete_recruitimage'),
(96, 'Can view recruit image', 24, 'view_recruitimage');

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
  `phone_number` varchar(20) DEFAULT NULL,
  `member_id` bigint(20) NOT NULL,
  `industry_id` bigint(20) NOT NULL,
  `clicks` bigint(20) NOT NULL,
  `created_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `company_company`
--

INSERT INTO `company_company` (`id`, `name`, `positions`, `description`, `products`, `product_description`, `photo`, `website`, `address`, `email`, `phone_number`, `member_id`, `industry_id`, `clicks`, `created_at`) VALUES
(1, '彬彬炸雞店(虛擬)', '員工', '歡迎光臨【彬彬炸雞店(虛擬)】，這裡是喜愛炸物的饕客天堂！我們店內以現炸現做為宗旨，提供多樣化的餐點選擇，從經典的炸雞、薯條到創意的海鮮拼盤，每一道餐點都以新鮮食材製作，讓您品嚐到食材的原汁原味。\r\n\r\n【彬彬炸雞店(虛擬)】特別注重口味的搭配，我們精選多種秘製調味料，無論是香辣、胡椒還是蒜香口味，都能讓您每一口都充滿驚喜。店內環境舒適、明亮，適合三五好友聚餐或是忙碌一天後的放鬆享受。我們提供乾淨衛生的用餐空間，讓每位顧客都能在輕鬆的氛圍下享受美食。\r\n\r\n多位顧客給予我們高度好評，尤其是對於食材的新鮮度與炸物的酥脆口感讚不絕口。我們不僅追求美味，也重視每一位顧客的用餐體驗，期望讓大家在這裡找到專屬於自己的炸物幸福時刻。', '炸物', '酥脆炸雞翅、黃金薯條、香辣雞米花、脆皮花枝圈、炸蝦天婦羅、鹽酥雞、香酥雞腿排、起司玉米球、酥炸甜不辣、韓式辣炸雞。', 'static/company/_70b986cc-1d1c-4b4b-816d-fa09a005c7f8.jpg', 'https://www.instagram.com/nkust_ic/', '新北市蘆洲區光明路50巷', 'c110156220@nkust.edu.tw', '0966684323', 1, 4, 0, '2024-10-10 11:02:38.522324');

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
(1, '3C', '代表電子產品、電腦、通訊產品等，例如手機、筆記型電腦、平板、數位相機等科技產品。'),
(2, '家電', '家用電器，包括冰箱、洗衣機、微波爐、冷氣機等，提升居家生活品質的電器設備。'),
(3, '美妝個清', '美妝及個人清潔用品，如化妝品、保養品、洗髮精、沐浴乳、香水等，關注外貌與個人衛生的產品。'),
(4, '保健/食品', '健康相關產品及食品，如維他命、保健品、健康食品、零食、飲料等，維持健康與生活品質。'),
(5, '服飾/內衣', '各式服裝、配件及內衣，包括日常穿著、運動服裝、時尚服飾等，滿足不同場合的需求。'),
(6, '鞋包/精品', '鞋類與包包，包括皮鞋、運動鞋、時尚包包，以及奢侈品配件如手錶、飾品等。'),
(7, '母嬰用品', '專為母親與嬰兒設計的產品，如嬰兒車、奶瓶、尿布、孕婦裝等，關注母嬰健康與舒適。'),
(8, '圖書文具', '書籍與文具用品，包括教科書、小說、學習書籍、筆記本、書寫工具等，支持學習與辦公需求。'),
(9, '傢寢運動', '家庭用品、寢具及運動器材，如床墊、被單、健身器材等，提升家居舒適度與運動習慣。'),
(10, '運動用品', '與運動相關的產品，如球具、運動服、運動配件等，支援各種運動活動的進行。'),
(11, '戶外休閒', '戶外活動與休閒用品，如露營設備、釣魚工具、登山用品等，適合愛好戶外活動的人群。'),
(12, '數位內容', '數位產品與服務，包括遊戲、軟體、應用程式、線上課程等，提供數位娛樂與學習資源。'),
(13, '玩具遊戲', '玩具與遊戲產品，從嬰幼兒玩具到成人桌遊、模型、拼圖等，增添娛樂與親子互動的樂趣。'),
(14, '教育', '教學方面'),
(15, '其他', '暫無介紹');

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
(1, '2024-09-30 20:43:16.491720', '1', 'Industry object (1)', 1, '[{\"added\": {}}]', 13, 2),
(2, '2024-09-30 20:43:29.699179', '2', 'Industry object (2)', 1, '[{\"added\": {}}]', 13, 2),
(3, '2024-09-30 20:43:36.397195', '3', 'Industry object (3)', 1, '[{\"added\": {}}]', 13, 2),
(4, '2024-09-30 20:43:42.568843', '4', 'Industry object (4)', 1, '[{\"added\": {}}]', 13, 2),
(5, '2024-09-30 20:43:50.658792', '5', 'Industry object (5)', 1, '[{\"added\": {}}]', 13, 2),
(6, '2024-09-30 20:43:58.005016', '6', 'Industry object (6)', 1, '[{\"added\": {}}]', 13, 2),
(7, '2024-09-30 20:44:04.376997', '7', 'Industry object (7)', 1, '[{\"added\": {}}]', 13, 2),
(8, '2024-09-30 20:44:10.561408', '8', 'Industry object (8)', 1, '[{\"added\": {}}]', 13, 2),
(9, '2024-09-30 20:44:16.692115', '9', 'Industry object (9)', 1, '[{\"added\": {}}]', 13, 2),
(10, '2024-09-30 20:44:23.487461', '10', 'Industry object (10)', 1, '[{\"added\": {}}]', 13, 2),
(11, '2024-09-30 20:44:31.637286', '11', 'Industry object (11)', 1, '[{\"added\": {}}]', 13, 2),
(12, '2024-09-30 20:44:38.588538', '12', 'Industry object (12)', 1, '[{\"added\": {}}]', 13, 2),
(13, '2024-09-30 20:44:46.677333', '13', 'Industry object (13)', 1, '[{\"added\": {}}]', 13, 2),
(14, '2024-09-30 20:48:00.111832', '1', '會長', 1, '[{\"added\": {}}]', 11, 2),
(15, '2024-09-30 20:48:09.516581', '2', '測試', 1, '[{\"added\": {}}]', 11, 2),
(16, '2024-09-30 20:48:25.778289', '1', '國立高雄科技大學 智慧商務系 - 113', 1, '[{\"added\": {}}]', 10, 2),
(17, '2024-09-30 20:48:28.152618', '1', '楊兆彬 - 測試', 1, '[{\"added\": {}}]', 12, 2),
(18, '2024-09-30 20:51:29.185862', '3', '副會長', 1, '[{\"added\": {}}]', 11, 2),
(19, '2024-09-30 20:51:38.599678', '4', '會員', 1, '[{\"added\": {}}]', 11, 2),
(20, '2024-09-30 20:57:43.918863', '1', '彬彬炸雞店(虛擬)', 1, '[{\"added\": {}}]', 14, 2),
(21, '2024-09-30 21:02:27.129965', '1', '商品總攬', 1, '[{\"added\": {}}]', 15, 2),
(22, '2024-09-30 21:03:20.668283', '2', '黃金薯條', 1, '[{\"added\": {}}]', 15, 2),
(23, '2024-09-30 21:03:38.908587', '3', '香辣雞米花', 1, '[{\"added\": {}}]', 15, 2),
(24, '2024-09-30 21:04:00.203637', '4', '脆皮花枝圈', 1, '[{\"added\": {}}]', 15, 2),
(25, '2024-09-30 21:06:06.924155', '1', 'Recruit object (1)', 1, '[{\"added\": {}}]', 22, 2),
(26, '2024-09-30 21:06:29.287745', '2', 'Recruit object (2)', 1, '[{\"added\": {}}]', 22, 2),
(27, '2024-09-30 21:07:27.632056', '14', '教育', 1, '[{\"added\": {}}]', 13, 2),
(28, '2024-09-30 21:07:37.311517', '15', '其他', 1, '[{\"added\": {}}]', 13, 2),
(29, '2024-10-06 19:02:37.035614', '1', '高科大校友會教師節健行活動', 1, '[{\"added\": {}}]', 16, 2),
(30, '2024-10-06 19:04:08.473175', '2', 'Image for 高科大校友會教師節健行活動', 1, '[{\"added\": {}}]', 17, 2),
(31, '2024-10-06 19:04:13.977059', '3', 'Image for 高科大校友會教師節健行活動', 1, '[{\"added\": {}}]', 17, 2),
(32, '2024-10-06 19:04:19.535110', '4', 'Image for 高科大校友會教師節健行活動', 1, '[{\"added\": {}}]', 17, 2),
(33, '2024-10-06 19:04:24.159617', '5', 'Image for 高科大校友會教師節健行活動', 1, '[{\"added\": {}}]', 17, 2),
(34, '2024-10-06 19:04:30.626246', '6', 'Image for 高科大校友會教師節健行活動', 1, '[{\"added\": {}}]', 17, 2),
(35, '2024-10-06 19:04:37.871450', '7', 'Image for 高科大校友會教師節健行活動', 1, '[{\"added\": {}}]', 17, 2),
(36, '2024-10-06 19:04:42.777305', '8', 'Image for 高科大校友會教師節健行活動', 1, '[{\"added\": {}}]', 17, 2),
(37, '2024-10-06 19:04:47.951564', '9', 'Image for 高科大校友會教師節健行活動', 1, '[{\"added\": {}}]', 17, 2),
(38, '2024-10-10 09:12:33.304981', '1', 'SlideImage object (1)', 1, '[{\"added\": {}}]', 18, 1),
(39, '2024-10-10 10:36:19.284815', '1', '高科大校友會教師節健行活動', 2, '[{\"changed\": {\"fields\": [\"\\u662f\\u5426\\u516c\\u958b\"]}}]', 16, 1);

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
(23, 'notice', 'notice'),
(19, 'picture', 'companyimage'),
(20, 'picture', 'productimage'),
(21, 'picture', 'selfimage'),
(18, 'picture', 'slideimage'),
(9, 'Private', 'passwordresetcode'),
(8, 'Private', 'private'),
(15, 'product', 'product'),
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
(1, 'contenttypes', '0001_initial', '2024-09-30 20:34:32.882230'),
(2, 'contenttypes', '0002_remove_content_type_name', '2024-09-30 20:34:32.912996'),
(3, 'auth', '0001_initial', '2024-09-30 20:34:33.018118'),
(4, 'auth', '0002_alter_permission_name_max_length', '2024-09-30 20:34:33.040429'),
(5, 'auth', '0003_alter_user_email_max_length', '2024-09-30 20:34:33.043848'),
(6, 'auth', '0004_alter_user_username_opts', '2024-09-30 20:34:33.046932'),
(7, 'auth', '0005_alter_user_last_login_null', '2024-09-30 20:34:33.050516'),
(8, 'auth', '0006_require_contenttypes_0002', '2024-09-30 20:34:33.051518'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2024-09-30 20:34:33.055525'),
(10, 'auth', '0008_alter_user_username_max_length', '2024-09-30 20:34:33.058533'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2024-09-30 20:34:33.061038'),
(12, 'auth', '0010_alter_group_name_max_length', '2024-09-30 20:34:33.067567'),
(13, 'auth', '0011_update_proxy_permissions', '2024-09-30 20:34:33.071370'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2024-09-30 20:34:33.075595'),
(15, 'Private', '0001_initial', '2024-09-30 20:34:33.242076'),
(16, 'admin', '0001_initial', '2024-09-30 20:34:33.297097'),
(17, 'admin', '0002_logentry_remove_auto_add', '2024-09-30 20:34:33.301479'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2024-09-30 20:34:33.305610'),
(19, 'member', '0001_initial', '2024-09-30 20:34:33.370322'),
(20, 'company', '0001_initial', '2024-09-30 20:34:33.439181'),
(21, 'notice', '0001_initial', '2024-09-30 20:34:33.484206'),
(22, 'product', '0001_initial', '2024-09-30 20:34:33.514607'),
(23, 'picture', '0001_initial', '2024-09-30 20:34:33.650442'),
(24, 'recruit', '0001_initial', '2024-09-30 20:34:33.683038'),
(25, 'sessions', '0001_initial', '2024-09-30 20:34:33.701415'),
(26, 'token_blacklist', '0001_initial', '2024-09-30 20:34:33.773766'),
(27, 'token_blacklist', '0002_outstandingtoken_jti_hex', '2024-09-30 20:34:33.783031'),
(28, 'token_blacklist', '0003_auto_20171017_2007', '2024-09-30 20:34:33.795254'),
(29, 'token_blacklist', '0004_auto_20171017_2013', '2024-09-30 20:34:33.824175'),
(30, 'token_blacklist', '0005_remove_outstandingtoken_jti', '2024-09-30 20:34:33.834723'),
(31, 'token_blacklist', '0006_auto_20171017_2113', '2024-09-30 20:34:33.842590'),
(32, 'token_blacklist', '0007_auto_20171017_2214', '2024-09-30 20:34:34.548464'),
(33, 'token_blacklist', '0008_migrate_to_bigautofield', '2024-09-30 20:34:34.767960'),
(34, 'token_blacklist', '0010_fix_migrate_to_bigautofield', '2024-09-30 20:34:34.775500'),
(35, 'token_blacklist', '0011_linearizes_history', '2024-09-30 20:34:34.776503'),
(36, 'token_blacklist', '0012_alter_outstandingtoken_user', '2024-09-30 20:34:34.781314'),
(37, 'company', '0002_alter_industry_options', '2024-10-06 18:53:49.794565'),
(38, 'recruit', '0002_alter_recruit_intro_recruitimage', '2024-10-06 18:53:49.841499'),
(39, 'article', '0001_initial', '2024-10-06 18:59:31.646982'),
(40, 'article', '0002_alter_articleimage_image', '2024-10-08 19:11:48.869578'),
(41, 'recruit', '0003_recruit_active_alter_recruitimage_image', '2024-10-08 19:11:48.892647'),
(42, 'company', '0003_company_clicks', '2024-10-10 08:32:58.714359'),
(43, 'company', '0004_company_created_at', '2024-10-10 11:02:38.530322'),
(44, 'picture', '0002_alter_productimage_image_alter_slideimage_image', '2024-10-10 11:02:38.538359');

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
('j1pfydo70c5lgygsdr6y62iy21ua68z5', '.eJxVjMEOwiAQRP-FsyGwLSt49O43kIUFqRpISnsy_rtt0oNe5jDvzbyFp3Upfu1p9hOLiwBx-u0CxWeqO-AH1XuTsdVlnoLcFXnQLm-N0-t6uH8HhXrZ1tESKYdhgDQGNQxb2JxHSg4NG22U5gxsQCOHCBbRnAMaclkjRGQWny_guDfK:1svNDO:yZI7ztrCQAK66NvITd6oGoPASZ35jmr2uFDwi9bQFoc', '2024-10-14 20:41:54.103773'),
('v19lc8l93mq3sb8p2l96on7v3z8j90zg', '.eJxVjMEOwiAQRP-FsyFAQcCjd7-B7C5bqRpISnsy_rtt0oNe5jDvzbxFgnUpae08pymLi9Di9Nsh0JPrDvID6r1JanWZJ5S7Ig_a5a1lfl0P9--gQC_bmiI6xwhoaPBbDj4EyuhC5ozMXo2BLSqt4ewH7aON2llDypGxI2MUny8KTDhg:1sypCb:F1yb2NjxOXYamBfBdRrzLCDPh1TRUc4I-9U_eIRLlRc', '2024-10-24 09:11:21.470234');

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
(1, '國立高雄科技大學 智慧商務系', '113');

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
  `position_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `member_member`
--

INSERT INTO `member_member` (`id`, `name`, `home_phone`, `mobile_phone`, `gender`, `address`, `is_paid`, `intro`, `birth_date`, `photo`, `date_joined`, `graduate_id`, `position_id`) VALUES
(1, '楊兆彬', '0222856679', '0966683955', 'M', '新北市蘆洲區光明路50巷38號4樓', 1, '你好，我是彬彬，目前就讀大學或研究所即將要畢業了，主修後端開發。我熱愛寫程式，尤其專注於伺服器端的邏輯處理和資料庫管理。我經常使用 Python 作為主要開發語言，並在專案中使用 Django 框架來構建可靠且擴展性強的應用程式。\r\n\r\n我喜歡解決技術挑戰，無論是處理 API、JWT 驗證，還是設計高效的資料結構，都讓我感到充滿成就感。在開發中，我也會關注效能最佳化和安全性，確保每個專案都能穩定運行。\r\n\r\n除了專業技術，我也會持續學習新技術，像是嘗試前端開發工具，如 React，讓自己具備全端開發能力。我希望能將這些技能應用在實際專案中，並持續進步。', '2003-06-25', '', '2024-10-01', 1, 2);

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
(2, '測試', 50),
(3, '副會長', 2),
(4, '會員', 10);

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
(1, 'None', 'static/slide/326431594_911615443529376_4304352214119373700_n.jpg', '會長交接大會', '', 1, '2024-10-10 09:12:33.304981');

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

--
-- 傾印資料表的資料 `private_passwordresetcode`
--

INSERT INTO `private_passwordresetcode` (`id`, `code`, `created_at`, `expires_at`, `private_id`) VALUES
(1, '715332', '2024-10-18 01:49:49.636937', '2024-10-18 02:49:49.636937', 1),
(2, '570583', '2024-10-18 01:53:37.338776', '2024-10-18 02:53:37.337788', 1),
(3, '196098', '2024-10-18 01:53:37.353734', '2024-10-18 02:53:37.352735', 1);

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
(1, 'c110156220@nkust.edu.tw', 'pbkdf2_sha256$720000$30pAsidGTVwwikdSOj8Kul$lfGxquzQV9xEd6kfTYksoz5I5OBPIABOwtYU2h8McKQ=', 1, 1, 1, '2024-10-18 01:54:33.907052', '2024-09-30 20:40:13.423038'),
(2, 'robin92062574@gmail.com', 'pbkdf2_sha256$720000$XfcR9CBZORnRONaK5we41m$j+hv9QfVo1mODWiDcxZ2UPmkImjGK8kvU/cDWcwyQ0o=', 1, 1, 1, '2024-09-30 20:41:54.102770', '2024-09-30 20:40:36.100570'),
(3, 'robin92062522@gmail.com', 'pbkdf2_sha256$720000$wALjxWoo0emqcvM06fiarl$hSGnDgHuNLloHAEjnEtgCbWgGqh9SEMGtA6f2bX+Pho=', 1, 1, 1, '2024-09-30 20:41:43.043416', '2024-09-30 20:41:43.043416');

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

--
-- 傾印資料表的資料 `product_product`
--

INSERT INTO `product_product` (`id`, `name`, `description`, `photo`, `created_at`, `updated_at`, `company_id`) VALUES
(1, '商品總攬', '很好吃', 'static/product/123.png', '2024-09-30 21:02:27.128632', '2024-09-30 21:02:27.128632', 1),
(2, '黃金薯條', '現切馬鈴薯炸至金黃酥脆，外層酥脆、內裡軟綿，搭配鹽調味，簡單又美味。無論單吃還是搭配其他餐點，都是無法抗拒的美食選擇。', 'static/product/123-1.png', '2024-09-30 21:03:20.667280', '2024-09-30 21:03:20.667280', 1),
(3, '香辣雞米花', '這款香辣雞米花採用新鮮去骨雞腿肉，外層酥脆，裡面多汁，灑上香辣調料，每一口都充滿著濃郁的辛香風味。小巧可口，是聚會或小酌的最佳搭配。', 'static/product/123-2.png', '2024-09-30 21:03:38.908587', '2024-09-30 21:03:38.908587', 1),
(4, '脆皮花枝圈', '我們的花枝圈選用新鮮的花枝，外層裹上薄脆的麵衣，炸至金黃酥脆，搭配檸檬片和特調醬料，每一口都能感受到海鮮的鮮甜與酥脆的完美融合。', 'static/product/123-3.png', '2024-09-30 21:04:00.202130', '2024-09-30 21:04:00.202130', 1);

-- --------------------------------------------------------

--
-- 資料表結構 `recruit_recruit`
--

CREATE TABLE `recruit_recruit` (
  `id` bigint(20) NOT NULL,
  `title` varchar(50) NOT NULL,
  `intro` longtext NOT NULL,
  `click` int(11) NOT NULL,
  `deadline` date NOT NULL,
  `release_date` date NOT NULL,
  `company_id` bigint(20) NOT NULL,
  `active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf32 COLLATE=utf32_general_ci;

--
-- 傾印資料表的資料 `recruit_recruit`
--

INSERT INTO `recruit_recruit` (`id`, `title`, `intro`, `click`, `deadline`, `release_date`, `company_id`, `active`) VALUES
(1, '收銀工讀生', '主要負責點餐、傳菜及顧客服務，確保顧客有愉快的用餐體驗。需要擁有良好的溝通能力和親切的服務態度，並能處理顧客需求與問題。\n\n薪水183/時', 0, '2024-10-17', '2024-10-01', 1, 1),
(2, '協助備料', '負責協助廚房日常運作，包括準備食材、簡單的炸物烹調及清潔工作。需要具備良好的團隊合作精神，能夠在快速的工作環境中保持效率。', 0, '2024-10-25', '2024-10-01', 1, 1);

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
(1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyODY1NDg4NywiaWF0IjoxNzI4NTY4NDg3LCJqdGkiOiI5NTA5Y2RjNDc1ZWM0NDY1YjkxZWE3NmEwZjJjMmU1NyIsInVzZXJfaWQiOjF9.G6T1buD4l7Yp3hfAqN4m_YpXAA2MPQ_DS5JADsXR9bs', '2024-10-10 13:54:47.270190', '2024-10-11 13:54:47.000000', 1, '9509cdc475ec4465b91ea76a0f2c2e57'),
(2, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyODY1NDk1OSwiaWF0IjoxNzI4NTY4NTU5LCJqdGkiOiI2OGMyNjMxZWNhMGY0OGU4YTMyMDAyNTU0ZjkyODY1YSIsInVzZXJfaWQiOjF9.QiS4z8sPD9KIMZJOwP9VsUHdZoOtazD0aeAPws-5KBg', '2024-10-10 13:55:59.701023', '2024-10-11 13:55:59.000000', 1, '68c2631eca0f48e8a32002554f92865a'),
(3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyODY1NTIwNCwiaWF0IjoxNzI4NTY4ODA0LCJqdGkiOiIxOTAxZWNiM2UxMGQ0NDk5YWVmZTQyODhmOWYxNDllZiIsInVzZXJfaWQiOjF9.zpZTCt-4bx21lhZ0ogl93MRMeQCFlEQWeIi5SLaSvO8', '2024-10-10 14:00:04.158785', '2024-10-11 14:00:04.000000', 1, '1901ecb3e10d4499aefe4288f9f149ef'),
(4, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyOTIzNjE3MCwiaWF0IjoxNzI5MTQ5NzcwLCJqdGkiOiI0YmU3MDA2OWNmN2I0Mzg1Yjk2YWViNWIyYTVkMTRhZCIsInVzZXJfaWQiOjF9.Fcq1oiWME8vqsy7WzsDslIxVP9bU7pBmEosewvr7nxg', '2024-10-17 07:22:50.999032', '2024-10-18 07:22:50.000000', 1, '4be70069cf7b4385b96aeb5b2a5d14ad'),
(5, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyOTMwMjkyMiwiaWF0IjoxNzI5MjE2NTIyLCJqdGkiOiJkZTdhZWEzMzczZjc0ZDM5YmVhMTkyODc3NGM4ODViNiIsInVzZXJfaWQiOjF9.QVj9VA67W5SOQe5lppgmvOhcWMcEwMLYm-7kM7vTcFM', '2024-10-18 01:55:22.090466', '2024-10-19 01:55:22.000000', 1, 'de7aea3373f74d39bea1928774c885b6'),
(6, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyOTMyNzc2MiwiaWF0IjoxNzI5MjQxMzYyLCJqdGkiOiJiZGU1ZjJhYmI3ZTY0NmNlYWRiZDAzNzdlNTBhNTgxOSIsInVzZXJfaWQiOjF9.MAdtEJiPbtdXdMMXEVn5B_jbDg6s-3O62g6eHCCj5mU', '2024-10-18 08:49:22.890048', '2024-10-19 08:49:22.000000', 1, 'bde5f2abb7e646ceadbd0377e50a5819');

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
  ADD KEY `member_member_position_id_4ed12437_fk_member_position_id` (`position_id`);

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
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `article_articleimage`
--
ALTER TABLE `article_articleimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=97;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `company_company`
--
ALTER TABLE `company_company`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `company_industry`
--
ALTER TABLE `company_industry`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `member_graduate`
--
ALTER TABLE `member_graduate`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `member_member`
--
ALTER TABLE `member_member`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `member_position`
--
ALTER TABLE `member_position`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `notice_notice`
--
ALTER TABLE `notice_notice`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `picture_companyimage`
--
ALTER TABLE `picture_companyimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `picture_productimage`
--
ALTER TABLE `picture_productimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `picture_selfimage`
--
ALTER TABLE `picture_selfimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `picture_slideimage`
--
ALTER TABLE `picture_slideimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `private_passwordresetcode`
--
ALTER TABLE `private_passwordresetcode`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `private_private`
--
ALTER TABLE `private_private`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

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
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `recruit_recruit`
--
ALTER TABLE `recruit_recruit`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `recruit_recruitimage`
--
ALTER TABLE `recruit_recruitimage`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `token_blacklist_blacklistedtoken`
--
ALTER TABLE `token_blacklist_blacklistedtoken`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `token_blacklist_outstandingtoken`
--
ALTER TABLE `token_blacklist_outstandingtoken`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

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
  ADD CONSTRAINT `member_member_position_id_4ed12437_fk_member_position_id` FOREIGN KEY (`position_id`) REFERENCES `member_position` (`id`);

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
