create database rfm;
go

use rfm
go

drop table retail
go

CREATE TABLE retail (
    invoice_no VARCHAR(20) PRIMARY KEY,
    quantity INT,
    price DECIMAL(10,2),
    totalamount DECIMAL(12,2),
    customer_id VARCHAR(20),
    gender VARCHAR(10),
    age INT,
    payment_method VARCHAR(20),
    invoice_date DATE,
    day INT,
    month INT,
    quarter INT,
    year INT,
    category VARCHAR(50),
    shopping_mall VARCHAR(100)
);
go

BULK INSERT retail
FROM 'C:\Users\admin\Downloads\retail.csv'
WITH (
    FIRSTROW = 2, -- bỏ qua dòng tiêu đề
    FIELDTERMINATOR = ',', -- phân tách cột bằng dấu phẩy
    ROWTERMINATOR = '\n',
    TABLOCK
);


select * from retail;

ALTER LOGIN [json] WITH PASSWORD = '123456';