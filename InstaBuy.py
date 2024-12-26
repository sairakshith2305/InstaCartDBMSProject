import time
from getpass import getpass

import uuid

import pymysql
import bcrypt
import getpass
import tabulate

from AdminInstaBuy import Admin

customer_id_global = "placeholder"
p_cart_id = "placeholder"
delivery_id = "placeholder"

def connectToDB():
    while True:
        username = input("Enter your MySQL username: ").lower()
        password = getpass.getpass("Enter your MySQL password: ")

        print("Connecting to the MySQL database server...")

        try:
            # Try to establish a connection
            cnx = pymysql.connect(
                host='localhost',
                user=username,
                password=password,
                db='instabuy',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Connected!")
            return cnx

        except Exception:
            print("ERROR : Username or password is wrong. Please re-enter the details.")


def create_account(cnx):
    """Allow the user to create a new account."""
    username = input("Enter a username: ").lower()
    password = input("Enter a password: ")
    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")
    phone_number = input("Enter your phone number: ")
    email_id = input("Enter your email ID: ")

    cursor = cnx.cursor()

    try:
        queryUsername = "SELECT username FROM customer WHERE username = %s"
        cursor.execute(queryUsername, (username,))
        if cursor.fetchone():
            print("Username already exists. Try a different one.")
            return

        hashed_password = hash_password(password)

        cursor.callproc('addCustomer', (first_name, last_name, phone_number, email_id, username, hashed_password,))
        cnx.commit()
        print("Account created successfully!")
    except pymysql.MySQLError as e:
        if cnx:
            cnx.rollback()
            print("Database error:", e)
    except Exception as e:
        print("Error:", e)
        cnx.rollback()
    finally:
        cursor.close()


def login(cnx):
    username = input("Enter your username: ").lower()
    password = getpass.getpass("Enter your password: ")

    cursor = cnx.cursor()

    try:
        query = "SELECT password FROM customer WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        if not result:
            print("Username not found. Please create an account.")
            return -1

        hashed_password = result.get("password")

        if verify_password(password, hashed_password.encode('utf-8')):
            # set the global customer_id to keep track of the correct customer
            global customer_id_global
            query = "SELECT customer_id FROM customer WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            customer_id_global = result['customer_id']

            print()
            print(f"Welcome to InstaBuy, {username}!")
            if username == "admin":
                return "admin"
            return 1
        else:
            print("Invalid password. Please try again.")
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)


def displayCategoriesList(cnx):
    cursor = cnx.cursor()
    try:
        cursor.callproc("Retrieve_categories_list", ())
        results = cursor.fetchall()
        tabulateAndDisplayContent(results, cursor)

    except Exception:
        print("Error fetching categories!")


def getProducts(choice, cnx):
    cursor = cnx.cursor()
    try:
        cursor.callproc("retrieve_product_details", (choice,))
        rows = cursor.fetchall()

        tabulateAndDisplayContent(rows, cursor)

        cursor.close()

    except Exception as e:
        print("Error fetching product details!")


def addProductToCart(choice, cnx, quantity, i):
    # assuming customer_id is a global variable and we set the customer_id global variable when we login.
    cursor = cnx.cursor()
    try:
        cursor.callproc("AddProductToCart", (customer_id_global, choice, quantity,i))
        print("Successfully added product to cart!")
        cnx.commit()
    except Exception as e:
        print(e)
        print("Error adding product to cart!")


def showReviews(review_product_id, cnx):
    cursor = cnx.cursor()

    try:
        cursor.callproc("FetchReviews", (review_product_id,))
        rows = cursor.fetchall()
        tabulateAndDisplayContent(rows, cursor)
        cursor.close()
    except Exception as e:
        print("Error fetching product reviews!")
        cursor.close()


def getAvailableQuantity(choice, cnx):
    cursor = cnx.cursor()
    try:
        cursor.callproc("get_available_quantity", (choice,))
        rows = cursor.fetchall()
        quantity = rows[0]['quantity']
        return quantity
    except Exception:
        print("Could not fetch available quantity for the product")


