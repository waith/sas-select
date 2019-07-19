BEGIN TRANSACTION;
DROP TABLE IF EXISTS tbl_products;
CREATE TABLE tbl_products (
    ID integer primary key,
    GroupID varchar,
    SASCode varchar,
    CompanyCode varchar,
    BrandName varchar,
    ProductDescription varchar,
    PackSize numeric,
    MaximumQty varchar,
    PackPrice numeric,
    PackPremium numeric
);
COMMIT;
