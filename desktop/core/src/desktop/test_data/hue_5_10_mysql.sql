-- MySQL dump 10.14  Distrib 5.5.56-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: hueserverd48da0da04827981b667ae3b040ddb6c
-- ------------------------------------------------------
-- Server version	5.5.56-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (1,'default');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_5f412f9a` (`group_id`),
  KEY `auth_group_permissions_83d7f98b` (`permission_id`),
  CONSTRAINT `group_id_refs_id_f4b32aac` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `permission_id_refs_id_6ba0f519` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_37ef4eb4` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_d043b34a` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=229 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add nonce',4,'add_nonce'),(11,'Can change nonce',4,'change_nonce'),(12,'Can delete nonce',4,'delete_nonce'),(13,'Can add association',5,'add_association'),(14,'Can change association',5,'change_association'),(15,'Can delete association',5,'delete_association'),(16,'Can add user open id',6,'add_useropenid'),(17,'Can change user open id',6,'change_useropenid'),(18,'Can delete user open id',6,'delete_useropenid'),(19,'Can add content type',7,'add_contenttype'),(20,'Can change content type',7,'change_contenttype'),(21,'Can delete content type',7,'delete_contenttype'),(22,'Can add session',8,'add_session'),(23,'Can change session',8,'change_session'),(24,'Can delete session',8,'delete_session'),(25,'Can add site',9,'add_site'),(26,'Can change site',9,'change_site'),(27,'Can delete site',9,'delete_site'),(28,'Can add log entry',10,'add_logentry'),(29,'Can change log entry',10,'change_logentry'),(30,'Can delete log entry',10,'delete_logentry'),(31,'Can add migration history',11,'add_migrationhistory'),(32,'Can change migration history',11,'change_migrationhistory'),(33,'Can delete migration history',11,'delete_migrationhistory'),(34,'Can add access attempt',12,'add_accessattempt'),(35,'Can change access attempt',12,'change_accessattempt'),(36,'Can delete access attempt',12,'delete_accessattempt'),(37,'Can add access log',13,'add_accesslog'),(38,'Can change access log',13,'change_accesslog'),(39,'Can delete access log',13,'delete_accesslog'),(40,'Can add document',19,'add_document'),(41,'Can change document',19,'change_document'),(42,'Can delete document',19,'delete_document'),(43,'Can add pig script',18,'add_pigscript'),(44,'Can change pig script',18,'change_pigscript'),(45,'Can delete pig script',18,'delete_pigscript'),(46,'Can add job',20,'add_job'),(47,'Can change job',20,'change_job'),(48,'Can delete job',20,'delete_job'),(49,'Can add workflow',14,'add_workflow'),(50,'Can change workflow',14,'change_workflow'),(51,'Can delete workflow',14,'delete_workflow'),(52,'Can add link',21,'add_link'),(53,'Can change link',21,'change_link'),(54,'Can delete link',21,'delete_link'),(55,'Can add node',22,'add_node'),(56,'Can change node',22,'change_node'),(57,'Can delete node',22,'delete_node'),(58,'Can add mapreduce',23,'add_mapreduce'),(59,'Can change mapreduce',23,'change_mapreduce'),(60,'Can delete mapreduce',23,'delete_mapreduce'),(61,'Can add streaming',24,'add_streaming'),(62,'Can change streaming',24,'change_streaming'),(63,'Can delete streaming',24,'delete_streaming'),(64,'Can add java',25,'add_java'),(65,'Can change java',25,'change_java'),(66,'Can delete java',25,'delete_java'),(67,'Can add pig',26,'add_pig'),(68,'Can change pig',26,'change_pig'),(69,'Can delete pig',26,'delete_pig'),(70,'Can add hive',27,'add_hive'),(71,'Can change hive',27,'change_hive'),(72,'Can delete hive',27,'delete_hive'),(73,'Can add sqoop',28,'add_sqoop'),(74,'Can change sqoop',28,'change_sqoop'),(75,'Can delete sqoop',28,'delete_sqoop'),(76,'Can add ssh',29,'add_ssh'),(77,'Can change ssh',29,'change_ssh'),(78,'Can delete ssh',29,'delete_ssh'),(79,'Can add shell',30,'add_shell'),(80,'Can change shell',30,'change_shell'),(81,'Can delete shell',30,'delete_shell'),(82,'Can add dist cp',31,'add_distcp'),(83,'Can change dist cp',31,'change_distcp'),(84,'Can delete dist cp',31,'delete_distcp'),(85,'Can add fs',32,'add_fs'),(86,'Can change fs',32,'change_fs'),(87,'Can delete fs',32,'delete_fs'),(88,'Can add email',33,'add_email'),(89,'Can change email',33,'change_email'),(90,'Can delete email',33,'delete_email'),(91,'Can add sub workflow',34,'add_subworkflow'),(92,'Can change sub workflow',34,'change_subworkflow'),(93,'Can delete sub workflow',34,'delete_subworkflow'),(94,'Can add generic',35,'add_generic'),(95,'Can change generic',35,'change_generic'),(96,'Can delete generic',35,'delete_generic'),(97,'Can add start',36,'add_start'),(98,'Can change start',36,'change_start'),(99,'Can delete start',36,'delete_start'),(100,'Can add end',37,'add_end'),(101,'Can change end',37,'change_end'),(102,'Can delete end',37,'delete_end'),(103,'Can add kill',38,'add_kill'),(104,'Can change kill',38,'change_kill'),(105,'Can delete kill',38,'delete_kill'),(106,'Can add fork',39,'add_fork'),(107,'Can change fork',39,'change_fork'),(108,'Can delete fork',39,'delete_fork'),(109,'Can add join',40,'add_join'),(110,'Can change join',40,'change_join'),(111,'Can delete join',40,'delete_join'),(112,'Can add decision',41,'add_decision'),(113,'Can change decision',41,'change_decision'),(114,'Can delete decision',41,'delete_decision'),(115,'Can add decision end',42,'add_decisionend'),(116,'Can change decision end',42,'change_decisionend'),(117,'Can delete decision end',42,'delete_decisionend'),(118,'Can add coordinator',15,'add_coordinator'),(119,'Can change coordinator',15,'change_coordinator'),(120,'Can delete coordinator',15,'delete_coordinator'),(121,'Can add dataset',43,'add_dataset'),(122,'Can change dataset',43,'change_dataset'),(123,'Can delete dataset',43,'delete_dataset'),(124,'Can add data input',44,'add_datainput'),(125,'Can change data input',44,'change_datainput'),(126,'Can delete data input',44,'delete_datainput'),(127,'Can add data output',45,'add_dataoutput'),(128,'Can change data output',45,'change_dataoutput'),(129,'Can delete data output',45,'delete_dataoutput'),(130,'Can add bundled coordinator',46,'add_bundledcoordinator'),(131,'Can change bundled coordinator',46,'change_bundledcoordinator'),(132,'Can delete bundled coordinator',46,'delete_bundledcoordinator'),(133,'Can add bundle',16,'add_bundle'),(134,'Can change bundle',16,'change_bundle'),(135,'Can delete bundle',16,'delete_bundle'),(136,'Can add history',47,'add_history'),(137,'Can change history',47,'change_history'),(138,'Can delete history',47,'delete_history'),(139,'Can add user preferences',48,'add_userpreferences'),(140,'Can change user preferences',48,'change_userpreferences'),(141,'Can delete user preferences',48,'delete_userpreferences'),(142,'Can add settings',49,'add_settings'),(143,'Can change settings',49,'change_settings'),(144,'Can delete settings',49,'delete_settings'),(145,'Can add default configuration',50,'add_defaultconfiguration'),(146,'Can change default configuration',50,'change_defaultconfiguration'),(147,'Can delete default configuration',50,'delete_defaultconfiguration'),(148,'Can add document tag',51,'add_documenttag'),(149,'Can change document tag',51,'change_documenttag'),(150,'Can delete document tag',51,'delete_documenttag'),(151,'Can add document',52,'add_document'),(152,'Can change document',52,'change_document'),(153,'Can delete document',52,'delete_document'),(154,'Can add document permission',53,'add_documentpermission'),(155,'Can change document permission',53,'change_documentpermission'),(156,'Can delete document permission',53,'delete_documentpermission'),(157,'Can add document2',54,'add_document2'),(158,'Can change document2',54,'change_document2'),(159,'Can delete document2',54,'delete_document2'),(160,'Can add directory',54,'add_directory'),(161,'Can change directory',54,'change_directory'),(162,'Can delete directory',54,'delete_directory'),(163,'Can add document2 permission',55,'add_document2permission'),(164,'Can change document2 permission',55,'change_document2permission'),(165,'Can delete document2 permission',55,'delete_document2permission'),(166,'Can add query history',57,'add_queryhistory'),(167,'Can change query history',57,'change_queryhistory'),(168,'Can delete query history',57,'delete_queryhistory'),(169,'Can add hive server query history',57,'add_hiveserverqueryhistory'),(170,'Can change hive server query history',57,'change_hiveserverqueryhistory'),(171,'Can delete hive server query history',57,'delete_hiveserverqueryhistory'),(172,'Can add saved query',58,'add_savedquery'),(173,'Can change saved query',58,'change_savedquery'),(174,'Can delete saved query',58,'delete_savedquery'),(175,'Can add session',59,'add_session'),(176,'Can change session',59,'change_session'),(177,'Can delete session',59,'delete_session'),(178,'Can add meta install',60,'add_metainstall'),(179,'Can change meta install',60,'change_metainstall'),(180,'Can delete meta install',60,'delete_metainstall'),(181,'Can add job design',62,'add_jobdesign'),(182,'Can change job design',62,'change_jobdesign'),(183,'Can delete job design',62,'delete_jobdesign'),(184,'Can add check for setup',63,'add_checkforsetup'),(185,'Can change check for setup',63,'change_checkforsetup'),(186,'Can delete check for setup',63,'delete_checkforsetup'),(187,'Can add oozie action',64,'add_oozieaction'),(188,'Can change oozie action',64,'change_oozieaction'),(189,'Can delete oozie action',64,'delete_oozieaction'),(190,'Can add oozie design',65,'add_ooziedesign'),(191,'Can change oozie design',65,'change_ooziedesign'),(192,'Can delete oozie design',65,'delete_ooziedesign'),(193,'Can add oozie mapreduce action',66,'add_ooziemapreduceaction'),(194,'Can change oozie mapreduce action',66,'change_ooziemapreduceaction'),(195,'Can delete oozie mapreduce action',66,'delete_ooziemapreduceaction'),(196,'Can add oozie streaming action',67,'add_ooziestreamingaction'),(197,'Can change oozie streaming action',67,'change_ooziestreamingaction'),(198,'Can delete oozie streaming action',67,'delete_ooziestreamingaction'),(199,'Can add oozie java action',68,'add_ooziejavaaction'),(200,'Can change oozie java action',68,'change_ooziejavaaction'),(201,'Can delete oozie java action',68,'delete_ooziejavaaction'),(202,'Can add job history',69,'add_jobhistory'),(203,'Can change job history',69,'change_jobhistory'),(204,'Can delete job history',69,'delete_jobhistory'),(205,'Can add facet',70,'add_facet'),(206,'Can change facet',70,'change_facet'),(207,'Can delete facet',70,'delete_facet'),(208,'Can add result',71,'add_result'),(209,'Can change result',71,'change_result'),(210,'Can delete result',71,'delete_result'),(211,'Can add sorting',72,'add_sorting'),(212,'Can change sorting',72,'change_sorting'),(213,'Can delete sorting',72,'delete_sorting'),(214,'Can add collection',73,'add_collection'),(215,'Can change collection',73,'change_collection'),(216,'Can delete collection',73,'delete_collection'),(217,'Can add user profile',74,'add_userprofile'),(218,'Can change user profile',74,'change_userprofile'),(219,'Can delete user profile',74,'delete_userprofile'),(220,'Can add ldap group',75,'add_ldapgroup'),(221,'Can change ldap group',75,'change_ldapgroup'),(222,'Can delete ldap group',75,'delete_ldapgroup'),(223,'Can add group permission',76,'add_grouppermission'),(224,'Can change group permission',76,'change_grouppermission'),(225,'Can delete group permission',76,'delete_grouppermission'),(226,'Can add hue permission',77,'add_huepermission'),(227,'Can change hue permission',77,'change_huepermission'),(228,'Can delete hue permission',77,'delete_huepermission');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=1100714 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$12000$Zu2EqSvu9Xfy$015XJJy7JIMpKqGKR3ZSBbSUVA2DDtfR06a75UaDbVI=','2018-06-19 06:14:49',1,'admin','','','',0,1,'2018-06-19 06:14:49'),(1100713,'!','2018-06-19 06:15:51',0,'hue','','','',0,0,'2018-06-19 06:15:51');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_6340c63c` (`user_id`),
  KEY `auth_user_groups_5f412f9a` (`group_id`),
  CONSTRAINT `user_id_refs_id_40c41112` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `group_id_refs_id_274b862c` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