def tabulateAndDisplayContent(rows, cursor):
    column_names = [desc[0] for desc in cursor.description]
    rows_as_lists = [list(row.values()) for row in rows]
    print(tabulate.tabulate(rows_as_lists, headers=column_names, tablefmt="grid"))


def fetchCartItems(cnx) :
    cursor = cnx.cursor()
    try:
        cursor.callproc("FetchCartItems", (customer_id_global, ))
        rows = cursor.fetchall()
        if not rows:
            return -1
        else:
            tabulateAndDisplayContent(rows, cursor)
        cursor.close()
    except Exception:
        print("Error fetching cart items!")
        cursor.close()


def updateCartItems(cnx):
    cursor = cnx.cursor()
    try:
        cursor.callproc("update_cart_on_removal", (customer_id_global,))
        print("Successfully updated Cart Items!")
        cnx.commit()
        cursor.close()
    except Exception as e:
        print("Error updating cart items!")
        cursor.close()

def deleteCartItems(cnx,productId):
    cursor = cnx.cursor()
    try :
        cursor.callproc("DeleteProductFromCart", (customer_id_global,productId,))
        print("Successfully deleted cart item!")
        cnx.commit()
        cursor.close()
    except Exception as e:
        print("Error deleting cart items!")
        cursor.close()


def checkWalletMoney(cnx, customer_id_global):
    cursor = cnx.cursor()
    try:
        cursor.callproc("FetchWalletBalance", (customer_id_global,))
        result = cursor.fetchone()
        cursor.close()
        return result['balance']
    except Exception as e:
        print("Error checking wallet money!")

def UpdateWalletBalance(cnx, customer_id_global, money):
    cursor = cnx.cursor()
    try:
        cursor.callproc("UpdateWalletBalance", (customer_id_global, money))
        cnx.commit()
    except Exception as e:
        print("Error updating wallet balance!")


def add_delivery_address(cnx, customer_id_global):
    cursor = cnx.cursor()
    Street_name = input("Street name: ")
    Street_number = input("Enter Street Number: ")
    City = input("Enter City: ")
    State = input("Enter State: ")
    zip_code = input("Enter Zip Code: ")
    global delivery_id
    delivery_id = uuid.uuid4()

    try:
        cursor.callproc("add_delivery_address",
                        (delivery_id, Street_number, Street_name, City, State, zip_code, customer_id_global))
        print("Successfully added delivery address!")
        cnx.commit()
        cursor.close()
        return 1
    except Exception as e:
        print("Error adding delivery address!")

def productExists(cnx, productID):
    try:
        cursor = cnx.cursor()
        cursor.callproc("CheckProductInCart", (customer_id_global, productID,))
        row_count = cursor.fetchone()
        if row_count is None:
            return False
        return True
    except Exception as e:
        print(e)
        print("Could not check if product exists!")

def updateProductToCart(cnx, productID, quantity):
    try:
        cursor = cnx.cursor()
        cursor.callproc("UpdateProductQuantityInCart", (customer_id_global, productID, quantity,))
        cnx.commit()
    except Exception as e:
        print(e)
        print("Could not update product to cart!")

def fetchTotalCartValue(cnx):
    cursor = cnx.cursor()
    try:
        cursor.callproc("FetchCartItems", (customer_id_global,))
        result = cursor.fetchall()
        totalSum = 0
        for row in result:
            totalSum += row['Total Price']
        cursor.close()
        return totalSum
    except Exception as e:
        print("Error fetching total cart amount!")

def getDeliveryStatus(cnx,delivery_id):
    try:
        cursor = cnx.cursor()
        cursor.callproc("GetDeliveryStatus", (customer_id_global,delivery_id,))
        result = cursor.fetchall()
        return result[0]['delivery_status']

    except Exception:
        print("Error fetching delivery status!")

def setDeliveryStatus(cnx, status,delivery_id):
    try:
        cursor = cnx.cursor()
        cursor.callproc("SetDeliveryStatus", (customer_id_global, status,delivery_id,))
        cnx.commit()
    except Exception:
        print("Error fetching delivery status!")

