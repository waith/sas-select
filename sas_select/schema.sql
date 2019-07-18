BEGIN TRANSACTION;
CREATE TABLE tbl_products (
    ID integer primary key,
    GroupID varchar,
    SASCode varchar,
    CompanyCode varchar,
    BrandName varchar,
    ProductDescription varchar,
    MaximumQty varchar,
    PackSize numeric,
    PackPrice numeric,
    PackPremium numeric
);
COMMIT;
