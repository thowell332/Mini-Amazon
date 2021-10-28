CREATE TABLE Account
(account_id SERIAL NOT NULL PRIMARY KEY, -- System assigned
email VARCHAR(256) NOT NULL UNIQUE,
name VARCHAR(32) NOT NULL,
balance DECIMAL NOT NULL, -- 4 byte floating point number
address VARCHAR(256) NOT NULL,
password VARCHAR(256) NOT NULL
);
 
CREATE TABLE Seller
(seller_id INTEGER NOT NULL PRIMARY KEY REFERENCES Account(account_id)
);
 
CREATE TABLE Category
(name VARCHAR(32) NOT NULL PRIMARY KEY 
);
 
CREATE TABLE Product
(product_id SERIAL NOT NULL PRIMARY KEY, -- Serial
 owner_id INTEGER NOT NULL REFERENCES Seller(seller_id),
 description VARCHAR(512) NOT NULL,
 name VARCHAR(256) NOT NULL UNIQUE,
 image VARCHAR(512) NOT NULL, -- Image URL
 category VARCHAR(32) NOT NULL REFERENCES Category (name)
);
 
CREATE TABLE SellsProduct
(
seller_id INTEGER NOT NULL REFERENCES Seller(seller_id),
product_id INTEGER NOT NULL REFERENCES Product(product_id),
price DECIMAL NOT NULL,
PRIMARY KEY (seller_id, product_id)
);

CREATE TABLE SellsItem
(
seller_id INTEGER NOT NULL,
product_id INTEGER NOT NULL,
item_id INTEGER NOT NULL,
PRIMARY KEY (product_id, item_id),
FOREIGN KEY(seller_id, product_id) REFERENCES SellsProduct(seller_id, product_id)
);

CREATE TABLE Purchase
(
buyer_id INTEGER NOT NULL REFERENCES Account(account_id),
product_id INTEGER NOT NULL,
item_id INTEGER NOT NULL,
purchase_id INTEGER NOT NULL,
status VARCHAR(32) NOT NULL,
date TIMESTAMP WITH TIME ZONE NOT NULL,
PRIMARY KEY (buyer_id, product_id, item_id),
FOREIGN KEY(product_id, item_id) REFERENCES SellsItem(product_id, item_id)
);
 
CREATE TABLE SellerReview
(buyer_id INTEGER NOT NULL REFERENCES Account(account_id),
 seller_id INTEGER NOT NULL REFERENCES Seller(seller_id),
 num_stars DECIMAL NOT NULL, -- # stars is float
 date TIMESTAMP NOT NULL,
 description VARCHAR(512), -- Can have stars with no description
 PRIMARY KEY(buyer_id, seller_id)
);
 
CREATE TABLE ProductReview
(buyer_id INTEGER NOT NULL REFERENCES Account(account_id),
 product_id INTEGER NOT NULL REFERENCES Product(product_id),
 num_stars REAL NOT NULL,
 date TIMESTAMP NOT NULL,
 description VARCHAR(512),
 PRIMARY KEY(buyer_id, product_id)
);
 
CREATE TABLE Cart
(
buyer_id INTEGER NOT NULL REFERENCES Account(account_id),
seller_id INTEGER NOT NULL REFERENCES Seller(seller_id),
product_id INTEGER NOT NULL REFERENCES Product(product_id),
quantity INTEGER NOT NULL,
PRIMARY KEY (buyer_id, seller_id, product_id)
);
 

CREATE FUNCTION Product_Reviewer() RETURNS TRIGGER AS $$
BEGIN 
	IF NOT (NEW.buyer_id IN (SELECT Purchase.buyer_id FROM Purchase WHERE Purchase.product_id = NEW.product_id)) THEN
       RAISE EXCEPTION 'Buyers cannot write reviews for products they have not  
       purchased';
       END IF;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;
 
CREATE TRIGGER Product_Reviewer
  BEFORE INSERT ON ProductReview
  FOR EACH ROW
  EXECUTE PROCEDURE Product_Reviewer();
 