def getProductsInCart(cnx):
    cursor = cnx.cursor()
    try:
        cursor.callproc("GetProductIdsByCartId", (customer_id_global,))
        result = cursor.fetchall()
        cursor.close()
        values = [row['product_id'] for row in result]
        return values
    except Exception:
        print("Error getting product from cart!")

def clearCartValues(cnx):
    cursor = cnx.cursor()
    try:
        cursor.callproc("ClearCart", (customer_id_global,))
        cursor.close()
        cnx.commit()
    except Exception:
        print("Error in clearing cart values!")

def writeReview(cnx, productID) :
    cursor = cnx.cursor()

    inputRating = float(input("Enter the rating for the product (1-5): "))
    while inputRating > 5 or inputRating < 0:
        print("Please enter a rating between 1 and 5!")
        inputRating = int(input("Enter the rating for the product (1-5): "))

    inputTextComment = input("Enter the comment for the product: ")
    try :
        cursor.callproc("AddReview", (customer_id_global, productID, inputTextComment, inputRating,))
        print("Successfully written review!")
        cursor.close()
        cnx.commit()
    except Exception as e:
        print(e)
        print("Error writing review!")

def updatePaymentDetails(cnx, cartAmt):
    cursor = cnx.cursor()
    try:
        payment_id = uuid.uuid4()
        cursor.callproc("UpdatePayment", (payment_id, cartAmt, customer_id_global,))
        cnx.commit()
    except Exception:
        print("Error updating payment details!")

def checkProductAvailability(productID, cnx):
    cursor = cnx.cursor()
    try:
        query = "SELECT verify_product_exists(%s);"
        cursor.execute(query, (productID,))
        result = cursor.fetchone()
        result = result['verify_product_exists(' + str(productID) + ')']
        return result
    except Exception:
        print("Could not check product availability!")

def getLatestCategoryID(cnx):
    cursor = cnx.cursor()
    try:
        query = "SELECT get_latest_category_id();"
        cursor.execute(query, ())
        result = cursor.fetchone()
        return result['get_latest_category_id()']
    except Exception:
        print("Error fetching latest category ID!")

def quantityOfItemInCart(cnx,productID) :
    cursor = cnx.cursor()
    try :
        cursor.callproc("GetCartQuantity", (customer_id_global, productID,))
        result = cursor.fetchone()
        result = result['quantity']
        return result
    except Exception:
        print("Error getting cart quantity!")

