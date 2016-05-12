DROP TABLE IF EXISTS lj_pudong;
CREATE TABLE lj_pudong (
  guid CHAR(32) PRIMARY KEY,
  url TEXT,
  location TEXT,
  layout TEXT,
  area TEXT,
  size TEXT,
  buildtime TEXT,
  price TEXT,
  updated DATETIME
) DEFAULT CHARSET=utf8;