CREATE FUNCTION TF_Seller_Reviewer() RETURNS TRIGGER AS $seller_review$
BEGIN
	IF NOT (NEW.buyer_id IN (SELECT Purchase.buyer_id FROM Purchase, SellsItem WHERE SellsItem.seller_id = NEW.seller_id AND Purchase.product_id = SellsItem.product_id AND Purchase.item_id = SellsItem.item_id)) THEN
	RAISE EXCEPTION 'Buyers cannot review sellers they have not bought from before';
	END IF;
	RETURN NEW;
END;
$seller_review$ LANGUAGE plpgsql;
 
CREATE TRIGGER TG_Seller_Reviewer
	BEFORE INSERT ON SellerReview
	FOR EACH ROW
	EXECUTE PROCEDURE TF_Seller_Reviewer();
 
CREATE FUNCTION TF_Cart_Product_Exists() RETURNS TRIGGER AS $cart_product_exists$
BEGIN
	IF NOT((NEW.seller_id, NEW.product_id) IN (SELECT seller_id, product_id FROM SellsProduct)) THEN
	RAISE EXCEPTION 'The product you placed in the cart is not listed by any seller';
	END IF;
	RETURN NEW;
END;
$cart_product_exists$ LANGUAGE plpgsql;
 
CREATE TRIGGER TG_Cart_Product_Exists
	BEFORE INSERT ON Cart
	FOR EACH ROW
	EXECUTE PROCEDURE TF_Cart_Product_Exists();
 
CREATE FUNCTION TF_Cart_Quantity_Available() RETURNS TRIGGER AS $cart_quantity_available$
BEGIN
	IF ((SELECT COUNT(*) FROM SellsItem WHERE NEW.product_id = SellsItem.item_id AND NEW.seller_id = SellsItem.seller_id) > NEW.quantity) THEN
	RAISE EXCEPTION 'The quantity you selected is not available';
	END IF;
	RETURN NEW;
END;
$cart_quantity_available$ LANGUAGE plpgsql;
 
CREATE TRIGGER TG_Cart_Quantity_Available
	BEFORE INSERT ON Cart
	FOR EACH ROW
	EXECUTE PROCEDURE TF_Cart_Quantity_Available();

CREATE FUNCTION One_Product_Review() RETURNS TRIGGER AS $one_product_review$
BEGIN 
	IF EXISTS(SELECT * FROM ProductReview WHERE NEW.buyer_id = ProductReview.buyer_id AND NEW.product_id = ProductReview.product_id) THEN
	RAISE EXCEPTION 'A user cannot submit more than one rating/review for a single product';
	END IF;
	RETURN NEW;
END;
$one_product_review$ LANGUAGE plpgsql;

CREATE TRIGGER One_Product_Review
	BEFORE INSERT OR UPDATE ON ProductReview
	FOR EACH ROW
	EXECUTE PROCEDURE One_Product_Review();

CREATE FUNCTION One_Seller_Review() RETURNS TRIGGER AS $one_seller_review$
BEGIN 
	IF EXISTS(SELECT * FROM SellerReview WHERE NEW.buyer_id = SellerReview.buyer_id AND NEW.seller_id = SellerReview.seller_id) THEN
	RAISE EXCEPTION 'A user cannot submit more than one rating/review for a single seller';
	END IF;
	RETURN NEW;
END;
$one_seller_review$ LANGUAGE plpgsql;

CREATE TRIGGER One_Seller_Review
	BEFORE INSERT OR UPDATE ON SellerReview
	FOR EACH ROW
	EXECUTE PROCEDURE One_Seller_Review();

--All ratings/reviews authored by the user in reverse chronological order
--SELECT * FROM ProductReview, SellerReview
--WHERE NEW.account_id = ProductReview.account_id
--ORDER BY date DESC

--List of ratings for product
--SELECT * FROM ProductReview 
--WHERE NEW.product_id = ProductReview.product_id
--ORDER BY ProductReview.num_stars DESC

--Average, number of ratings for product
--SELECT AVG(num_stars), COUNT(*) FROM ProductReview
--WHERE NEW.product_id = ProductReview.product_id


--List of ratings for seller
--SELECT * FROM SellerReview 
--WHERE NEW.seller_id = SellerReview.seller_id
--ORDER BY SellerReview.num_stars DESC

--Average, number of ratings for seller
--SELECT AVG(num_stars), COUNT(*) FROM SellerReview
--WHERE NEW.seller_id = SellerReview.seller_id