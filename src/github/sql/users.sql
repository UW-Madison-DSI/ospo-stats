CREATE TABLE `users` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `login` varchar(128) DEFAULT NULL,
  `avatar_url` varchar(255) DEFAULT NULL,
  `html_url` varchar(255) DEFAULT NULL,
  `type` varchar(16) DEFAULT NULL,
  `score` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=161102717 DEFAULT CHARSET=utf8;