def inputCheckForInt(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")

def isFloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def inputCheckForString(prompt):
    while True:
        user_input = input(prompt)
        if user_input.isdigit() or isFloat(user_input):
            print("Invalid input. Please enter a string.")
        else:
            return user_input


def postCartFlow (cnx) :
    while True:
        cartResult = fetchCartItems(cnx)
        if cartResult == -1:
            print("Cart is empty! Please add products to the cart")

        print("1. Update cart items")
        print("2. Delete cart items")
        print("3. Move to payment")

        if cartResult == -1 :
            print("4. Show categories")

        choice = inputCheckForInt("Choose an option: ")

        if choice == 1:
            print("1. Add more items to the cart")
            print("2. Remove more items from the cart")

            operation = inputCheckForInt("Enter your choice : ")
            productID = inputCheckForInt("Enter the product ID to be updated : ")
            quantity = inputCheckForInt("Enter the required quantity : ")

            updateQuantityForProductID = getAvailableQuantity(productID, cnx)

            existingProducts = getProductsInCart(cnx)

            if productID not in existingProducts:
                print("Invalid product ID! Please enter a Product ID present in cart")
                continue

            if (quantity > updateQuantityForProductID):
                print("Please enter a quantity less than " + str(updateQuantityForProductID))
                continue


            if operation == 1:
                updateProductToCart(cnx, productID, quantity)
            else:
                quantityOfItemInCartValue = quantityOfItemInCart(cnx, productID)
                if quantity == quantityOfItemInCartValue:
                    deleteCartItems(cnx, productID)
                else:
                    quantity = -1 * quantity
                    updateProductToCart(cnx, productID, quantity)
        elif choice == 2:
            productID = inputCheckForInt("Enter the product Id to be deleted from the cart : ")
            existingProductsForDelete = getProductsInCart(cnx)
            if productID not in existingProductsForDelete:
                print("Invalid product ID! Please enter a Product ID present in cart.")
                continue

            deleteCartItems(cnx, productID)
        elif choice == 3:
            paymentValue = fetchCartItems(cnx)
            if paymentValue == -1:
                print("Please add products to the cart !")
                return -1
            else:
                return 1
        elif choice == 4 and cartResult == -1:
            return -1
        else :
            print("Invalid choice!")


def main():
    cnx = connectToDB()

    while True:
        print("1. Create account")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            create_account(cnx)
        elif choice == "2":
            value = login(cnx)
            if value == 1:
                break
            elif value == "admin":
                admin = Admin(customer_id_global)
                admin.execute_admin_flow(cnx)
        elif choice == "3":
            print("Thank you for using the instaBuy Application!")
            exit(0)
        else:
            print("Invalid choice. Please try again.")

    # Display the list of categories
    while True:
        print()
        displayCategoriesList(cnx)
        print()

        choice_category = inputCheckForInt("Choose a category to select the products: ")

        if choice_category > getLatestCategoryID(cnx) or choice_category < 1 :
            print("Invalid choice. Try again.")
        else :
            # display the products based on the category
            print()
            print("1. Show products to add to cart")
            print("2. Show cart")
            option_products = inputCheckForInt("Enter your option: ")
            if option_products == 1:
                getProducts(choice_category, cnx)

                choice_reviews = inputCheckForString("See reviews for a product? (y/n): ")
                while choice_reviews.lower() not in ("y", "n", "yes", "no"): #error handling
                    print("Please enter y or n!")
                    choice_reviews = inputCheckForString("See reviews for a product? (y/n): ")

                while choice_reviews.lower() != "no" and choice_reviews.lower() != "n":
                    review_product_id = inputCheckForInt("Enter the product id to review: ")
                    showReviews(review_product_id, cnx)
                    choice_reviews = inputCheckForString("See reviews for another product? (y/n): ")
                    while choice_reviews.lower() not in ("y", "n", "yes", "no"): #error handling
                        print("Please enter y or n!")
                        choice_reviews = inputCheckForString("See reviews for another product? (y/n): ")

                choice = inputCheckForInt("Enter the product ID to be added to cart : ")
                productAvailable = checkProductAvailability(choice, cnx)
                while productAvailable == 0:
                    print("Product does not exist !!")
                    choice = inputCheckForInt("Choose an existing product to add to cart : ")
                    productAvailable = checkProductAvailability(choice, cnx)

                available_quantity_for_that_product = getAvailableQuantity(choice, cnx)

                quantity = inputCheckForInt("Enter the quantity of the product to be added to cart : ")

                if quantity > available_quantity_for_that_product:
                    print("Maximum quantity that can be added to cart is ", available_quantity_for_that_product)
                elif quantity < 0:
                    print("Quantity to be added cannot be less than zero!")
                else:
                    if productExists(cnx, choice):
                        updateProductToCart(cnx, choice, quantity)
                    else:
                        # query = "SELECT COUNT(*) FROM shopping_cart"
                        query = "SELECT get_latest_cart_instance_id()"
                        cursor = cnx.cursor()
                        cursor.execute(query, ())
                        row_count = cursor.fetchone()
                        rows = row_count['get_latest_cart_instance_id()']
                        if rows is None:
                            rows = 0
                        #generate cart_instance_id
                        rows += 1
                        addProductToCart(choice, cnx, quantity, rows)
            elif option_products == 2:
                fetchCartResult = fetchCartItems(cnx)
                if fetchCartResult != -1:
                    cartChoice = inputCheckForString("Do you want to move to cart? (y/n): ")
                    while cartChoice.lower() not in ("y", "n", "yes", "no"): #error handling
                        print("Please enter y or n!")
                        cartChoice = inputCheckForString("Do you want to move to cart? (y/n): ")

                    if (cartChoice.lower() == "yes") or (cartChoice.lower() == "y"):
                        print("Your cart is: ")
                        paymentOption = postCartFlow(cnx)
                        if paymentOption == 1:
                            break
                        else:
                            continue
                    else:
                        continue
                else:
                    print("Your cart is empty! Please add products to your cart.")
                    continue
            else:
                print("Invalid choice. Try again!")
                continue

            cartChoice = inputCheckForString("Do you want to move to cart? (y/n): ")
            while cartChoice.lower() not in ("y", "n", "yes", "no"):  # error handling
                print("Please enter y or n!")
                cartChoice = inputCheckForString("Do you want to move to cart? (y/n): ")
            if (cartChoice.lower() == "yes") or (cartChoice.lower() == "y"):
                print("Your cart is: ")
                paymentOption = postCartFlow(cnx)
                if paymentOption == 1:
                    break
                else:
                    continue
                break
            else:
                continue

    totalQuantityAmount = round(fetchTotalCartValue(cnx), 2)
    money = checkWalletMoney(cnx, customer_id_global)
    print()
    print("Your total cart value is : ", totalQuantityAmount)
    print("Wallet money available in your account is: ", money)

    while money - totalQuantityAmount < 0:
        print("Wallet balance is low to place this order !!")
        walletMoney = inputCheckForInt("Please enter the amount you want to add to your wallet: ")
        UpdateWalletBalance(cnx, customer_id_global, walletMoney)
        print("Successfully updated wallet balance!")
        money = checkWalletMoney(cnx, customer_id_global)
        print("Current wallet balance: ", money)

    updatedAmount = -1 * totalQuantityAmount
    UpdateWalletBalance(cnx, customer_id_global, updatedAmount)
    updatePaymentDetails(cnx, totalQuantityAmount)
    print()
    print("Payment was Successfully completed with wallet balance!")
    print()
    print("Please add your delivery address: ")
    status = add_delivery_address(cnx, customer_id_global)

    while status != 1:
        print("Please enter a valid address in the address fields!")
        print()
        status = add_delivery_address(cnx, customer_id_global)

    #Mocking the delivery activity in the program to simulate real world physical delivery.
    print("Delivery status: ", getDeliveryStatus(cnx,delivery_id))
    setDeliveryStatus(cnx, "IN-TRANSIT",delivery_id)
    time.sleep(2)
    print() #prints an empty line
    print("Delivery status: ", getDeliveryStatus(cnx,delivery_id))
    setDeliveryStatus(cnx, "DELIVERED",delivery_id)
    time.sleep(2)
    print() #prints an empty line
    print("Delivery status: ", getDeliveryStatus(cnx,delivery_id))

    #review the product
    reviewChoice = inputCheckForString("Would you like to review the product? (y/n) : ")
    while reviewChoice.lower() not in ("y", "n", "yes", "no"):  # error handling
        print("Please enter y or n!")
        reviewChoice = inputCheckForString("Would you like to review the product? (y/n) : ")

    if (reviewChoice.lower() == "yes") or (reviewChoice.lower() == "y"):
        existingProducts = getProductsInCart(cnx)
        for product in existingProducts:
            queryProductName = "SELECT product_name FROM product_instance where product_id = %s"
            cursor = cnx.cursor()
            cursor.execute(queryProductName, (product))
            result = cursor.fetchone()
            ratingsForEachProduct = inputCheckForString("Would you like to review : " + result['product_name'] + "(y/n) ? ")
            while ratingsForEachProduct.lower() not in ("y", "n", "yes", "no"):  # error handling
                print("Please enter y or n!")
                ratingsForEachProduct = inputCheckForString("Would you like to review : " + result['product_name'] + "(y/n) ? ")

            if (ratingsForEachProduct.lower() == "yes") or (ratingsForEachProduct.lower() == "y"):
                writeReview(cnx,product)

    clearCartValues(cnx)  # so that when a customer logs in again AFTER the payment cart has to be cleared.
    print("Thank you for using the instaBuy Application!")


if __name__ == "__main__":
    main()