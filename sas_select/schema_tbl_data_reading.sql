BEGIN TRANSACTION;
DROP TABLE IF EXISTS tbl_data_reading;
CREATE TABLE tbl_data_reading (
    ID integer primary key,
    FileURL varchar,
    FileName varchar,
    ReadDate timestamp,
    LastScrapeDate timestamp
);
COMMIT;