INSERT INTO `auth_user_groups` VALUES (1,1,1),(2,1100713,1);
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_6340c63c` (`user_id`),
  KEY `auth_user_user_permissions_83d7f98b` (`permission_id`),
  CONSTRAINT `user_id_refs_id_4dc23c39` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `permission_id_refs_id_35d9ac25` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `axes_accessattempt`
--

DROP TABLE IF EXISTS `axes_accessattempt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `axes_accessattempt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_agent` varchar(255) NOT NULL,
  `ip_address` char(39) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `trusted` tinyint(1) NOT NULL,
  `http_accept` varchar(1025) NOT NULL,
  `path_info` varchar(255) NOT NULL,
  `attempt_time` datetime NOT NULL,
  `get_data` longtext NOT NULL,
  `post_data` longtext NOT NULL,
  `failures_since_start` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `axes_accessattempt`
--

LOCK TABLES `axes_accessattempt` WRITE;
/*!40000 ALTER TABLE `axes_accessattempt` DISABLE KEYS */;
INSERT INTO `axes_accessattempt` VALUES (1,'python-requests/2.15.1','172.31.112.42','admin',1,'*/*','/accounts/login/','2018-06-19 06:14:50','','username=admin\nserver=Local',0);
/*!40000 ALTER TABLE `axes_accessattempt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `axes_accesslog`
--

DROP TABLE IF EXISTS `axes_accesslog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `axes_accesslog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_agent` varchar(255) NOT NULL,
  `ip_address` char(39) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `trusted` tinyint(1) NOT NULL,
  `http_accept` varchar(1025) NOT NULL,
  `path_info` varchar(255) NOT NULL,
  `attempt_time` datetime NOT NULL,
  `logout_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `axes_accesslog`
--

LOCK TABLES `axes_accesslog` WRITE;
/*!40000 ALTER TABLE `axes_accesslog` DISABLE KEYS */;
INSERT INTO `axes_accesslog` VALUES (1,'python-requests/2.15.1','172.31.112.42','admin',1,'*/*','/accounts/login/','2018-06-19 06:14:50',NULL);
/*!40000 ALTER TABLE `axes_accesslog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `beeswax_metainstall`
--

DROP TABLE IF EXISTS `beeswax_metainstall`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `beeswax_metainstall` (
  `installed_example` tinyint(1) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `beeswax_metainstall`
--

LOCK TABLES `beeswax_metainstall` WRITE;
/*!40000 ALTER TABLE `beeswax_metainstall` DISABLE KEYS */;
/*!40000 ALTER TABLE `beeswax_metainstall` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `beeswax_queryhistory`
--

DROP TABLE IF EXISTS `beeswax_queryhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `beeswax_queryhistory` (
  `submission_date` datetime NOT NULL,
  `last_state` int(11) NOT NULL,
  `server_id` varchar(1024) DEFAULT NULL,
  `log_context` varchar(1024) DEFAULT NULL,
  `design_id` int(11) DEFAULT NULL,
  `owner_id` int(11) NOT NULL,
  `query` longtext NOT NULL,
  `has_results` tinyint(1) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `notify` tinyint(1) NOT NULL,
  `server_name` varchar(128) NOT NULL,
  `server_host` varchar(128) NOT NULL,
  `server_port` int(10) unsigned NOT NULL,
  `server_type` varchar(128) NOT NULL,
  `server_guid` varchar(1024) DEFAULT NULL,
  `operation_type` smallint(6),
  `modified_row_count` double,
  `statement_number` smallint(6) NOT NULL,
  `query_type` smallint(6) NOT NULL,
  `is_redacted` tinyint(1) NOT NULL,
  `extra` longtext NOT NULL,
  `is_cleared` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `beeswax_queryhistory_bfe02e93` (`last_state`),
  KEY `beeswax_queryhistory_38ebade8` (`design_id`),
  KEY `beeswax_queryhistory_cb902d83` (`owner_id`),
  CONSTRAINT `design_id_refs_id_f8250ba5` FOREIGN KEY (`design_id`) REFERENCES `beeswax_savedquery` (`id`),
  CONSTRAINT `owner_id_refs_id_d5c13755` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `beeswax_queryhistory`
--

LOCK TABLES `beeswax_queryhistory` WRITE;
/*!40000 ALTER TABLE `beeswax_queryhistory` DISABLE KEYS */;
/*!40000 ALTER TABLE `beeswax_queryhistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `beeswax_savedquery`
--

DROP TABLE IF EXISTS `beeswax_savedquery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `beeswax_savedquery` (
  `name` varchar(80) NOT NULL,
  `type` int(11) NOT NULL,
  `is_auto` tinyint(1) NOT NULL,
  `mtime` datetime NOT NULL,
  `owner_id` int(11) NOT NULL,
  `data` longtext NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `desc` longtext NOT NULL,
  `is_trashed` tinyint(1) NOT NULL,
  `is_redacted` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `beeswax_savedquery_db558b3c` (`is_auto`),
  KEY `beeswax_savedquery_cb902d83` (`owner_id`),
  KEY `beeswax_savedquery_863b5435` (`is_trashed`),
  CONSTRAINT `owner_id_refs_id_9ecea72d` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `beeswax_savedquery`
--

LOCK TABLES `beeswax_savedquery` WRITE;
/*!40000 ALTER TABLE `beeswax_savedquery` DISABLE KEYS */;
INSERT INTO `beeswax_savedquery` VALUES ('Sample: Top salary',0,0,'2018-06-19 06:15:51',1100713,'{\"query\": {\"email_notify\": false, \"query\": \"SELECT sample_07.description, sample_07.salary\\r\\nFROM\\r\\n  sample_07\\r\\nWHERE\\r\\n( sample_07.salary > 100000)\\r\\nORDER BY sample_07.salary DESC\\r\\nLIMIT 1000\", \"type\": 0, \"is_parameterized\": false, \"database\": \"default\"}, \"functions\": [], \"VERSION\": \"0.4.1\", \"file_resources\": [], \"settings\": []}',1,'Top salary 2007 above $100k',0,0),('Sample: Salary growth',0,0,'2018-06-19 06:15:51',1100713,'{\"query\": {\"email_notify\": false, \"query\": \"SELECT s07.description, s07.salary, s08.salary,\\r\\n  s08.salary - s07.salary\\r\\nFROM\\r\\n  sample_07 s07 JOIN sample_08 s08\\r\\nON ( s07.code = s08.code)\\r\\nWHERE\\r\\n s07.salary < s08.salary\\r\\nORDER BY s08.salary-s07.salary DESC\\r\\nLIMIT 1000\", \"type\": 0, \"is_parameterized\": false, \"database\": \"default\"}, \"functions\": [], \"VERSION\": \"0.4.1\", \"file_resources\": [], \"settings\": []}',2,'Salary growth (sorted) from 2007-08',0,0),('Sample: Job loss',0,0,'2018-06-19 06:15:51',1100713,'{\"query\": {\"email_notify\": false, \"query\": \"SELECT s07.description, s07.total_emp, s08.total_emp, s07.salary\\r\\nFROM\\r\\n  sample_07 s07 JOIN \\r\\n  sample_08 s08\\r\\nON ( s07.code = s08.code )\\r\\nWHERE\\r\\n( s07.total_emp > s08.total_emp\\r\\n AND s07.salary > 100000 )\\r\\nORDER BY s07.salary DESC\\nLIMIT 1000\", \"type\": 0, \"is_parameterized\": false, \"database\": \"default\"}, \"functions\": [], \"VERSION\": \"0.4.1\", \"file_resources\": [], \"settings\": []}',3,'Job loss among the top earners 2007-08',0,0),('Sample: Customers',0,0,'2018-06-19 06:15:51',1100713,'{\"query\": {\"email_notify\": false, \"query\": \"-- Get email survey opt-in values for all customers\\nSELECT\\r\\n  c.id,\\r\\n  c.name,\\r\\n  c.email_preferences.categories.surveys\\r\\nFROM customers c;\\n\\n\\n\\n-- Select customers for a given shipping ZIP Code\\nSELECT\\r\\n  customers.id,\\r\\n  customers.name\\r\\nFROM customers\\r\\nWHERE customers.addresses[\'shipping\'].zip_code = \'76710\';\\n\\n\\n\\n-- Compute total amount per order for all customers\\nSELECT\\r\\n  c.id AS customer_id,\\r\\n  c.name AS customer_name,\\r\\n  ords.order_id AS order_id,\\r\\n  SUM(order_items.price * order_items.qty) AS total_amount\\r\\nFROM\\r\\n  customers c\\r\\nLATERAL VIEW EXPLODE(c.orders) o AS ords\\r\\nLATERAL VIEW EXPLODE(ords.items) i AS order_items\\r\\nGROUP BY c.id, c.name, ords.order_id;\", \"type\": 0, \"is_parameterized\": false, \"database\": \"default\"}, \"functions\": [], \"VERSION\": \"0.4.1\", \"file_resources\": [], \"settings\": []}',4,'Email Survey Opt-Ins, Customers for Shipping ZIP Code, Total Amount per Order',0,0);
/*!40000 ALTER TABLE `beeswax_savedquery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `beeswax_session`
--

DROP TABLE IF EXISTS `beeswax_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `beeswax_session` (
  `last_used` datetime NOT NULL,
  `status_code` smallint(5) unsigned NOT NULL,
  `server_protocol_version` smallint(6) NOT NULL,
  `secret` longtext NOT NULL,
  `owner_id` int(11) NOT NULL,
  `guid` longtext NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `application` varchar(128) NOT NULL,
  `properties` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `beeswax_session_cdfd3889` (`last_used`),
  KEY `beeswax_session_cb902d83` (`owner_id`),
  CONSTRAINT `owner_id_refs_id_0417c1ac` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `beeswax_session`
--

LOCK TABLES `beeswax_session` WRITE;
/*!40000 ALTER TABLE `beeswax_session` DISABLE KEYS */;
INSERT INTO `beeswax_session` VALUES ('2018-06-19 06:15:52',0,6,'Xwer/bL0Qaa9RMQNUPxT+Q==\n',1,'Oe0ihqi+SqadBHbOz/ifGg==\n',1,'beeswax','{\"hive.exec.compress.output\": \"false\", \"hive.execution.engine\": \"mr\", \"hive.exec.parallel\": \"false\", \"mapreduce.job.queuename\": \"root.users.admin\", \"hive.map.aggr\": \"true\"}');
/*!40000 ALTER TABLE `beeswax_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `defaultconfiguration_groups`
--

DROP TABLE IF EXISTS `defaultconfiguration_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `defaultconfiguration_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `defaultconfiguration_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `defaultconfigurati_defaultconfiguration_id_13559ffa29a523a_uniq` (`defaultconfiguration_id`,`group_id`),
  KEY `defaultconfiguration_groups_3c818360` (`defaultconfiguration_id`),
  KEY `defaultconfiguration_groups_5f412f9a` (`group_id`),
  CONSTRAINT `group_id_refs_id_cbed91a7` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `defaultconfiguration_id_refs_id_b639c3b2` FOREIGN KEY (`defaultconfiguration_id`) REFERENCES `desktop_defaultconfiguration` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `defaultconfiguration_groups`
--

LOCK TABLES `defaultconfiguration_groups` WRITE;
/*!40000 ALTER TABLE `defaultconfiguration_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `defaultconfiguration_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `desktop_defaultconfiguration`
--

DROP TABLE IF EXISTS `desktop_defaultconfiguration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `desktop_defaultconfiguration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(32) NOT NULL,
  `properties` longtext NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `desktop_defaultconfiguration_60fc113e` (`app`),
  KEY `desktop_defaultconfiguration_d2c4b3f2` (`is_default`),
  KEY `desktop_defaultconfiguration_6340c63c` (`user_id`),
  CONSTRAINT `user_id_refs_id_5d426dc2` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `desktop_defaultconfiguration`
--

LOCK TABLES `desktop_defaultconfiguration` WRITE;
/*!40000 ALTER TABLE `desktop_defaultconfiguration` DISABLE KEYS */;
/*!40000 ALTER TABLE `desktop_defaultconfiguration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `desktop_document`
--

DROP TABLE IF EXISTS `desktop_document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `desktop_document` (
  `description` longtext NOT NULL,
  `extra` longtext NOT NULL,
  `object_id` int(10) unsigned NOT NULL,
  `last_modified` datetime NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `version` smallint(6) NOT NULL,
  `owner_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `desktop_document_content_type_id_24066d293ce4f1bf_uniq` (`content_type_id`,`object_id`),
  KEY `desktop_document_5ccb38e5` (`last_modified`),
  KEY `desktop_document_37ef4eb4` (`content_type_id`),
  KEY `desktop_document_cb902d83` (`owner_id`),
  CONSTRAINT `content_type_id_refs_id_800664c4` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `owner_id_refs_id_6062a036` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `desktop_document`
--

LOCK TABLES `desktop_document` WRITE;
/*!40000 ALTER TABLE `desktop_document` DISABLE KEYS */;
INSERT INTO `desktop_document` VALUES ('Top salary 2007 above $100k','0',1,'2018-06-19 06:16:03',58,1,1100713,1,'Sample: Top salary'),('Salary growth (sorted) from 2007-08','0',2,'2018-06-19 06:16:03',58,1,1100713,2,'Sample: Salary growth'),('Job loss among the top earners 2007-08','0',3,'2018-06-19 06:16:03',58,1,1100713,3,'Sample: Job loss'),('Email Survey Opt-Ins, Customers for Shipping ZIP Code, Total Amount per Order','0',4,'2018-06-19 06:16:03',58,1,1100713,4,'Sample: Customers'),('','',1,'2018-06-19 06:16:03',54,1,1100713,5,''),('','',2,'2018-06-19 06:16:03',54,1,1100713,6,'.Trash'),('','',3,'2018-06-19 06:16:03',54,1,1100713,7,'examples'),('Email Survey Opt-Ins, Customers for Shipping ZIP Code, Total Amount per Order','',7,'2018-06-19 06:16:03',54,1,1100713,8,'Sample: Customers'),('Job loss among the top earners 2007-08','',6,'2018-06-19 06:16:03',54,1,1100713,9,'Sample: Job loss'),('Salary growth (sorted) from 2007-08','',5,'2018-06-19 06:16:03',54,1,1100713,10,'Sample: Salary growth'),('Top salary 2007 above $100k','',4,'2018-06-19 06:16:03',54,1,1100713,11,'Sample: Top salary');
/*!40000 ALTER TABLE `desktop_document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `desktop_document2`
--

DROP TABLE IF EXISTS `desktop_document2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `desktop_document2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `owner_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `uuid` varchar(36) NOT NULL,
  `type` varchar(32) NOT NULL,
  `data` longtext NOT NULL,
  `extra` longtext NOT NULL,
  `last_modified` datetime NOT NULL,
  `version` smallint(6) NOT NULL,
  `is_history` tinyint(1) NOT NULL,
  `parent_directory_id` int(11),
  `search` longtext,
  `is_managed` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `desktop_document2_uuid_71ec93c81d6e68e7_uniq` (`uuid`,`version`,`is_history`),
  KEY `desktop_document2_cb902d83` (`owner_id`),
  KEY `desktop_document2_6f6e1b62` (`uuid`),
  KEY `desktop_document2_403d8ff3` (`type`),
  KEY `desktop_document2_5ccb38e5` (`last_modified`),
  KEY `desktop_document2_f516c2b3` (`version`),
  KEY `desktop_document2_dd08191e` (`is_history`),
  KEY `desktop_document2_9ffde453` (`parent_directory_id`),
  KEY `desktop_document2_0f116c0b` (`is_managed`),
  CONSTRAINT `owner_id_refs_id_04b63201` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `parent_directory_id_refs_id_4fe2babf` FOREIGN KEY (`parent_directory_id`) REFERENCES `desktop_document2` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `desktop_document2`
--

LOCK TABLES `desktop_document2` WRITE;
/*!40000 ALTER TABLE `desktop_document2` DISABLE KEYS */;
INSERT INTO `desktop_document2` VALUES (1,1100713,'','','a26755c4-fdd0-4dc8-b249-23a477f48a89','directory','{}','','2018-06-19 06:15:51',1,0,NULL,NULL,0),(2,1100713,'.Trash','','cf2ce463-5cc3-4b2f-b51a-ee1a032b0c78','directory','{}','','2018-06-19 06:15:51',1,0,1,NULL,0),(3,1100713,'examples','','5f1aa269-4ad6-4b60-ba6a-e6e929e38edb','directory','{}','','2018-06-19 06:15:51',1,0,1,NULL,0),(4,1100713,'Sample: Top salary','Top salary 2007 above $100k','d95852e3-54ea-4328-b844-65911df1f27e','query-hive','{\"showHistory\": true, \"description\": \"Top salary 2007 above $100k\", \"sessions\": [{\"type\": \"hive\", \"properties\": [{\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Files\", \"key\": \"files\", \"help_text\": \"Add one or more files, jars, or archives to the list of resources.\", \"type\": \"hdfs-files\"}, {\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Functions\", \"key\": \"functions\", \"help_text\": \"Add one or more registered UDFs (requires function name and fully-qualified class name).\", \"type\": \"functions\"}, {\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Settings\", \"key\": \"settings\", \"help_text\": \"Hive and Hadoop configuration properties.\", \"type\": \"settings\", \"options\": [\"hive.map.aggr\", \"hive.exec.compress.output\", \"hive.exec.parallel\", \"hive.execution.engine\", \"mapreduce.job.queuename\"]}], \"id\": null}], \"uuid\": \"d95852e3-54ea-4328-b844-65911df1f27e\", \"isSaved\": true, \"selectedSnippet\": \"hive\", \"type\": \"query-hive\", \"snippets\": [{\"status\": \"ready\", \"wasBatchExecuted\": false, \"name\": \"Sample: Top salary\", \"database\": \"default\", \"variables\": [], \"statement_raw\": \"SELECT sample_07.description, sample_07.salary\\r\\nFROM\\r\\n  sample_07\\r\\nWHERE\\r\\n( sample_07.salary > 100000)\\r\\nORDER BY sample_07.salary DESC\\r\\nLIMIT 1000\", \"id\": \"25a1725e-00ce-4501-9a5f-1dd14953889c\", \"result\": {}, \"statement\": \"SELECT sample_07.description, sample_07.salary\\r\\nFROM\\r\\n  sample_07\\r\\nWHERE\\r\\n( sample_07.salary > 100000)\\r\\nORDER BY sample_07.salary DESC\\r\\nLIMIT 1000\", \"type\": \"hive\", \"properties\": {\"files\": [], \"functions\": [], \"settings\": []}}], \"name\": \"Sample: Top salary\"}','','2018-06-19 06:15:51',1,0,3,NULL,0),(5,1100713,'Sample: Salary growth','Salary growth (sorted) from 2007-08','d4d3ba38-bf80-4225-9e43-fb126153a831','query-hive','{\"showHistory\": true, \"description\": \"Salary growth (sorted) from 2007-08\", \"sessions\": [{\"type\": \"hive\", \"properties\": [{\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Files\", \"key\": \"files\", \"help_text\": \"Add one or more files, jars, or archives to the list of resources.\", \"type\": \"hdfs-files\"}, {\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Functions\", \"key\": \"functions\", \"help_text\": \"Add one or more registered UDFs (requires function name and fully-qualified class name).\", \"type\": \"functions\"}, {\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Settings\", \"key\": \"settings\", \"help_text\": \"Hive and Hadoop configuration properties.\", \"type\": \"settings\", \"options\": [\"hive.map.aggr\", \"hive.exec.compress.output\", \"hive.exec.parallel\", \"hive.execution.engine\", \"mapreduce.job.queuename\"]}], \"id\": null}], \"uuid\": \"d4d3ba38-bf80-4225-9e43-fb126153a831\", \"isSaved\": true, \"selectedSnippet\": \"hive\", \"type\": \"query-hive\", \"snippets\": [{\"status\": \"ready\", \"wasBatchExecuted\": false, \"name\": \"Sample: Salary growth\", \"database\": \"default\", \"variables\": [], \"statement_raw\": \"SELECT s07.description, s07.salary, s08.salary,\\r\\n  s08.salary - s07.salary\\r\\nFROM\\r\\n  sample_07 s07 JOIN sample_08 s08\\r\\nON ( s07.code = s08.code)\\r\\nWHERE\\r\\n s07.salary < s08.salary\\r\\nORDER BY s08.salary-s07.salary DESC\\r\\nLIMIT 1000\", \"id\": \"d140870f-ec94-4a85-b449-f060a5d62ac5\", \"result\": {}, \"statement\": \"SELECT s07.description, s07.salary, s08.salary,\\r\\n  s08.salary - s07.salary\\r\\nFROM\\r\\n  sample_07 s07 JOIN sample_08 s08\\r\\nON ( s07.code = s08.code)\\r\\nWHERE\\r\\n s07.salary < s08.salary\\r\\nORDER BY s08.salary-s07.salary DESC\\r\\nLIMIT 1000\", \"type\": \"hive\", \"properties\": {\"files\": [], \"functions\": [], \"settings\": []}}], \"name\": \"Sample: Salary growth\"}','','2018-06-19 06:15:51',1,0,3,NULL,0),(6,1100713,'Sample: Job loss','Job loss among the top earners 2007-08','330c03f7-943b-471f-a069-652e25a2c672','query-hive','{\"showHistory\": true, \"description\": \"Job loss among the top earners 2007-08\", \"sessions\": [{\"type\": \"hive\", \"properties\": [{\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Files\", \"key\": \"files\", \"help_text\": \"Add one or more files, jars, or archives to the list of resources.\", \"type\": \"hdfs-files\"}, {\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Functions\", \"key\": \"functions\", \"help_text\": \"Add one or more registered UDFs (requires function name and fully-qualified class name).\", \"type\": \"functions\"}, {\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Settings\", \"key\": \"settings\", \"help_text\": \"Hive and Hadoop configuration properties.\", \"type\": \"settings\", \"options\": [\"hive.map.aggr\", \"hive.exec.compress.output\", \"hive.exec.parallel\", \"hive.execution.engine\", \"mapreduce.job.queuename\"]}], \"id\": null}], \"uuid\": \"330c03f7-943b-471f-a069-652e25a2c672\", \"isSaved\": true, \"selectedSnippet\": \"hive\", \"type\": \"query-hive\", \"snippets\": [{\"status\": \"ready\", \"wasBatchExecuted\": false, \"name\": \"Sample: Job loss\", \"database\": \"default\", \"variables\": [], \"statement_raw\": \"SELECT s07.description, s07.total_emp, s08.total_emp, s07.salary\\r\\nFROM\\r\\n  sample_07 s07 JOIN \\r\\n  sample_08 s08\\r\\nON ( s07.code = s08.code )\\r\\nWHERE\\r\\n( s07.total_emp > s08.total_emp\\r\\n AND s07.salary > 100000 )\\r\\nORDER BY s07.salary DESC\\nLIMIT 1000\", \"id\": \"0351736f-599c-4c35-8036-11b6bf77a38e\", \"result\": {}, \"statement\": \"SELECT s07.description, s07.total_emp, s08.total_emp, s07.salary\\r\\nFROM\\r\\n  sample_07 s07 JOIN \\r\\n  sample_08 s08\\r\\nON ( s07.code = s08.code )\\r\\nWHERE\\r\\n( s07.total_emp > s08.total_emp\\r\\n AND s07.salary > 100000 )\\r\\nORDER BY s07.salary DESC\\nLIMIT 1000\", \"type\": \"hive\", \"properties\": {\"files\": [], \"functions\": [], \"settings\": []}}], \"name\": \"Sample: Job loss\"}','','2018-06-19 06:15:51',1,0,3,NULL,0),(7,1100713,'Sample: Customers','Email Survey Opt-Ins, Customers for Shipping ZIP Code, Total Amount per Order','30aebc49-ec9c-4754-93c7-fa861d57d8d7','query-hive','{\"showHistory\": true, \"description\": \"Email Survey Opt-Ins, Customers for Shipping ZIP Code, Total Amount per Order\", \"sessions\": [{\"type\": \"hive\", \"properties\": [{\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Files\", \"key\": \"files\", \"help_text\": \"Add one or more files, jars, or archives to the list of resources.\", \"type\": \"hdfs-files\"}, {\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Functions\", \"key\": \"functions\", \"help_text\": \"Add one or more registered UDFs (requires function name and fully-qualified class name).\", \"type\": \"functions\"}, {\"multiple\": true, \"defaultValue\": [], \"value\": [], \"nice_name\": \"Settings\", \"key\": \"settings\", \"help_text\": \"Hive and Hadoop configuration properties.\", \"type\": \"settings\", \"options\": [\"hive.map.aggr\", \"hive.exec.compress.output\", \"hive.exec.parallel\", \"hive.execution.engine\", \"mapreduce.job.queuename\"]}], \"id\": null}], \"uuid\": \"30aebc49-ec9c-4754-93c7-fa861d57d8d7\", \"isSaved\": true, \"selectedSnippet\": \"hive\", \"type\": \"query-hive\", \"snippets\": [{\"status\": \"ready\", \"wasBatchExecuted\": false, \"name\": \"Sample: Customers\", \"database\": \"default\", \"variables\": [], \"statement_raw\": \"-- Get email survey opt-in values for all customers\\nSELECT\\r\\n  c.id,\\r\\n  c.name,\\r\\n  c.email_preferences.categories.surveys\\r\\nFROM customers c;\\n\\n\\n\\n-- Select customers for a given shipping ZIP Code\\nSELECT\\r\\n  customers.id,\\r\\n  customers.name\\r\\nFROM customers\\r\\nWHERE customers.addresses[\'shipping\'].zip_code = \'76710\';\\n\\n\\n\\n-- Compute total amount per order for all customers\\nSELECT\\r\\n  c.id AS customer_id,\\r\\n  c.name AS customer_name,\\r\\n  ords.order_id AS order_id,\\r\\n  SUM(order_items.price * order_items.qty) AS total_amount\\r\\nFROM\\r\\n  customers c\\r\\nLATERAL VIEW EXPLODE(c.orders) o AS ords\\r\\nLATERAL VIEW EXPLODE(ords.items) i AS order_items\\r\\nGROUP BY c.id, c.name, ords.order_id;\", \"id\": \"0a93dae4-d677-444f-9f0e-0aa3254db3a2\", \"result\": {}, \"statement\": \"-- Get email survey opt-in values for all customers\\nSELECT\\r\\n  c.id,\\r\\n  c.name,\\r\\n  c.email_preferences.categories.surveys\\r\\nFROM customers c;\\n\\n\\n\\n-- Select customers for a given shipping ZIP Code\\nSELECT\\r\\n  customers.id,\\r\\n  customers.name\\r\\nFROM customers\\r\\nWHERE customers.addresses[\'shipping\'].zip_code = \'76710\';\\n\\n\\n\\n-- Compute total amount per order for all customers\\nSELECT\\r\\n  c.id AS customer_id,\\r\\n  c.name AS customer_name,\\r\\n  ords.order_id AS order_id,\\r\\n  SUM(order_items.price * order_items.qty) AS total_amount\\r\\nFROM\\r\\n  customers c\\r\\nLATERAL VIEW EXPLODE(c.orders) o AS ords\\r\\nLATERAL VIEW EXPLODE(ords.items) i AS order_items\\r\\nGROUP BY c.id, c.name, ords.order_id;\", \"type\": \"hive\", \"properties\": {\"files\": [], \"functions\": [], \"settings\": []}}], \"name\": \"Sample: Customers\"}','','2018-06-19 06:15:51',1,0,3,NULL,0);
/*!40000 ALTER TABLE `desktop_document2` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `desktop_document2_dependencies`
--

DROP TABLE IF EXISTS `desktop_document2_dependencies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `desktop_document2_dependencies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_document2_id` int(11) NOT NULL,
  `to_document2_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `desktop_document2_depen_from_document2_id_180cf2c525720117_uniq` (`from_document2_id`,`to_document2_id`),
  KEY `desktop_document2_dependencies_5248ab40` (`from_document2_id`),
  KEY `desktop_document2_dependencies_19db1b82` (`to_document2_id`),
  CONSTRAINT `to_document2_id_refs_id_a2dfdbb8` FOREIGN KEY (`to_document2_id`) REFERENCES `desktop_document2` (`id`),
  CONSTRAINT `from_document2_id_refs_id_a2dfdbb8` FOREIGN KEY (`from_document2_id`) REFERENCES `desktop_document2` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `desktop_document2_dependencies`
--

LOCK TABLES `desktop_document2_dependencies` WRITE;
/*!40000 ALTER TABLE `desktop_document2_dependencies` DISABLE KEYS */;
/*!40000 ALTER TABLE `desktop_document2_dependencies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `desktop_document2permission`
--

DROP TABLE IF EXISTS `desktop_document2permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `desktop_document2permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `doc_id` int(11) NOT NULL,
  `perms` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `desktop_document2permission_doc_id_103d6b15a9f268ba_uniq` (`doc_id`,`perms`),
  KEY `desktop_document2permission_fbbb6049` (`doc_id`),
  KEY `desktop_document2permission_148edb5b` (`perms`),
  CONSTRAINT `doc_id_refs_id_8784c160` FOREIGN KEY (`doc_id`) REFERENCES `desktop_document2` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `desktop_document2permission`
--

LOCK TABLES `desktop_document2permission` WRITE;
/*!40000 ALTER TABLE `desktop_document2permission` DISABLE KEYS */;
INSERT INTO `desktop_document2permission` VALUES (1,3,'read'),(2,4,'read'),(3,5,'read'),(4,6,'read'),(5,7,'read');
/*!40000 ALTER TABLE `desktop_document2permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `desktop_document_tags`
--

DROP TABLE IF EXISTS `desktop_document_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `desktop_document_tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `document_id` int(11) NOT NULL,
  `documenttag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `desktop_document_tags_document_id_22435f97005dd9b0_uniq` (`document_id`,`documenttag_id`),
  KEY `desktop_document_tags_b7398729` (`document_id`),
  KEY `desktop_document_tags_21e9f328` (`documenttag_id`),
  CONSTRAINT `documenttag_id_refs_id_f5f1db6f` FOREIGN KEY (`documenttag_id`) REFERENCES `desktop_documenttag` (`id`),
  CONSTRAINT `document_id_refs_id_599007de` FOREIGN KEY (`document_id`) REFERENCES `desktop_document` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `desktop_document_tags`
--

LOCK TABLES `desktop_document_tags` WRITE;
/*!40000 ALTER TABLE `desktop_document_tags` DISABLE KEYS */;
INSERT INTO `desktop_document_tags` VALUES (1,1,1),(2,2,1),(3,3,1),(4,4,1),(5,5,1),(6,6,1),(7,7,1),(8,8,1),(9,9,1),(10,10,1),(11,11,1);
/*!40000 ALTER TABLE `desktop_document_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `desktop_documentpermission`
--

DROP TABLE IF EXISTS `desktop_documentpermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `desktop_documentpermission` (
  `perms` varchar(10) NOT NULL,
  `doc_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `desktop_documentpermission_doc_id_60b132dd84ab9469_uniq` (`doc_id`,`perms`),
  KEY `desktop_documentpermission_fbbb6049` (`doc_id`),
  CONSTRAINT `doc_id_refs_id_6e61f686` FOREIGN KEY (`doc_id`) REFERENCES `desktop_document` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `desktop_documentpermission`
--

LOCK TABLES `desktop_documentpermission` WRITE;
/*!40000 ALTER TABLE `desktop_documentpermission` DISABLE KEYS */;
/*!40000 ALTER TABLE `desktop_documentpermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `desktop_documenttag`
--

DROP TABLE IF EXISTS `desktop_documenttag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `desktop_documenttag` (
  `owner_id` int(11) NOT NULL,
  `tag` varchar(50) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `desktop_documenttag_owner_id_1d5f76680ee9998b_uniq` (`owner_id`,`tag`),
  KEY `desktop_documenttag_cb902d83` (`owner_id`),
  KEY `desktop_documenttag_5659cca2` (`tag`),
  CONSTRAINT `owner_id_refs_id_a0e6eebe` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `desktop_documenttag`
--

LOCK TABLES `desktop_documenttag` WRITE;
/*!40000 ALTER TABLE `desktop_documenttag` DISABLE KEYS */;
INSERT INTO `desktop_documenttag` VALUES (1100713,'default',1);
/*!40000 ALTER TABLE `desktop_documenttag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `desktop_settings`
--

DROP TABLE IF EXISTS `desktop_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `desktop_settings` (
  `collect_usage` tinyint(1) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tours_and_tutorials` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `desktop_settings_02d738b3` (`collect_usage`),
  KEY `desktop_settings_73ca4b20` (`tours_and_tutorials`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `desktop_settings`
--

LOCK TABLES `desktop_settings` WRITE;
/*!40000 ALTER TABLE `desktop_settings` DISABLE KEYS */;
INSERT INTO `desktop_settings` VALUES (1,1,1);
/*!40000 ALTER TABLE `desktop_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `desktop_userpreferences`
--

DROP TABLE IF EXISTS `desktop_userpreferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `desktop_userpreferences` (
  `value` longtext NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `desktop_userpreferences_6340c63c` (`user_id`),
  CONSTRAINT `user_id_refs_id_6de51743` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `desktop_userpreferences`
--

LOCK TABLES `desktop_userpreferences` WRITE;
/*!40000 ALTER TABLE `desktop_userpreferences` DISABLE KEYS */;
/*!40000 ALTER TABLE `desktop_userpreferences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_6340c63c` (`user_id`),
  KEY `django_admin_log_37ef4eb4` (`content_type_id`),
  CONSTRAINT `user_id_refs_id_c0d12874` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `content_type_id_refs_id_93d2d1f8` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission'),(2,'group','auth','group'),(3,'user','auth','user'),(4,'nonce','django_openid_auth','nonce'),(5,'association','django_openid_auth','association'),(6,'user open id','django_openid_auth','useropenid'),(7,'content type','contenttypes','contenttype'),(8,'session','sessions','session'),(9,'site','sites','site'),(10,'log entry','admin','logentry'),(11,'migration history','south','migrationhistory'),(12,'access attempt','axes','accessattempt'),(13,'access log','axes','accesslog'),(14,'workflow','oozie','workflow'),(15,'coordinator','oozie','coordinator'),(16,'bundle','oozie','bundle'),(18,'pig script','pig','pigscript'),(19,'document','pig','document'),(20,'job','oozie','job'),(21,'link','oozie','link'),(22,'node','oozie','node'),(23,'mapreduce','oozie','mapreduce'),(24,'streaming','oozie','streaming'),(25,'java','oozie','java'),(26,'pig','oozie','pig'),(27,'hive','oozie','hive'),(28,'sqoop','oozie','sqoop'),(29,'ssh','oozie','ssh'),(30,'shell','oozie','shell'),(31,'dist cp','oozie','distcp'),(32,'fs','oozie','fs'),(33,'email','oozie','email'),(34,'sub workflow','oozie','subworkflow'),(35,'generic','oozie','generic'),(36,'start','oozie','start'),(37,'end','oozie','end'),(38,'kill','oozie','kill'),(39,'fork','oozie','fork'),(40,'join','oozie','join'),(41,'decision','oozie','decision'),(42,'decision end','oozie','decisionend'),(43,'dataset','oozie','dataset'),(44,'data input','oozie','datainput'),(45,'data output','oozie','dataoutput'),(46,'bundled coordinator','oozie','bundledcoordinator'),(47,'history','oozie','history'),(48,'user preferences','desktop','userpreferences'),(49,'settings','desktop','settings'),(50,'default configuration','desktop','defaultconfiguration'),(51,'document tag','desktop','documenttag'),(52,'document','desktop','document'),(53,'document permission','desktop','documentpermission'),(54,'document2','desktop','document2'),(55,'document2 permission','desktop','document2permission'),(56,'directory','desktop','directory'),(57,'query history','beeswax','queryhistory'),(58,'saved query','beeswax','savedquery'),(59,'session','beeswax','session'),(60,'meta install','beeswax','metainstall'),(61,'hive server query history','beeswax','hiveserverqueryhistory'),(62,'job design','jobsub','jobdesign'),(63,'check for setup','jobsub','checkforsetup'),(64,'oozie action','jobsub','oozieaction'),(65,'oozie design','jobsub','ooziedesign'),(66,'oozie mapreduce action','jobsub','ooziemapreduceaction'),(67,'oozie streaming action','jobsub','ooziestreamingaction'),(68,'oozie java action','jobsub','ooziejavaaction'),(69,'job history','jobsub','jobhistory'),(70,'facet','search','facet'),(71,'result','search','result'),(72,'sorting','search','sorting'),(73,'collection','search','collection'),(74,'user profile','useradmin','userprofile'),(75,'ldap group','useradmin','ldapgroup'),(76,'group permission','useradmin','grouppermission'),(77,'hue permission','useradmin','huepermission');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_openid_auth_association`
--

DROP TABLE IF EXISTS `django_openid_auth_association`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_openid_auth_association` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_url` longtext NOT NULL,
  `handle` varchar(255) NOT NULL,
  `secret` longtext NOT NULL,
  `issued` int(11) NOT NULL,
  `lifetime` int(11) NOT NULL,
  `assoc_type` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_openid_auth_association`
--

LOCK TABLES `django_openid_auth_association` WRITE;
/*!40000 ALTER TABLE `django_openid_auth_association` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_openid_auth_association` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_openid_auth_nonce`
--

DROP TABLE IF EXISTS `django_openid_auth_nonce`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_openid_auth_nonce` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_url` varchar(1000) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `salt` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_openid_auth_nonce`
--

LOCK TABLES `django_openid_auth_nonce` WRITE;
/*!40000 ALTER TABLE `django_openid_auth_nonce` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_openid_auth_nonce` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_openid_auth_useropenid`
--

DROP TABLE IF EXISTS `django_openid_auth_useropenid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_openid_auth_useropenid` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `claimed_id` varchar(255) NOT NULL,
  `display_id` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `claimed_id` (`claimed_id`),
  KEY `django_openid_auth_useropenid_6340c63c` (`user_id`),
  CONSTRAINT `user_id_refs_id_8f018ae0` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_openid_auth_useropenid`
--

LOCK TABLES `django_openid_auth_useropenid` WRITE;
/*!40000 ALTER TABLE `django_openid_auth_useropenid` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_openid_auth_useropenid` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_b7b81f0c` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('94ql9fbxwdgtcjua9wylhqasffc4ddkv','NGI4MWI5ZGZhMjlkNjEzYzU5ZWZlZjBlOGE2ZjIwMzc4YjgzYzE3Mzp7InRlc3Rjb29raWUiOiJ3b3JrZWQifQ==','2018-07-03 06:14:47'),('ugbkckpvpthnvnrr4xriihxbbhtx0dw9','NTZhM2JkYzJjZTI5YjdlY2E3OWMwMmE3MTAxNDdiMjI2ODAxZWFjYjp7Il9hdXRoX3VzZXJfYmFja2VuZCI6ImRlc2t0b3AuYXV0aC5iYWNrZW5kLkFsbG93Rmlyc3RVc2VyRGphbmdvQmFja2VuZCIsIl9hdXRoX3VzZXJfaWQiOjF9','2018-07-03 06:14:50');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documentpermission2_groups`
--

DROP TABLE IF EXISTS `documentpermission2_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `documentpermission2_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `document2permission_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `documentpermission_document2permission_id_153e37c3da5a9480_uniq` (`document2permission_id`,`group_id`),
  KEY `documentpermission2_groups_7a114f0f` (`document2permission_id`),
  KEY `documentpermission2_groups_5f412f9a` (`group_id`),
  CONSTRAINT `group_id_refs_id_cae4462f` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `document2permission_id_refs_id_1ab9731a` FOREIGN KEY (`document2permission_id`) REFERENCES `desktop_document2permission` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documentpermission2_groups`
--

LOCK TABLES `documentpermission2_groups` WRITE;
/*!40000 ALTER TABLE `documentpermission2_groups` DISABLE KEYS */;
INSERT INTO `documentpermission2_groups` VALUES (13,1,1),(17,2,1),(16,3,1),(15,4,1),(14,5,1);
/*!40000 ALTER TABLE `documentpermission2_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documentpermission2_users`
--

DROP TABLE IF EXISTS `documentpermission2_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `documentpermission2_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `document2permission_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `documentpermission_document2permission_id_68f73063f13e5b46_uniq` (`document2permission_id`,`user_id`),
  KEY `documentpermission2_users_7a114f0f` (`document2permission_id`),
  KEY `documentpermission2_users_6340c63c` (`user_id`),
  CONSTRAINT `user_id_refs_id_ca751e07` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `document2permission_id_refs_id_9e0e3849` FOREIGN KEY (`document2permission_id`) REFERENCES `desktop_document2permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documentpermission2_users`
--

LOCK TABLES `documentpermission2_users` WRITE;
/*!40000 ALTER TABLE `documentpermission2_users` DISABLE KEYS */;
/*!40000 ALTER TABLE `documentpermission2_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documentpermission_groups`
--

DROP TABLE IF EXISTS `documentpermission_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `documentpermission_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `documentpermission_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `documentpermission__documentpermission_id_69436afd449228fe_uniq` (`documentpermission_id`,`group_id`),
  KEY `documentpermission_groups_35c59db1` (`documentpermission_id`),
  KEY `documentpermission_groups_5f412f9a` (`group_id`),
  CONSTRAINT `group_id_refs_id_dcacd481` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `documentpermission_id_refs_id_b50c1f1d` FOREIGN KEY (`documentpermission_id`) REFERENCES `desktop_documentpermission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documentpermission_groups`
--

LOCK TABLES `documentpermission_groups` WRITE;
/*!40000 ALTER TABLE `documentpermission_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `documentpermission_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documentpermission_users`
--

DROP TABLE IF EXISTS `documentpermission_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `documentpermission_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `documentpermission_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `documentpermission__documentpermission_id_6577517b9e586968_uniq` (`documentpermission_id`,`user_id`),
  KEY `documentpermission_users_35c59db1` (`documentpermission_id`),
  KEY `documentpermission_users_6340c63c` (`user_id`),
  CONSTRAINT `user_id_refs_id_70816365` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `documentpermission_id_refs_id_b8222d7f` FOREIGN KEY (`documentpermission_id`) REFERENCES `desktop_documentpermission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documentpermission_users`
--

LOCK TABLES `documentpermission_users` WRITE;
/*!40000 ALTER TABLE `documentpermission_users` DISABLE KEYS */;
/*!40000 ALTER TABLE `documentpermission_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobsub_checkforsetup`
--

DROP TABLE IF EXISTS `jobsub_checkforsetup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jobsub_checkforsetup` (
  `setup_run` tinyint(1) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `setup_level` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobsub_checkforsetup`
--

LOCK TABLES `jobsub_checkforsetup` WRITE;
/*!40000 ALTER TABLE `jobsub_checkforsetup` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobsub_checkforsetup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobsub_jobdesign`
--

DROP TABLE IF EXISTS `jobsub_jobdesign`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jobsub_jobdesign` (
  `description` varchar(1024) NOT NULL,
  `data` longtext NOT NULL,
  `last_modified` datetime NOT NULL,
  `owner_id` int(11) NOT NULL,
  `type` varchar(128) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jobsub_jobdesign_cb902d83` (`owner_id`),
  CONSTRAINT `owner_id_refs_id_753082e9` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobsub_jobdesign`
--

LOCK TABLES `jobsub_jobdesign` WRITE;
/*!40000 ALTER TABLE `jobsub_jobdesign` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobsub_jobdesign` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobsub_jobhistory`
--

DROP TABLE IF EXISTS `jobsub_jobhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jobsub_jobhistory` (
  `owner_id` int(11) NOT NULL,
  `submission_date` datetime NOT NULL,
  `design_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `job_id` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jobsub_jobhistory_cb902d83` (`owner_id`),
  KEY `jobsub_jobhistory_38ebade8` (`design_id`),
  CONSTRAINT `design_id_refs_id_5e12bb2f` FOREIGN KEY (`design_id`) REFERENCES `jobsub_ooziedesign` (`id`),
  CONSTRAINT `owner_id_refs_id_58370e7c` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobsub_jobhistory`
--

LOCK TABLES `jobsub_jobhistory` WRITE;
/*!40000 ALTER TABLE `jobsub_jobhistory` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobsub_jobhistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobsub_oozieaction`
--

DROP TABLE IF EXISTS `jobsub_oozieaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jobsub_oozieaction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_type` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobsub_oozieaction`
--

LOCK TABLES `jobsub_oozieaction` WRITE;
/*!40000 ALTER TABLE `jobsub_oozieaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobsub_oozieaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobsub_ooziedesign`
--

DROP TABLE IF EXISTS `jobsub_ooziedesign`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jobsub_ooziedesign` (
  `description` varchar(1024) NOT NULL,
  `last_modified` datetime NOT NULL,
  `owner_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `root_action_id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jobsub_ooziedesign_cb902d83` (`owner_id`),
  KEY `jobsub_ooziedesign_ce106e64` (`root_action_id`),
  CONSTRAINT `root_action_id_refs_id_26319073` FOREIGN KEY (`root_action_id`) REFERENCES `jobsub_oozieaction` (`id`),
  CONSTRAINT `owner_id_refs_id_55551230` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobsub_ooziedesign`
--

LOCK TABLES `jobsub_ooziedesign` WRITE;
/*!40000 ALTER TABLE `jobsub_ooziedesign` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobsub_ooziedesign` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobsub_ooziejavaaction`
--

DROP TABLE IF EXISTS `jobsub_ooziejavaaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jobsub_ooziejavaaction` (
  `oozieaction_ptr_id` int(11) NOT NULL,
  `files` varchar(512) NOT NULL,
  `jar_path` varchar(512) NOT NULL,
  `java_opts` varchar(256) NOT NULL,
  `args` longtext NOT NULL,
  `job_properties` longtext NOT NULL,
  `archives` varchar(512) NOT NULL,
  `main_class` varchar(256) NOT NULL,
  PRIMARY KEY (`oozieaction_ptr_id`),
  CONSTRAINT `oozieaction_ptr_id_refs_id_890da3c3` FOREIGN KEY (`oozieaction_ptr_id`) REFERENCES `jobsub_oozieaction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobsub_ooziejavaaction`
--

LOCK TABLES `jobsub_ooziejavaaction` WRITE;
/*!40000 ALTER TABLE `jobsub_ooziejavaaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobsub_ooziejavaaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobsub_ooziemapreduceaction`
--

DROP TABLE IF EXISTS `jobsub_ooziemapreduceaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jobsub_ooziemapreduceaction` (
  `oozieaction_ptr_id` int(11) NOT NULL,
  `files` varchar(512) NOT NULL,
  `jar_path` varchar(512) NOT NULL,
  `archives` varchar(512) NOT NULL,
  `job_properties` longtext NOT NULL,
  PRIMARY KEY (`oozieaction_ptr_id`),
  CONSTRAINT `oozieaction_ptr_id_refs_id_85f71d45` FOREIGN KEY (`oozieaction_ptr_id`) REFERENCES `jobsub_oozieaction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobsub_ooziemapreduceaction`
--

LOCK TABLES `jobsub_ooziemapreduceaction` WRITE;
/*!40000 ALTER TABLE `jobsub_ooziemapreduceaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobsub_ooziemapreduceaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobsub_ooziestreamingaction`
--

DROP TABLE IF EXISTS `jobsub_ooziestreamingaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jobsub_ooziestreamingaction` (
  `oozieaction_ptr_id` int(11) NOT NULL,
  `files` varchar(512) NOT NULL,
  `mapper` varchar(512) NOT NULL,
  `reducer` varchar(512) NOT NULL,
  `job_properties` longtext NOT NULL,
  `archives` varchar(512) NOT NULL,
  PRIMARY KEY (`oozieaction_ptr_id`),
  CONSTRAINT `oozieaction_ptr_id_refs_id_6dad0be7` FOREIGN KEY (`oozieaction_ptr_id`) REFERENCES `jobsub_oozieaction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobsub_ooziestreamingaction`
--

LOCK TABLES `jobsub_ooziestreamingaction` WRITE;
/*!40000 ALTER TABLE `jobsub_ooziestreamingaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `jobsub_ooziestreamingaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_bundle`
--

DROP TABLE IF EXISTS `oozie_bundle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_bundle` (
  `kick_off_time` datetime NOT NULL,
  `job_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`job_ptr_id`),
  CONSTRAINT `job_ptr_id_refs_id_dfe854cc` FOREIGN KEY (`job_ptr_id`) REFERENCES `oozie_job` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_bundle`
--

LOCK TABLES `oozie_bundle` WRITE;
/*!40000 ALTER TABLE `oozie_bundle` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_bundle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_bundledcoordinator`
--

DROP TABLE IF EXISTS `oozie_bundledcoordinator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_bundledcoordinator` (
  `coordinator_id` int(11) NOT NULL,
  `parameters` longtext NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bundle_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `oozie_bundledcoordinator_a376e044` (`coordinator_id`),
  KEY `oozie_bundledcoordinator_2243b87b` (`bundle_id`),
  CONSTRAINT `bundle_id_refs_job_ptr_id_49f6b676` FOREIGN KEY (`bundle_id`) REFERENCES `oozie_bundle` (`job_ptr_id`),
  CONSTRAINT `coordinator_id_refs_job_ptr_id_4b9a476a` FOREIGN KEY (`coordinator_id`) REFERENCES `oozie_coordinator` (`job_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_bundledcoordinator`
--

LOCK TABLES `oozie_bundledcoordinator` WRITE;
/*!40000 ALTER TABLE `oozie_bundledcoordinator` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_bundledcoordinator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_coordinator`
--

DROP TABLE IF EXISTS `oozie_coordinator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_coordinator` (
  `end` datetime NOT NULL,
  `concurrency` smallint(5) unsigned DEFAULT NULL,
  `frequency_number` smallint(6) NOT NULL,
  `workflow_id` int(11) DEFAULT NULL,
  `job_ptr_id` int(11) NOT NULL,
  `frequency_unit` varchar(20) NOT NULL,
  `start` datetime NOT NULL,
  `timeout` smallint(6) DEFAULT NULL,
  `timezone` varchar(24) NOT NULL,
  `throttle` smallint(5) unsigned DEFAULT NULL,
  `execution` varchar(10) DEFAULT NULL,
  `job_properties` longtext NOT NULL,
  PRIMARY KEY (`job_ptr_id`),
  KEY `oozie_coordinator_17b2fdb1` (`workflow_id`),
  CONSTRAINT `job_ptr_id_refs_id_02836103` FOREIGN KEY (`job_ptr_id`) REFERENCES `oozie_job` (`id`),
  CONSTRAINT `workflow_id_refs_job_ptr_id_eff253f3` FOREIGN KEY (`workflow_id`) REFERENCES `oozie_workflow` (`job_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_coordinator`
--

LOCK TABLES `oozie_coordinator` WRITE;
/*!40000 ALTER TABLE `oozie_coordinator` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_coordinator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_datainput`
--

DROP TABLE IF EXISTS `oozie_datainput`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_datainput` (
  `coordinator_id` int(11) NOT NULL,
  `dataset_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dataset_id` (`dataset_id`),
  KEY `oozie_datainput_a376e044` (`coordinator_id`),
  CONSTRAINT `dataset_id_refs_id_6d9c387e` FOREIGN KEY (`dataset_id`) REFERENCES `oozie_dataset` (`id`),
  CONSTRAINT `coordinator_id_refs_job_ptr_id_a7f5bae4` FOREIGN KEY (`coordinator_id`) REFERENCES `oozie_coordinator` (`job_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_datainput`
--

LOCK TABLES `oozie_datainput` WRITE;
/*!40000 ALTER TABLE `oozie_datainput` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_datainput` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_dataoutput`
--

DROP TABLE IF EXISTS `oozie_dataoutput`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_dataoutput` (
  `coordinator_id` int(11) NOT NULL,
  `dataset_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dataset_id` (`dataset_id`),
  KEY `oozie_dataoutput_a376e044` (`coordinator_id`),
  CONSTRAINT `dataset_id_refs_id_c25267c2` FOREIGN KEY (`dataset_id`) REFERENCES `oozie_dataset` (`id`),
  CONSTRAINT `coordinator_id_refs_job_ptr_id_35e76a9d` FOREIGN KEY (`coordinator_id`) REFERENCES `oozie_coordinator` (`job_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_dataoutput`
--

LOCK TABLES `oozie_dataoutput` WRITE;
/*!40000 ALTER TABLE `oozie_dataoutput` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_dataoutput` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_dataset`
--

DROP TABLE IF EXISTS `oozie_dataset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_dataset` (
  `description` varchar(1024) NOT NULL,
  `frequency_number` smallint(6) NOT NULL,
  `coordinator_id` int(11) NOT NULL,
  `frequency_unit` varchar(20) NOT NULL,
  `uri` varchar(1024) NOT NULL,
  `start` datetime NOT NULL,
  `timezone` varchar(24) NOT NULL,
  `done_flag` varchar(64) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  `advanced_start_instance` varchar(128) NOT NULL,
  `instance_choice` varchar(10) NOT NULL,
  `advanced_end_instance` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `oozie_dataset_a376e044` (`coordinator_id`),
  CONSTRAINT `coordinator_id_refs_job_ptr_id_c1a45b56` FOREIGN KEY (`coordinator_id`) REFERENCES `oozie_coordinator` (`job_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_dataset`
--

LOCK TABLES `oozie_dataset` WRITE;
/*!40000 ALTER TABLE `oozie_dataset` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_dataset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_decision`
--

DROP TABLE IF EXISTS `oozie_decision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_decision` (
  `node_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_67bc250e` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_decision`
--

LOCK TABLES `oozie_decision` WRITE;
/*!40000 ALTER TABLE `oozie_decision` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_decision` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_decisionend`
--

DROP TABLE IF EXISTS `oozie_decisionend`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_decisionend` (
  `node_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_31e174a0` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_decisionend`
--

LOCK TABLES `oozie_decisionend` WRITE;
/*!40000 ALTER TABLE `oozie_decisionend` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_decisionend` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_distcp`
--

DROP TABLE IF EXISTS `oozie_distcp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_distcp` (
  `prepares` longtext NOT NULL,
  `job_xml` varchar(512) NOT NULL,
  `params` longtext NOT NULL,
  `job_properties` longtext NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_94a882fe` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_distcp`
--

LOCK TABLES `oozie_distcp` WRITE;
/*!40000 ALTER TABLE `oozie_distcp` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_distcp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_email`
--

DROP TABLE IF EXISTS `oozie_email`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_email` (
  `cc` longtext NOT NULL,
  `to` longtext NOT NULL,
  `subject` longtext NOT NULL,
  `body` longtext NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_a770716b` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_email`
--

LOCK TABLES `oozie_email` WRITE;
/*!40000 ALTER TABLE `oozie_email` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_email` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_end`
--

DROP TABLE IF EXISTS `oozie_end`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_end` (
  `node_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_d2ab2ce2` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_end`
--

LOCK TABLES `oozie_end` WRITE;
/*!40000 ALTER TABLE `oozie_end` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_end` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_fork`
--

DROP TABLE IF EXISTS `oozie_fork`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_fork` (
  `node_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_08311288` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_fork`
--

LOCK TABLES `oozie_fork` WRITE;
/*!40000 ALTER TABLE `oozie_fork` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_fork` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_fs`
--

DROP TABLE IF EXISTS `oozie_fs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_fs` (
  `mkdirs` longtext NOT NULL,
  `touchzs` longtext NOT NULL,
  `chmods` longtext NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  `moves` longtext NOT NULL,
  `deletes` longtext NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_f2c6c820` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_fs`
--

LOCK TABLES `oozie_fs` WRITE;
/*!40000 ALTER TABLE `oozie_fs` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_fs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_generic`
--

DROP TABLE IF EXISTS `oozie_generic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_generic` (
  `xml` longtext NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_52bde32b` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_generic`
--

LOCK TABLES `oozie_generic` WRITE;
/*!40000 ALTER TABLE `oozie_generic` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_generic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_history`
--

DROP TABLE IF EXISTS `oozie_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_history` (
  `submission_date` datetime NOT NULL,
  `job_id` int(11) NOT NULL,
  `properties` longtext NOT NULL,
  `oozie_job_id` varchar(128) NOT NULL,
  `submitter_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `oozie_history_0ebd36f3` (`submission_date`),
  KEY `oozie_history_218f3960` (`job_id`),
  KEY `oozie_history_5f7282ee` (`submitter_id`),
  CONSTRAINT `submitter_id_refs_id_be4aca60` FOREIGN KEY (`submitter_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `job_id_refs_id_aca84a0b` FOREIGN KEY (`job_id`) REFERENCES `oozie_job` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_history`
--

LOCK TABLES `oozie_history` WRITE;
/*!40000 ALTER TABLE `oozie_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_hive`
--

DROP TABLE IF EXISTS `oozie_hive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_hive` (
  `files` longtext NOT NULL,
  `job_xml` varchar(512) NOT NULL,
  `job_properties` longtext NOT NULL,
  `params` longtext NOT NULL,
  `archives` longtext NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  `prepares` longtext NOT NULL,
  `script_path` varchar(256) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_7061d230` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_hive`
--

LOCK TABLES `oozie_hive` WRITE;
/*!40000 ALTER TABLE `oozie_hive` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_hive` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_java`
--

DROP TABLE IF EXISTS `oozie_java`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_java` (
  `files` longtext NOT NULL,
  `job_xml` varchar(512) NOT NULL,
  `jar_path` varchar(512) NOT NULL,
  `java_opts` varchar(256) NOT NULL,
  `args` longtext NOT NULL,
  `job_properties` longtext NOT NULL,
  `prepares` longtext NOT NULL,
  `archives` longtext NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  `main_class` varchar(256) NOT NULL,
  `capture_output` tinyint(1) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_c5504fe4` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_java`
--

LOCK TABLES `oozie_java` WRITE;
/*!40000 ALTER TABLE `oozie_java` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_java` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_job`
--

DROP TABLE IF EXISTS `oozie_job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_job` (
  `is_shared` tinyint(1) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `parameters` longtext NOT NULL,
  `deployment_dir` varchar(1024) NOT NULL,
  `schema_version` varchar(128) NOT NULL,
  `last_modified` datetime NOT NULL,
  `owner_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `is_trashed` tinyint(1) NOT NULL,
  `data` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `oozie_job_b91b90da` (`is_shared`),
  KEY `oozie_job_5ccb38e5` (`last_modified`),
  KEY `oozie_job_cb902d83` (`owner_id`),
  KEY `oozie_job_863b5435` (`is_trashed`),
  CONSTRAINT `owner_id_refs_id_b9eb9598` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_job`
--

LOCK TABLES `oozie_job` WRITE;
/*!40000 ALTER TABLE `oozie_job` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_job` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_join`
--

DROP TABLE IF EXISTS `oozie_join`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_join` (
  `node_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_5fe5ad59` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_join`
--

LOCK TABLES `oozie_join` WRITE;
/*!40000 ALTER TABLE `oozie_join` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_join` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_kill`
--

DROP TABLE IF EXISTS `oozie_kill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_kill` (
  `message` varchar(256) NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_6a5609f4` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_kill`
--

LOCK TABLES `oozie_kill` WRITE;
/*!40000 ALTER TABLE `oozie_kill` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_kill` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_link`
--

DROP TABLE IF EXISTS `oozie_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_link` (
  `comment` varchar(1024) NOT NULL,
  `name` varchar(40) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL,
  `child_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `oozie_link_410d0aac` (`parent_id`),
  KEY `oozie_link_0b25fb00` (`child_id`),
  CONSTRAINT `child_id_refs_id_4c5f8d9b` FOREIGN KEY (`child_id`) REFERENCES `oozie_node` (`id`),
  CONSTRAINT `parent_id_refs_id_4c5f8d9b` FOREIGN KEY (`parent_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_link`
--

LOCK TABLES `oozie_link` WRITE;
/*!40000 ALTER TABLE `oozie_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_mapreduce`
--

DROP TABLE IF EXISTS `oozie_mapreduce`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_mapreduce` (
  `files` longtext NOT NULL,
  `job_xml` varchar(512) NOT NULL,
  `jar_path` varchar(512) NOT NULL,
  `job_properties` longtext NOT NULL,
  `archives` longtext NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  `prepares` longtext NOT NULL,
  UNIQUE KEY `node_ptr_id` (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_faafd42d` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_mapreduce`
--

LOCK TABLES `oozie_mapreduce` WRITE;
/*!40000 ALTER TABLE `oozie_mapreduce` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_mapreduce` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_node`
--

DROP TABLE IF EXISTS `oozie_node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_node` (
  `description` varchar(1024) NOT NULL,
  `workflow_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `node_type` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `data` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `oozie_node_17b2fdb1` (`workflow_id`),
  CONSTRAINT `workflow_id_refs_job_ptr_id_61733cb8` FOREIGN KEY (`workflow_id`) REFERENCES `oozie_workflow` (`job_ptr_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_node`
--

LOCK TABLES `oozie_node` WRITE;
/*!40000 ALTER TABLE `oozie_node` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_node` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_pig`
--

DROP TABLE IF EXISTS `oozie_pig`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_pig` (
  `files` longtext NOT NULL,
  `job_xml` varchar(512) NOT NULL,
  `job_properties` longtext NOT NULL,
  `params` longtext NOT NULL,
  `archives` longtext NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  `prepares` longtext NOT NULL,
  `script_path` varchar(256) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_3a145eb2` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_pig`
--

LOCK TABLES `oozie_pig` WRITE;
/*!40000 ALTER TABLE `oozie_pig` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_pig` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_shell`
--

DROP TABLE IF EXISTS `oozie_shell`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_shell` (
  `files` longtext NOT NULL,
  `job_xml` varchar(512) NOT NULL,
  `job_properties` longtext NOT NULL,
  `capture_output` tinyint(1) NOT NULL,
  `params` longtext NOT NULL,
  `archives` longtext NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  `prepares` longtext NOT NULL,
  `command` varchar(256) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_6a9f9c63` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_shell`
--

LOCK TABLES `oozie_shell` WRITE;
/*!40000 ALTER TABLE `oozie_shell` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_shell` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_sqoop`
--

DROP TABLE IF EXISTS `oozie_sqoop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_sqoop` (
  `files` longtext NOT NULL,
  `job_xml` varchar(512) NOT NULL,
  `job_properties` longtext NOT NULL,
  `params` longtext NOT NULL,
  `archives` longtext NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  `prepares` longtext NOT NULL,
  `script_path` longtext NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_51abc83b` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_sqoop`
--

LOCK TABLES `oozie_sqoop` WRITE;
/*!40000 ALTER TABLE `oozie_sqoop` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_sqoop` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_ssh`
--

DROP TABLE IF EXISTS `oozie_ssh`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_ssh` (
  `capture_output` tinyint(1) NOT NULL,
  `host` varchar(256) NOT NULL,
  `params` longtext NOT NULL,
  `user` varchar(64) NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  `command` varchar(256) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_e6a21afc` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_ssh`
--

LOCK TABLES `oozie_ssh` WRITE;
/*!40000 ALTER TABLE `oozie_ssh` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_ssh` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_start`
--

DROP TABLE IF EXISTS `oozie_start`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_start` (
  `node_ptr_id` int(11) NOT NULL,
  UNIQUE KEY `node_ptr_id` (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_ed4928be` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_start`
--

LOCK TABLES `oozie_start` WRITE;
/*!40000 ALTER TABLE `oozie_start` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_start` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_streaming`
--

DROP TABLE IF EXISTS `oozie_streaming`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_streaming` (
  `files` longtext NOT NULL,
  `mapper` varchar(512) NOT NULL,
  `reducer` varchar(512) NOT NULL,
  `job_properties` longtext NOT NULL,
  `archives` longtext NOT NULL,
  `node_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_5857900b` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_streaming`
--

LOCK TABLES `oozie_streaming` WRITE;
/*!40000 ALTER TABLE `oozie_streaming` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_streaming` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_subworkflow`
--

DROP TABLE IF EXISTS `oozie_subworkflow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_subworkflow` (
  `propagate_configuration` tinyint(1) NOT NULL,
  `job_properties` longtext NOT NULL,
  `sub_workflow_id` int(11),
  `node_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`node_ptr_id`),
  KEY `oozie_subworkflow_7c14fdc3` (`sub_workflow_id`),
  CONSTRAINT `sub_workflow_id_refs_job_ptr_id_b9cfb611` FOREIGN KEY (`sub_workflow_id`) REFERENCES `oozie_workflow` (`job_ptr_id`),
  CONSTRAINT `node_ptr_id_refs_id_9a2f74e6` FOREIGN KEY (`node_ptr_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_subworkflow`
--

LOCK TABLES `oozie_subworkflow` WRITE;
/*!40000 ALTER TABLE `oozie_subworkflow` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_subworkflow` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `oozie_workflow`
--

DROP TABLE IF EXISTS `oozie_workflow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oozie_workflow` (
  `job_xml` varchar(512) NOT NULL,
  `end_id` int(11) DEFAULT NULL,
  `is_single` tinyint(1) NOT NULL,
  `job_ptr_id` int(11) NOT NULL,
  `job_properties` longtext NOT NULL,
  `start_id` int(11) DEFAULT NULL,
  `managed` tinyint(1) NOT NULL,
  PRIMARY KEY (`job_ptr_id`),
  KEY `oozie_workflow_536e023f` (`end_id`),
  KEY `oozie_workflow_6f89268d` (`start_id`),
  CONSTRAINT `end_id_refs_id_92f16762` FOREIGN KEY (`end_id`) REFERENCES `oozie_node` (`id`),
  CONSTRAINT `job_ptr_id_refs_id_8bb519fb` FOREIGN KEY (`job_ptr_id`) REFERENCES `oozie_job` (`id`),
  CONSTRAINT `start_id_refs_id_92f16762` FOREIGN KEY (`start_id`) REFERENCES `oozie_node` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `oozie_workflow`
--

LOCK TABLES `oozie_workflow` WRITE;
/*!40000 ALTER TABLE `oozie_workflow` DISABLE KEYS */;
/*!40000 ALTER TABLE `oozie_workflow` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pig_document`
--

DROP TABLE IF EXISTS `pig_document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pig_document` (
  `owner_id` int(11) NOT NULL,
  `is_design` tinyint(1) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `pig_document_cb902d83` (`owner_id`),
  KEY `pig_document_63cbf1fe` (`is_design`),
  CONSTRAINT `owner_id_refs_id_8d390f80` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pig_document`
--

LOCK TABLES `pig_document` WRITE;
/*!40000 ALTER TABLE `pig_document` DISABLE KEYS */;
/*!40000 ALTER TABLE `pig_document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pig_pigscript`
--

DROP TABLE IF EXISTS `pig_pigscript`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pig_pigscript` (
  `document_ptr_id` int(11) NOT NULL,
  `data` longtext NOT NULL,
  PRIMARY KEY (`document_ptr_id`),
  CONSTRAINT `document_ptr_id_refs_id_17b4e137` FOREIGN KEY (`document_ptr_id`) REFERENCES `pig_document` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pig_pigscript`
--

LOCK TABLES `pig_pigscript` WRITE;
/*!40000 ALTER TABLE `pig_pigscript` DISABLE KEYS */;
/*!40000 ALTER TABLE `pig_pigscript` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `search_collection`
--

DROP TABLE IF EXISTS `search_collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `search_collection` (
  `properties` longtext NOT NULL,
  `sorting_id` int(11) NOT NULL,
  `name` varchar(40) NOT NULL,
  `facets_id` int(11) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `label` varchar(100) NOT NULL,
  `is_core_only` tinyint(1) NOT NULL,
  `result_id` int(11) NOT NULL,
  `cores` longtext NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `owner_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `search_collection_1ee0a855` (`sorting_id`),
  KEY `search_collection_be9133f8` (`facets_id`),
  KEY `search_collection_f41c4334` (`result_id`),
  KEY `search_collection_cb902d83` (`owner_id`),
  CONSTRAINT `owner_id_refs_id_fb75896c` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `facets_id_refs_id_109f7b9d` FOREIGN KEY (`facets_id`) REFERENCES `search_facet` (`id`),
  CONSTRAINT `result_id_refs_id_cef2c4d1` FOREIGN KEY (`result_id`) REFERENCES `search_result` (`id`),
  CONSTRAINT `sorting_id_refs_id_63666e75` FOREIGN KEY (`sorting_id`) REFERENCES `search_sorting` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `search_collection`
--

LOCK TABLES `search_collection` WRITE;
/*!40000 ALTER TABLE `search_collection` DISABLE KEYS */;
/*!40000 ALTER TABLE `search_collection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `search_facet`
--

DROP TABLE IF EXISTS `search_facet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `search_facet` (
  `data` longtext NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `search_facet`
--

LOCK TABLES `search_facet` WRITE;
/*!40000 ALTER TABLE `search_facet` DISABLE KEYS */;
/*!40000 ALTER TABLE `search_facet` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `search_result`
--

DROP TABLE IF EXISTS `search_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `search_result` (
  `data` longtext NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `search_result`
--

LOCK TABLES `search_result` WRITE;
/*!40000 ALTER TABLE `search_result` DISABLE KEYS */;
/*!40000 ALTER TABLE `search_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `search_sorting`
--

DROP TABLE IF EXISTS `search_sorting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `search_sorting` (
  `data` longtext NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `search_sorting`
--

LOCK TABLES `search_sorting` WRITE;
/*!40000 ALTER TABLE `search_sorting` DISABLE KEYS */;
/*!40000 ALTER TABLE `search_sorting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `south_migrationhistory`
--

DROP TABLE IF EXISTS `south_migrationhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `south_migrationhistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_name` varchar(255) NOT NULL,
  `migration` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `south_migrationhistory`
--

LOCK TABLES `south_migrationhistory` WRITE;
/*!40000 ALTER TABLE `south_migrationhistory` DISABLE KEYS */;
INSERT INTO `south_migrationhistory` VALUES (1,'django_extensions','0001_empty','2018-06-19 05:42:52'),(2,'pig','0001_initial','2018-06-19 05:42:52'),(3,'oozie','0001_initial','2018-06-19 05:42:53'),(4,'oozie','0002_auto__add_hive','2018-06-19 05:42:53'),(5,'oozie','0003_auto__add_sqoop','2018-06-19 05:42:53'),(6,'oozie','0004_auto__add_ssh','2018-06-19 05:42:53'),(7,'oozie','0005_auto__add_shell','2018-06-19 05:42:53'),(8,'oozie','0006_auto__chg_field_java_files__chg_field_java_archives__chg_field_sqoop_f','2018-06-19 05:42:53'),(9,'oozie','0007_auto__chg_field_sqoop_script_path','2018-06-19 05:42:53'),(10,'oozie','0008_auto__add_distcp','2018-06-19 05:42:53'),(11,'oozie','0009_auto__add_decision','2018-06-19 05:42:53'),(12,'oozie','0010_auto__add_fs','2018-06-19 05:42:53'),(13,'oozie','0011_auto__add_email','2018-06-19 05:42:53'),(14,'oozie','0012_auto__add_subworkflow__chg_field_email_subject__chg_field_email_body','2018-06-19 05:42:54'),(15,'oozie','0013_auto__add_generic','2018-06-19 05:42:54'),(16,'oozie','0014_auto__add_decisionend','2018-06-19 05:42:54'),(17,'oozie','0015_auto__add_field_dataset_advanced_start_instance__add_field_dataset_ins','2018-06-19 05:42:54'),(18,'oozie','0016_auto__add_field_coordinator_job_properties','2018-06-19 05:42:54'),(19,'oozie','0017_auto__add_bundledcoordinator__add_bundle','2018-06-19 05:42:54'),(20,'oozie','0018_auto__add_field_workflow_managed','2018-06-19 05:42:54'),(21,'oozie','0019_auto__add_field_java_capture_output','2018-06-19 05:42:54'),(22,'oozie','0020_chg_large_varchars_to_textfields','2018-06-19 05:42:55'),(23,'oozie','0021_auto__chg_field_java_args__add_field_job_is_trashed','2018-06-19 05:42:55'),(24,'oozie','0022_auto__chg_field_mapreduce_node_ptr__chg_field_start_node_ptr','2018-06-19 05:42:55'),(25,'oozie','0022_change_examples_path_format','2018-06-19 05:42:55'),(26,'oozie','0023_auto__add_field_node_data__add_field_job_data','2018-06-19 05:42:55'),(27,'oozie','0024_auto__chg_field_subworkflow_sub_workflow','2018-06-19 05:42:55'),(28,'oozie','0025_change_examples_path_format','2018-06-19 05:42:55'),(29,'desktop','0001_initial','2018-06-19 05:42:55'),(30,'desktop','0002_add_groups_and_homedirs','2018-06-19 05:42:55'),(31,'desktop','0003_group_permissions','2018-06-19 05:42:55'),(32,'desktop','0004_grouprelations','2018-06-19 05:42:55'),(33,'desktop','0005_settings','2018-06-19 05:42:55'),(34,'desktop','0006_settings_add_tour','2018-06-19 05:42:55'),(35,'beeswax','0001_initial','2018-06-19 05:42:55'),(36,'beeswax','0002_auto__add_field_queryhistory_notify','2018-06-19 05:42:55'),(37,'beeswax','0003_auto__add_field_queryhistory_server_name__add_field_queryhistory_serve','2018-06-19 05:42:56'),(38,'beeswax','0004_auto__add_session__add_field_queryhistory_server_type__add_field_query','2018-06-19 05:42:56'),(39,'beeswax','0005_auto__add_field_queryhistory_statement_number','2018-06-19 05:42:56'),(40,'beeswax','0006_auto__add_field_session_application','2018-06-19 05:42:56'),(41,'beeswax','0007_auto__add_field_savedquery_is_trashed','2018-06-19 05:42:56'),(42,'beeswax','0008_auto__add_field_queryhistory_query_type','2018-06-19 05:42:56'),(43,'desktop','0007_auto__add_documentpermission__add_documenttag__add_document','2018-06-19 05:42:56'),(44,'desktop','0008_documentpermission_m2m_tables','2018-06-19 05:42:56'),(45,'desktop','0009_auto__chg_field_document_name','2018-06-19 05:42:56'),(46,'desktop','0010_auto__add_document2__chg_field_userpreferences_key__chg_field_userpref','2018-06-19 05:42:57'),(47,'desktop','0011_auto__chg_field_document2_uuid','2018-06-19 05:42:57'),(48,'desktop','0012_auto__chg_field_documentpermission_perms','2018-06-19 05:42:57'),(49,'desktop','0013_auto__add_unique_documenttag_owner_tag','2018-06-19 05:42:57'),(50,'desktop','0014_auto__add_unique_document_content_type_object_id','2018-06-19 05:42:57'),(51,'desktop','0015_auto__add_unique_documentpermission_doc_perms','2018-06-19 05:42:57'),(52,'desktop','0016_auto__add_unique_document2_uuid_version_is_history','2018-06-19 05:42:57'),(53,'desktop','0017_auto__add_document2permission__add_unique_document2permission_doc_perm','2018-06-19 05:42:57'),(54,'desktop','0018_auto__add_field_document2_parent_directory','2018-06-19 05:42:57'),(55,'desktop','0019_auto','2018-06-19 05:42:57'),(56,'desktop','0020_auto__del_field_document2permission_all','2018-06-19 05:42:57'),(57,'desktop','0021_auto__add_defaultconfiguration__add_unique_defaultconfiguration_app_is','2018-06-19 05:42:57'),(58,'desktop','0022_auto__del_field_defaultconfiguration_group__del_unique_defaultconfigur','2018-06-19 05:42:57'),(59,'desktop','0023_auto__del_unique_defaultconfiguration_app_is_default_user__add_field_d','2018-06-19 05:42:57'),(60,'desktop','0024_auto__add_field_document2_is_managed','2018-06-19 05:42:57'),(61,'beeswax','0009_auto__add_field_savedquery_is_redacted__add_field_queryhistory_is_reda','2018-06-19 05:42:58'),(62,'beeswax','0009_auto__chg_field_queryhistory_server_port','2018-06-19 05:42:58'),(63,'beeswax','0010_merge_database_state','2018-06-19 05:42:58'),(64,'beeswax','0011_auto__chg_field_savedquery_name','2018-06-19 05:42:58'),(65,'beeswax','0012_auto__add_field_queryhistory_extra','2018-06-19 05:42:58'),(66,'beeswax','0013_auto__add_field_session_properties','2018-06-19 05:42:58'),(67,'beeswax','0014_auto__add_field_queryhistory_is_cleared','2018-06-19 05:42:58'),(68,'jobsub','0001_initial','2018-06-19 05:42:58'),(69,'jobsub','0002_auto__add_ooziestreamingaction__add_oozieaction__add_oozieworkflow__ad','2018-06-19 05:42:59'),(70,'jobsub','0003_convertCharFieldtoTextField','2018-06-19 05:42:59'),(71,'jobsub','0004_hue1_to_hue2','2018-06-19 05:42:59'),(72,'jobsub','0005_unify_with_oozie','2018-06-19 05:42:59'),(73,'jobsub','0006_chg_varchars_to_textfields','2018-06-19 05:42:59'),(74,'oozie','0026_set_default_data_values','2018-06-19 05:42:59'),(75,'oozie','0027_auto__chg_field_node_name__chg_field_job_name','2018-06-19 05:42:59'),(76,'search','0001_initial','2018-06-19 05:43:00'),(77,'search','0002_auto__del_core__add_collection','2018-06-19 05:43:00'),(78,'search','0003_auto__add_field_collection_owner','2018-06-19 05:43:00'),(79,'sqoop','0001_initial','2018-06-19 05:43:00'),(80,'useradmin','0001_permissions_and_profiles','2018-06-19 05:43:00'),(81,'useradmin','0002_add_ldap_support','2018-06-19 05:43:00'),(82,'useradmin','0003_remove_metastore_readonly_huepermission','2018-06-19 05:43:00'),(83,'useradmin','0004_add_field_UserProfile_first_login','2018-06-19 05:43:00'),(84,'useradmin','0005_auto__add_field_userprofile_last_activity','2018-06-19 05:43:00'),(85,'useradmin','0006_auto__add_index_userprofile_last_activity','2018-06-19 05:43:00'),(86,'useradmin','0007_remove_s3_access','2018-06-19 05:43:00'),(87,'notebook','0001_initial','2018-06-19 05:43:01');
/*!40000 ALTER TABLE `south_migrationhistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `useradmin_grouppermission`
--

DROP TABLE IF EXISTS `useradmin_grouppermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `useradmin_grouppermission` (
  `hue_permission_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `useradmin_grouppermission_9dd0e7a9` (`hue_permission_id`),
  KEY `useradmin_grouppermission_5f412f9a` (`group_id`),
  CONSTRAINT `group_id_refs_id_d2a5bba4` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `hue_permission_id_refs_id_53ff8024` FOREIGN KEY (`hue_permission_id`) REFERENCES `useradmin_huepermission` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `useradmin_grouppermission`
--

LOCK TABLES `useradmin_grouppermission` WRITE;
/*!40000 ALTER TABLE `useradmin_grouppermission` DISABLE KEYS */;
INSERT INTO `useradmin_grouppermission` VALUES (1,1,1),(2,1,2),(3,1,3),(5,1,4),(6,1,5),(7,1,6),(8,1,7),(10,1,8),(11,1,9),(12,1,10),(14,1,11),(15,1,12),(16,1,13),(17,1,14),(19,1,15),(20,1,16),(21,1,17),(22,1,18),(24,1,19),(25,1,20),(26,1,21),(27,1,22);
/*!40000 ALTER TABLE `useradmin_grouppermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `useradmin_huepermission`
--

DROP TABLE IF EXISTS `useradmin_huepermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `useradmin_huepermission` (
  `action` varchar(100) NOT NULL,
  `app` varchar(30) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `useradmin_huepermission`
--

LOCK TABLES `useradmin_huepermission` WRITE;
/*!40000 ALTER TABLE `useradmin_huepermission` DISABLE KEYS */;
INSERT INTO `useradmin_huepermission` VALUES ('access','about',1,'Launch this application'),('access','beeswax',2,'Launch this application'),('access','filebrowser',3,'Launch this application'),('s3_access','filebrowser',4,'Access to S3 from filebrowser and filepicker.'),('access','help',5,'Launch this application'),('access','impala',6,'Launch this application'),('access','jobbrowser',7,'Launch this application'),('access','jobsub',8,'Launch this application'),('write','metastore',9,'Allow DDL operations. Need the app access too.'),('access','metastore',10,'Launch this application'),('dashboard_jobs_access','oozie',11,'Oozie Dashboard read-only user for all jobs'),('access','oozie',12,'Launch this application'),('disable_editor_access','oozie',13,'Disable Oozie Editor access'),('access','pig',14,'Launch this application'),('access','proxy',15,'Launch this application'),('access','rdbms',16,'Launch this application'),('access','search',17,'Launch this application'),('impersonate','security',18,'Let a user impersonate another user when listing objects like files or tables.'),('access','security',19,'Launch this application'),('access','sqoop',20,'Launch this application'),('access_view:useradmin:view_user','useradmin',21,'Access to any profile page on User Admin'),('access_view:useradmin:edit_user','useradmin',22,'Access to profile page on User Admin'),('access','useradmin',23,'Launch this application'),('access','indexer',24,'Launch this application'),('write','metadata',25,'Allow edition of metadata like tags.'),('access','metadata',26,'Launch this application'),('access','notebook',27,'Launch this application');
/*!40000 ALTER TABLE `useradmin_huepermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `useradmin_ldapgroup`
--

DROP TABLE IF EXISTS `useradmin_ldapgroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `useradmin_ldapgroup` (
  `group_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `useradmin_ldapgroup_5f412f9a` (`group_id`),
  CONSTRAINT `group_id_refs_id_23c2c967` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `useradmin_ldapgroup`
--

LOCK TABLES `useradmin_ldapgroup` WRITE;
/*!40000 ALTER TABLE `useradmin_ldapgroup` DISABLE KEYS */;
/*!40000 ALTER TABLE `useradmin_ldapgroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `useradmin_userprofile`
--

DROP TABLE IF EXISTS `useradmin_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `useradmin_userprofile` (
  `home_directory` varchar(1024) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `creation_method` varchar(64) NOT NULL,
  `first_login` tinyint(1) NOT NULL,
  `last_activity` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `useradmin_userprofile_9cf27b62` (`last_activity`),
  CONSTRAINT `user_id_refs_id_e66f296b` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `useradmin_userprofile`
--

LOCK TABLES `useradmin_userprofile` WRITE;
/*!40000 ALTER TABLE `useradmin_userprofile` DISABLE KEYS */;
INSERT INTO `useradmin_userprofile` VALUES ('/user/admin',1,1,'HUE',0,'2018-06-19 06:15:51');
/*!40000 ALTER TABLE `useradmin_userprofile` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-06-19 18:10:09
