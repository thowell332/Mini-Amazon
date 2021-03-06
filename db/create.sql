CREATE TABLE Account
(account_id SERIAL NOT NULL PRIMARY KEY, -- System assigned
email VARCHAR(256) NOT NULL UNIQUE,
firstname VARCHAR(32) NOT NULL,
lastname VARCHAR(32) NOT NULL,
address VARCHAR(256) NOT NULL,
balance DECIMAL NOT NULL, -- 4 byte floating point number
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
price DECIMAL NOT NULL CHECK (price > 0),
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
seller_id INTEGER NOT NULL REFERENCES Seller(seller_id),
product_id INTEGER NOT NULL,
item_id INTEGER NOT NULL,
purchase_id INTEGER NOT NULL,
status INTEGER NOT NULL,
date TIMESTAMP WITH TIME ZONE NOT NULL,
price DECIMAL NOT NULL CHECK (price > 0),
PRIMARY KEY (buyer_id, product_id, item_id)
);
 
CREATE TABLE SellerReview
(buyer_id INTEGER NOT NULL REFERENCES Account(account_id),
 seller_id INTEGER NOT NULL REFERENCES Seller(seller_id),
 num_stars DECIMAL NOT NULL, -- # stars is float
 date TIMESTAMP NOT NULL,
 description VARCHAR(512), -- Can have stars with no description
 upvotes INTEGER NOT NULL,
 images TEXT[],
 PRIMARY KEY(buyer_id, seller_id)
);
 
CREATE TABLE ProductReview
(buyer_id INTEGER NOT NULL REFERENCES Account(account_id),
 product_id INTEGER NOT NULL REFERENCES Product(product_id),
 seller_id INTEGER NOT NULL REFERENCES Seller(seller_id),
 num_stars REAL NOT NULL,
 date TIMESTAMP NOT NULL,
 description VARCHAR(512),
 upvotes INTEGER NOT NULL,
 images TEXT[],
 PRIMARY KEY(buyer_id, product_id, seller_id)
);
 
CREATE TABLE Cart
(
buyer_id INTEGER NOT NULL REFERENCES Account(account_id),
seller_id INTEGER NOT NULL REFERENCES Seller(seller_id),
product_id INTEGER NOT NULL REFERENCES Product(product_id),
quantity INTEGER NOT NULL CHECK (quantity > 0),
saved_for_later BOOLEAN NOT NULL,
PRIMARY KEY (buyer_id, seller_id, product_id, saved_for_later)
);
 
CREATE FUNCTION Product_Reviewer() RETURNS TRIGGER AS $$
BEGIN 
	IF NOT (NEW.buyer_id IN (SELECT Purchase.buyer_id FROM Purchase WHERE Purchase.product_id = NEW.product_id AND Purchase.seller_id = NEW.seller_id)) THEN
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
	IF NOT (NEW.buyer_id IN (SELECT Purchase.buyer_id FROM Purchase WHERE Purchase.seller_id = NEW.seller_id AND Purchase.buyer_id = NEW.buyer_id)) THEN
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

CREATE FUNCTION One_Product_Review() RETURNS TRIGGER AS $one_product_review$
BEGIN 
	IF EXISTS(SELECT * FROM ProductReview WHERE NEW.buyer_id = ProductReview.buyer_id AND NEW.product_id = ProductReview.product_id AND NEW.seller_id = ProductReview.seller_id) THEN
	RAISE EXCEPTION 'A user cannot submit more than one rating/review for a single product';
	END IF;
	RETURN NEW;
END;
$one_product_review$ LANGUAGE plpgsql;

CREATE TRIGGER One_Product_Review
	BEFORE INSERT ON ProductReview 
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
	BEFORE INSERT ON SellerReview
	FOR EACH ROW
	EXECUTE PROCEDURE One_Seller_Review();
