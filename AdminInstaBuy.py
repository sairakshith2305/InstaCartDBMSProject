import csv
import os

import tabulate
from decimal import Decimal


class Admin :
    customer_id = ""
    def __init__(self, customer_id_global):
        self.customer_id = customer_id_global

    def isFloatAdmin(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def inputCheckForStringAdmin(self, prompt):
        while True:
            user_input = input(prompt)
            if user_input.isdigit() or self.isFloatAdmin(user_input):
                print("Invalid input. Please enter a string.")
            else:
                return user_input

    def inputCheckForIntAdmin(self, prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a number.")

    def tabulateAndDisplayContent(self, rows, cursor):
        column_names = [desc[0] for desc in cursor.description]
        rows_as_lists = [list(map(lambda x: float(x) if isinstance(x, Decimal) else x, row.values())) for row in rows]
        print(tabulate.tabulate(rows_as_lists, headers=column_names, tablefmt="grid"))

    def retrievePaymentDetails(self, cnx):
        cursor = cnx.cursor()
        try:
            customerID = self.inputCheckForIntAdmin("Enter the customerID whose payment details have to be retrieved: ")
            cursor.callproc("FetchPaymentDetails", (customerID,))
            results = cursor.fetchall()
            self.tabulateAndDisplayContent(results, cursor)
        except Exception:
            print("Error fetching customer's payment details!")

    def retrieveTurnover(self, cnx):
        cursor = cnx.cursor()
        try:
            print("The total company turnover is: ")
            cursor.callproc("get_turnover", ())
            result = cursor.fetchall()
            self.tabulateAndDisplayContent(result, cursor)
        except Exception:
            print("Error retrieving company turnover!")

    def deleteReview(self, cnx):

        reviewID = self.inputCheckForIntAdmin("Enter the review ID to delete: ")
        customerID = self.inputCheckForIntAdmin("Enter the ID of the customer who wrote the review: ")
        productID = self.inputCheckForIntAdmin("Enter the productID whose review has to deleted: ")

        cursor = cnx.cursor()
        try:
            cursor.callproc("delete_review", (reviewID, customerID, productID,))
            cnx.commit()
            print("Review successfully deleted!")
        except Exception:
            print("Error deleting the review!")

    def updateProductDetails(self, cnx):
        category_id = self.inputCheckForIntAdmin("Enter the category ID to update the products: ")
        print("Enter the product details to update the database: ")
        cursor = cnx.cursor()
        try:
            product_id = self.inputCheckForIntAdmin("Enter the product id of the item to be updated: ")
            quantity = self.inputCheckForIntAdmin("Enter the quantity of the product: ")
            product_name = input("Enter the name of the product: ")
            brand = self.inputCheckForStringAdmin("Enter the brand name of the product: ")
            cost = float(input("Enter the cost of the product: "))

            cursor.callproc("update_product", (product_id, quantity, product_name, brand, cost, category_id,))
            cnx.commit()
            print("Successfully updated product!")
        except Exception:
            print("Error updating product!")

    def deleteProduct(self, cnx):
        productID = self.inputCheckForIntAdmin("Enter the product id to delete from the database: ")
        cursor = cnx.cursor()
        try:
            cursor.callproc("delete_product", (productID,))
            print("Product successfully deleted !")
            cnx.commit()
        except Exception:
            print("Error deleting product!")

    def addProduct(self, cnx):
        category_id = self.inputCheckForIntAdmin("Enter the category ID to add the products: ")
        print("Enter the product details to add to the database: ")
        cursor = cnx.cursor()
        try:
            product_id = self.inputCheckForIntAdmin("Enter the product id: ")
            quantity = self.inputCheckForIntAdmin("Enter the quantity of the product: ")
            product_name = input("Enter the name of the product: ")
            brand = self.inputCheckForStringAdmin("Enter the brand name of the product: ")
            cost = float(input("Enter the cost of the product: "))

            cursor.callproc("add_new_product", (product_id, quantity, product_name, brand, cost, category_id,))
            print("Product successfully added!")
            cnx.commit()
        except Exception:
            print("Error adding new products!!")

    def addProductThroughCSV(self,cnx) :
        inputFile = self.inputCheckForStringAdmin("Enter the file location for the csv file: ")
        absolute_path = os.path.abspath(inputFile)
        cursor = cnx.cursor()
        try :
            with open(absolute_path, mode='r', newline='', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)# Create a CSV reader object
                for row in csv_reader:
                    product_id = row[0]
                    quantity = row[1]
                    product_name = row[2]
                    brand = row[3]
                    cost = row[4]
                    category_id = row[5]
                    cursor.callproc("add_new_product", (product_id, quantity, product_name, brand, cost, category_id,))
                    cnx.commit()
                print("Product successfully Uploaded!")

        except Exception as e:
            print(e)
            print("Error adding new products!!")



    def execute_admin_flow(self, cnx):
        print("Hey Admin !!")
        while True :
            print() #prints an empty line
            print("1. Add a product to existing category")
            print("2. Delete a product")
            print("3. Update a product")
            print("4. Delete a review")
            print("5. Retrieve company turnover")
            print("6. Retrieve payment details of a customer")
            print("7. Add products through csv file")
            print("8. Exit")

            # adminChoice = int(input("Enter your choice : "))
            adminChoice = self.inputCheckForIntAdmin("Enter your choice : ")

            if adminChoice == 1:
                self.addProduct(cnx)

            elif adminChoice == 2:
                self.deleteProduct(cnx)

            elif adminChoice  == 3:
                self.updateProductDetails(cnx)

            elif adminChoice == 4 :
                self.deleteReview(cnx)

            elif adminChoice == 5:
                self.retrieveTurnover(cnx)

            elif adminChoice == 6:
                self.retrievePaymentDetails(cnx)

            elif adminChoice == 7:
                print("Please make sure you have manually added the category mentioned in the csv to the database!")
                self.addProductThroughCSV(cnx)

            elif adminChoice == 8:
                print("Thank you!")
                exit(0)

            else :
                print("Wrong Choice !! Try Again")