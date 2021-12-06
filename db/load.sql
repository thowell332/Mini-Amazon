\COPY Account (email, firstname, lastname, address, balance, password) FROM 'generated/Account.csv' WITH DELIMITER ',' NULL '' CSV;
\COPY Seller FROM 'generated/Seller.csv' WITH DELIMITER ',' NULL '' CSV;
\COPY Category FROM 'generated/Category.csv' WITH DELIMITER ',' NULL '' CSV;
\COPY Product (owner_id, description, name, image, category) FROM 'generated/Product.csv' WITH DELIMITER ',' NULL '' CSV;
\COPY SellsProduct FROM 'generated/SellsProduct.csv' WITH DELIMITER ',' NULL '' CSV;
\COPY SellsItem FROM 'generated/SellsItem.csv' WITH DELIMITER ',' NULL '' CSV;
-- \COPY Purchase FROM 'generated/Purchase.csv' WITH DELIMITER ',' NULL '' CSV;
-- \COPY SellerReview FROM 'generated/SellerReview.csv' WITH DELIMITER ',' NULL '' CSV;
-- \COPY ProductReview FROM 'generated/ProductReview.csv' WITH DELIMITER ',' NULL '' CSV;
\COPY Cart FROM 'generated/Cart.csv' WITH DELIMITER ',' NULL '' CSV;